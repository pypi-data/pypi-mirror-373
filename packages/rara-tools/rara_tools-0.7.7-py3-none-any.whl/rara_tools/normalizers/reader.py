from pymarc import Record, Field, Subfield, Leader, JSONReader
import logging

logger = logging.getLogger(__name__)

DEFAULT_LEADER = '01682nz a2200349n 4500'

class SafeJSONReader(JSONReader):

    def __next__(self):
        while True:
            try:
                jobj = next(self.iter)
                rec = Record()

                # Use custom default leader if missing
                leader_str = jobj.get("leader")
                if leader_str:
                    rec.leader = Leader(leader_str)
                else:
                    logger.warning("Missing leader in record. Using DEFAULT_LEADER.")
                    rec.leader = Leader(DEFAULT_LEADER)

                for field in jobj["fields"]:
                    k, v = list(field.items())[0]

                    if isinstance(v, dict) and "subfields" in v:
                        subfields = []
                        for sub in v["subfields"]:
                            for code, value in sub.items():
                                subfields.append(Subfield(code, value))
                        ind1 = v.get("ind1", " ")
                        ind2 = v.get("ind2", " ")
                        fld = Field(tag=k, indicators=[ind1, ind2], subfields=subfields)
                    else:
                        fld = Field(tag=k, data=v)
                    rec.add_field(fld)

                return rec

            except StopIteration:
                raise
            except Exception as e:
                logger.error(f"Skipping invalid record: {e}")
                continue
