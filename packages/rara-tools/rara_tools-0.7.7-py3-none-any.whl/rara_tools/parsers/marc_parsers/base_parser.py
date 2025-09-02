from typing import List, NoReturn
from pymarc.record import Record
from pymarc import MARCReader
from abc import abstractmethod
from collections.abc import Iterator, Iterable
import jsonlines


class BaseMARCParser:
    """ Base class for MARC parsers.
    """
    def __init__(self,
            marc_file_path: str,
            add_variations: bool = True
        ) -> NoReturn:
        """ Initializes BaseMARCParser object.

        Parameters
        -----------
        marc_file_path: str
            Full path to .mrc file containing EMS data.
        add_variations: bool
            If enabled, constructs an additional variations field, which
            combines the content of multiple fields + adds some generated
            variations. If the output is uploaded into Elastic and used
            via rara-norm-linker, it is necessary to enable this.
        """
        self.add_variations = add_variations
        self.marc_file_path = marc_file_path

    def _write_line(self, line: dict, file_path: str) -> NoReturn:
        with jsonlines.open(file_path, "a") as f:
            f.write(line)

    def marc_record_generator(self) -> Iterator[Record]:
        """ Generates pymarc.record.Record objects.
        """
        with open(self.marc_file_path, "rb") as fh:
            reader = MARCReader(fh)
            for record in reader:
                if record:
                    yield record

    @abstractmethod
    def record_generator(self) -> Iterator:
        pass

    def save_as_jl(self, jl_file_path: str) -> NoReturn:
        for record in self.record_generator():
            self._write_line(record, jl_file_path)
