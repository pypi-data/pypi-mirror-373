import logging
from abc import ABC, abstractmethod
from typing import Any, List
from rara_digitizer.utils.constants import REQUIRED_TEXT_SECTION_KEYS, TEXT_SECTION_KEY_DEFAULTS, EVALUATOR_DEFAULT_RESPONSE

logger = logging.getLogger("rara-digitizer")


class FileHandler(ABC):
    def __init__(self, file_path: str, **kwargs) -> None:
        """
        Initialize the FileHandler with a file path, and set up default attributes for images,
        page count, physical dimensions and pages (items to extract text from).

        Parameters
        ----------
        file_path : str
            The path to the file.
        """
        self.document: Any = None
        self.file_path = file_path

        self.alto_based_text_quality: float | None = None
        self.page_count: int | None = None
        self.physical_dimensions: int | None = None
        self.estimate_page_count: bool | None = None
        self.epub_metadata = None
        self.mets_alto_metadata = None
        self.enable_image_extraction: bool = kwargs.get("enable_image_extraction", True)
        self.evaluator_default_response: Any = kwargs.get("evaluator_default_response", EVALUATOR_DEFAULT_RESPONSE)

    def __enter__(self):
        """
        Context manager entry point.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point. Calls the _cleanup method.
        """
        self._cleanup()

    def _cleanup(self) -> None:
        """
        Do whatever cleanup is necessary for the file handler.
        This method is called when the file handler is exited.

        As this is not always necessary, the default implementation does nothing.

        Returns
        -------
        None
        """
        return None

    @abstractmethod
    def requires_ocr(self) -> bool:
        """
        Determines if the file requires OCR for text extraction.

        Returns
        -------
        bool
            True if the file requires OCR, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def extract_text(self) -> list[dict[str, str | int | None]]:
        """
        Extracts text from the file.

        Returns
        -------
        list[dict[str, str | int | None]]
            The extracted text from the file in format:
                - text: str
                - section_type: str | None
                - section_meta: str | None
                - section_title: str | None
                - start_page: int | None
                - end_page: int | None
                - sequence_nr: int | None
                - language: str | None
                - text_quality: int | None
                - n_words: int | None
                - n_chars: int | None
            If extraction fails, returns [].
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def extract_images(self) -> list[dict[str, str | int | dict | None]]:
        """
        Extracts images from the file and returns them as a list of dictionaries.

        Returns
        -------
        list[dict[str, str | int | dict | None]]
            A list of dictionaries for each image containing:
                - the image label,
                - the image id,
                - the coordinates as a dictionary containing HPOS, VPOS, WIDTH, HEIGHT,
                - the page number the image is on (if document has explicit pages).
            If not applicable - for example for .txt files - an empty list is returned.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def extract_page_numbers(self) -> int | None:
        """
        Extracts the total number of pages in the file and stores it in the `self.page_count` attribute.

        Returns
        -------
        int | None
            The total number of pages in the file, or None if extraction fails.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def extract_physical_dimensions(self) -> int | None:
        """
        Extracts the largest physical dimension of the document and stores
        it in the `self.physical_dimensions` attribute.

        Returns
        -------
        int | None
            An int representing the largest physical dimension of the document, or None if extraction fails.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def extract_all_data(self) -> dict[str, Any]:
        """
        Combines all extracted data into a single dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary containing all extracted data from the file.
        """
        logger.info(f"Extracting data from {self.file_path}:")
        logger.info("Extracting text...")
        texts = self.extract_text()

        logger.info("Extracting OCR requirement and text quality...")
        ocr_applied = self.requires_ocr()

        alto_based_text_quality = (
            round(self.alto_based_text_quality, 2)
            if self.alto_based_text_quality
            else None
        )
        evaluable_qualities = None
        if texts:
            evaluable_qualities = [
                t["text_quality"] for t in texts if t["text_quality"] != self.evaluator_default_response
            ]
            logger.info(
                f"Removed {len(texts) - len(evaluable_qualities)} texts not surpassing the requires length limit " \
                f"from final text quality evaluation."
            )
        text_quality = (
            round(sum(evaluable_qualities) / len(evaluable_qualities), 2)
            if evaluable_qualities
            else self.evaluator_default_response
        )
        if text_quality == self.evaluator_default_response:
            logger.info(
                f"Could not detect a single text surpassing the required length limit. " \
                f"Returning a default value for `text_quality`: {self.evaluator_default_response}."
            )

        logger.info("Extracting images...")
        images = self.extract_images()

        logger.info("Extracting physical dimensions...")
        physical_measurements = self.extract_physical_dimensions()

        logger.info("Extracting page numbers...")
        segment_count = 0
        if texts:
            segment_count = len(texts)
        page_count = self.extract_page_numbers() or segment_count

        logger.info("Calculating language statistics...")
        languages = self._compute_language_statistics(texts)
        texts = self._add_missing_keys(texts)

        return {
            "doc_meta": {
                "physical_measurements": physical_measurements,
                "pages": {
                    "count": page_count,
                    "is_estimated": self.estimate_page_count,
                },
                "alto_based_text_quality": alto_based_text_quality,
                "text_quality": text_quality,
                "ocr_applied": ocr_applied,
                "n_words": sum([text["n_words"] for text in texts]) if texts else 0,
                "n_chars": sum([text["n_chars"] for text in texts]) if texts else 0,
                "languages": languages,
                "mets_alto_metadata": (
                    self.mets_alto_metadata if self.mets_alto_metadata else None
                ),
                "epub_metadata": self.epub_metadata if self.epub_metadata else None,
            },
            "texts": texts,
            "images": images,
        }
    
    def _add_missing_keys(self, texts: List[dict]) -> List[dict]:
        """ Makes sure that all required keys are present in each 
        text section. If a missing key is detected, it will be added 
        with a default value.
        
        Parameters
        ------------
        texts: List[dict]
            List of dictionaries containing text data. 
            
        Returns:
        ------------
        List[dict]
            `texts` with previously missing keys.
        """
        
        for doc in texts:
            for key in REQUIRED_TEXT_SECTION_KEYS:
                if key not in doc:
                    default_value = TEXT_SECTION_KEY_DEFAULTS.get(key, None)
                    doc[key] = default_value
        return texts
        
    def _compute_language_statistics(
        self, texts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Computes statistics for languages in the document.

        Parameters
        ----------
        texts : list[dict[str, Any]]
            List of dictionaries containing text data.

        Returns
        -------
        list[dict[str, Any]]
            A list of dictionaries with language statistics, sorted by frequency.
        """
        if not texts:
            return []

        language_counts = {}
        for text in texts:
            lang = text.get("language")
            if lang not in language_counts:
                language_counts[lang] = 0
            language_counts[lang] += 1

        total_segments = sum(language_counts.values())

        statistics = []
        for lang, count in language_counts.items():
            ratio = round(count / total_segments, 3)
            statistics.append({
                "language": lang,
                "count": count,
                "ratio": ratio
            })

        statistics.sort(key=lambda x: x["count"], reverse=True)
        return statistics
