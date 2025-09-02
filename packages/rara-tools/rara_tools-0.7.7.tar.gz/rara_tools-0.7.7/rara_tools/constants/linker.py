import logging

from rara_tools.constants.normalizers import EntityType

COMPONENT_KEY = "linker"


class Tasks:
    BASE = "base_linker_task"
    VECTORIZE = "vectorize_text"
    VECTORIZE_WITH_CORE = "vectorize_text_with_core_logic"
    PIPELINE = "link_keywords_with_core_logic"

    LINK_AND_NORMALIZE = "core_linker_with_normalization"
    VECTORIZE_AND_INDEX = "core_vectorize_and_index"
    RECEIVE_LINK_AND_NORMALIZE = "receive_link_and_normalize"


class Queue:
    LINKER = "linker"
    VECTORIZER = "vectorizer"


class StatusKeys:
    VECTORIZE_CONTEXT = "vectorize_context"
    LINK_KEYWORDS = "link_keywords"


class URLSource:
    VIAF = "VIAF"
    SIERRA = "Sierra"
    EMS = "EMS"


class KeywordType:
    LOC = "Kohamärksõnad"
    TIME = "Ajamärksõnad"
    TOPIC = "Teemamärksõnad"
    GENRE = "Vormimärksõnad"
    TITLE = "Teose pealkiri"
    PER = "Isikunimi"
    ORG = "Kollektiivi nimi"
    EVENT = "Ajutine kollektiiv või sündmus"
    CATEGORY = "Valdkonnamärksõnad"
    UDC = "UDC Summary"
    UDK = "UDK Rahvusbibliograafia"


class KeywordMARC:
    PER = 600
    ORG = 610
    TOPIC = 650
    GENRE = 655
    TIME = 648
    LOC = 651
    EVENT = 611
    TITLE = 630
    TITLE_LINKED = 600


class KeywordSource:
    EMS = "EMS"
    SIERRA = "SIERRA"
    VIAF = "VIAF"
    AI = "AI"


class Filters:
    AUTHOR = "author"
    YEAR = "year"


class Error:
    VECTORIZATION = "Failed to vectorize text!"
    LINKING_KEYWORDS = "Failed to link keywords!"
    LINKING_META = "Failed to link meta!"

UNLINKED_KEYWORD_MARC_FIELD = 693

ALLOWED_FILTERS_MAP = {
    EntityType.PER: [Filters.YEAR],
    EntityType.ORG: [Filters.YEAR],
    EntityType.TITLE: [Filters.YEAR, Filters.AUTHOR],
    EntityType.KEYWORD: [],
    EntityType.LOC: []
}
KEYWORD_MARC_MAP = {
    KeywordType.LOC: KeywordMARC.LOC,
    KeywordType.TIME: KeywordMARC.TIME,
    KeywordType.TOPIC: KeywordMARC.TOPIC,
    KeywordType.GENRE: KeywordMARC.GENRE,
    KeywordType.TITLE: KeywordMARC.TITLE,
    KeywordType.ORG: KeywordMARC.ORG,
    KeywordType.PER: KeywordMARC.PER,
    KeywordType.EVENT: KeywordMARC.EVENT
}

URL_SOURCE_MAP = {
    EntityType.PER: URLSource.VIAF,
    EntityType.ORG: URLSource.VIAF,
    EntityType.TITLE: URLSource.VIAF,
    EntityType.KEYWORD: URLSource.EMS,
    EntityType.LOC: URLSource.EMS
}

# Ignore those "keyword types" while linking the
# rara-subject-indexer results
KEYWORD_TYPES_TO_IGNORE = [
    KeywordType.CATEGORY,
    KeywordType.UDC,
    KeywordType.UDK
]

ALLOWED_ENTITY_TYPES = [
    EntityType.PER,
    EntityType.ORG,
    EntityType.KEYWORD,
    EntityType.LOC,
    EntityType.TITLE,
    EntityType.UNK,
]

KEYWORD_TYPE_MAP = {
    KeywordType.TIME: EntityType.KEYWORD,
    KeywordType.GENRE: EntityType.KEYWORD,
    KeywordType.LOC: EntityType.LOC,
    KeywordType.PER: EntityType.PER,
    KeywordType.ORG: EntityType.ORG,
    KeywordType.TOPIC: EntityType.KEYWORD,
    KeywordType.TITLE: EntityType.TITLE,
    KeywordType.EVENT: EntityType.ORG
}

EMS_ENTITY_TYPES = [EntityType.KEYWORD, EntityType.LOC]
SIERRA_ENTITY_TYPES = [EntityType.PER, EntityType.ORG, EntityType.TITLE]
VIAF_ENTITY_TYPES = [EntityType.PER, EntityType.ORG, EntityType.TITLE]

# Params for filters
MIN_AUTHOR_SIMILARITY = 0.95
YEAR_EXCEPTION_VALUE = True

LOGGER_NAME = "rara-tools-norm-linker"
LOGGER = logging.getLogger(LOGGER_NAME)

MAIN_TAXONOMY_LANG = "et"
