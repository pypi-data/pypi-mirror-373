from dataclasses import dataclass

COMPONENT_KEY = "meta_extractor"


class Tasks:
    SINGLE = "extract_meta_from_text"
    PIPELINE = "run_meta_extractor_with_core_logic"


class Queue:
    MAIN = "meta_extractor"


class StatusKeys:
    EXTRACT_METADATA = "extract_metadata"

class Error:
    UNKNOWN = "Failed to extract meta information from digitizer output!"


@dataclass(frozen=True)
class TitleType:
    AUTHOR_WITHOUT_TITLE: str = "pealkirjata autor"
    NORMALIZED_TITLE: str = "normitud eelispealkiri"
    TITLE: str = "väljaandes esitatud kujul põhipealkiri"
    PARALLEL_TITLE: str = "rööppealkiri"
    ADDITIONAL_TITLE: str = "alampealkiri"
    METS_TITLE: str = "väljaandes esitatud kujul põhipealkiri"
    ANON: str = "anonüümne väljaanne"


TITLE_TYPES_MAP = {
    TitleType.AUTHOR_WITHOUT_TITLE: 130,
    TitleType.NORMALIZED_TITLE: 240,
    TitleType.TITLE: 245,
    TitleType.PARALLEL_TITLE: 246,
    TitleType.ADDITIONAL_TITLE: 245,
    TitleType.METS_TITLE: 245,
    TitleType.ANON: 130
}


PUBLISHER_KEY = "Väljaandja"
