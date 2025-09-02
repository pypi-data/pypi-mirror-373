import pymarc
from typing import NoReturn


class MarcConverter:
    def __init__(self):
        pass

    @staticmethod
    def marc21xml_to_mrc(input_file: str, output_file: str) -> NoReturn:
        """ Converts Marc21XML file into a MRC file.
        """
        with open(output_file, "wb") as f:
            writer = pymarc.MARCWriter(f)
            records = pymarc.marcxml.map_xml(writer.write, input_file)
