"""Object storage for tag instances."""

import dataclasses
import functools
import operator
import typing


def convert_dim(tokens):
    """Converts parsing tokens into an array dimension.

    Dimensions appear in the L5K as "[Dim2,Dim1,Dim0]"; they are reversed so
    the resulting storage tuple can be indexed as tuple[DimX] = DimX.
    """
    dim = tokens.as_list()
    dim.reverse()
    return tuple(dim)


@dataclasses.dataclass
class Tag:
    """Storage for a single, non-alias tag."""

    datatype: str
    dim: tuple
    attributes: dict
    value: typing.Any

    def convert_value(self, datatypes):
        """Replaces the value with an object representing the data type."""
        self.value = convert_value(datatypes, self.datatype, self.dim, self.value)


def convert_tag(tokens):
    """Converts parsing tokens into a Tag instance."""
    try:
        dim = tokens["dim"][0]
    except KeyError:
        dim = None

    try:
        raw = tokens["value"]
        value = raw.as_list()
    except KeyError:
        value = None

    # Atomic value, not a list of values.
    except AttributeError:
        value = raw

    tag = Tag(
        datatype=tokens["datatype"],
        dim=dim,
        attributes=tokens["attributes"][0],
        value=value,
    )

    return tokens["name"], tag


def convert_value(datatypes, type_name, dim, raw):
    """Translates a raw value into an object representing the data type.

    Compound types, such as arrays and UDTs, are converted recursively,
    yielding a nested Python data structure representing the data type.
    """
    if dim:
        return array_value(datatypes, type_name, dim, raw)

    try:
        this_type = datatypes[type_name]

    # Undefined types simply return the original raw value. This applies
    # to base data types such as INT and REAL as those values have already
    # been converted by the parser, and built-in structures lacking
    # a manual definition, e.g., CONTROL and MESSAGE.
    except KeyError:
        return raw

    try:
        this_type.local_tags
    except AttributeError:
        return struct_value(datatypes, this_type, raw)
    return aoi_value(datatypes, this_type, raw)


def struct_value(datatypes, this_type, raw):
    """Converts raw tag data for a structured data type, e.g, UDT.

    Structured data types are converted into dictionaries, with member
    names as keys.
    """
    struct = {}

    for member_name, member in this_type.members.items():
        try:
            member_value = (struct[member.target] >> member.bit) & 1

        except AttributeError:
            member_value = convert_value(
                datatypes,
                member.datatype,
                member.dim,
                raw.pop(0),
            )

        struct[member_name] = member_value

    strip_hidden(this_type, struct)
    return struct


def strip_hidden(datatype, value):
    """Removes hidden members from a structured data value."""
    remove = set()

    for name, member in datatype.members.items():
        try:
            hidden = member.attributes["Hidden"]
        except KeyError:
            continue
        if int(hidden) == 1:
            remove.add(name)

    for member in remove:
        del value[member]


def array_value(datatypes, this_type, dim, raw):
    """Converts raw tag data for an array.

    Array values are converted to a list. The original raw data is also
    a list, however, each of the values are now converted based on the
    array's data type.
    """
    array = []

    # Remove most most-significant dimension to determine the dimensions,
    # if any, that will apply to array items.
    item_dim = dim[:-1]

    for i in range(dim[-1]):

        # Recursively generate a nested list if dimensions remain, i.e.,
        # multidimensional array.
        if item_dim:
            # Compute the number of list items allocated to the subarray as
            # the product of all remaining dimensions.
            subarray_len = functools.reduce(operator.mul, item_dim, 1)

            # Compute the range of raw data items assigned to the subarray.
            start = i * subarray_len
            end = start + subarray_len
            subarray_data = raw[start:end]

            item = array_value(datatypes, this_type, item_dim, subarray_data)

        # Add converted array values if no dimensions remain, i.e., no
        # further nesting for this array.
        else:
            item = convert_value(datatypes, this_type, None, raw[i])

        array.append(item)

    return array


def aoi_value(datatypes, aoi, raw):
    """Converts raw tag data into a structured AOI value."""
    value = {}
    for name, member in aoi.value_members.items():
        # Skip packed BOOLs that have already been converted.
        if name in value:
            continue

        next_raw = raw.pop(0)

        # See if this is a packed BOOL member.
        try:
            bits = aoi.packed_bools[name]

        # Convert nonpacked BOOL members.
        except KeyError:
            value[name] = convert_value(
                datatypes,
                member.datatype,
                member.dim,
                next_raw,
            )

        # Extract all members packed from this DINT value.
        else:
            for bname in bits:
                value[bname] = next_raw & 1
                next_raw >>= 1

    return value
