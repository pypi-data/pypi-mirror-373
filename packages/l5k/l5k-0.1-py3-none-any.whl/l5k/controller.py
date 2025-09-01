"""Storage representation of the top-level Controller component."""

import copy
import dataclasses

from . import builtin


@dataclasses.dataclass
class Controller:
    """Storage object for the top-level Controller component."""

    name: str
    attributes: dict
    datatypes: dict
    aois: dict
    tags: dict
    programs: dict

    def __post_init__(self):
        # Tag values are converted after initialization because
        # data type definions are now available.
        self._convert_tag_values()

    def _convert_tag_values(self):
        """Converts tag values across all scopes."""
        # Combine built-in, AOIs, and user-defined types into a complete set of
        # data types for value conversion.
        datatypes = copy.copy(builtin.BUILT_INS)
        datatypes.update(self.aois)
        datatypes.update(self.datatypes)

        # Controller tags
        for t in self.tags.values():
            t.convert_value(datatypes)

        # Program tags
        for prg in self.programs.values():
            for tag in prg.tags.values():
                tag.convert_value(datatypes)


def convert(tokens):
    """Converts the parser tokens into a Controller object."""
    return Controller(
        tokens["name"],
        tokens["attributes"][0],
        datatypes=tokens["datatypes"][0],
        aois=tokens["aois"][0],
        tags=tokens["tags"][0],
        programs=tokens["programs"][0],
    )
