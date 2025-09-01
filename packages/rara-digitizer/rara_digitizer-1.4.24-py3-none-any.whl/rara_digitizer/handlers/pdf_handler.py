import logging
import os
import re
from io import BytesIO

import pypdf

from ..exceptions import NotLoadedOrEmpty, PageOutOfRange
from ..factory.resource_manager import ResourceManager
from ..handlers.base_handler import FileHandler
from ..tools.image_classification import ImageClassificator
from ..tools.ocr_strategy import OCRStrategy
from ..tools.text_postproc import TextPostprocessor

logger = logging.getLogger("rara-digitizer")


class PDFHandler(FileHandler):
    def __init__(
            self, file_path: str, resource_manager: ResourceManager, **kwargs
    ) -> None:
        """
        Initializes the PDFHandler by loading the PDF document into `self.document`.
        If the user provides a subset of pages, it handles the selection of pages for extraction.

        Parameters
        ----------
        file_path: str
            The path to the PDF file.

        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.

        Keyword Arguments
        -----------------
        force_ocr: bool
            Whether to force OCR on the PDF file.

        start_page: int
            The page number to start extracting from (1-based).

        max_pages: int | None
            The maximum number of pages to extract (from start_page).

        converted_image: bool
            Whether the PDF file was originally an image file.

        text_length_cutoff: str
            Minimum length texts need to be evaluated.

        evaluator_default_response: Any
            Default quality value for texts that don't make the length cutoff.
        """
        super().__init__(file_path, **kwargs)

        self.resource_manager = resource_manager
        self.image_processor = resource_manager.image_processor()

        self.start_page = max(
            1, kwargs.get("start_page", 1)
        )  # Ensure start_page is indexed from 1
        self.max_pages = kwargs.get("max_pages", None)
        self._converted_image = kwargs.get("converted_image", False)
        self.estimate_page_count = False

        self._pdf_bytes = self._read_pdf()
        self.document = pypdf.PdfReader(self._pdf_bytes)

        initial_text = self._extract_machine_readable_text()

        self.ocr_strategy = OCRStrategy(
            file_bytes=self._pdf_bytes,
            initial_text=initial_text,
            convert_to_images=True,
            resource_manager=self.resource_manager,
            **kwargs,
        )

        self.local_image_classifier_path = kwargs.get("local_image_classifier_path", None)
        self.image_classificator = ImageClassificator(
            resource_manager=self.resource_manager,
            local_image_classifier_path=self.local_image_classifier_path
        )

        self.text_postprocessor = TextPostprocessor(self.resource_manager, **kwargs)

    def _read_pdf(self) -> BytesIO:
        """
        Reads the PDF file and stores the document in `self.document`. If a subset of pages is requested,
        it extracts only the specified pages and stores the result in-memory.

        Raises
        ------
        PageOutOfRange
            If the start page is out of range for the PDF file.

        Returns
        -------
        BytesIO
            The extracted PDF file as a BytesIO object.
        """
        reader = pypdf.PdfReader(self.file_path)
        writer = pypdf.PdfWriter()

        # Adjust page range to zero-based for pypdf
        start_page_idx = self.start_page - 1
        end_page_idx = (
            start_page_idx + self.max_pages if self.max_pages else len(reader.pages)
        )

        if start_page_idx >= len(reader.pages):
            raise PageOutOfRange(
                f"Start page {self.start_page} is out of range for the PDF file."
            )

        # Extract only the required pages
        for i in range(start_page_idx, min(end_page_idx, len(reader.pages))):
            writer.add_page(reader.pages[i])

        try:
            pdf_bytes = BytesIO()
            writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")

    def _cleanup(self) -> None:
        """
        Remove the converted PDF file if it was originally an image file.
        """
        if self._converted_image:
            logger.info("Removing temporary PDF file converted from image.")
            os.remove(self.file_path)

        if self.ocr_strategy.existing_image_paths:
            logger.info("Removing temporary image files.")
            for img_path in self.ocr_strategy.existing_image_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)

    def _extract_machine_readable_text(self) -> list[dict] | None:
        """
        Extracts machine-readable text from the PDF.

        Returns
        -------
        list[dict] | None
            The extracted text from the PDF file, or None if extraction fails.
        """
        try:
            text_content = []
            for i, page in enumerate(self.document.pages, start=1):
                text = page.extract_text()
                text = self._clean_text(text) if text else None
                if text:
                    text_content.append({"page": i, "text": text})
            return text_content if len(text_content) > 0 else None

        except Exception as e:
            logger.error(f"Error extracting machine-readable text from PDF: {e}")

    def _clean_text(self, text: str) -> str:
        """
        Clean the text from artifacts.

        Parameters
        ----------
        text : str
            Text to clean.

        Returns
        -------
        text : str
            Cleaned text.
        """
        # Remove specific unwanted Unicode characters
        text = text.replace("\u0e00", " ")
        # Remove cid codes
        text = re.sub(r"\(cid:\d+\)", "", text)
        # Remove redundant space before closing brackets
        text = re.sub(r"\s+(?=[)\]}])", "", text)
        return text

    def requires_ocr(self) -> bool:
        """
        Determines if the file requires OCR for text extraction.

        Returns
        -------
        bool
            True if the file requires OCR, False otherwise.
        """
        return self.ocr_strategy.requires_ocr()

    def extract_text(self) -> list[dict[str, str | int | None]]:
        """
        Extracts text from the PDF file by determining if OCR is required or if the text is machine-readable.

        Returns
        -------
        list[dict[str, str | int | None]]
            The extracted text from the file, if extraction fails, returns [].
        """
        if not self.document:
            raise NotLoadedOrEmpty("PDF document is not loaded.")

        output = self.ocr_strategy.perform_ocr_if_needed()
        return (
            self.text_postprocessor.postprocess_text(
                input_data=output, split_long_texts=self.estimate_page_count
            )
            if output
            else []
        )

    def extract_images(self) -> list[dict[str, str | int | dict | None]]:
        """
        Extracts images from the PDF file.

        Returns
        -------
        list[dict[str, str | int | dict | None]]
            A list of dictionaries containing the metadata of the extracted images.
        """
        if not self.enable_image_extraction or not self.document:
            return []
        extracted_images = []
        for page_nr, img_file_path in enumerate(self.ocr_strategy.image_paths, start=1):
            detected_labels_and_regions = self.image_processor.detect_regions(
                img_file_path
            )
            for image_id, dlr in enumerate(detected_labels_and_regions):
                if dlr["label"] not in ["Picture", "Table"]:
                    continue
                if dlr["label"] == "Table":
                    dlr["label"] = "Tabel"
                page_images_and_tables = {
                    "label": dlr["label"].lower(),
                    "image_id": image_id,
                    "coordinates": {
                        "HPOS": dlr["HPOS"],
                        "VPOS": dlr["VPOS"],
                        "WIDTH": dlr["WIDTH"],
                        "HEIGHT": dlr["HEIGHT"],
                    },
                    "cropped_image": dlr["cropped_image"],
                    "page": page_nr,
                }
                extracted_images.append(page_images_and_tables)
        clf_images = self.image_classificator.classify_extracted_images(
            extracted_images
        )
        clf_images = [
            {k: v for k, v in image.items() if k != "cropped_image"}
            for image in clf_images
        ]
        return clf_images

    def extract_page_numbers(self) -> int | None:
        """
        Extracts the total number of pages in the subset of the PDF (based on start_page and max_pages)
        and stores it in the `self.page_count` attribute.

        Raises
        ------
        NotLoadedOrEmpty
            If the PDF document has not been loaded

        Returns
        -------
        int | None
            The total number of pages in the subset of the PDF file, or None if extraction fails.
        """
        if not self.document:
            raise NotLoadedOrEmpty("PDF document is not loaded.")

        self.page_count = len(self.document.pages)
        return self.page_count

    def extract_physical_dimensions(self) -> int | None:
        """
        Extracts the largest physical dimension (cm) of the PDF and stores
        it in the `self.physical_dimensions` attribute.

        Returns
        -------
        int | None
            An int representing the largest physical dimension (cm) of the document, or None if extraction fails.
        """
        if self._converted_image:
            return None

        try:
            page = self.document.pages[0]
            largest_dim = max(page.mediabox.width, page.mediabox.height)
            # Convert points to inches (1 point = 1/72 inches)
            largest_dim_inches = largest_dim / 72
            # Convert inches to centimeters (1 inch = 2.54 cm)
            largest_dim_cm = largest_dim_inches * 2.54
            self.physical_dimensions = round(largest_dim_cm)
            return self.physical_dimensions

        except Exception as e:
            logger.error(f"Error extracting physical dimension from PDF: {e}")
            return None
