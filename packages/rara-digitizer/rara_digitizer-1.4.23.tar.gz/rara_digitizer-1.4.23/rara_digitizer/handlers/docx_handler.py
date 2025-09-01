import logging
import os
import zipfile
from io import BytesIO

from PIL import Image
from docx import Document

from ..exceptions import NotLoadedOrEmpty
from ..factory.resource_manager import ResourceManager
from ..handlers.base_handler import FileHandler
from ..tools.image_classification import ImageClassificator
from ..tools.text_postproc import TextPostprocessor

logger = logging.getLogger("rara-digitizer")


class DOCXHandler(FileHandler):

    def __init__(
        self,
        file_path: str,
        resource_manager: ResourceManager,
        converted_doc: bool = False,
        **kwargs,
    ) -> None:
        """
        Initializes the DOCXHandler by loading the DOCX document into `self.document`.

        Parameters
        ----------
        file_path : str
            The path to the DOCX file.

        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.

        converted_doc: bool
            Whether the DOCX file was converted from a DOC file.

        Keyword Arguments
        -----------------
        text_length_cutoff: str
            Minimum length texts need to be evaluated.

        evaluator_default_response: Any
            Default quality value for texts that don't make the length cutoff.
        """
        self.resource_manager = resource_manager
        super().__init__(file_path, **kwargs)
        self.converted_doc = converted_doc
        self.estimate_page_count = True
        self._read_docx()

        self.local_image_classifier_path = kwargs.get("local_image_classifier_path", None)
        self.image_classificator = ImageClassificator(
            resource_manager=self.resource_manager,
            local_image_classifier_path=self.local_image_classifier_path,
        )

        self.text_postprocessor = TextPostprocessor(self.resource_manager, **kwargs)

    def _read_docx(self) -> None:
        """
        Reads the DOCX file and stores the document in `self.document`.
        """
        try:
            self.document = Document(self.file_path)

            with open(self.file_path, "rb") as file:
                self.docx_zip_data = file.read()
        except Exception as e:
            logger.error(f"Error reading DOCX file: {e}")
            self.document = None
            self.docx_zip_data = None

    def _cleanup(self) -> None:
        """
        Remove the converted DOCX file if it was originally a DOC file.

        Returns
        -------
        None
        """
        if self.converted_doc:
            logger.info(
                f"Removing temporary DOCX file converted from original DOC {self.file_path}"
            )
            os.remove(self.file_path)

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
        Extracts text from the DOCX file using python-docx.

        Raises
        ------
        NotLoadedOrEmpty
            If the DOCX file has not been loaded.

        Returns
        -------
        list[dict[str, str | int | None]]
            The extracted text from the file, if extraction fails, returns [].
        """
        if not self.document:
            raise NotLoadedOrEmpty("DOCX document has not been loaded.")

        output = []
        for paragraph in self.document.paragraphs:
            text = paragraph.text
            if text:
                output.append(text)

        output = "\n".join(output)
        return (
            self.text_postprocessor.postprocess_text(
                input_data=output, split_long_texts=self.estimate_page_count
            )
            if output
            else []
        )

    def extract_images(self) -> list[dict[str, str | int | dict | None]]:
        """
        Extracts images from the in-memory DOCX file.

        Raises
        ------
        NotLoadedOrEmpty
            If there is no DOCX data to extract images from.

        Returns
        -------
        list[dict[str, str | int | dict | None]]
            A list of PIL Image objects representing the images in the DOCX file.
        """
        if not self.enable_image_extraction or not self.docx_zip_data:
            return []

        extracted_images = []
        sequence_nr = 1
        try:
            if not self.docx_zip_data:
                raise NotLoadedOrEmpty("No DOCX data to extract images from.")
            with zipfile.ZipFile(BytesIO(self.docx_zip_data), "r") as docx_zip:
                for file_info in docx_zip.infolist():
                    if file_info.filename.startswith("word/media/"):
                        image_bytes = BytesIO(docx_zip.read(file_info.filename))
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
                        sequence_nr += 1
            clf_images = self.image_classificator.classify_extracted_images(
                extracted_images
            )
            clf_images = [
                {k: v for k, v in image.items() if k != "cropped_image"}
                for image in clf_images
            ]
            return clf_images

        except Exception as e:
            logger.error(f"Error extracting images from DOCX: {e}")
            return []

    def extract_page_numbers(self) -> int | None:
        """
        Extracts the total number of pages in the file and stores it in the `self.page_count` attribute.

        Returns
        -------
        int | None
            Returns None as DOCX files do not have a concept of pages.
        """
        return None

    def extract_physical_dimensions(self) -> int | None:
        """
        Extracts the largest physical dimension of the DOCX and stores
        it in the `self.physical_dimensions` attribute.

        Returns
        -------
        int | None
            Returns None as DOCX files do not have explicit physical dimensions.
        """
        return None
