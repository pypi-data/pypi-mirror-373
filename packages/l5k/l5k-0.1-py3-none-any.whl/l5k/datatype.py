"""Storage objects for user-defined data types."""

import collections
import dataclasses


@dataclasses.dataclass
class DataType:
    """A user-defined data type."""

    members: collections.OrderedDict
    attributes: dict = dataclasses.field(default_factory=dict)


def convert_datatype(tokens):
    """Converts parsing tokens into a DataType instance."""
    datatype = DataType(
        attributes=tokens["attributes"][0],
        members=collections.OrderedDict(list(tokens["members"])),
    )

    # Returned as a name/type pair to populate the datatype dictionary
    # in the parent controller object.
    return tokens["name"], datatype


@dataclasses.dataclass
class Member:
    """A normal(non-bit) member of a user-defined data type."""

    datatype: str
    dim: tuple = None
    attributes: dict = dataclasses.field(default_factory=dict)


def convert_member(tokens):
    """Converts parsing tokens into a Member instance."""
    try:
        dim = tokens["dim"][0]
    except KeyError:
        dim = None

    member = Member(
        datatype=tokens["datatype"],
        dim=dim,
        attributes=tokens["attributes"][0],
    )

    # A name/member pair is returned to be collected into the parent
    # DataType members dictionary.
    return tokens["name"], member


@dataclasses.dataclass
class BitMember:
    """A bit member of a user-defined data type."""

    target: str
    bit: int
    attributes: dict = dataclasses.field(default_factory=dict)


def convert_bit_member(tokens):
    """Converts parsing tokens into a BitMember instance."""
    member = BitMember(
        target=tokens["target"],
        bit=tokens["bit"],
        attributes=tokens["attributes"][0],
    )

    # A name/member pair is returned to be collected into the parent
    # DataType members dictionary.
    return tokens["name"], member
