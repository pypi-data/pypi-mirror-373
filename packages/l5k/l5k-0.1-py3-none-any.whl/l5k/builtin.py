"""Definitions for built-in structured data types.

This list is far from exhaustive; built-ins not defined here will return
unstructured values, i.e., a raw list of values.

Data formats for these types have been determined empirically as they are
otherwise undocumented.
"""

from .datatype import DataType, Member, BitMember


BUILT_INS = {
    "CONTROL": DataType(
        members={
            "bits": Member(datatype="DINT", attributes={"Hidden": "1"}),
            "EN": BitMember(target="bits", bit=31),
            "EU": BitMember(target="bits", bit=30),
            "DN": BitMember(target="bits", bit=29),
            "EM": BitMember(target="bits", bit=28),
            "ER": BitMember(target="bits", bit=27),
            "UL": BitMember(target="bits", bit=26),
            "IN": BitMember(target="bits", bit=25),
            "FD": BitMember(target="bits", bit=24),
            "LEN": Member(datatype="DINT"),
            "POS": Member(datatype="DINT"),
        }
    ),
    "COUNTER": DataType(
        members={
            "bits": Member(datatype="DINT", attributes={"Hidden": "1"}),
            "PRE": Member(datatype="DINT"),
            "ACC": Member(datatype="DINT"),
            "CU": BitMember(target="bits", bit=31),
            "CD": BitMember(target="bits", bit=30),
            "DN": BitMember(target="bits", bit=29),
            "OV": BitMember(target="bits", bit=28),
            "UN": BitMember(target="bits", bit=27),
        }
    ),
    "TIMER": DataType(
        members={
            "bits": Member(datatype="DINT", attributes={"Hidden": "1"}),
            "PRE": Member(datatype="DINT"),
            "ACC": Member(datatype="DINT"),
            "EN": BitMember(target="bits", bit=31),
            "TT": BitMember(target="bits", bit=30),
            "DN": BitMember(target="bits", bit=29),
        }
    ),
}
