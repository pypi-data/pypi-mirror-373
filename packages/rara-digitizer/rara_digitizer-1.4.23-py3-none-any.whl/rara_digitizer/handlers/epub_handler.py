import logging
import re
import warnings
from io import BytesIO

import ebooklib
from PIL import Image
from bs4 import BeautifulSoup
from ebooklib import epub
from ebooklib.epub import EpubBook

from ..exceptions import NotLoadedOrEmpty
from ..factory.resource_manager import ResourceManager
from ..handlers.base_handler import FileHandler
from ..tools.image_classification import ImageClassificator
from ..tools.text_postproc import TextPostprocessor

logger = logging.getLogger("rara-digitizer")

# Optionally suppress FutureWarnings from ebooklib
warnings.filterwarnings("ignore", category=FutureWarning)


class EPUBHandler(FileHandler):
    def __init__(
        self, file_path: str, resource_manager: ResourceManager, **kwargs
    ) -> None:
        """
        Initializes the EPUBHandler by loading the EPUB document into `self.document`.

        Parameters
        ----------
        file_path : str
            The path to the EPUB file.

        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.

        Keyword Arguments
        -----------------
        text_length_cutoff: str
            Minimum length texts need to be evaluated.

        evaluator_default_response: Any
            Default quality value for texts that don't make the length cutoff.
        """
        self.resource_manager = resource_manager
        super().__init__(file_path, **kwargs)
        self.estimate_page_count = True
        self.document = self._read_epub()
        self.epub_metadata = self._extract_document_metadata()

        self.local_image_classifier_path = kwargs.get("local_image_classifier_path", None)
        self.image_classificator = ImageClassificator(
            resource_manager=self.resource_manager,
            local_image_classifier_path=self.local_image_classifier_path,
        )

        self.text_postprocessor = TextPostprocessor(self.resource_manager, **kwargs)

    def _read_epub(self) -> EpubBook:
        """
        Reads the EPUB file and stores the document in `self.document`.
        """
        try:
            return epub.read_epub(self.file_path, {"ignore_ncx": True})

        except Exception as e:
            logger.error(f"Error reading EPUB file: {e}")

    def requires_ocr(self) -> bool:
        """
        EPUB files do not require OCR.

        Returns
        -------
        bool
            Always returns False since EPUB files contain machine-readable text.
        """
        return False

    def extract_text(self) -> list[dict[str, str | int | None]]:
        """
        Extracts text from the EPUB file. Returns text by chapters.
        If self.estimate_page_count is set to True, the chapters are split into smaller chunks.

        Raises
        ------
        NotLoadedOrEmpty
            If the EPUB document has not been loaded.

        Returns
        -------
        list[dict[str, str | int | None]]
            The extracted text from the file, if extraction fails, returns [].
        """
        if not self.document:
            raise NotLoadedOrEmpty("EPUB document has not been loaded.")

        output = []
        for item_id, _ in self.document.spine:
            item = self.document.get_item_with_id(item_id)
            if item and item.media_type == "application/xhtml+xml":
                try:
                    content = item.get_content().decode("utf-8")
                    soup = BeautifulSoup(content, "lxml")
                    title = self._extract_title(soup)
                    text = soup.get_text(strip=False)
                    cleaned_text = self._clean_text(text)
                    if cleaned_text:
                        output.append(
                            {
                                "section_title": title if title else None,
                                "text": cleaned_text,
                            }
                        )
                except Exception as e:
                    logger.error(f"Error extracting text from EPUB: {e}")
                    return []

        return (
            self.text_postprocessor.postprocess_text(
                input_data=output,
                split_long_texts=self.estimate_page_count,
            )
            if output
            else []
        )

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        """
        Extracts the first heading (h1-h6) from the soup as the title.

        Parameters
        ----------
        soup : BeautifulSoup
            Extracted section content from the epub.

        Returns
        -------
        str | None
            The first heading with meaningful text (h1-h6) from the section content.
        """
        for heading_tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            for heading in soup.find_all(heading_tag):
                text = heading.get_text(strip=True)
                if text:
                    return self._clean_text(text)
        return None

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text.

        Parameters
        ----------
        text : str

        Returns
        -------
        str
            Cleaned text.
        """
        text = text.strip()
        text = text.replace("\xad", "")  # Remove soft hyphen
        text = text.replace(
            "\xa0", " "
        )  # Replace non-breaking space with a normal space
        text = text.replace("\r", "")  # Remove carriage return
        text = re.sub(
            r"\n+", "\n", text
        )  # Replace multiple consecutive newlines with a single newline
        text = re.sub(r" +", " ", text)  # Normalize multiple spaces to a single space
        text = re.sub(
            r"\n\s*\n", "\n", text
        )  # Replace empty lines in between with a single newline
        text = text.strip()
        return text

    def extract_images(self) -> list[dict[str, str | int | dict | None]]:
        """
        Extracts images from the EPUB file.

        Returns
        -------
        list[dict[str, str | int | dict | None]]
            A list of PIL Image objects representing the images in the EPUB file.
        """
        if not self.enable_image_extraction or not self.document:
            return []

        extracted_images = []
        try:
            for sequence_nr, item in enumerate(
                self.document.get_items_of_type(ebooklib.ITEM_IMAGE), start=1
            ):
                image_bytes = BytesIO(item.get_content())
                image = Image.open(image_bytes)
                image_data = {
                    "label": None,
                    "image_id": sequence_nr,
                    "coordinates": {
                        "HPOS": None,
                        "VPOS": None,
                        "WIDTH": None,
                        "HEIGHT": None,
                    },
                    "cropped_image": image,
                    "page": None,
                }
                extracted_images.append(image_data)
            clf_images = self.image_classificator.classify_extracted_images(
                extracted_images
            )
            clf_images = [
                {k: v for k, v in image.items() if k != "cropped_image"}
                for image in clf_images
            ]
            return clf_images
        except Exception as e:
            logger.error(f"Error extracting images from EPUB: {e}")
            return []

    def extract_page_numbers(self) -> None:
        """
        Extracts the total number of pages in the EPUB file. EPUB files do not have a concept of pages,
        so this method returns None. The method is defined to maintain consistency with the base class.

        Returns
        -------
        None
            Returns None as EPUB files do not have a concept of pages.
        """
        return None

    def extract_physical_dimensions(self) -> None:
        """
        Extracts the physical dimensions of the EPUB file. EPUB files generally do not have
        physical dimensions, but the method is defined to maintain consistency with the base class.

        Returns
        -------
        None
            Returns None as EPUB files do not have explicit physical dimensions.
        """
        return None

    def _extract_document_metadata(self):
        """
        Extracts the slice containing document metadata from the EPUB file.

        Returns
        -------
        dict | None
            A dictionary containing metadata extracted from the EPUB file.
        """
        try:
            return self.document.metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from the EPUB file: {e}")
