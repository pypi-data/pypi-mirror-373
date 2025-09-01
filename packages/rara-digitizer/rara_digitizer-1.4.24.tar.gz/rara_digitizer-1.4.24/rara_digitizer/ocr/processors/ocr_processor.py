import logging
from collections import defaultdict

import pytesseract
from pytesseract import TesseractError

from ...utils.constants import OCR_CONFIDENCE_THRESHOLD

logger = logging.getLogger("rara-digitizer")


class OCRProcessor:
    """
    Handles the OCR process by running PyTesseract on preprocessed images and extracting confident OCR data.
    """

    def __init__(
        self,
        image_file_paths: list[str],
        lang: str = None,
        ocr_threshold: float = OCR_CONFIDENCE_THRESHOLD,
        tesseract_scipt_overrides: dict[str, str] = None,
    ) -> None:
        """
        Initializes the OCRProcessor.

        Parameters
        ----------
        image_file_paths : list[str]
            A list of file paths to the images to perform OCR on.

        lang : str, default = None
            The language to use for OCR processing. If None, the script is detected and the language is set accordingly.

        ocr_threshold : float, default = OCR_CONFIDENCE_THRESHOLD
            The minimum confidence level required for outputting OCR results.

        tesseract_scipt_overrides : dict[str, str], default = None
            A mapping of language codes to specific Tesseract OCR script configurations for improved recognition.
        """
        self.__ocr_threshold = ocr_threshold

        self.image_file_paths = image_file_paths
        self.lang = lang
        self.tesseract_script_overrides = tesseract_scipt_overrides
        self.all_ocr_data = []

    @property 
    def ocr_threshold(self) -> float:
        # If the threshold is in range between 0 and 1,
        # convert it to scale 1-100
        if 0.0 <= self.__ocr_threshold < 1.0:
            _ocr_threshold = self.__ocr_threshold * 100 
        # If the threshold is in range between 1 and 100,
        # keep it as it is
        elif 1.0 < self.__ocr_threshold <= 100.0:
            _ocr_threshold = self.__ocr_threshold 
        # If the threshold is bigger than 100, set it to 
        # the actual max value (100)
        else:
            _ocr_threshold = 100.0
        return _ocr_threshold
        

    def extract_ocr_text(self) -> list[dict] | None:
        """
        Extracts text from the provided image file paths by reading them in and performing OCR.

        Returns
        -------
        list[dict] | None
            The extracted text from the OCR process, or None if extraction fails.
        """
        try:
            logger.info(f"Performing OCR on {len(self.image_file_paths)} images")
            self.run_ocr()

            confident_ocr_data = self.get_confident_ocr_data()
            return self._reconstruct_text_from_tesseract(confident_ocr_data)
        except Exception as e:
            logger.error(f"Error performing OCR on images: {e}")

    def run_ocr(self) -> list[dict]:
        """
        Runs OCR on a list of images, provided through file paths.

        Returns
        -------
        list[dict]
            A list of OCR data for each image.
        """
        for i, image_file_path in enumerate(self.image_file_paths, start=1):
            logger.info(f"Running OCR on image {i}/{len(self.image_file_paths)}")
            page_ocr_data = self._run_pytesseract(image_file_path)
            self.all_ocr_data.append(page_ocr_data)

        return self.all_ocr_data

    def _run_pytesseract(self, image_file_path: str) -> dict:
        """
        Provided an image file path, does OCR on the image using Pytesseract.

        If a language is specified, uses that language for OCR.
        Otherwise, detects the script of the text and changes the language parameter accordingly.

        The supported scripts are:
            Fraktur - fine-tuned variant of the base Fraktur model, using Estonian training data.
            Cyrillic - base Tesseract model for Cyrillic script.

        If the script is not one of the supported scripts, the default Latin script is used.

        Parameters
        ----------
        image_file_path : str
            The file path to the image to perform OCR on.

        Returns
        -------
        dict
            The OCR data extracted from the image.
        """
        if self.lang:  # Use specified language, otherwise check for various scripts
            logger.info(f"Running OCR on {image_file_path} with language '{self.lang}'")
            return pytesseract.image_to_data(
                image_file_path, lang=self.lang, output_type=pytesseract.Output.DICT
            )

        logger.info(f"Document language not specified. Detecting script for {image_file_path}")

        try:
            detected_script = pytesseract.image_to_osd(
                image_file_path, output_type="dict"
            )["script"]
        except TesseractError:
            detected_script = None

        # Override language if any of specified scripts are detected
        if detected_script in list(self.tesseract_script_overrides.keys()):
            page_lang = self.tesseract_script_overrides[detected_script]
            logger.info(
                f"Detected {detected_script} script. Using '{page_lang}.traineddata'"
            )
        else:
            page_lang = "Latin"
            logger.info(
                f"Detected script {page_lang} not in supported scripts. Using default Latin script."
            )

        return pytesseract.image_to_data(
            image_file_path, lang=page_lang, output_type=pytesseract.Output.DICT
        )

    def get_confident_ocr_data(self) -> list[dict]:
        """
        Filters out text with confidence below the threshold.
        Additionally, removes empty strings from the text data.

        Returns
        -------
        confident_ocr_data : list[dict]
            A list of OCR data, where each element is a dict containing OCR data for a page.
        """

        confident_ocr_data = []

        for page in self.all_ocr_data:
            confidence_list = page["conf"]
            text_list = page["text"]

            valid_indices = [
                i
                for i, (confidence, text) in enumerate(zip(confidence_list, text_list))
                if confidence >= self.ocr_threshold and not text.isspace()
            ]

            filtered_dict = {
                key: [value[i] for i in valid_indices] for key, value in page.items()
            }
            confident_ocr_data.append(filtered_dict)

        return confident_ocr_data

    def _reconstruct_text_from_tesseract(self, ocr_data: list[dict]) -> list[dict]:
        """
        Reconstruct text layout from Tesseract data for each page.

        Parameters
        ----------
        ocr_data : list[dict]
        A list containing a dictionary for each page in the document. Each dictionary has the following keys:
        - 'level': list[int] - The level of the text element (e.g., block, paragraph, line).
        - 'page_num': list[int] - The page number in the document.
        - 'block_num': list[int] - The block number of the text.
        - 'par_num': list[int] - The paragraph number within the block.
        - 'line_num': list[int] - The line number within the paragraph.
        - 'word_num': list[int] - The word number within the line.
        - 'left': list[int] - The x-coordinate of the text element's position.
        - 'top': list[int] - The y-coordinate of the text element's position.
        - 'width': list[int] - The width of the text element.
        - 'height': list[int] - The height of the text element.
        - 'conf': list[int] - The confidence level of the OCR for the text element.
        - 'text': list[str] - The actual text content extracted from the document.

        Returns
        -------
        document_content : list[dict]
            A list containing information about the text extracted from each page in the document.
            For each page the page number, section_meta (defaults to None) and
            text content is saved to be compatible with the other classes.
        """

        document_content = []

        for page_index, page in enumerate(ocr_data):
            blocks = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

            # Construct blocks from Tesseract data
            for i, word in enumerate(page["text"]):
                blocks[page["block_num"][i]][page["par_num"][i]][
                    page["line_num"][i]
                ].append((page["left"][i], word))

            # Format extracted page text
            page_text = "\n".join(
                "\n".join(
                    " ".join(
                        word
                        for _, word in sorted(blocks[b][p][line], key=lambda x: x[0])
                    )
                    for line in sorted(blocks[b][p])
                )
                for b in sorted(blocks)
                for p in sorted(blocks[b])
            )

            if not page_text.strip():
                continue

            document_content.append(
                {"page": page_index + 1, "section_meta": None, "text": page_text}
            )
        return document_content
