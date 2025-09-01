import json
import time

import pytest
from PIL import Image

from rara_digitizer.factory.file_handler_factory import FileHandlerFactory
from rara_digitizer.factory.resource_manager import ResourceManager
from rara_digitizer.tools.image_classification import ImageClassificator
from .utils import structure_check, check_image_data, check_language_data

TEST_GOOD_METS_ALTO = "data/test_data/mets_alto"
TEST_BAD_METS_ALTO = "data/test_data/bad_mets_alto"
TEST_PDF_OCR = "data/test_data/test_no_text_layer.pdf"
TEST_PDF_OCR_FRACTURE = "data/test_data/eesti_majandus_1921_07_lk_7.pdf"
TEST_PDF_TEXT_LAYER_1 = "data/test_data/test_with_text_layer.pdf"
TEST_PDF_TEXT_LAYER_2 = "data/test_data/0001.pdf"
TEST_EPUB = "data/test_data/liiv.epub"
TEST_DOC = "data/test_data/test.doc"
TEST_TXT = "data/test_data/test.txt"
TEST_JPG = "data/test_data/test.jpg"
TEST_HTML = "data/test_data/html/test.html"
TEST_HTML_DIR = "data/test_data/html"
TEST_XML = "data/test_data/test.xml"
TEST_SH = "data/test_data/test.sh"


def test_ocr_force_flag_pdf():
    """Tests whether force_ocr flag works on PDFs which otherwise wouldn't be OCR'd."""
    kwargs = {"max_pages": 2, "text_extraction_method": "ocr"}
    with FileHandlerFactory().get_handler(TEST_PDF_TEXT_LAYER_1, **kwargs) as handler:
        output = handler.extract_all_data()
    assert output["doc_meta"]["ocr_applied"] is True

    kwargs = {"max_pages": 2, "text_extraction_method": "text_layer_extraction"}
    with FileHandlerFactory().get_handler(TEST_PDF_TEXT_LAYER_1, **kwargs) as handler:
        output = handler.extract_all_data()
    assert output["doc_meta"]["ocr_applied"] is False

    kwargs = {"max_pages": 2, "text_extraction_method": "auto"}
    with FileHandlerFactory().get_handler(TEST_PDF_TEXT_LAYER_1, **kwargs) as handler:
        output = handler.extract_all_data()
    assert output["doc_meta"]["ocr_applied"] is False

def test_ocr_force_flag_metsalto():
    """Tests whether force_ocr flag works on METS/ALTO which otherwise wouldn't be OCR'd"""
    kwargs = {"start_page": 9, "max_pages": 1, "text_extraction_method": "ocr"}
    with FileHandlerFactory().get_handler(TEST_GOOD_METS_ALTO, **kwargs) as handler:
        output = handler.extract_all_data()

    # Output will be from original METS/ALTO, despite force_ocr being True, as its quality is better than OCR
    assert output["doc_meta"]["ocr_applied"] is False

    kwargs = {"max_pages": 1, "text_extraction_method": "ocr"}
    with FileHandlerFactory().get_handler(TEST_GOOD_METS_ALTO, **kwargs) as handler:
        output = handler.extract_all_data()

    # Output will be from OCR as its quality is better than OCR
    assert output["doc_meta"]["ocr_applied"] is True
    assert output["texts"][0]["text"].startswith("Läänemaal")
    assert output["texts"][-1]["text"].endswith("KAIRE REILJAN")

    kwargs = {"max_pages": 1, "text_extraction_method": "auto"}
    with FileHandlerFactory().get_handler(TEST_GOOD_METS_ALTO, **kwargs) as handler:
        output = handler.extract_all_data()

    # Output will be from original METS/ALTO as original text is good enough and OCR is not forced
    assert output["doc_meta"]["ocr_applied"] is False
    assert output["texts"][0]["text"].startswith("Lääne Elu")
    assert output["texts"][-1]["text"].endswith("Kaire Reiljan")


def test_mets_alto_ocr():
    """Tests METS/ALTO folder handling. Input document requires OCR due to poor text.
    Note that the input document has manipulated ALTO texts to simulate poor OCR quality.
    """
    with FileHandlerFactory().get_handler(
        TEST_BAD_METS_ALTO, **{"max_pages": 2}
    ) as handler:
        output = handler.extract_all_data()

    assert output["doc_meta"]["ocr_applied"] is True

    text_data = [text_meta for text_meta in output["texts"]]
    assert "Läänemaal" in text_data[0]["text"]
    assert (
        sum(text_meta["language"] == "et" for text_meta in text_data)
        > len(text_data) / 2
    )


def test_mets_alto_no_ocr():
    """Tests METS/ALTO folder handling. Input document has good enough text quality to not require OCR."""
    with FileHandlerFactory().get_handler(
        TEST_GOOD_METS_ALTO, **{"max_pages": 2}
    ) as handler:
        output = handler.extract_all_data()

    assert output["doc_meta"]["ocr_applied"] is False

    text_data = [text_meta for text_meta in output["texts"]]
    assert "Lääne Elu" in text_data[0]["text"]

    # Since the text is extracted in METS/ALTO blocks which are much shorter than pages
    # and can have different languages, just assume that most of the blocks are in Estonian
    assert (
        sum(text_meta["language"] == "et" for text_meta in text_data)
        > len(text_data) / 2
    )


def test_mets_alto_no_image_extraction():
    """Tests METS/ALTO folder handling without image extraction."""
    kwargs = {"enable_image_extraction": False}
    with FileHandlerFactory().get_handler(
        file_or_folder_path=TEST_GOOD_METS_ALTO, **kwargs
    ) as handler:
        output = handler.extract_all_data()

    check_language_data(output["doc_meta"]["languages"])

    metadata_json = json.dumps(output["doc_meta"]["mets_alto_metadata"], indent=4)
    assert isinstance(metadata_json, str)

    assert output["images"] == []
    check_image_data(output["images"], coordinates=False)


def test_pdf_ocr_fracture():
    """Tests PDF handling with OCR & fracture text."""
    with FileHandlerFactory().get_handler(
        TEST_PDF_OCR_FRACTURE,
    ) as handler:
        output = handler.extract_all_data()
        assert output["doc_meta"]["pages"]["count"] == 1

    structure_check(output)

    text_data = [text_meta for text_meta in output["texts"]]
    assert "pidiwad" in text_data[0]["text"]
    assert [text_meta["language"] for text_meta in text_data] == ["et"] * len(text_data)

    check_image_data(output["images"], coordinates=True)


def test_pdf_ocr():
    """Tests PDF handling for document without text layer. We limit max_pages, because OCR is slow..."""
    with FileHandlerFactory().get_handler(TEST_PDF_OCR, max_pages=2) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    check_language_data(output["doc_meta"]["languages"])

    assert output["doc_meta"]["pages"]["count"] == 2
    assert output["doc_meta"]["pages"]["is_estimated"] is False
    assert output["doc_meta"]["ocr_applied"] is True

    text_data = [text_meta for text_meta in output["texts"]]
    assert "EESTI MAJANDUS" in text_data[0]["text"]
    assert [text_meta["language"] for text_meta in text_data] == ["et"] * len(text_data)

    check_image_data(output["images"], coordinates=True)


def test_pdf_text_layer_compare_with_ocr():
    """Tests PDF handling from text layer. We limit max_pages, because OCR is slow..."""
    with FileHandlerFactory().get_handler(TEST_PDF_TEXT_LAYER_1, max_pages=2) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    check_language_data(output["doc_meta"]["languages"])

    assert output["doc_meta"]["pages"]["count"] == 2
    assert output["doc_meta"]["pages"]["is_estimated"] is False
    assert output["doc_meta"]["ocr_applied"] is False

    text_data = [text_meta for text_meta in output["texts"]]
    assert "EESTI VANIM" in text_data[0]["text"]
    assert [text_meta["language"] for text_meta in text_data] == ["et"] * len(text_data)

    check_image_data(output["images"], coordinates=True)


def test_pdf_text_layer_force_text_layer_output():
    """Tests PDF handling from text layer. We limit max_pages, because OCR is slow..."""
    kwargs = {"force_text_layer_output": False, "max_pages": 2}
    with FileHandlerFactory().get_handler(TEST_PDF_TEXT_LAYER_2, **kwargs) as handler:
        output = handler.extract_all_data()

    structure_check(output)

    assert output["doc_meta"]["pages"]["count"] == 2
    assert output["doc_meta"]["pages"]["is_estimated"] is False
    assert output["doc_meta"]["ocr_applied"] is False

    text_data = [text_meta for text_meta in output["texts"]]
    assert 'EESTI VABARIIGI\nAASTAPÄEVA  PIDULIK  AKTUS' in text_data[0]["text"]

    check_image_data(output["images"], coordinates=True)


def test_pdf_with_text_layer_no_image_extraction():
    """Tests PDF handling from text layer without image extraction."""
    kwargs = {"max_pages": 2, "enable_image_extraction": False}
    with FileHandlerFactory().get_handler(
        file_or_folder_path=TEST_PDF_TEXT_LAYER_1, **kwargs
    ) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    assert output["images"] == []
    check_image_data(output["images"], coordinates=False)


def test_epub():
    """Tests .epub handling."""
    with FileHandlerFactory().get_handler(TEST_EPUB) as handler:
        output = handler.extract_all_data()

    metadata_json = json.dumps(output["doc_meta"]["epub_metadata"], indent=4)
    assert isinstance(metadata_json, str)

    structure_check(output)
    check_language_data(output["doc_meta"]["languages"])

    assert output["doc_meta"]["physical_measurements"] is None
    assert output["doc_meta"]["pages"]["count"] is 47
    assert output["doc_meta"]["ocr_applied"] is False
    assert output["doc_meta"]["pages"]["is_estimated"] is True

    text_data = [text_meta for text_meta in output["texts"]]
    assert "Juhan Liiv" in text_data[0]["text"]
    assert [text_meta["language"] for text_meta in text_data] == ["et"] * len(text_data)

    check_image_data(output["images"], coordinates=False)


def test_epub_no_image_extraction():
    """Tests .epub handling without image extraction."""
    kwargs = {"enable_image_extraction": False}
    with FileHandlerFactory().get_handler(
        file_or_folder_path=TEST_EPUB, **kwargs
    ) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    assert output["images"] == []
    check_image_data(output["images"], coordinates=False)


def test_doc():
    """Tests .doc handling."""
    with FileHandlerFactory().get_handler(TEST_DOC) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    check_language_data(output["doc_meta"]["languages"])

    assert output["doc_meta"]["pages"]["is_estimated"] is True
    assert output["doc_meta"]["pages"]["count"] is 3
    assert output["doc_meta"]["ocr_applied"] is False

    text_data = [text_meta for text_meta in output["texts"]]
    assert "Lorem ipsum" in text_data[0]["text"]
    assert [text_meta["sequence_nr"] for text_meta in text_data] == list(
        range(1, len(text_data) + 1)
    )
    assert [text_meta["language"] for text_meta in text_data] == ["ca"] * len(text_data)

    check_image_data(output["images"], coordinates=False)


def test_doc_no_image_extraction():
    """Tests .doc handling without image extraction."""
    kwargs = {"enable_image_extraction": False}
    with FileHandlerFactory().get_handler(
        file_or_folder_path=TEST_DOC, **kwargs
    ) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    assert output["images"] == []
    check_image_data(output["images"], coordinates=False)


def test_txt():
    """Tests .txt handling."""
    with FileHandlerFactory().get_handler(TEST_TXT) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    check_language_data(output["doc_meta"]["languages"])

    assert output["doc_meta"]["pages"]["is_estimated"] is True
    assert output["doc_meta"]["pages"]["count"] is 4
    assert output["doc_meta"]["ocr_applied"] is False

    assert 0.0 <= output["doc_meta"]["text_quality"] <= 1.0
    assert (
        sum([len(text_data["text"]) for text_data in output["texts"]])
        == output["doc_meta"]["n_chars"]
    )

    text_data = output["texts"][0]
    assert "English\nThe sun" in text_data["text"]
    assert text_data["sequence_nr"] == 1
    assert text_data["start_page"] == 1
    assert text_data["end_page"] == 1
    assert text_data["language"] == "en"

    assert output["doc_meta"]["languages"] == [
        {"language": "et", "count": 2, "ratio": 0.5},
        {"language": "en", "count": 1, "ratio": 0.25},
        {"language": "de", "count": 1, "ratio": 0.25},
    ]

    assert output["images"] == []


def test_image_classifier():
    """Tests image classifier."""
    resource_manager = ResourceManager()
    clf = ImageClassificator(
        resource_manager=resource_manager,
    )

    classification_output = clf.classify_extracted_images(
        [
            {"label": "tabel", "cropped_image": Image.open(TEST_JPG)},
            {"label": "pilt", "cropped_image": Image.open(TEST_JPG)},
            {"label": None, "cropped_image": Image.open(TEST_JPG)},
        ]
    )

    assert (
        classification_output[0]["label"] == "tabel"
    )  # "Tabel" should be used as-is and not reclassified
    assert (
        classification_output[1]["label"] != "pilt"
    )  # "Pilt" isn't an allowed label, should be reclassified
    assert (
        classification_output[2]["label"] is not None
    )  # No label, should be classified
    assert (
        classification_output[2]["label"] == "graafika"
    )  # Label should be "graafika" for test picture


def test_jpg():
    """Tests .jpg handling."""
    with FileHandlerFactory().get_handler(TEST_JPG) as handler:
        output = handler.extract_all_data()

    structure_check(output)
    check_language_data(output["doc_meta"]["languages"])

    assert output["doc_meta"]["pages"]["count"] == 1
    assert output["doc_meta"]["pages"]["is_estimated"] is False

    assert len(output["images"]) > 0
    assert output["doc_meta"]["ocr_applied"] is True
    assert output["doc_meta"]["n_words"] == 0
    assert output["doc_meta"]["n_chars"] == 0
    assert output["texts"] == []

    check_image_data(output["images"], coordinates=True)


def test_html():
    """Tests .html handling."""
    with FileHandlerFactory().get_handler(TEST_HTML) as handler:
        output = handler.extract_all_data()

    check_language_data(output["doc_meta"]["languages"])
    assert output["doc_meta"]["pages"]["count"] == 4
    assert output["doc_meta"]["pages"]["is_estimated"] is True

    text_data = [text_meta for text_meta in output["texts"]]
    assert "Documentation" in text_data[0]["text"]
    assert [text_meta["language"] for text_meta in text_data] == ["en"] * len(text_data)

    assert output["images"] == []


def test_xml():
    """Tests .xml handling."""
    with FileHandlerFactory().get_handler(
        file_or_folder_path=TEST_XML,
    ) as handler:
        output = handler.extract_all_data()

    check_language_data(output["doc_meta"]["languages"])
    assert output["doc_meta"]["pages"]["is_estimated"] is True
    text_data = [text_meta for text_meta in output["texts"]]
    assert "Põltsamaalt" in text_data[0]["text"]
    assert [text_meta["language"] for text_meta in text_data] == ["et"] * len(text_data)

    assert output["images"] == []


def test_model_cache_being_used():
    factory = FileHandlerFactory()
    cacheless_start = time.time()
    with factory.get_handler(TEST_JPG) as handler:
        output = handler.extract_all_data()
    cacheless_end = time.time()

    cached_start = time.time()
    with factory.get_handler(TEST_JPG) as handler:
        output = handler.extract_all_data()
    cached_end = time.time()

    assert (cacheless_end - cacheless_start) > (cached_end - cached_start)
    assert factory.resource_manager.resource_cache != {}


def test_incorrect_dir():
    """We expect this test to fail, because the parser expects METS/ALTO formatted
    folder as ONLY type of folder input. We gave it some HTML to chew...
    """
    with pytest.raises(Exception) as exc_info:
        with FileHandlerFactory().get_handler(TEST_HTML_DIR) as handler:
            handler.extract_all_data()
    assert str(exc_info.value) == "No METS files found. Input must contain a METS file."


def test_unsupported_file():
    """We expect this test to fail, because the extension is so wrong."""
    with pytest.raises(Exception) as exc_info:
        with FileHandlerFactory().get_handler(TEST_SH) as handler:
            handler.extract_all_data()
    assert str(exc_info.value) == "Unsupported file type: .sh"


def test_using_custom_resource():
    import pathlib
    from rara_digitizer.factory.resources.base import Resource
    from rara_digitizer.factory.resource_manager import (
        ResourceManager,
        DEFAULT_RESOURCES,
    )

    class Huggingface(Resource):
        unique_key = "huggingface"
        resource_uri = "..."
        location_dir = "..."
        models = ["..."]
        default_model = "..."

        def __init__(self, base_directory: str, **kwargs):
            self.base_directory = pathlib.Path(base_directory)

        def download_resource(self):
            print("Downloading resource")

        def initialize_resource(self):
            print("Post load steps")

        def get_resource(self, **kwargs):
            return True

    huggingface_resource = Huggingface(base_directory="./models")
    resource_manager = ResourceManager(
        resources=[*DEFAULT_RESOURCES, huggingface_resource]
    )
    assert "huggingface" in resource_manager.initialized_resources
    assert isinstance(
        resource_manager.initialized_resources["huggingface"], Huggingface
    )
    assert resource_manager.get_resource("huggingface") is True


def test_limited_resource_initialization():
    class_paths = ["rara_digitizer.factory.resources.yolo.YOLOImageDetector"]
    resource_manager = ResourceManager(resources=class_paths)
    factory = FileHandlerFactory(resource_manager=resource_manager)
    assert len(factory.resource_manager.initialized_resources) == 1
