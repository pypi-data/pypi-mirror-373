import logging
from io import BytesIO
from typing import List, Dict, Union

from rara_text_evaluator.quality_evaluator import QualityEvaluator

from ..converters.pdf2img import PDFToCleanedIMGConverter
from ..factory.resource_manager import ResourceManager
from ..ocr.processors.ocr_processor import OCRProcessor
from ..utils.constants import TEXT_QUALITY_THRESHOLD, OCR_CONFIDENCE_THRESHOLD, TESSERACT_SCRIPT_OVERRIDES

logger = logging.getLogger("rara-digitizer")


class OCRStrategy:

    def __init__(
        self,
        resource_manager: ResourceManager,
        file_bytes: BytesIO | None = None,
        initial_text: list[dict[str, str | int | None]] | None = None,
        image_paths: list[str] | None = None,
        **kwargs,
    ):
        """
        Initializes OCRStrategyMixin with initial text, file path, configurations, and quality validator.

        Parameters
        ----------
        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.

        file_bytes : BytesIO
            Path to the document file (PDF or METS/ALTO).

        initial_text : List[Dict[str, Union[str, int, None]]]
            Initial machine-readable text from the document.

        image_paths : List[str]
            Pre-existing list of image paths for METS/ALTO files. Ignored for PDF files if `convert_to_images` is True.

        Keyword Arguments
        -----------------
        force_ocr : bool
            Whether to force OCR regardless of text quality.

        lang: str
            Default language for Tesseract OCR.

        ocr_confidence_threshold: float
            Threshold of OCR confidence. OCR output with confidence below this threshold will be filtered out.

        text_quality_threshold: float
            Threshold of text quality, beneath which the text is considered to be of low quality and requires OCR.

        text_length_cutoff: int
            Minimum length for a text to be considered for quality evaluation
        """
        self.resource_manager = resource_manager
        self.quality_evaluator: QualityEvaluator = resource_manager.quality_evaluator()
        self.initial_text = initial_text
        self._initial_text_evaluation = None
        self.file_bytes = file_bytes
        self.force_ocr = kwargs.get("force_ocr", False)
        self.force_text_layer_output = kwargs.get("force_text_layer_output", False)
        self.text_quality_threshold = kwargs.get(
            "text_quality_threshold", TEXT_QUALITY_THRESHOLD
        )
        self.text_length_cutoff = kwargs.get("text_length_cutoff", 30)
        self.lang = kwargs.get("lang", None)
        self.tesseract_script_overrides = kwargs.get(
            "tesseract_script_overrides",
            TESSERACT_SCRIPT_OVERRIDES,
        )
        self.ocr_confidence_threshold = kwargs.get(
            "ocr_confidence_threshold", OCR_CONFIDENCE_THRESHOLD
        )
        self._image_paths = image_paths if not file_bytes else None

        self._ocr_required = None
        self._ocr_processor = None

    @property
    def existing_image_paths(self) -> list[str] | None:
        return self._image_paths

    @property
    def image_paths(self) -> list[str] | None:
        """Returns the cached image paths, converting PDF to images if necessary.

        Returns
        -------
        list[str] | None
            List of image paths.
        """
        if self.file_bytes and not self._image_paths:
            self._convert_pdf_to_images()
        return self._image_paths

    def requires_ocr(self) -> bool:
        """
        Determines if OCR is needed based on the quality of the provided initial text.

        Returns
        -------
        bool
            True if OCR is required, False otherwise.
        """
        if self._ocr_required is not None:
            logger.info(f"OCR was previously determined to be {self._ocr_required}.")
            return self._ocr_required

        if self.force_ocr:
            logger.info("Forcing OCR due to `force_ocr` flag.")
            self._ocr_required = True
            return self._ocr_required

        if not self.initial_text:
            logger.info("No machine-readable text found; OCR is required.")
            self._ocr_required = True
            return self._ocr_required

        if self.force_text_layer_output:
            logger.info("Forcing initial text output due to `force_intial_text_output` flag.")
            self._ocr_required = False
            return self._ocr_required

        self._initial_text_evaluation = self._calculate_mean_text_quality(
            self.initial_text
        )
        logger.info(
            f"Initial text quality score: {self._initial_text_evaluation}, threshold: {self.text_quality_threshold}"
        )
        logger.info(
            f"OCR required: {self._initial_text_evaluation < self.text_quality_threshold}"
        )
        self._ocr_required = self._initial_text_evaluation < self.text_quality_threshold
        return self._ocr_required

    def _convert_pdf_to_images(self) -> None:
        """
        Converts the PDF file to images if OCR is deemed necessary.
        Sets the converted image paths in `self._image_paths`.

        Returns
        -------
        None
        """
        logger.info("Converting PDF pages to images for OCR processing.")
        pdf2img = PDFToCleanedIMGConverter()
        self._image_paths = pdf2img.clean_convert_document_to_temp_imgs(self.file_bytes)

    def perform_ocr_if_needed(self) -> list[dict[str, str | int | None]]:
        """
        Performs OCR if needed and rechecks if OCR text quality is better than the original.

        Returns
        -------
        list[dict[str, str | int | None]]
            Extracted text with the highest quality.
        """
        if self.requires_ocr():
            # Use existing images or convert to images if needed
            self._ocr_processor = OCRProcessor(
                self.image_paths,
                lang=self.lang,
                ocr_threshold=self.ocr_confidence_threshold,
                tesseract_scipt_overrides=self.tesseract_script_overrides,
            )
            ocr_text = self._ocr_processor.extract_ocr_text()
            if not ocr_text:
                return self.initial_text

            ocr_quality_score = self._calculate_mean_text_quality(ocr_text)
            if not self._initial_text_evaluation:
                self._initial_text_evaluation = self._calculate_mean_text_quality(
                    self.initial_text
                )

            if ocr_quality_score > self._initial_text_evaluation:
                logger.info(
                    f"OCR text quality ({ocr_quality_score}) exceeds "
                    f"original ({self._initial_text_evaluation}); using OCR text."
                )
                return ocr_text
            else:
                logger.info(
                    f"OCR text quality ({ocr_quality_score}) is lower than or equal "
                    f"to original ({self._initial_text_evaluation}); retaining original text."
                )
                self._ocr_required = False  # OCR had poor results, further calls to _requires_ocr() should be False
        return self.initial_text

    def _calculate_mean_text_quality(
        self, text_content: list[dict[str, str | int | None]]
    ) -> float:
        """
        Calculates the mean text quality score for the provided text content.
        Takes into account only text sections with `text_length_cutoff` or more characters,
        due to the minimum length required for quality evaluation.

        Parameters
        ----------
        text_content: list[dict[str, str | int | None]]
            List of dictionaries containing text from each page.

        Returns
        -------
        float
            Mean quality score for the text content.
        """
        if not text_content:
            return 0.0

        evaluable_text = [
            section["text"]
            for section in text_content
            if len(section["text"]) >= self.text_length_cutoff
        ]

        # If no text is equal to or more than `text_length_cutoff` characters, assume scanned document and perform OCR
        if not evaluable_text:
            return 0.0

        scores = [
            self.quality_evaluator.get_probability(text) for text in evaluable_text
        ]
        return round(sum(scores) / len(scores), 2) if scores else 0.0
