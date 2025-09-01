import json
import time

import pytest
from PIL import Image

from rara_digitizer.factory.file_handler_factory import FileHandlerFactory
from rara_digitizer.factory.resource_manager import ResourceManager
from rara_digitizer.tools.image_classification import ImageClassificator
from tests.utils import structure_check, check_image_data, check_language_data



TEST_GOOD_METS_ALTO = "data/test_data/mets_alto"
TEST_PDF_TEXT_LAYER = "data/test_data/0001.pdf"


def test_section_id_in_output_mets_alto():
    """Tests, if section_id is present in METS/ALTO output."""
    kwargs = {
        "enable_image_extraction": False, 
        "text_extraction_method": "text_layer_extraction"
    }
    with FileHandlerFactory().get_handler(
        file_or_folder_path=TEST_GOOD_METS_ALTO, **kwargs
    ) as handler:
        output = handler.extract_all_data()

    assert "section_id" in output["texts"][0]
    

def test_section_id_in_output_pdf():
    """Tests if section_id is present in PDF output."""
    kwargs = {
        "text_extraction_method": "text_layer_extraction", 
        "max_pages": 2, 
        "enable_image_extraction": False
    }
    with FileHandlerFactory().get_handler(TEST_PDF_TEXT_LAYER, **kwargs) as handler:
        output = handler.extract_all_data()

    assert "section_id" in output["texts"][0]

