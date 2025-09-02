from pymarc import Indicators
import os

class EntityType:
    PER = "PER"
    ORG = "ORG"
    KEYWORD = "EMS_KEYWORD"
    LOC = "LOC"
    TITLE = "TITLE"
    UNK = "UNKNOWN"


EMPTY_INDICATORS = Indicators(" ", " ")
VIAF_ALLOWED_SOURCES = ["LC", "DNB", "LNB", "NLL",
                        "ERRR", "J9U"]

DEFAULT_VIAF_FIELD = "local.names"

ALLOWED_VIAF_FIELDS = [
    "cql.any",                          # All fields
    "local.names",                      # All headings
    "local.personalNames",              # Personal names
    "local.corporateNames",             # Corporate names
    "local.geographicNames",            # Geographic names
    "local.uniformTitleWorks",          # Works
    "local.uniformTitleExpressions",    # Expressions
    "local.mainHeadingEl",              # Preferred headings
    "Xlocal.names",                     # Exact headings
    "local.title"                       # Bibliographic titles
]

# For mapping rara-linker's entity type's to corresponding VIAF fields
VIAF_ENTITY_MAP = {
    EntityType.PER: "local.personalNames",
    EntityType.ORG: "local.corporateNames",
    EntityType.LOC: "loca.geographicNames",
    EntityType.TITLE: "local.uniformTitleWorks"


}
ALLOWED_VIAF_WIKILINK_LANGS = ["en", "et"]
VIAF_SIMILARITY_THRESHOLD = 0.92
VERIFY_VIAF_RECORD = True
MAX_VIAF_RECORDS_TO_VERIFY = 10
