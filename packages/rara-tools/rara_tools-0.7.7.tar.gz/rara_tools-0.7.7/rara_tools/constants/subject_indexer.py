from rara_tools.constants.normalizers import EntityType

COMPONENT_KEY = "subject_indexer"


class Tasks:
    SINGLE = "run_subject_indexer_process"
    PIPELINE = "run_subject_indexer_with_core_logic"
    PURGE_MODELS = "purge_unused_subjectindexer_models"


class Queue:
    MAIN = "subject-indexer"
    UTILITY = "subjectindexer-utility"


class StatusKeys:
    EXTRACT_KEYWORDS = "extract_keywords"


class Error:
    UNKNOWN = "Could not extract keywords from text!"


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


class KeywordSource:
    EMS = "EMS"
    SIERRA = "SIERRA"
    VIAF = "VIAF"
    AI = "AI"


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

KEYWORD_TYPES_TO_IGNORE = [
    KeywordType.CATEGORY,
    KeywordType.UDC,
    KeywordType.UDK
]

EMS_ENTITY_TYPES = [EntityType.KEYWORD, EntityType.LOC]
SIERRA_ENTITY_TYPES = [EntityType.PER, EntityType.ORG, EntityType.TITLE]
VIAF_ENTITY_TYPES = [EntityType.PER, EntityType.ORG, EntityType.TITLE]
