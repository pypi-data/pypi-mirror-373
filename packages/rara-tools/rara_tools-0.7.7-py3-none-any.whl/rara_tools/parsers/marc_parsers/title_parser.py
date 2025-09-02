from typing import NoReturn
from collections.abc import Iterator
from rara_tools.parsers.marc_parsers.base_parser import BaseMARCParser
from rara_tools.parsers.marc_records.title_record import TitleRecord
from rara_tools.constants.parsers import LOGGER


class TitlesMARCParser(BaseMARCParser):
    """ MARC parser for titles' .mrc files.
    """
    def __init__(self,
            marc_file_path: str,
            add_variations: bool = True
        ) -> NoReturn:
        """ Initializes OrganizationsMARCParser object.

        Parameters
        -----------
        marc_file_path: str
            Full path to .mrc file containing titles' data.
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

    def record_generator(self) -> Iterator[TitleRecord]:
        """ Generates TitleRecord objects.
        """
        LOGGER.info(
            f"Generating title records from " \
            f"MARC dump '{self.marc_file_path}'."
        )
        for record in self.marc_record_generator():
            title_record = TitleRecord(
                record=record,
                add_variations=self.add_variations
            )
            yield title_record.full_record
