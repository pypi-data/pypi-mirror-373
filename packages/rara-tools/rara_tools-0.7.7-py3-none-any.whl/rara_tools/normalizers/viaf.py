import requests
import json
import regex as re
from typing import List, Dict
from collections import defaultdict
from jellyfish import jaro_winkler_similarity as jw
from requests.models import Response
from rara_tools.parsers.tools.entity_normalizers import PersonalName, Normalizer
from rara_tools.constants.normalizers import (
    DEFAULT_VIAF_FIELD, ALLOWED_VIAF_FIELDS, ALLOWED_VIAF_WIKILINK_LANGS,
    VIAF_SIMILARITY_THRESHOLD, VIAF_ALLOWED_SOURCES
)

import logging
logger = logging.getLogger(__name__)

class VIAFRecord:
    """ Takes in a VIAF query response JSON and wraps
    information extraction from it.
    """
    def __init__(self,
            record: dict,
            allowed_sources: List[str] = VIAF_ALLOWED_SOURCES
    ):
        """ Initializes VIAFRecord class.

        Parameters
        -----------
        record: dict
            VIAF query response JSON.
        allowed_sources: List[str]
            Only exracts information from these sources. Other
            sources are ignored.
        """
        self.__record: dict = record
        self.__record_data: dict = {}
        self.__allowed_sources: List[str] = allowed_sources
        self.__viaf_id: int = None
        self.__viaf_url: str = ""
        self.__name_variations: List[str] = []
        self.__birth_date: str = None
        self.__death_date: str = None
        self.__occupations: List[str] = []
        self.__all_fields: dict = {}
        self.__nationality: str = ""
        self.__has_isni: bool = False
        self.__name: str = ""
        self.__name_type: str = ""
        self.__has_isni: str = ""
        self.__activity_start: str = None
        self.__activity_end: str = None,
        self.__works: List[str] = []
        self.__wikilinks: dict = {}
        self.__all_wikilinks: List[str] = []
        self.__has_isni: bool | None = None
        self.__marc_400: List[dict] = []
        self.__marc_500: List[dict] = []
        self.__marc_main: List[dict] = []
        self.__subfield_indicator: str = ""

        self.__value_fields: List[str] = [
            "text", "value", "title", "datafield"
        ]
        self.__title_types: List[str] = ["UniformTitleWork"]


    def __get_data(self, field_name: str, subfield_name: str = "data",
            allowed_sources: List[str] = []
    ) -> List[str]:

        if not allowed_sources:
            allowed_sources = self.__allowed_sources

        data = []

        try:
            entries = self.record_data.get(
                field_name, {}
                ).get(subfield_name, [])

            for entry in entries:
                sources = entry.get("sources", {}).get("s", [])
                if set(allowed_sources).intersection(set(sources)):
                    for field in self.__value_fields:
                        value = entry.get(field, "")
                        if value:
                            data.append(value)
                            break
        except Exception as e:
            logger.error(
                f"Failed extracting data from field '{field_name}' with subfield " \
                f"'{subfield_name}'. '{field_name}' dict has the following " \
                f"structure: {self.record_data.get(field_name)}. " \
                f"Exception reason: {e}."
            )
        return data

    def _get_wikilink_lang(self, wikilink: str) -> str:
        """ Parses the language of the Wikipedia page
        from wikilink.
        """
        pattern = r"(?<=https\W{3})\w+(?=[.])"
        match = re.search(pattern, wikilink)
        wikilink_lang = ""
        if match:
            wikilink_lang = match.group()
        return wikilink_lang

    def _get_marc_field(self, marc_dict: dict, subfield: str = "a",
                        strict_subfield: bool = True
    ) -> str:
        """ Retrieve value from a MARC dict

        Parameters
        -----------
        marc_dict: dict
            MARC dictionaryself.
        subfield: str
            Subfield to extract
        strict_subfield: bool
            If set to True, data is extracted ONLY from
            the subfield set with param `subfield`. If set to False,
            data can be extracted from other subfields as well as long
            there is only one subfield in the dict. This might be necessary
            for uniformTitleWorks as sometimes the title is present in
            subfield (t) while subfield (a) contains the author. However,
            there are instances, where the title is present is subfield (a)
            with no author.
        """
        value = ""
        if marc_dict.get("dtype", "") == "MARC21":
            subfields = marc_dict.get("subfield", [])
            for _subfield in subfields:
                if len(subfields) > 1 and _subfield.get("code", "") == subfield:
                    value = _subfield.get("value", "")
                    break
                elif len(subfields) == 1 and not strict_subfield:
                    value = _subfield.get("value", "")
        return value

    def _get_marc_tag(self, marc_dict: dict) -> str:
        tag = ""
        if marc_dict.get("dtype", "") == "MARC21":
            tag = marc_dict.get("tag", "")
        return tag

    def _get_names(self, marc_dicts: List[dict]) -> List[str]:
        names_d = defaultdict(int)
        for marc_dict in marc_dicts:
            name = self._get_marc_field(
                marc_dict=marc_dict,
                subfield=self.subfield_indicator,
                strict_subfield=False
            )
            names_d[name]+=1
        name_list = sorted(
            list(names_d.items()),
            key=lambda x: x[1],
            reverse=True
        )
        names = []
        for n in name_list:
            _name = self._strip_punctuation(n[0])
            if _name not in names:
                names.append(_name)

        return names

    def _get_name(self, marc_dicts: List[dict]) -> str:
        names = self._get_names(marc_dicts)
        name = ""
        if names:
            name = names[0]
        return name

    def _strip_punctuation(self, entity: str) -> str:
        entity = entity.strip(",")
        # Strip "." only if the last token is not an initial,
        # e.g: "Meri, Lennart." -> Strip
        # "Meri, L." -> Do not strip.
        ent_tokens = [t.strip() for t in entity.split() if t.strip()]
        if ent_tokens and len(ent_tokens[-1]) > 2:
            entity = entity.strip(".")
        return entity

    def _strip_parenthesis(self, entity: str) -> str:
        """ Strip information in parenthesis from VIAF records
        in order to compare the records more easily.
        """
        _entity = re.sub(r"[(][^)][)]", "", entity)
        return _entity.strip()

    @property
    def record(self) -> dict:
        return self.__record

    @property
    def record_data(self) -> dict:
        return self.__record_data

    @property
    def subfield_indicator(self) -> str:
        if not self.__subfield_indicator:
            if self.name_type in self.__title_types:
                subfield_name = "t"
            else:
                subfield_name = "a"
            self.__subfield_indicator = subfield_name
        return self.__subfield_indicator

    @property
    def name(self) -> str:
        # author -> name
        if not self.__name:
            if self.marc_main:
                self.__name = self._get_name(self.marc_main)
            else:
                names = self.__get_data("mainHeadings", "data")
                if names:
                    self.__name = names[0]
        return self.__name

    @property
    def name_type(self) -> str:
        # author_type -> name_type
        """ Type of name (personal, corporate, title, etc)
        """
        if not self.__name_type:
            self.__name_type = self.record_data.get("nameType")
        return self.__name_type

    @property
    def viaf_id(self) -> int:
        if not self.__viaf_id:
            self.__viaf_id = self.record_data.get("viafID", "")
        return self.__viaf_id

    @property
    def viaf_url(self) -> str:
        if not self.__viaf_url:
            self.__viaf_url = self.record_data.get(
                "Document", {}).get("about", "")
        return self.__viaf_url

    @property
    def has_isni(self) -> bool:
        if self.__has_isni == None:
            self.__has_isni = bool(self.record_data.get("isni", ""))
        return self.__has_isni

    @property
    def record_data(self) -> dict:
        if not self.__record_data:
            try:
                self.__record_data = self.__record["queryResult"]
            except:
                self.__record_data = self.__record["recordData"]["VIAFCluster"]

        return self.__record_data

    @property
    def name_variations(self) -> List[str]:
        if not self.__name_variations:
            if self.marc_400:
                var_1 = self._get_names(self.marc_400)
                var_2 = self._get_names(self.marc_main)
                _vars = var_1 + var_2

            else:
                _vars = self.__get_data("mainHeadings")
            vars_3 = [Normalizer.clean_entity(v) for v in _vars]

            vars = _vars + vars_3
            self.__name_variations = list(set(vars))
        return self.__name_variations

    @property
    def birth_date(self) -> str:
        if not self.__birth_date:
            self.__birth_date = self.record_data.get("birthDate", None)
        return self.__birth_date

    @property
    def death_date(self) -> str:
        if not self.__death_date:
            self.__death_date = self.record_data.get("deathDate", None)
        return self.__death_date

    @property
    def occupations(self) -> List[str]:
        if not self.__occupations:
            self.__occupations = self.__get_data("occupation")
        return self.__occupations

    @property
    def activity_start(self) -> str:
        if not self.__birth_date:
            self.__birth_date = self.record_data.get("activityStart", None)
        return self.__birth_date

    @property
    def activity_end(self) -> str:
        if not self.__death_date:
            self.__death_date = self.record_data.get("activityEnd", None)
        return self.__death_date

    @property
    def nationality(self) -> str:
        if not self.__nationality:
            nationalities = self.__get_data("nationalityOfEntity")
            nationalities_dict = defaultdict(int)
            for n in nationalities:
                nationalities_dict[n.lower()] += 1
            if nationalities:
                self.__nationality = sorted(
                    nationalities_dict.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[0][0]
        return self.__nationality

    @property
    def works(self) -> List[str]:
        if not self.__works:
            self.__works = list(set(self.__get_data(
                field_name="titles",
                subfield_name="work"
            )))
        return self.__works

    @property
    def all_wikilinks(self) -> List[str]:
        if not self.__all_wikilinks:
            self.__all_wikilinks = self.__get_data(
                field_name="xLinks", subfield_name="xLink",
                allowed_sources=["WKP"]
            )
        return self.__all_wikilinks

    @property
    def wikilinks(self) -> dict:
        if not self.__wikilinks:
            for wikilink in self.all_wikilinks:
                wikilink_lang = self._get_wikilink_lang(wikilink)
                if wikilink_lang and wikilink_lang in ALLOWED_VIAF_WIKILINK_LANGS:
                    self.__wikilinks[wikilink_lang] = wikilink
        return self.__wikilinks

    @property
    def marc_400(self) -> List[dict]:
        if not self.__marc_400:
            self.__marc_400 = self.__get_data(
                field_name="x400s",
                subfield_name="x400"
            )
        return self.__marc_400

    @property
    def marc_500(self) -> List[dict]:
        if not self.__marc_500:
            self.__marc_500 = self.__get_data(
                field_name="x500s",
                subfield_name="x500"
            )
        return self.__marc_500


    @property
    def marc_main(self) -> List[dict]:
        if not self.__marc_main:
            self.__marc_main = self.__get_data(
                field_name="mainHeadings",
                subfield_name="mainHeadingEl"
            )
        return self.__marc_main

    @property
    def all_fields(self) -> dict:
        if not self.__all_fields:
            self.__all_fields = {
                "viaf_id": self.viaf_id,
                "viaf_url": self.viaf_url,
                "name": self.name,
                "name_type": self.name_type,
                "name_variations": self.name_variations,
                "birth_date": self.birth_date,
                "death_date": self.death_date,
                "occupations": self.occupations,
                "nationality": self.nationality,
                "activity_start": self.activity_start,
                "activity_end": self.activity_end,
                "has_isni": self.has_isni,
                "works": self.works,
                "wikilinks": self.wikilinks,
                "marc_400": self.marc_400,
                "marc_500": self.marc_500,
                "marc_main": self.marc_main
            }
        return self.__all_fields


class VIAFClient:
    def __init__(self,
            viaf_api_url: str = "https://viaf.org/api",
            allowed_viaf_sources: List[str] = VIAF_ALLOWED_SOURCES
        ):
        self.root_url: str = viaf_api_url.strip("/")
        self.record_url: str = f"{self.root_url}/cluster-record"
        self.search_url: str = f"{self.root_url}/search"
        self.headers: dict = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.allowed_viaf_sources: List[str] = allowed_viaf_sources

    def check_search_term_query(self) -> bool:
        """ Function for checking, if VIAF search term
        query works as expected.
        """
        test_entity = "Lennart Meri"
        record = self.get_normalized_data_by_search_term(
            search_term=test_entity,
            max_records=1,
            verify=False
        )
        success = True

        if record:
            if record.name != "Meri, Lennart":
                success = False
        else:
            success = False
        if not success:
            logger.error(f"VIAF search term query has changed or not working!")
        return success

    def check_id_query(self) -> bool:
        """ Function for checking, if VIAF search term
        query works as expected.
        """
        test_id = "84153775"
        records = self.get_normalized_data_by_ids([test_id])
        success = True
        if records:
            record = records[0]
            if record.name != "Meri, Lennart":
                success = False
        else:
            success = False

        if not success:
            logger.error(f"VIAF ID query has changed or not working!")
        return success

    @staticmethod
    def verify(entity: str, viaf_record: VIAFRecord,
            threshold: float = VIAF_SIMILARITY_THRESHOLD
    ) -> dict:
        """ Verifies, if entity to link is sufficiently
        similar to a VIAF Record based on name forms in
        VIAFRecord.name_variations.

        Parameters
        ------------
        entity: str
            Entity queried from VIAF.
        viaf_record: VIAFRecord
            A VIAFRecord object.
        threshold: float
            Min similarity threshold for a verified result
            Should be a float between 0 and 1.

        Returns
        ------------
        dict
            Dict with keys:
                verified: bool
                    If the VIAFRecord was verified to be
                    sufficiently similar.
                most_similar_record: str
                    The most similar string to entity
                    in VIAFRecord.name_variations.
                score: float
                    Similarity score of the most similar record.
        """
        logger.debug(
            f"Verifying if '{viaf_record.name}' is sufficiently similar to '{entity}'."
        )
        # might not always be personal name, but shouldn't break anything
        if len(entity.split()) > 1:
            pn = PersonalName(entity)
            name_forms = [pn.last_comma_first, pn.first_last]
        else:
            name_forms = [entity]
        max_similarity = 0
        most_similar_record = ""
        verified = False
        for var in viaf_record.name_variations:
            for name_form in name_forms:
                score = jw(name_form.lower(), var.lower())
                if score > max_similarity:
                    max_similarity = score
                    most_similar_record = var
                if score >= threshold:
                    logger.debug(
                        f"Verification successful! '{name_form}' sufficiently " \
                        f"similar to '{var}'! Score = {score}."
                    )
                    verified = True
                    break
            if verified:
                break
        out = {
            "verified": verified,
            "most_similar_record": most_similar_record,
            "score": max_similarity
        }
        return out

    @staticmethod
    def get_verified_record(search_term: str, viaf_records: List[VIAFRecord],
        threshold: float = VIAF_SIMILARITY_THRESHOLD
    ) -> VIAFRecord:
        """ Takes in n VIAFRecords found while searching the term `search_term`.
        Returns the most similar VIAFRecord.
        """
        logger.debug(
            f"Retrieving a single verified record from VIAF search results. " \
            f"search term = '{search_term}'."
        )
        verified_record = None
        max_score = 0
        most_similar_record = ""
        for record in viaf_records:
            verified = VIAFClient.verify(search_term, record, threshold)
            if verified.get("score") > max_score:
                most_similar_record = verified.get("most_similar_record")
                max_score = verified.get("score")
            if verified.get("verified"):
                verified_record = record
                break
        if not verified_record:
            logger.error(
                f"Verification failed. No matched record surpassed the set similarity " \
                f"threshold ({threshold}). Closest match for search term '{search_term}' was " \
                f"'{most_similar_record}' with similarity score {max_score} "
            )
        return verified_record

    def _send_request(self, url: str, data: dict) -> Response:
        return requests.post(url, data=json.dumps(data), headers=self.headers)

    def get_records_by_search_term(self,
            search_term: str,
            index: str = "VIAF",
            field: str = DEFAULT_VIAF_FIELD,
            page_index: int = 0,
            page_size: int = 50
     ) -> Response:
        """ Query VIAF records by search term.
        """
        logger.debug(f"Retriecing VIAF records for search term '{search_term}'.")
        if field and field not in ALLOWED_VIAF_FIELDS:
            logger.error(
                f"Field '{field}' is not allowed. Defaulting to '{DEFAULT_VIAF_FIELD}'. " \
                f"Allowed VIAF fields are: {ALLOWED_VIAF_FIELDS}. "
            )
            field = DEFAULT_VIAF_FIELD
        data = {
            "reqValues": {
                "field": field,
                "index": index,
                "searchTerms": search_term
            },
            "meta": {
                "env": "prod",
                "pageIndex": page_index,
                "pageSize": page_size
            }
        }
        response = self._send_request(url=self.search_url, data=data)
        return response

    def get_records_by_viaf_id(self, record_id: str) -> Response:
        """ Query VIAF records by ID.
        """
        logger.debug(f"Retrieving VIAF records for ID {record_id}.")
        data = {
            "reqValues": {
                "recordId": str(record_id)
            }
        }
        response = self._send_request(url=self.record_url, data=data)
        return response

    def extract_viaf_ids(self, search_query_response: Response) -> List[str]:
        """ Parse VIAF ID-s from search query response.
        """
        logger.debug("Extracting VIAF IDs from VIAF search query results.")
        try:
            records = search_query_response.json()["queryResult"]["records"]["record"]
        except Exception as e:
            logger.error(
                f"Parsing records from search query " \
                f"response failed with error: {e}."
            )
            records = []
        viaf_ids = []
        for record in records:
            try:
                viaf_id = record["recordData"]["VIAFCluster"]["viafID"]
                viaf_ids.append(viaf_id)
            except Exception as e:
                logger.error(
                    f"Extracing VIAF ID from record '{record}' " \
                    f"failed with error: {e}"
                )
        return viaf_ids

    def get_viaf_ids_by_search_terms(self,
            search_term: str, field: str = DEFAULT_VIAF_FIELD,
            viaf_index: str = "VIAF", page_size: int = 50
    ) -> List[str]:
        """ Get all matching VIAF IDs for a search term.
        """

        search_response = self.get_records_by_search_term(
            search_term=search_term,
            field=field,
            index=viaf_index,
            page_size=page_size
        )
        viaf_ids = self.extract_viaf_ids(search_response)
        return viaf_ids


    def fetch_viaf_clusters(self, viaf_ids: List[str]) -> Dict[str, dict]:
        results = {}
        for viaf_id in viaf_ids:
            try:
                response = self.get_records_by_viaf_id(viaf_id)
                response.raise_for_status()
                results[viaf_id] = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching VIAF record {viaf_id}: {e}")
                results[viaf_id] = {}

        return results

    def get_normalized_data_by_ids(self, record_ids: List[str]) -> List[VIAFRecord]:
        """ Fetch data required for normalization from VIAF. """
        logger.debug(f"Fetching VIAFRecords for the following IDs: {record_ids}.")
        response = self.fetch_viaf_clusters(record_ids)
        viaf_records = [
            VIAFRecord(
                record=response[record_id],
                allowed_sources=self.allowed_viaf_sources
            )
            for record_id in record_ids
        ]
        return viaf_records

    def get_normalized_data_by_search_term(self,
        search_term: str, field: str = DEFAULT_VIAF_FIELD, max_records: int = 10,
        verify: bool = True, threshold: float = VIAF_SIMILARITY_THRESHOLD,
        viaf_index: str = "VIAF"
    ) -> VIAFRecord | None:
        """ Fetch data required for normalization from VIAF. """
        logger.debug(
            f"Finding VIAFRecords with search term '{search_term}' " \
            f"using VIAF field='{field}', verify={verify}, threshold={threshold}. " \
            f"Allowed VIAF sources are: {self.allowed_viaf_sources}."
        )
        viaf_record = None
        verified_record = None
        viaf_ids = self.get_viaf_ids_by_search_terms(
            search_term=search_term,
            field=field,
            page_size=max_records,
            viaf_index=viaf_index
        )
        if verify:
            records = self.get_normalized_data_by_ids(viaf_ids[:max_records])
            verified_record = VIAFClient.get_verified_record(
                search_term=search_term,
                viaf_records=records,
                threshold=threshold
            )
        else:
            if viaf_ids:
                records = self.get_normalized_data_by_ids(viaf_ids[:1])
                verified_record = records[0] if records else None
        return verified_record
