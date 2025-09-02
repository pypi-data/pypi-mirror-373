from typing import NoReturn
from collections.abc import Iterator
from rara_tools.parsers.marc_parsers.base_parser import BaseMARCParser
from rara_tools.parsers.marc_records.ems_record import EMSRecord
from rara_tools.constants.parsers import KeywordType, LOGGER


class LocationMARCParser(BaseMARCParser):
    """ MARC parser for EMS .mrc files.
    """
    def __init__(self,
            marc_file_path: str,
            add_variations: bool = True
        ) -> NoReturn:
        """ Initializes LocationMARCParser object.

        Parameters
        -----------
        marc_file_pasth: str
            Full path to .mrc file containing EMS data.
        add_variations: bool
            If enabled, constructs an additional variations field, which
            combines the content of multiple fields + adds some generated
            variations. If the output is uploaded into Elastic and used
            via rara-norm-linker, it is necessary to enable this.
        """

        super().__init__(
            marc_file_path=marc_file_path,
            add_variations=add_variations
        )

    def record_generator(self) -> Iterator[EMSRecord]:
        """ Generates EMSRecord objects for location keywords.
        """
        LOGGER.info(
            f"Generating EMS-based location records " \
            f"from MARC dump '{self.marc_file_path}'."
        )
        for record in self.marc_record_generator():
            try:
                ems_record = EMSRecord(
                    record=record,
                    add_variations=self.add_variations
                )
                if ems_record.keyword_type == KeywordType.LOC:
                    yield ems_record.full_record
            except Exception as e:
                LOGGER.warning(
                    f"Error while parsing record {record}: {e}"
                )
                continue
