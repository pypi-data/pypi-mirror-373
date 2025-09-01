import re

from langdetect import detect, LangDetectException

from rara_digitizer.factory.resource_manager import ResourceManager
from rara_digitizer.utils.constants import UNKNOWN_LANGUAGE_FALLBACK, EVALUATOR_DEFAULT_RESPONSE, CHARACTER_MAP


class TextPostprocessor:

    def __init__(self, resource_manager: ResourceManager, **kwargs):
        self.resource_manager = resource_manager
        self.quality_evaluator = self.resource_manager.quality_evaluator()
        self.text_length_cutoff = kwargs.get("text_length_cutoff", 30)
        self.evaluator_default_response = kwargs.get("evaluator_default_response", EVALUATOR_DEFAULT_RESPONSE)
        self.unknown_language_fallback = kwargs.get("unknown_language_fallback", UNKNOWN_LANGUAGE_FALLBACK)
        self.enable_character_mapping = kwargs.get("enable_character_mapping", False)
        self.character_map = kwargs.get("character_map", CHARACTER_MAP)

    def postprocess_text(
        self,
        input_data: str | list[dict[str, str | int | None]],
        split_long_texts: bool,
        n_words_per_page: int = 300,
    ) -> list[dict[str, str | int | None]]:
        """
        Process the input data to ensure it's in the correct format. If the input is already a list of dictionaries,
        it verifies that it conforms to the expected format. If it's a string, it splits the text into chunks of
        n_words_per_page words and formats each chunk as a dictionary with an estimated page number.

        Parameters
        ----------
        input_data : str or list[dict[str, str | int | None]]
            The input data, which could be a string or a list of dictionaries.
        split_long_texts : bool
            Whether to split longer texts by word limit.
        n_words_per_page : int, optional
            The number of words per page for the text chunking (default is 300).

        Raises
        ------
        TypeError
            If the input is neither a string nor a list of dictionaries.

        Returns
        -------
        list[dict[str, str | int | None]]
            A list of dictionaries where each dictionary represents a page of text.
        """
        if isinstance(input_data, list):
            processed_data = self._process_list_of_dicts(
                input_data, split_long_texts, n_words_per_page
            )
        elif isinstance(input_data, str):
            processed_data = self._process_string(input_data, n_words_per_page)
        else:
            raise TypeError("Input must be either a string or a list of dictionaries.")

        processed_data = [self._normalize_page_keys(item) for item in processed_data]
        processed_data = self._add_language_and_stats(processed_data)
        if self.enable_character_mapping:
            processed_data = self._map_characters(processed_data)
        return processed_data

    def _map_characters(
        self, data: list[dict[str, str | int | float | None]]
    ) -> list[dict[str, str | int | float | None]]:
        """
        Map characters in the text using a character map.

        Parameters
        ----------
        data : list[dict[str, str | int | float | None]]
            The list of dictionaries containing text data.

        Returns
        -------
        list[dict[str, str | int | float | None]]
            The list of dictionaries with mapped characters.
        """
        if self.character_map:
            for item in data:
                lang = item["language"]
                if lang and lang in self.character_map:
                    for char, replacement in self.character_map[lang].items():
                        item["text"] = item["text"].replace(char, replacement)
        return data

    def _process_list_of_dicts(
        self,
        input_data: list[dict[str, str | int | None]],
        split_long_texts: bool,
        n_words_per_page: int,
    ) -> list[dict[str, str | int | None]]:
        """
        Process a list of dictionaries and optionally split text if split_chapters is True.

        Parameters
        ----------
        input_data : list[dict[str, str | int | None]]
            The input data in the form of a list of dictionaries.
        split_long_texts : bool
            Whether to split longer texts by word limit.
        n_words_per_page : int
            The number of words per page for the text chunking.

        Returns
        -------
        list[dict[str, str | int | None]]
            A list of dictionaries where each dictionary represents a page of text.
        """
        required_keys = {"page", "section_meta", "section_type", "text", "sequence_nr"}
        for i, entry in enumerate(input_data):
            entry.setdefault("section_meta", None)
            entry.setdefault("section_title", None)
            entry.setdefault("section_type", None)
            entry.setdefault("page", None)
            entry.setdefault("sequence_nr", i + 1)
        self._validate_required_keys(input_data, required_keys)

        if split_long_texts:
            return self._split_text_in_dicts(input_data, n_words_per_page)
        else:
            return input_data

    def _process_string(
        self, input_data: str, n_words_per_page: int
    ) -> list[dict[str, str | int | None]]:
        """
        Process a string by splitting it into estimated_pages based on n_words_per_page.

        Parameters
        ----------
        input_data : str
            The input data in the form of a string.
        n_words_per_page : int
            The number of words per page for the text chunking.

        Returns
        -------
        list[dict[str, str | int | None]]
            A list of dictionaries where each dictionary represents a page of text.
        """
        words = self._split_text_preserving_structure(input_data)
        estimated_pages = self._group_words_into_pages(words, n_words_per_page)

        return [
            {
                "page": page_nr,
                "section_meta": None,
                "section_type": None,
                "section_title": None,
                "text": page_text,
            }
            for page_nr, page_text in enumerate(estimated_pages, start=1)
        ]

    def _split_text_in_dicts(
        self, input_data: list[dict[str, str | int | None]], n_words_per_page: int
    ) -> list[dict[str, str | int | None]]:
        """
        Split text in each dictionary into chunks and create new entries for each page.

        Parameters
        ----------
        input_data : list[dict[str, str | int | None]]
            The input data in the form of a list of dictionaries.
        n_words_per_page : int
            The number of words per page for the text chunking.

        Returns
        -------
        list[dict[str, str | int | None]]
            A list of dictionaries where each dictionary represents a page of text.
        """
        result = []
        for item in input_data:
            text = item["text"]
            words = self._split_text_preserving_structure(text)
            estimated_pages = self._group_words_into_pages(words, n_words_per_page)

            for page_nr, page_text in enumerate(estimated_pages, start=1):
                result.append(
                    {
                        "page": len(result) + 1,
                        "section_meta": item["section_meta"],
                        "section_type": item["section_type"],
                        "section_title": item["section_title"],
                        "text": page_text,
                    }
                )

        return result

    def _split_text_preserving_structure(self, text: str) -> list[str]:
        """
        Split the text into words or word-like units while preserving punctuation and line breaks.

        Parameters
        ----------
        text : str
            The input text to be split.

        Returns
        -------
        list[str]
            A list of word-like units from the text, preserving punctuation and whitespace.
        """
        # Splits on whitespace while preserving punctuation and line breaks
        return re.findall(r"\S+|\s+", text)

    def _group_words_into_pages(
        self, words: list[str], n_words_per_page: int
    ) -> list[str]:
        """
        Group words into pages based on a given number of words per page.

        Parameters
        ----------
        words : list[str]
            A list of words or tokens, including punctuation and whitespace.
        n_words_per_page : int
            The number of words per page for text chunking.

        Returns
        -------
        list[str]
            A list of pages, each represented as a single string.
        """
        pages = []
        current_page = []
        word_count = 0

        for word in words:
            if word.strip():
                word_count += 1

            current_page.append(word)

            if word_count >= n_words_per_page:
                pages.append("".join(current_page))
                current_page = []
                word_count = 0

        if current_page:  # If we did not reach the word limit and there is content left
            pages.append(
                "".join(current_page)
            )  # Add remaining content as the last page

        return pages

    def _validate_required_keys(
        self, input_data: list[dict[str, str | int | None]], required_keys: set
    ):
        """
        Validate that each dictionary in the input list contains the required keys.

        Raises
        ------
        TypeError
            If any item in the input list is not a dictionary.
        ValueError
            If any dictionary is missing required keys.

        Parameters
        ----------
        input_data : list[dict[str, str | int | None]]
            The list of dictionaries to validate.
        required_keys : set
            The set of keys that each dictionary must contain.
        """
        if not all(isinstance(item, dict) for item in input_data):
            raise TypeError("All items in the input list must be dictionaries.")

        for text_output_dict in input_data:
            if not all(key in text_output_dict.keys() for key in required_keys):
                raise ValueError(
                    f"Each dictionary must contain the following keys: {', '.join(required_keys)}"
                    f"The following are missing: {', '.join(required_keys - text_output_dict.keys())}"
                )

    def _detect_language(self, text: str) -> str | None:
        """
        Detect the language of the provided text, return None if detection fails
        (for example if the text contains no alphabetic characters).

        Parameters
        ----------
        text : str
            The text to detect the language of.

        Returns
        -------
        str | None
            The detected language code (e.g., "en" for English) or None if detection fails.
        """
        try:
            return detect(text)
        except LangDetectException:
            return self.unknown_language_fallback

    def _add_language_and_stats(
        self, data: list[dict[str, str | int | float | None]]
    ) -> list[dict[str, str | int | float | None]]:
        """
        Add language and text statistics to each item in the data list.

        Parameters
        ----------
        data : list[dict[str, str | int | float | None]]
            The list of dictionaries containing text data.

        Returns
        -------
        list[dict[str, str | int | float | None]]
            The list of dictionaries with added language and text statistics.
        """

        for i, item in enumerate(data):
            text = item["text"]
            language = self._detect_language(text)
            words = [
                word
                for word in self._split_text_preserving_structure(text)
                if word.strip()
            ]
            text_quality = self.quality_evaluator.get_probability(
                text,
                length_limit=self.text_length_cutoff,
                default_response=self.evaluator_default_response,
                lang=language,
            )

            item["language"] = language
            item["n_words"] = len(words)
            item["n_chars"] = len(text)
            item["text_quality"] = (
                round(text_quality, 2)
                if text_quality
                else self.evaluator_default_response
            )

            item.setdefault("sequence_nr", i + 1)

        return data

    def _normalize_page_keys(
        self, item: dict[str, str | int | None]
    ) -> dict[str, str | int | None]:
        """
        Normalize the "page" key to "start_page" and "end_page". If "page" is a set of integers,
        replace it with the min and max values. If it's an integer, both "start_page" and "end_page"
        will have the same value.

        Parameters
        ----------
        item : dict[str, str | int | None]
            The dictionary item to normalize.

        Returns
        -------
        dict[str, str | int | None]
            The dictionary with normalized page information.
        """
        if "page" in item:
            page_value = item["page"]
            if isinstance(page_value, set) and all(
                isinstance(num, int) for num in page_value
            ):
                item["start_page"] = min(page_value)
                item["end_page"] = max(page_value)
            elif isinstance(page_value, int):
                item["start_page"] = item["end_page"] = page_value
            del item["page"]

        return item
