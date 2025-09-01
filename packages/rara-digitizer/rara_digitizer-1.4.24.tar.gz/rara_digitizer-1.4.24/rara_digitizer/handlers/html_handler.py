import logging
import re

from bs4 import BeautifulSoup

from ..exceptions import NotLoadedOrEmpty
from ..factory.resource_manager import ResourceManager
from ..handlers.base_handler import FileHandler
from ..tools.text_postproc import TextPostprocessor

logger = logging.getLogger("rara-digitizer")


class HTMLHandler(FileHandler):
    def __init__(
        self, file_path: str, resource_manager: ResourceManager, **kwargs
    ) -> None:
        """
        Initializes the HTMLHandler by loading the HTML document into `self.document`.

        Parameters
        ----------
        file_path : str
            The path to the HTML file.

        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.

        Keyword Arguments
        -----------------
        text_length_cutoff: str
            Minimum length texts need to be evaluated.

        evaluator_default_response: Any
            Default quality value for texts that don't make the length cutoff.
        """
        super().__init__(file_path)
        self.resource_manager = resource_manager
        self.text_postprocessor = TextPostprocessor(self.resource_manager, **kwargs)
        self.estimate_page_count = True
        self._read_html()

    def _read_html(self) -> None:
        """
        Reads the HTML file and stores the document in `self.document`.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                html_content = file.read()
            self.document = BeautifulSoup(html_content, "lxml")

        except Exception as e:
            logger.error(f"Error reading HTML file: {e}")
            self.document = None

    def requires_ocr(self) -> bool:
        """
        Determines if the file requires OCR for text extraction.

        Returns
        -------
        bool
            True if the file requires OCR, False otherwise.
        """
        return False

    def extract_text(self) -> list[dict[str, str | int | None]]:
        """
        Extracts plain output from the HTML file.

        Raises
        ------
        NotLoadedOrEmpty
            If the HTML document is not loaded or is empty.

        Returns
        -------
        list[dict[str, str | int | None]]
            The extracted text from the file, if extraction fails, returns [].
        """

        if not self.document:
            raise NotLoadedOrEmpty("HTML document has not been loaded or is empty.")

        output = self.document.get_text()
        cleaned_output = output.replace("\uf0c1", "")
        cleaned_output = cleaned_output.replace("\xa0", " ")
        cleaned_output = re.sub(r"\n{3,}", "\n", cleaned_output)
        lines = [line.strip() for line in cleaned_output.splitlines() if line.strip()]
        cleaned_output = "\n".join(lines)
        return (
            self.text_postprocessor.postprocess_text(
                input_data=cleaned_output, split_long_texts=self.estimate_page_count
            )
            if output
            else []
        )

    def extract_images(self) -> list[dict[str, str | int | dict | None]]:
        """
        Extracting HTML images is out of scope for this project. Returns an empty list.

        Returns
        -------
        list[dict[str, str | int | dict | None]]
            An empty list as no images are extracted from HTML files.
        """
        return []

    def extract_page_numbers(self) -> None:
        """
        There are no page numbers in HTML files, no pages extracted.

        Returns
        -------
        None
        """
        return None

    def extract_physical_dimensions(self) -> None:
        """
        HTML files do not have physical dimensions. Extracting physical dimensions returns None.

        Returns
        -------
        None
        """
        return None
