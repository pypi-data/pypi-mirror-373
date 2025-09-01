"""Add-on instruction storage objects."""

import collections
import dataclasses
import itertools

from . import datatype


@dataclasses.dataclass
class AddOnInstruction:
    """Storage object for an add-on instruction definition."""

    attributes: dict
    parameters: collections.OrderedDict
    local_tags: collections.OrderedDict
    value_members: collections.OrderedDict = dataclasses.field(
        default_factory=collections.OrderedDict,
        init=False,
    )
    packed_bools: dict = dataclasses.field(default_factory=dict, init=False)

    def __post_init__(self):
        self._populate_value_members()
        self._assemble_bools()

    def _populate_value_members(self):
        """Assembles members whose value is stored in the tag value.

        All non-InOut parameters and all local tags get their value stored
        in AOI instances.
        """
        # Start with non-InOut parameters.
        for name, param in self.parameters.items():
            try:
                if param.attributes["Usage"] == "InOut":
                    continue
            except KeyError:
                pass
            self.value_members[name] = param

        # Add all local tags after the parameters.
        self.value_members.update(self.local_tags)

    def _assemble_bools(self):
        """Collects BOOL values that are packed into words.

        BOOL values are implicitly packed into 32-bit words(DINT), starting
        with parameters, followed by local tags. Pack order follows the
        definition order, and does not separate parameters and local tags,
        i.e., BOOL parameters may share the same DINT with BOOL local tags.
        """
        bools = []
        for name, member in self.value_members.items():
            # Add non-array BOOLs; BOOL arrays are excluded because they
            # are not packed into words.
            if member.datatype == "BOOL" and not member.dim:
                bools.append(name)

        # Organize resulting BOOL items into groups of 32, each
        # representing a single DINT, and keyed by the first member's name.
        for bits in itertools.batched(bools, 32):
            self.packed_bools[bits[0]] = bits


def convert(tokens):
    """Converts parser tokens into an AOI definition object."""
    params = list(tokens["parameters"])

    # Some Logix versions do not explicitly list the EnableIn and
    # EnableOut parameters. Those two parameters are always present, so
    # they are added here if omitted from the AOI definition.
    try:
        if params[0][0] != "EnableIn":
            raise IndexError
    except IndexError:
        params.insert(
            0,
            (
                "EnableIn",
                datatype.Member(
                    datatype="BOOL",
                    attributes={"Usage": "Input"},
                ),
            ),
        )
        params.insert(
            1,
            (
                "EnableOut",
                datatype.Member(
                    datatype="BOOL",
                    attributes={"Usage": "Output"},
                ),
            ),
        )

    aoi = AddOnInstruction(
        attributes=tokens["attributes"][0],
        parameters=collections.OrderedDict(params),
        local_tags=collections.OrderedDict(list(tokens["local_tags"])),
    )

    return tokens["name"], aoi
