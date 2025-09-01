import logging
import os
import warnings
from collections import defaultdict
from urllib.parse import urlparse
from typing import List

import numpy as np
from PIL import Image
from bs4 import BeautifulSoup, Tag

from rara_digitizer.utils.constants import (
    LOOKUP_METSALTO_SECTIONS,
    METS_META_IDS,
    METS_FILEGROUP_PATTERNS,
    METSALTO_IMG_LABELS,
    KEEP_METSALTO_IMG_LABELS,
)
from ..factory.resource_manager import ResourceManager
from ..handlers.base_handler import FileHandler
from ..tools.image_classification import ImageClassificator
from ..tools.ocr_strategy import OCRStrategy
from ..tools.text_postproc import TextPostprocessor

logger = logging.getLogger("rara-digitizer")

warnings.filterwarnings("ignore", category=FutureWarning)


class METSALTOHandler(FileHandler):
    def __init__(
        self,
        mets_folder_path: str,
        mets_file_path: str,
        resource_manager: ResourceManager,
        **kwargs,
    ) -> None:
        """
        Initializes the METSALTOHandler by loading the METS content into `self.document` and ALTO content into
        `self.pages`.

        Parameters
        ----------
        mets_folder_path: str
            The path to the METS/ALTO root folder.

        mets_file_path: str
            The path to the METS file.

        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.

        Keyword Arguments
        -----------------
        text_length_cutoff: str
            Minimum length texts need to be evaluated.

        evaluator_default_response: Any
            Default quality value for texts that don't make the length cutoff.
        """
        super().__init__(mets_file_path, **kwargs)
        self.resource_manager = resource_manager
        self.mets_folder_path = mets_folder_path
        self.mets_path = mets_file_path
        self.document = self._read_mets()
        self.estimate_page_count = False

        self.start_page = (
            max(1, kwargs.get("start_page", 1)) - 1
        )  # Ensure start_page is indexed from 0
        self.end_page = (
            self.start_page + kwargs.get("max_pages", 0)
            if kwargs.get("max_pages", 0)
            else None
        )
        self.lookup_metsalto_sections = kwargs.get(
            "lookup_metsalto_sections", LOOKUP_METSALTO_SECTIONS
        )
        self.mets_meta_ids = kwargs.get("mets_meta_ids", METS_META_IDS)
        self.mets_filegroup_patterns = kwargs.get(
            "mets_filegroup_patterns", METS_FILEGROUP_PATTERNS
        )
        self.metsalto_img_labels = kwargs.get(
            "metsalto_img_labels", METSALTO_IMG_LABELS
        )
        self.keep_metsalto_img_labels = kwargs.get(
            "keep_metsalto_img_labels", KEEP_METSALTO_IMG_LABELS
        )

        self.alto_paths = self._parse_file_group("alto")
        self.alto_image_paths = self._parse_file_group("images")
        self.pages = self._read_alto()
        self.alto_id_to_page_nr = self._create_alto_id_to_page_nr_dict()
        self.mets_alto_metadata = self._extract_document_metadata()
        self.alto_based_text_quality = self._calculate_mean_wc_from_soups(
            list(self.pages.values())
        )

        self.ocr_strategy = OCRStrategy(
            resource_manager=self.resource_manager,
            initial_text=self.extract_text_from_metsalto(),
            image_paths=list(self.alto_image_paths.values()),
            **kwargs,
        )

        self.local_image_classifier_path = kwargs.get("local_image_classifier_path", None)
        self.image_classificator = ImageClassificator(
            resource_manager=self.resource_manager,
            local_image_classifier_path=self.local_image_classifier_path,
        )

        self.text_postprocessor = TextPostprocessor(self.resource_manager, **kwargs)

    def _load_xml_content(self, xml_file_path: str) -> BeautifulSoup | None:
        """
        Loads xml file into a BeautifulSoup object.

        Parameters
        ----------
        xml_file_path: str
            The path to the xml file.

        Returns
        -------
        BeautifulSoup | None
        """
        try:
            with open(xml_file_path, "r", encoding="utf-8") as file:
                content = file.read()
                soup = BeautifulSoup(content, "xml")
            return soup
        except FileNotFoundError as e:
            logger.error(f"Error reading xml file content: {e}")

    def _read_mets(self) -> BeautifulSoup | None:
        """
        Reads the xml content from the METS file.

        Returns
        -------
        soup: BeautifulSoup | None
            The content of the METS file as a BeautifulSoup object.
        """
        try:
            soup = self._load_xml_content(self.mets_path)
            mets_tag = soup.find("mets")
            if mets_tag is None:
                logger.error("METS file is invalid: mets tag not found.")
            return soup

        except Exception as e:
            logger.error(f"Error reading METS file: {e}")

    def _parse_file_group(self, group_name: str) -> dict | None:
        """
        Finds file locations and ids from specified file group.

        Parameters
        ----------
        group_name : str
            The file group we are looking for. Allowed values are "alto", "images".
            "alto" references ALTO files, "images" image files.

        Returns
        -------
        dict | None
            A dictionary containing file ids and locations.
        """
        file_locations = dict()
        if group_name not in ["alto", "images"]:
            return file_locations
        try:
            file_group = self.document.find(
                "fileGrp",
                {
                    "ID": lambda x: x
                    and any(
                        pattern.lower() in x.lower()
                        for pattern in self.mets_filegroup_patterns[group_name]
                    )
                },
            )
            if file_group:
                for file in file_group.find_all("file")[
                    self.start_page : self.end_page
                ]:
                    file_id = file.get("ID")
                    href = file.find("FLocat").get("xlink:href")
                    href = href.replace("file://", "")
                    rel_file_path = urlparse(href).path.lstrip("/")
                    mets_dir = os.path.dirname(self.mets_path)
                    full_file_path = os.path.join(mets_dir, rel_file_path)
                    file_locations[file_id] = full_file_path
            return file_locations
        except Exception as e:
            logger.error(
                f"Error reading file group information from the METS file: {e}"
            )

    def _read_alto(self) -> dict | None:
        """
        Reads the ALTO content and stores the pages in a dictionary as BeautifulSoup objects.

        Returns
        -------
        dict
            Dictionary containing the ALTO pages with keys in the format defined in the METS file.
        """
        try:
            pages_dict = {}
            for alto_id, alto_path in self.alto_paths.items():
                soup = self._load_xml_content(alto_path)
                pages_dict[alto_id] = soup
            return pages_dict

        except Exception as e:
            logger.error(f"Error reading ALTO files: {e}")

    def _create_alto_id_to_page_nr_dict(self) -> dict:
        """
        Create a dictionary for mapping page ids to page numbers.

        Returns
        -------
        dict
            A dictionary containing the page numbers of the corresponding alto ids.
        """
        return {key: index for index, key in enumerate(self.alto_paths.keys(), start=1)}

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
        Extracts text from the file.

        Returns
        -------
        list[dict[str, str | int | None]]
            The extracted text from the file, if extraction fails, returns [].
        """
        output = self.ocr_strategy.perform_ocr_if_needed()
        return (
            self.text_postprocessor.postprocess_text(
                input_data=output, split_long_texts=self.estimate_page_count
            )
            if output
            else []
        )

    def extract_text_from_metsalto(self) -> list[dict[str, str | int | None]] | None:
        """
        Extracts text from the METS/ALTO file.

        Returns
        -------
        list[dict[str, str | int | None]] | None
        """
        try:
            doc_structure = self.document.find("structMap", {"TYPE": "LOGICAL"})
            if doc_structure:
                document_content = self._extract_sections(doc_structure)
                merged_content = self._merge_content_by_section(document_content)
                content = self._add_section_meta(merged_content)
                extracted_texts = self._format_text_content_for_json(content)
            else:
                extracted_texts = self._extract_text_based_on_pages()
            return extracted_texts if extracted_texts else None
        except Exception as e:
            logger.error(f"Error extracting text from the METS/ALTO file: {e}")

    def _calculate_mean_wc_from_soups(
        self, soup_objects: list[BeautifulSoup]
    ) -> float | None:
        """
        Calculate the mean of the word count (WC) attribute values for all
        String tags across multiple BeautifulSoup objects.

        Parameters
        ----------
        soup_objects : list[BeautifulSoup]
            A list of BeautifulSoup objects representing parsed XML contents.

        Returns
        -------
        float | None
            The mean of the WC values across all XML contents, or None if no valid WC values are found.
        """
        wc_values = []

        for soup in soup_objects:
            for string_tag in soup.find_all("String", WC=True):
                wc_value = string_tag.get("WC")
                try:
                    wc_values.append(float(wc_value))
                except (ValueError, TypeError):
                    continue

        if wc_values:
            return sum(wc_values) / len(wc_values)
        else:
            return None

    def _extract_alto_references(self, div: Tag) -> list[dict[str, str]] | list:
        """
        Extract file pointer information (alto file id and block tag) from div.

        Parameters
        ----------
        div: Tag
            The div where file pointer information is extracted.

        Returns
        -------
        list[dict[str, str]] | list
            The list of dictionaries containing block tags and alto ids.
        """
        alto_refs = []
        file_pointers = div.find_all("fptr")
        for pointer in file_pointers:
            areas = pointer.find_all("area")
            for area in areas:
                alto_id = area.get("FILEID")
                block_tag = area.get("BEGIN")
                if alto_id in self.pages.keys():
                    alto_refs.append({"alto_id": alto_id, "block_tag": block_tag})
                else:
                    # Ideally this should only happen when start/max page is set
                    # but might also occur when the METS/ALTO structure is completely broken
                    logger.warning(f"ALTO reference {alto_id} not found.")
        return alto_refs

    def _extract_text_from_block(
        self, alto_id: str, block_tag: str, carried_word: str
    ) -> tuple[str, str]:
        """
        Extracts text from the referenced block, handling hyphenated words.

        Parameters
        ----------
        alto_id : str
            The alto id which shows in which alto file the content lies.

        block_tag : str
            The block tag that can be used to access the content.

        carried_word : str
            The word carried over from the previous section in case there is hyphenation.

        Returns
        -------
        tuple[str, str]
            Tuple containing the extracted text and the carried word if there is hyphenation.
        """
        page = self.pages[alto_id]
        block = page.find("TextBlock", {"ID": block_tag})
        if not block:
            block = page.find("ComposedBlock", {"ID": block_tag})
        # Variables for handling hyphenated words
        waiting_for_hyp_part2 = bool(carried_word)
        full_word = carried_word

        if not block:
            return "", carried_word

        text = []
        for line in block.find_all("TextLine"):
            for string in line.find_all("String"):
                subs_type = string.get("SUBS_TYPE")
                if subs_type == "HypPart1":
                    full_word = string.get(
                        "SUBS_CONTENT"
                    )  # First part of hyphenated word
                    waiting_for_hyp_part2 = True
                elif subs_type == "HypPart2" and waiting_for_hyp_part2:
                    text.append(full_word)  # Append the full hyphenated word
                    waiting_for_hyp_part2 = False
                    full_word = None
                else:
                    text.append(string["CONTENT"])  # Append regular text
        return " ".join(text).strip(), full_word

    def _extract_sections(self, doc_structure: Tag) -> list | None:
        """
        Extract METS/ALTO text based on the logical structure given in the METS file.

        Parameters
        ----------
        doc_structure : Tag
            The logical structure of the document.

        Returns
        -------
        list | None
            List of dictionaries containing paragraph information.
        """
        document_content = []
        sections = doc_structure.find_all(
            "div", {"TYPE": lambda x: x and x.lower() in self.lookup_metsalto_sections}
        )
        for section in sections:
            section_id = section.get("DMDID")
            section_type = section.get("TYPE")
            if section.find("fptr"):
                self._process_single_div(
                    section, section_id, section_type, document_content
                )

            for div in section.find_all("div"):
                if any(child.name == "fptr" for child in div.children):
                    self._process_single_div(
                        div, section_id, section_type, document_content
                    )

        # Parse divs without a section
        divs_with_fptr = [
            div
            for div in doc_structure.find_all("div")
            if any(child.name == "fptr" for child in div.children)
        ]
        processed_div_ids = {item["sequence_nr"] for item in document_content}
        unprocessed_divs = [
            div for div in divs_with_fptr if div.get("ID") not in processed_div_ids
        ]

        for div in unprocessed_divs:
            self._process_single_div(div, None, None, document_content)

        return sorted(document_content, key=lambda x: int(x["sequence_nr"][4:]))

    def _merge_content_by_section(self, document_content: list) -> list:
        """
        Merge texts from the same section into one entry.

        Parameters
        ----------
        document_content: list
            A list of dictionaries containing METS/ALTO content split into paragraphs

        Returns
        -------
        list
            A list of dictionaries containing METS/ALTO content split into sections
        """
        data = sorted(document_content, key=lambda x: int(x["sequence_nr"][4:]))
        section_dict = defaultdict(
            lambda: {
                "text": "",
                "section_id": None,
                "section_type": None,
                "sequence_nr": None,
                "page": set(),
            }
        )
        for entry in data:
            section_key = (
                entry["section_id"] if entry["section_id"] is not None else id(entry)
            )
            merged_dict = section_dict[section_key]
            # Keep only first div_id for each section
            if merged_dict["section_id"] is None:
                merged_dict.update(
                    {
                        "section_id": entry["section_id"],
                        "sequence_nr": entry["sequence_nr"],
                        "section_type": entry["section_type"],
                    }
                )
            merged_dict["text"] += entry["text"] + "\n"
            merged_dict["page"].update(entry["page"])
        return [{**d, "text": d["text"].strip()} for d in section_dict.values()]

    def _add_section_meta(self, document_content: list) -> list:
        """
        Extract meta information from the METS file for each section. Add the xml slice to the document content.

        Parameters
        ----------
        document_content: list
            A list of dictionaries containing document content.

        Returns
        -------
        list
            A list of dictionaries containing document content with appended meta information.
        """
        for section in document_content:
            section_id = section["section_id"]
            if section_id:
                section_meta = self.document.find("dmdSec", {"ID": section_id})
            else:
                section_meta = None
                
            section["section_meta"] = section_meta
            
        return document_content

    def _process_single_div(
        self, div: Tag, section_id: str, section_type: str, document_content: list
    ):
        """
        Process a single div and append the parsed content to document_content.

        Parameters
        ----------
        div: Tag
            The div element containing the text to process.

        section_id: str or None
            The ID of the section the div belongs to, if any.

        document_content: list
            The list to append the parsed paragraph content to.
        """

        div_id, carried_word, div_text, page_ids = div.get("ID"), None, "", set()
        alto_refs = self._extract_alto_references(div)
        for ref in alto_refs:
            block_text, carried_word = self._extract_text_from_block(
                ref["alto_id"], ref["block_tag"], carried_word
            )
            div_text = " ".join([div_text, block_text]).strip()
            page_ids.add(ref["alto_id"])

        if div_text:
            document_content.append(
                {
                    "text": div_text,
                    "section_id": section_id,
                    "section_type": section_type,
                    "sequence_nr": div_id,
                    "page": {self.alto_id_to_page_nr[page_id] for page_id in page_ids},
                }
            )

    def _extract_text_based_on_pages(self) -> list | None:
        """
        Extracts the METS/ALTO text from the documents by taking out paragraphs from pages.
        Can be used to extract text if no logical structure is defined in the METS file.

        Returns
        -------
        list | None
            The list of sections split into paragraphs. Each paragraph is saved as a dictionary containing following
            fields:
                "text": The paragraph text
                "page": A set of pages where the text belongs
        """
        document_content = []
        for page_id, page in self.pages.items():
            carried_word = None
            text_blocks = page.find_all("TextBlock")
            for block in text_blocks:
                block_id = block.get("ID")
                block_text, carried_word = self._extract_text_from_block(
                    page_id, block_id, carried_word
                )
                if block_text != "":
                    paragraph_content = {
                        "text": block_text,
                        "page": {self.alto_id_to_page_nr[page_id]},
                    }
                    document_content.append(paragraph_content)
        return document_content


    def extract_page_numbers(self) -> int | None:
        """
        Extracts the total number of pages in the file and stores it in the `self.page_count` attribute.

        Returns
        -------
        int | None
            The total number of pages in the file, or None if extraction fails.
        """
        try:
            if not self.pages:
                return None
            self.page_count = len(self.pages)
            return self.page_count

        except Exception as e:
            logger.error(f"Error extracting page count from METS/ALTO: {e}")

    def extract_physical_dimensions(self) -> int | None:
        """
        Extracts the largest physical dimension [cm] of the document and stores it
        in the `self.physical_dimensions` attribute.
        Converts the dimension to cm based on the measurement unit specified in the ALTO file.
        The measurement unit defaults to mm10 as given in the METS/ALTO standard.

        Returns
        -------
        int | None
            An int representing the largest physical dimension of the document, or None if extraction fails.
        """
        try:
            if not self.document:
                return None
            first_page_index = next(iter(self.pages))
            page = self.pages[first_page_index].find("Page")
            width = int(float(page.get("WIDTH")))
            height = int(float(page.get("HEIGHT")))
            largest_dim = max(width, height)

            # Convert to cm
            measurement_unit_tag = page.find(".//MeasurementUnit")
            measurement_unit = (
                measurement_unit_tag.text
                if measurement_unit_tag is not None
                else "mm10"
            )

            default_dpi = 300
            if measurement_unit in ["dpi", "pixel"]:
                largest_dim = (largest_dim / default_dpi) * 2.54

            elif measurement_unit == "inch1200":
                largest_dim = (largest_dim / 1200) * 2.54

            else:
                largest_dim = largest_dim / 100
            self.physical_dimensions = round(largest_dim)
            return self.physical_dimensions

        except Exception as e:
            logger.error(f"Error extracting physical dimension from METS/ALTO: {e}")

    def _process_page(
        self, alto_page: BeautifulSoup, alto_image_path: str, alto_id: str
    ) -> list:
        """
        Processes a single ALTO page, extracts images and metadata (label, coordinates, page number).

        Parameters
        ----------
        alto_page : BeautifulSoup
            The ALTO page object.

        alto_image_path : str
            The file path of the corresponding ALTO image.

        alto_id : str
            The id of the alto page.

        Returns
        -------
        page_images : list
            The list of extracted images from one page
        """
        alto_image = Image.open(alto_image_path)
        scale_x, scale_y = self._calculate_scaling_factors(alto_page, alto_image)
        alto_image_array = np.array(alto_image)
        alto_image.close()
        page_nr = self.alto_id_to_page_nr[alto_id]
        page_images = []
        for block in alto_page.find_all(
            "ComposedBlock", TYPE=lambda t: t and t.lower() in self.metsalto_img_labels
        ):
            image_metadata = self._extract_image_block_meta(block, scale_x, scale_y)
            cropped_image = self._crop_image(
                alto_image_array, image_metadata["coordinates"]
            )
            image_metadata["cropped_image"] = cropped_image
            image_metadata["page"] = page_nr
            page_images.append(image_metadata)
        for illustration in alto_page.find_all("Illustration"):
            image_metadata = self._extract_image_block_meta(
                illustration, scale_x, scale_y, label="illustration"
            )
            cropped_image = self._crop_image(
                alto_image_array, image_metadata["coordinates"]
            )
            image_metadata["cropped_image"] = cropped_image
            image_metadata["page"] = page_nr
            page_images.append(image_metadata)
        return page_images

    def _calculate_scaling_factors(
        self, alto_page: BeautifulSoup, alto_image: Image
    ) -> tuple:
        """
        Calculates scaling factors based on the ALTO page and image dimensions.

        Parameters
        -----------
        alto_page : BeautifulSoup
            The ALTO page object.

        alto_image : Image
            The PIL image object.

        Returns
        --------
        tuple
            A tuple containing the scaling factors (scale_x, scale_y).
        """
        i_width, i_height = alto_image.size
        page_info = alto_page.find("Page")
        p_width = int(float(page_info.get("WIDTH")))
        p_height = int(float(page_info.get("HEIGHT")))
        scale_x = i_width / p_width
        scale_y = i_height / p_height
        return scale_x, scale_y

    def _extract_image_block_meta(
        self, block: BeautifulSoup, scale_x: float, scale_y: float, label: str = None
    ) -> dict:
        """
        Extracts image metadata from a block (label, coordinates).

        Parameters
        ----------
        block : BeautifulSoup
            The block as a BeautifulSoup object.

        scale_x : float
            The horizontal scaling factor.

        scale_y : float
            The vertical scaling factor.

        label : str
            The label to assign if the block TYPE attribute is None

        Returns
        -------
        metadata : dict
            A dictionary containing the metadata associated with the block.
        """
        label = label or block.get("TYPE")
        label = self.keep_metsalto_img_labels.get(label.lower(), label.lower())
        div_id = block.get("ID")
        hpos = int(float(block.get("HPOS")) * scale_x)
        vpos = int(float(block.get("VPOS")) * scale_y)
        width = int(float(block.get("WIDTH")) * scale_x)
        height = int(float(block.get("HEIGHT")) * scale_y)
        metadata = {
            "label": (
                label.lower()
                if label.lower() in self.keep_metsalto_img_labels.values()
                else None
            ),
            "image_id": div_id if div_id else None,
            "coordinates": {
                "HPOS": hpos,
                "VPOS": vpos,
                "WIDTH": width,
                "HEIGHT": height,
            },
        }
        return metadata

    def _crop_image(self, alto_image_array: np.ndarray, coords: dict) -> Image:
        """
        Crops the image based on the block's coordinates.

        Parameters
        ----------
        alto_image_array : np.ndarray
            The page image as a numpy array.

        coords : dict
            A dictionary containing the 'HPOS', 'VPOS', 'WIDTH', and 'HEIGHT' coordinates.

        Returns
        -------
        Image
            The cropped image.
        """
        cropped_image_array = alto_image_array[
            coords["VPOS"] : coords["VPOS"] + coords["HEIGHT"],
            coords["HPOS"] : coords["HPOS"] + coords["WIDTH"],
        ]
        return Image.fromarray(cropped_image_array)

    def extract_images(self) -> list[dict[str, str | int | dict | None]]:
        """
        Extracts images from the METS/ALTO file.

        Returns
        -------
        list[dict[str, str | int | dict | None]]
            A list of PIL Image objects representing the images in the METS/ALTO file.
        """
        if not self.enable_image_extraction or not self.pages:
            return []

        extracted_images = []
        for (alto_id, alto_page), (image_id, alto_image_path) in zip(
            self.pages.items(), self.alto_image_paths.items()
        ):
            page_images = self._process_page(alto_page, alto_image_path, alto_id)
            extracted_images.extend(page_images)
        clf_images = self.image_classificator.classify_extracted_images(
            extracted_images
        )
        clf_images = [
            {k: v for k, v in image.items() if k != "cropped_image"}
            for image in clf_images
        ]
        return clf_images

    def _extract_document_metadata(self):
        """
        Extracts the slice containing document metadata from the METS document.

        Returns
        -------
        list
            A list of xml elements containing the document metadata.
        """
        meta_elements = []
        for dmdsec in self.document.find_all("dmdSec"):
            target_ids = []
            for target_id in self.mets_meta_ids:
                target_ids.append(target_id)
            if any(target_ids):
                meta_elements.append(str(dmdsec))
        return meta_elements

    def _format_text_content_for_json(self, content: list, remove_keys: List[str] = []) -> List[dict]:
        """
        Remove unnecessary fields from the extracted content. Reformat div id from DIVL1 -> 1
        for unified sequence number extraction.

        Parameters
        ----------
        content: list
            A list of dictionaries containing document content split into sections

        Returns
        -------
        content: list
            A list of dictionaries containing document content split into sections
        """
     
        for entry in content:
            for remove_key in remove_keys:
                del entry[remove_key]
            entry["sequence_nr"] = int(entry["sequence_nr"][4:])
        return content
