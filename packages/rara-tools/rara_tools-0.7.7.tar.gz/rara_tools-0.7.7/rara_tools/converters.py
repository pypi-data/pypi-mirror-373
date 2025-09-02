from rara_tools.exceptions import SierraResponseConverterException


class SierraResponseConverter:
    """Converts a JSON response from the Sierra API to MARC-in-JSON format."""

    def __init__(self, response: dict):
        if not isinstance(response, dict):
            raise SierraResponseConverterException(
                "Please provide a valid JSON response.")
        self.response = response

    @staticmethod
    def _map_control_fields(field: dict) -> dict:
        # for tags < 010, no subfields, instead one str value in "value"
        return {field["tag"]: field["value"]}
    
    def _map_data_field_subfields(self, subfields: list) -> list:
        """ Maps data field subfields to the standardised format, if necessary.

        Args:
            subfields (list): List of subfields in format e.g
              "subfields": [
                        {
                            "code": "a",
                            "data": "foo"
                        }, 
                        {
                            "code": "c",
                            "data": "by me."
                        }
                    ]

        Returns:
            list: standardised marc-in-json format. e.g 
             "subfields": [
                            { "a": "foo /" },
                            { "c": "by me." }
                                ]
        """
        result = []
        for subfield in subfields:
            
            code = subfield.get("code")
            data = subfield.get("data")

            if not code or not data:
                # assume that the subfield is already in the correct format
                return subfields
            else:
                result.append({code: data})
                
        return result


    def _map_data_fields(self, field: dict) -> dict:
        """ Maps marc fields > 010. 

        Args:
            field (dict): Contains the marc tag and list with indicators and subfields.

        Returns:
            dict: standardised marc-in-json format.
        """

        data = field["data"]
        subfields = data.get("subfields", [])

        # Order matters ind1, in2, subfields
        field_data = {
            "ind1": data.get("ind1", " "),
            "ind2": data.get("ind2", " "),
            "subfields": self._map_data_field_subfields(subfields)
        }

        return {field["tag"]: field_data}

    @staticmethod
    def _is_marc21structured(field: dict) -> bool:
        """Checks if the field is already structured according to MARC21 in JSON"""
        return any(key.isdigit() for key in field.keys())
    
    def _handle_field_type(self, field: dict) -> dict:

        if self._is_marc21structured(field):
            return field

        if field.get("data"):
            return self._map_data_fields(field)

        tag = field.get("tag")

        if not tag:
            raise SierraResponseConverterException(
                "Field is missing MARC21 tag.")

        if tag < "010":
            return self._map_control_fields(field)
        else:
            return self._map_data_fields(field)

    def _convert_response(self) -> list:
        entries = self.response.get("entries")
        if not entries:
            raise SierraResponseConverterException(
                "No entries found in the response.")

        try:
            return [
                {
                    "sierraID": str(e["id"]),
                    "leader": e["marc"]["leader"],
                    "fields": [
                        self._handle_field_type(f) for f in e["marc"]["fields"]
                    ]}
                for e in entries
            ]

        except KeyError as e:
            raise SierraResponseConverterException(
                f"Malformed response: missing key {e}")

    def convert(self) -> list:
        try:
            return self._convert_response()
        except Exception as e:
            raise SierraResponseConverterException(
                f"An unexpected error occurred: {e}")
