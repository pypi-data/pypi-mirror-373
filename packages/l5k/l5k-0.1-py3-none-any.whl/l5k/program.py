"""Storage object for programs."""

import dataclasses


@dataclasses.dataclass
class Program:
    """Storage object for a single program."""

    attributes: dict
    tags: dict


def convert(tokens):
    """Converts parser tokens into a Program object."""
    program = Program(
        attributes=tokens["attributes"][0],
        tags=tokens["tags"][0],
    )

    # Return a key/value pair to be collected into the parent controller's
    # programs attribute.
    return tokens["name"], program
