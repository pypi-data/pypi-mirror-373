from collections import defaultdict
from typing import List, NoReturn

from rara_tools.utils import lang_to_iso639_2, ratio_to_percentage


UNDEFINED_LANGUAGE_VALUE = "unk"
QUALITY_RATIO_TYPE = "Float"


class ImagePageSchema:
    def __init__(self, image: dict) -> NoReturn:
        self.__image = image
        self.__schema: dict = {}

    @property
    def schema(self) -> dict:
        if not self.__schema:
            self.__schema = {
                "@type": "VisualArtwork",
                "@id": "",
                "value": self.__image.get("label"),
                "description": "",
                "schema:position": self.__image.get("page")
            }
        return self.__schema


class TextPageSchema:
    def __init__(self, page: dict) -> NoReturn:
        self.__page: dict = page
        self.__schema: dict = {}

    @property
    def schema(self) -> dict:
        if not self.__schema:
            self.__schema = {
                "@type": "Text",  # CONSTANT
                "@id": "",  # Will be added in a later stage
                "value": "Textblock",  # CONSTANT
                "content": self.__page.get("text"),
                "schema:position": self.__page.get("start_page")  # start_page ?
            }
        return self.__schema


class PageSchema:
    def __init__(
            self,
            page_texts: List[dict],
            page_images: List[dict],
            page_number: int,
            doc_id: str
    ) -> NoReturn:
        self.__page_texts: List[dict] = page_texts
        self.__page_images: List[dict] = page_images
        self.__page_nr: int = page_number
        self.__page_id: str = ""
        self.__doc_id: str = doc_id
        self.__schema: dict = {}

    def _add_segment_ids(self, segments: List[dict]) -> List[dict]:
        for i, segment in enumerate(segments):
            segment_id = f"{self.page_id}/{i + 1}"
            segment["@id"] = segment_id
        return segments

    @property
    def page_id(self) -> str:
        if not self.__page_id:
            self.__page_id = f"{self.__doc_id}/{self.__page_nr}"
        return self.__page_id

    @property
    def schema(self) -> dict:
        if not self.__schema:
            self.__schema = {
                "@type": "CreativeWork",  # CONSTANT for pages
                "@id": self.page_id,
                "hasPart": []
            }
            text_schemas = [
                TextPageSchema(page).schema
                for page in self.__page_texts
            ]
            image_schemas = [
                ImagePageSchema(image).schema
                for image in self.__page_images
            ]

            page_schemas = text_schemas + image_schemas
            page_schemas_with_ids = self._add_segment_ids(page_schemas)

            self.__schema["hasPart"].extend(page_schemas_with_ids)

        return self.__schema


class DocSchemas:
    def __init__(
            self,
            doc_meta: dict,
            sierra_id: str = "",
            generated_id: str = "",
            permalink: str = "",
            min_language_ratio: float = 0.2,
            convert_ratio: bool = True,
            generated_id_type: str = "CustomID"
    ) -> NoReturn:
        self.__convert_ratio = convert_ratio
        self.__min_language_ratio = min_language_ratio
        self.__sierra_id = sierra_id
        self.__generated_id = generated_id
        self.__permalink = permalink
        self.__generated_id_type = generated_id_type
        self.__doc_meta = doc_meta
        self.__ocr_accuracy_schema: dict = {}
        self.__text_quality_schema: dict = {}
        self.__language_schema: List[dict] = []
        self.__identifier_schema: List[dict] = []
        self.__origin_schema: dict = {}
        self.__origin: str = ""

    @property
    def origin(self) -> str:
        if not self.__origin:
            if self.__doc_meta["ocr_applied"]:
                self.__origin = "Reformatted digital"
            else:
                self.__origin = "Born digital"
        return self.__origin

    @property
    def ocr_accuracy_schema(self) -> dict:
        if not self.__ocr_accuracy_schema:
            ocr_quality = self.__doc_meta.get("alto_text_quality")
            if ocr_quality:
                self.__ocr_accuracy_schema = {
                    "comment": "Estimated OCR accuracy"
                }
                if self.__convert_ratio:
                    type_and_value = {
                        "@type": QUALITY_RATIO_TYPE,
                        "value": ocr_quality
                    }
                else:
                    type_and_value = {
                        "@type": "Text",
                        "value": ratio_to_percentage(ocr_quality)
                    }
                self.__ocr_accuracy_schema.update(type_and_value)
        return self.__ocr_accuracy_schema

    @property
    def text_quality_schema(self) -> dict:
        if not self.__text_quality_schema:
            text_quality = self.__doc_meta.get("text_quality")
            self.__text_quality_schema = {
                "comment": "Estimated n-gram-based text quality"
            }
            if self.__convert_ratio:
                type_and_value = {
                    "@type": QUALITY_RATIO_TYPE,
                    "value": text_quality
                }
            else:
                type_and_value = {
                    "@type": "Text",
                    "value": ratio_to_percentage(text_quality)
                }
            self.__text_quality_schema.update(type_and_value)
        return self.__text_quality_schema

    @property
    def language_schema(self) -> List[dict]:
        if not self.__language_schema:
            self.__language_schema = [
                {
                    "@type": "ISO 639-2",
                    "value": lang_to_iso639_2(
                        lang["language"],
                        unk_code=UNDEFINED_LANGUAGE_VALUE
                    )
                }
                for lang in self.__doc_meta["languages"]
                if lang["ratio"] >= self.__min_language_ratio
            ]
        return self.__language_schema

    @property
    def identifier_schema(self) -> List[dict]:
        if not self.__identifier_schema:
            identifiers = []
            if self.__sierra_id:
                identifiers.append(
                    {
                        "@type": "Identifier",
                        "qualifier": "OPAC",
                        "value": self.__sierra_id
                    }
                )
            if self.__permalink:
                identifiers.append(
                    {
                        "@type": "Identifier",
                        "qualifier": "Permalink",
                        "value": self.__permalink
                    }
                )
            if self.__generated_id:
                identifiers.append(
                    {
                        "@type": "Identifier",
                        "qualifier": self.__generated_id_type,
                        "value": self.__generated_id
                    }
                )
            self.__identifier_schema = identifiers

        return self.__identifier_schema

    @property
    def origin_schema(self) -> dict:
        if not self.__origin_schema:
            self.__origin_schema = {
                "@type": "Text",
                "value": self.origin,
                "comment": "Origin"
            }
        return self.__origin_schema


class DIGARSchemaConverter:
    def __init__(
            self,
            digitizer_output: dict,
            generated_id: str,
            sierra_id: str = "",
            permalink: str = "",
            generated_id_type: str = "CustomID",
            min_language_ratio: float = 0.2,
            convert_ratio: bool = False
    ) -> NoReturn:
        """ Initialize DIGARSchemaConverter object. 
        
        Parameters
        ----------
        digitizer_output: dict
            Raw output of rara-digitizer (https://pypi.org/project/rara-digitizer/).
        generated_id: str
            Some non-standard/generated document identifier used in ID fields.
        sierra_id: str
            Document's corresponding Sierra ID.
        permalink: str
            Permanent link, where the document can be accessed.
        generated_id_type: str
            Method / type of generated ID (e.g. 'UUID')
        min_language_ratio: float
            Cutoff ratio for languages. If ratio for some language
            does not exceed the set threshold, the language will not
            be added to the final output.
        convert_ratio: bool
            If enabled, all ratios are converted into percentages.
          
        """
        self.__digitizer_output: dict = digitizer_output
        self.__min_language_ratio: float = min_language_ratio
        self.__convert_ratio: bool = convert_ratio
        self.__sierra_id: str = sierra_id
        self.__generated_id: str = generated_id
        self.__permalink: str = permalink.removesuffix("/")
        self.__generated_id_type: str = generated_id_type
        self.__texts: List[dict] = []
        self.__images: List[dict] = []
        self.__doc_meta: dict = {}
        self.__page_mappings: List[dict] = []
        self.__dcterms_haspart: dict = {}
        self.__dcterms_conforms_to: dict = {}
        self.__dc_language: dict = {}
        self.__dc_origin: dict = {}
        self.__dc_identifier: List[dict] = []
        self.__doc_id: str = ""

        self.__doc_schemas = DocSchemas(
            doc_meta=self.doc_meta,
            sierra_id=self.__sierra_id,
            generated_id=self.__generated_id,
            permalink=self.__permalink,
            min_language_ratio=self.__min_language_ratio,
            convert_ratio=self.__convert_ratio,
            generated_id_type=self.__generated_id_type
        )
        self.__digar_schema: dict = {}

    def _get_page_number(self, page_content: dict) -> int:
        """ Retrieves page number from image or text object.
        """
        _segments = page_content["texts"] + page_content["images"]
        _first_segment = _segments[0]
        if "start_page" in _first_segment:
            page_number = _first_segment.get("start_page")
        elif "page" in _first_segment:
            page_number = _first_segment.get("page")
        return page_number

    @property
    def doc_id(self) -> str:
        """ Retrieves document ID to use for generating
        page and segment ids. Preference order:
        1. permalink; 2. sierra_id; 3. generated document id
        """
        if not self.__doc_id:
            if self.__permalink:
                self.__doc_id = self.__permalink
            elif self.__sierra_id:
                self.__doc_id = self.__sierra_id
            else:
                self.__doc_id = self.__generated_id
        return self.__doc_id

    @property
    def texts(self) -> List[dict]:
        if not self.__texts:
            self.__texts = self.__digitizer_output.get("texts")
        return self.__texts

    @property
    def images(self) -> List[dict]:
        if not self.__images:
            self.__images = self.__digitizer_output.get("images")
        return self.__images

    @property
    def doc_meta(self) -> dict:
        if not self.__doc_meta:
            self.__doc_meta = self.__digitizer_output.get("doc_meta")
        return self.__doc_meta

    @property
    def page_mappings(self) -> List[dict]:
        if not self.__page_mappings:
            mapped = defaultdict(lambda: defaultdict(list))
            for text in self.texts:
                mapped[text["start_page"]]["texts"].append(text)
            for img in self.images:
                mapped[img["page"]]["images"].append(img)

            self.__page_mappings = [
                v for k, v in sorted(list(mapped.items()), key=lambda x: x[0])
            ]
        return self.__page_mappings

    @property
    def dcterms_haspart(self) -> dict:
        if not self.__dcterms_haspart:
            self.__dcterms_haspart = {
                "dcterms:hasPart": [
                    PageSchema(
                        page_texts=page["texts"],
                        page_images=page["images"],
                        page_number=self._get_page_number(page),
                        doc_id=self.doc_id
                    ).schema
                    for page in self.page_mappings
                ]
            }
        return self.__dcterms_haspart

    @property
    def dcterms_conforms_to(self) -> dict:
        if not self.__dcterms_conforms_to:
            schema_content = [
                self.__doc_schemas.text_quality_schema,
            ]
            # Add OCR Accuracy only when it is not empty:
            if self.__doc_schemas.ocr_accuracy_schema:
                schema_content.append(self.__doc_schemas.ocr_accuracy_schema)
            self.__dcterms_conforms_to = {
                "dcterms:conformsTo": schema_content
            }
        return self.__dcterms_conforms_to

    @property
    def dc_language(self) -> dict:
        if not self.__dc_language:
            self.__dc_language = {
                "dc:language": self.__doc_schemas.language_schema
            }
        return self.__dc_language

    @property
    def dc_origin(self) -> dict:
        if not self.__dc_origin:
            self.__dc_origin = {
                "dcterms:provenance": self.__doc_schemas.origin_schema
            }
        return self.__dc_origin

    @property
    def dc_identifier(self) -> List[dict]:
        if not self.__dc_identifier:
            self.__dc_identifier = {
                "dc:identifier": self.__doc_schemas.identifier_schema
            }
        return self.__dc_identifier

    @property
    def digar_schema(self) -> dict:
        if not self.__digar_schema:
            self.__digar_schema = {}
            self.__digar_schema.update(self.dcterms_conforms_to)
            self.__digar_schema.update(self.dcterms_haspart)
            self.__digar_schema.update(self.dc_language)
            self.__digar_schema.update(self.dc_origin)
            self.__digar_schema.update(self.dc_identifier)
        return self.__digar_schema
