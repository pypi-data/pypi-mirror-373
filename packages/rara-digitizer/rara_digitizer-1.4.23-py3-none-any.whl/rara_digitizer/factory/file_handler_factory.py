import os

import magic

from .resource_manager import ResourceManager
from ..converters.doc2docx import DOCToDOCXConverter
from ..converters.img2pdf import ImageToPDFConverter
from ..exceptions import (
    NoMETSFileFound,
    MultipleMETSFilesFound,
    PathNotFound,
    UnsupportedFile,
    FileTypeOrStructureMismatch,
)
from ..handlers.base_handler import FileHandler
from ..handlers.docx_handler import DOCXHandler
from ..handlers.epub_handler import EPUBHandler
from ..handlers.html_handler import HTMLHandler
from ..handlers.metsalto_handler import METSALTOHandler
from ..handlers.pdf_handler import PDFHandler
from ..handlers.txt_handler import TXTHandler


class FileHandlerFactory:

    def __init__(
            self,
            base_dir: str = "./models",
            resource_manager: ResourceManager | None = None,
    ):
        """
        Factory for producing appropriate file handlers for a given file.

        Parameters
        ----------
        base_dir : str
            Path to the directory that holds all the resource files.

        resource_manager : ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.
        """
        self.base_dir = base_dir
        self.resource_manager = resource_manager or ResourceManager(self.base_dir)

    def _process_extraction_method(self, kwargs: dict, text_extraction_method: str) -> dict:
        if text_extraction_method == "auto":
            kwargs["force_ocr"] = False
            kwargs["force_text_layer_output"] = False

        elif text_extraction_method == "ocr":
            kwargs["force_ocr"] = True
            kwargs["force_text_layer_output"] = False

        elif text_extraction_method == "text_layer_extraction":
            kwargs["force_ocr"] = False
            kwargs["force_text_layer_output"] = True

        return kwargs

    def get_handler(self, file_or_folder_path: str, **kwargs) -> FileHandler:
        """
        Returns the appropriate file handler based on the file type (extension),
        and passes any extra keyword arguments to the handler.

        Parameters
        ----------
        file_or_folder_path : str
            The path to the file or folder.

        Keyword Arguments
        -----------------
        start_page : int, default = 1
            For paginated documents such as PDF and METS/ALTO, specifies the page to start processing from.

        max_pages : int, default = None
            For paginated documents such as PDF and METS/ALTO, specifies the maximum number of pages to process,
            starting from start_page.

        force_ocr : bool, default = False
            Whether to force OCR without evaluating text quality.

        text_quality_threshold : float, default = TEXT_QUALITY_THRESHOLD
            Threshold for assessing text quality; text with confidence below this value triggers OCR.

        ocr_confidence_threshold : float, default = OCR_CONFIDENCE_THRESHOLD
            Minimum confidence level required for OCR results; values below this result in alternate handling.

        lang : str, default = None
            Language used for OCR processing; determines the script and language-specific settings.

        text_extraction_method: str, default = "auto"
            Which text extraction method to use.

        text_length_cutoff : int, default = 30
            Minimum number of characters required to evaluate texts.

        evaluator_default_response : Any, default = None
            Default value used when evaluated text is shorter than text_length_cutoff

        tesseract_script_overrides : dict, default = {"Latin": "Latin", "Fraktur": "est_frak", "Cyrillic": "Cyrillic"}
            A mapping of language codes to specific Tesseract OCR script configurations for improved recognition.

        local_image_classifier_path: str, default = None
            Path to the directory containing the local image classifier model.

        enable_image_extraction : bool, default = True
            Whether to perform image extraction and classification during calls to
            extract_images() or extract_all_data().

        Raises
        ------
        PathNotFound
            If the file path for the file/folder isn't reachable.
        UnsupportedFile
            If the file type is unsupported.
        FileTypeOrStructureMismatch:
            In case the file type isn't parsable or the expected structure doesn't match requirements.

        Returns
        -------
        FileHandler
            A subclass of FileHandler appropriate for the file type, e.g., PDFHandler for '.pdf'.
        """

        if not os.path.exists(file_or_folder_path):
            raise PathNotFound(f"The path '{file_or_folder_path}' does not exist.")

        text_extraction_method = kwargs.pop("text_extraction_method", "auto")
        kwargs = self._process_extraction_method(kwargs, text_extraction_method)

        ext = os.path.splitext(file_or_folder_path)[-1].lower()
        if ext in (".doc",):
            converted_docx_path = DOCToDOCXConverter.convert(file_or_folder_path)
            return DOCXHandler(
                file_path=converted_docx_path,
                converted_doc=True,
                resource_manager=self.resource_manager,
                **kwargs,
            )

        if ext in (".docx",):
            return DOCXHandler(
                file_path=file_or_folder_path,
                resource_manager=self.resource_manager,
                **kwargs,
            )

        if ext in (".html", ".xml"):
            return HTMLHandler(
                file_path=file_or_folder_path, resource_manager=self.resource_manager
            )

        if ext in (".txt",):
            return TXTHandler(
                file_path=file_or_folder_path, resource_manager=self.resource_manager
            )

        if ext in (".jpg", ".jpeg", ".png"):
            converted_pdf_path = ImageToPDFConverter.convert(file_or_folder_path)
            return PDFHandler(
                file_path=converted_pdf_path,
                converted_image=True,
                resource_manager=self.resource_manager,
                **kwargs,
            )

        if ext in (".pdf",) and FileHandlerFactory._is_pdf_file(file_or_folder_path):
            return PDFHandler(
                file_path=file_or_folder_path,
                resource_manager=self.resource_manager,
                **kwargs,
            )

        if ext in (".epub",):
            return EPUBHandler(
                file_path=file_or_folder_path,
                resource_manager=self.resource_manager,
                **kwargs,
            )

        if os.path.isdir(file_or_folder_path):
            mets_folder_path = file_or_folder_path
            mets_file_path = FileHandlerFactory._find_mets_file_in_directory(
                file_or_folder_path
            )
            return METSALTOHandler(
                mets_folder_path=mets_folder_path,
                mets_file_path=mets_file_path,
                resource_manager=self.resource_manager,
                **kwargs,
            )

        if ext:
            raise UnsupportedFile(f"Unsupported file type: {ext}")

        raise FileTypeOrStructureMismatch(
            "No file type detected and no supported folder structure found."
        )

    @staticmethod
    def _is_pdf_file(file_path: str) -> bool:
        """
        Check if the given file is a PDF using python-magic.

        Parameters
        ----------
        file_path: str
            The path to the file.

        Returns
        -------
        bool
            True if the file is a PDF, False otherwise.
        """
        mime = magic.Magic(mime=True)
        file_mime_type = mime.from_file(file_path)
        return file_mime_type == "application/pdf"

    @staticmethod
    def _find_mets_file_in_directory(folder_path: str) -> str | None:
        """
        Check if the given folder contains a METS .xml document.

        Parameters
        ----------
        folder_path: str
            The path to the file.

        Returns
        -------
        str | None
           Returns the METS file path if the input is a METS/ALTO folder structure, None otherwise.
        """

        mets_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith("mets.xml"):
                    mets_files.append(os.path.join(root, file))

        if len(mets_files) == 0:
            raise NoMETSFileFound(
                "No METS files found. Input must contain a METS file."
            )

        if len(mets_files) > 1:
            raise MultipleMETSFilesFound(
                "Multiple METS files found. Input must contain only one METS file."
            )

        return mets_files[0]
