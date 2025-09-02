from typing import NoReturn
from collections.abc import Iterator
from rara_tools.parsers.marc_parsers.base_parser import BaseMARCParser
from rara_tools.parsers.marc_records.organization_record import OrganizationRecord
from rara_tools.constants.parsers import LOGGER


class OrganizationsMARCParser(BaseMARCParser):
    """ MARC parser for organizations' .mrc files.
    """
    def __init__(self,
            marc_file_path: str,
            add_variations: bool = True
        ) -> NoReturn:
        """ Initializes OrganizationsMARCParser object.

        Parameters
        -----------
        marc_file_path: str
            Full path to .mrc file containing organizations' data.
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

    def record_generator(self) -> Iterator[OrganizationRecord]:
        """ Generates OrganizationRecord objects.
        """
        LOGGER.info(
            f"Generating organization records from " \
            f"MARC dump '{self.marc_file_path}'."
        )
        for record in self.marc_record_generator():
            org_record = OrganizationRecord(
                record=record,
                add_variations=self.add_variations
            )
            yield org_record.full_record
