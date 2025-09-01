"""
This module implements the grammar to parse L5K content into tokens.
Other modules then convert these tokens into storage objects to be returned
to the user.

Many expressions defined here are liberal, possibly matching technically
invalid content. This is in the interest of simplicity as strict
expressions will invariably be more complicated; the intent of this
module is to extract information from well-formed sources, i.e., files
created by Logix5000.

The reference document used to define this grammer is Logix 5000
Controllers Import/Export Reference Manual, Rockwell Automation Publication
1756-RM014C-EN-P - September 2024.
"""

import pyparsing as pp

from . import (
    aoi,
    controller,
    datatype,
    program,
    tag,
)


def parse(filename):
    """Parses an L5K file."""
    result = prj.parse_file(filename, encoding="utf-8-sig")
    return result["controller"]


# The remainder of this file is excluded from Black formatting to preserve
# multi-line expressions, which Black may otherwise combine into a single
# line.
# fmt: off


def component(name, expr):
    """
    Creates an expression to parse a component between <name> and END_<name>
    keywords.
    """
    return (
        pp.Suppress(pp.Keyword(name))
        + expr
        + pp.Suppress(pp.Keyword(f"END_{name}"))
    )


# Optional header at the beginning of the file.
header = pp.Opt(pp.Suppress(
    pp.Regex(r"\(\*+")
    + pp.SkipTo("*)")
    + pp.Literal("*)")
))

assign = pp.Suppress(":=")
terminator = pp.Suppress(";")

# Version statement following the header.
version = pp.Suppress(
    pp.Keyword("IE_VER")
    + assign
    + pp.Regex(r"[\d.]+")
    + terminator
)

# Module names can be the combination of parent modules, separated by colons.
module_name = pp.Word(pp.alphanums + "_:")

# Name of a data type, which can also be a module type.
data_type_name = module_name

# Value on the right side of an attribute assignment.
attribute_value = pp.MatchFirst([
    pp.QuotedString('"'),

    # Unquoted values may include spaces, and continue until terminated by
    # another key/value(comma) or the end of the attribute list(parenthesis).
    pp.Word(pp.printables, pp.printables + " ", exclude_chars=",)")
])

# A single attribute key/value assignment.
attribute = pp.Group(
    pp.Word(pp.printables)
    + assign
    + attribute_value
)

attribute_list = pp.Opt(
    pp.Suppress("(")
    + pp.Dict(pp.DelimitedList(attribute), asdict=True)
    + pp.Suppress(")"),
    default={}
)

# A property is an assignment statement appearing in a component body
# after the attribute list.
prop_with_value = (
    pp.common.identifier

    # Some properties, e.g., safety CONNECTION InputData and OutputData,
    # include an attribute list which does not appear in the reference
    # documentation.
    + attribute_list

    + assign
    + pp.Regex(r"[^;]+").leave_whitespace()
    + terminator
)

# The assigned value is optional, such as with the undocumented
# MODULE InputAliasComments.
prop_no_value = (
    pp.common.identifier
    + attribute_list
    + terminator
)

prop_list = pp.ZeroOrMore(prop_with_value | prop_no_value)

# Comma-separated list of integers that may follow a tag name or type.
array_dim = pp.Opt(
    pp.Suppress("[")
    + pp.DelimitedList(pp.common.integer).set_parse_action(tag.convert_dim)
    + pp.Suppress("]")
)

binary_value = pp.Suppress("2#") + pp.Regex(r"[_01]+")
binary_value.add_parse_action(lambda toks: int(toks[0], 2))
octal_value = pp.Suppress("8#") + pp.Regex(r"[_0-7]+")
octal_value.add_parse_action(lambda toks: int(toks[0], 8))
decimal_value = pp.common.signed_integer
hex_value = pp.Suppress("16#") + pp.common.hex_integer
ascii_value = pp.QuotedString("'")
exp_value = pp.common.sci_real
float_value = pp.common.real

data_value = pp.Or([
    binary_value,
    octal_value,
    decimal_value,
    hex_value,
    ascii_value,
    exp_value,
    float_value,
])

# Recursive expression to capture the complete value of a tag. These may
# be a single value, or a list of, possibly nested, values.
tag_value = pp.Forward()
value_list = pp.Group(
    pp.Suppress("[")
    + pp.DelimitedList(tag_value)
    + pp.Suppress("]")
)
tag_value <<= data_value | value_list

# Statement defining a regular(nonbit) UDT member.
struct_member = (
    data_type_name("datatype")
    + pp.common.identifier("name")
    + array_dim("dim")
    + attribute_list("attributes")
    + terminator
)
struct_member.set_parse_action(datatype.convert_member)

# Statement defining a single-bit UDT member.
bit_member = (
    pp.Suppress(pp.Keyword("BIT"))
    + pp.common.identifier("name")
    + pp.common.identifier("target")
    + pp.Suppress(":")
    + pp.common.integer("bit")
    + attribute_list("attributes")
    + terminator
)
bit_member.set_parse_action(datatype.convert_bit_member)

# Statement define a single UDT member of any type.
data_type_member = struct_member | bit_member

# Data type defintion component.
DATATYPE = component(
    "DATATYPE",
    pp.common.identifier("name")
    + attribute_list("attributes")
    + pp.OneOrMore(data_type_member)("members")
)
DATATYPE.set_parse_action(datatype.convert_datatype)

# Connection definition component.
CONNECTION = component(
    "CONNECTION",
    pp.common.identifier
    + attribute_list
    + prop_list
)

module_ext_prop = pp.Opt(
    pp.Suppress("ExtendedProp")
    + assign
    + pp.QuotedString("[[[___", end_quote_char="___]]]")
)

# Module definition component.
MODULE = component(
    "MODULE",
    pp.MatchFirst([module_name, pp.Keyword("$NoName")])
    + attribute_list

    # Extended properties come before other properties, such as ConfigData,
    # even though the reference documentation shows extended properties
    # coming after.
    + module_ext_prop

    + prop_list
    + pp.ZeroOrMore(CONNECTION)
)

# Comment applied to a single ladder logic rung.
rung_comment = (
    pp.Suppress(pp.Keyword("RC:"))
    + pp.OneOrMore(pp.QuotedString('"'))
    + terminator
)

# Neutral text instructions in a single ladder logic rung.
rung_logic = (
    pp.Word(pp.alphas)
    + pp.Literal(":")
    + pp.Regex(r"[^;]+").leave_whitespace()
    + terminator
)

# Complete definition of a single ladder logic rung.
rung = pp.Opt(rung_comment) + rung_logic

# Ladder logic routine
ROUTINE = component(
    "ROUTINE",
    pp.common.identifier
    + attribute_list
    + pp.ZeroOrMore(rung)
)

# Single line of structured text
st_line = pp.Suppress("'") + pp.rest_of_line

PRESET = component("PRESET", attribute_list + pp.ZeroOrMore(st_line))
LIMITHIGH = component("LIMITHIGH", attribute_list + pp.ZeroOrMore(st_line))
LIMITLOW = component("LIMITLOW", attribute_list + pp.ZeroOrMore(st_line))
BODY = component("BODY", attribute_list + pp.ZeroOrMore(st_line))

ACTION = component(
    "ACTION",
    attribute_list

    # Reference documentation shows the PRESET and BODY declarations as
    # required, although they're actually optional.
    + pp.Opt(PRESET)
    + pp.Opt(BODY)
)

STEP = component(
    "STEP",
    attribute_list
    + pp.Opt(PRESET)
    + pp.Opt(LIMITHIGH)
    + pp.Opt(LIMITLOW)
    + pp.ZeroOrMore(ACTION)
)

CONDITION = component("CONDITION", attribute_list + pp.ZeroOrMore(st_line))
TRANSITION = component("TRANSITION", attribute_list + CONDITION)
SBR_RET = component("SBR_RET", attribute_list)
STOP = component("STOP", attribute_list)
LEG = component("LEG", attribute_list)
BRANCH = component("BRANCH", attribute_list + pp.OneOrMore(LEG))
DIRECTED_LINK = component("DIRECTED_LINK", attribute_list)

# Function block diagram sheet components.
IREF = component("IREF", attribute_list)
OREF = component("OREF", attribute_list)
ICON = component("ICON", attribute_list)
OCON = component("OCON", attribute_list)
JSR = component("JSR", attribute_list)
SBR = component("SBR", attribute_list)
RET = component("RET", attribute_list)
WIRE = component("WIRE", attribute_list)
FEEDBACK_WIRE = component("FEEDBACK_WIRE", attribute_list)
TEXT_BOX = component("TEXT_BOX", attribute_list)
ATTACHMENT = component( "ATTACHMENT", attribute_list)

# A single sequential function chart element.
sfc_element = pp.Or([
    STEP,
    TRANSITION,
    BRANCH,
    SBR_RET,
    STOP,
    DIRECTED_LINK,
    TEXT_BOX,
    ATTACHMENT,
])

# A block and function components include the mnemonic in the starting and
# ending keywords, e.g., ADD_FUNCTION/END_ADD_FUNCTION.
BLOCK = (
    pp.Regex(r"\w+BLOCK")
    + attribute_list
    + pp.Regex(r"END\w+BLOCK")
)
FUNCTION = (
    pp.Regex(r"\w+FUNCTION")
    + attribute_list
    + pp.Regex(r"END\w+FUNCTION")
)

# Function block AOI parameters.
FBD_PARAMETERS = component("FBD_PARAMETERS", attribute_list)

# Function block AOI reference, not an AOI definition.
ADD_ON_INSTRUCTION = component(
    "ADD_ON_INSTRUCTION",
    pp.common.identifier
    + attribute_list
    + FBD_PARAMETERS
)

# Function block sheet.
SHEET = component(
    "SHEET",
    attribute_list

    # Sheet elements can occur in any order even though the reference
    # documentation shows a specific order,
    + pp.ZeroOrMore(pp.MatchFirst([
        IREF,
        OREF,
        ICON,
        OCON,
        BLOCK,
        ADD_ON_INSTRUCTION,
        JSR,
        SBR,
        RET,
        WIRE,
        FEEDBACK_WIRE,
        FUNCTION,
        TEXT_BOX,
        ATTACHMENT,
    ]))
)

# Component containing online edits.
LOGIC = component(
    "LOGIC",
    attribute_list

    # This component can contain various logic types.
    + pp.ZeroOrMore(SHEET)  # Function block diagram
    + pp.ZeroOrMore(sfc_element)  # Sequential function chart
    + pp.ZeroOrMore(st_line)  # Structured text
)

# Function block diagram routine
FBD_ROUTINE = component(
    "FBD_ROUTINE",
    pp.common.identifier
    + attribute_list
    + pp.ZeroOrMore(pp.Or([SHEET, LOGIC]))
)

# Structured text routine
ST_ROUTINE = component(
    "ST_ROUTINE",
    pp.common.identifier
    + attribute_list
    + pp.ZeroOrMore(pp.Or([st_line, LOGIC]))
)

# Sequential function chart routine
SFC_ROUTINE = component(
    "SFC_ROUTINE",
    pp.common.identifier
    + attribute_list
    + pp.ZeroOrMore(pp.Or([sfc_element, LOGIC]))
)

# AOI signature history.
HISTORY_ENTRY = component(
    "HISTORY_ENTRY",
    attribute_list
)

# Statement definining a single AOI parameter.
parameter = (
    pp.common.identifier("name")
    + pp.Suppress(":")
    + data_type_name("datatype")
    + array_dim("dim")
    + attribute_list("attributes")
    + terminator
)
parameter.add_parse_action(datatype.convert_member)

# AOI parameter definition component
PARAMETERS = component(
    "PARAMETERS",
    pp.ZeroOrMore(parameter)
)

# An encoded routine or AOI.
ENCODED_DATA = component(
    "ENCODED_DATA",
    attribute_list

    # Components of encoded AOIs.
    + pp.ZeroOrMore(HISTORY_ENTRY)
    + pp.Opt(PARAMETERS)

    + pp.Word(pp.printables)
)

# Routine of any logic type.
routine = pp.Or([
    ROUTINE,
    ST_ROUTINE,
    FBD_ROUTINE,
    SFC_ROUTINE,
    ENCODED_DATA
])

# Statement defining a single AOI local tag.
local_tag = (
    pp.common.identifier("name")
    + pp.Suppress(":")
    + pp.common.identifier("datatype")
    + array_dim("dim")
    + attribute_list("attributes")
    + terminator
)
local_tag.add_parse_action(datatype.convert_member)

# AOI local tag definition component.
LOCAL_TAGS = component(
    "LOCAL_TAGS",

    # Permit an empty component even though the reference documentation
    # doesn't really show tag declarations are optional.
    pp.ZeroOrMore(local_tag)
)

# AOI definition block.
ADD_ON_INSTRUCTION_DEFINITION = component(
    "ADD_ON_INSTRUCTION_DEFINITION",
    pp.common.identifier("name")
    + attribute_list("attributes")
    + pp.ZeroOrMore(HISTORY_ENTRY)
    + pp.Opt(PARAMETERS, default=[])("parameters")
    + pp.Opt(LOCAL_TAGS, default=[])("local_tags")
    + pp.ZeroOrMore(routine)
)
ADD_ON_INSTRUCTION_DEFINITION.set_parse_action(aoi.convert)

# An actual AOI definition may be unencoded or encoded.
aoi_definition = pp.Or([ADD_ON_INSTRUCTION_DEFINITION, pp.Suppress(ENCODED_DATA)])

tag_force_data = pp.Opt(
    pp.Suppress(",")
    + pp.Suppress(pp.Keyword("TagForceData"))
    + assign
    + tag_value
)

# Statement defining a tag type not defined by a more specific expression.
default_tag = (
    pp.common.identifier("name")
    + pp.Suppress(":")
    + pp.common.identifier("datatype")
    + array_dim("dim")
    + attribute_list("attributes")

    # Value is absent for certain types, such as MESSAGE and motion tags.
    + pp.Opt(assign + tag_value("value"))

    + tag_force_data
    + terminator
)
default_tag.set_parse_action(tag.convert_tag)

# Statement defining an alias tag.
alias_tag = pp.Suppress(
    pp.common.identifier
    + pp.Suppress(pp.Keyword("OF"))
    + pp.Word(pp.printables)
    + attribute_list
    + terminator
)

tag_definition = default_tag | alias_tag

# Component declaring a set of tags.
TAG = component(
    "TAG",
    pp.ZeroOrMore(tag_definition)
)

CHILD_PROGRAMS = component(
    "CHILD_PROGRAMS",

    # The component end keyword needs to be excluded from program names
    # because the keyword itself is otherwise a valid program name.
    pp.ZeroOrMore(
        pp.NotAny(pp.Keyword("END_CHILD_PROGRAMS"))
        + pp.common.identifier
    )
)

# Component declaring a program.
PROGRAM = component(
    "PROGRAM",
    pp.common.identifier("name")
    + attribute_list("attributes")
    + pp.Opt(pp.Dict(TAG, asdict=True), default={})("tags")
    + pp.ZeroOrMore(routine)
    + pp.Opt(CHILD_PROGRAMS)
)
PROGRAM.set_parse_action(program.convert)

# Task definition component.
TASK = component(
    "TASK",
    pp.common.identifier
    + attribute_list
    + pp.ZeroOrMore(pp.common.identifier + terminator)
)

# Parameter connection definition component.
PARAMETER_CONNECTION = component(
    "PARAMETER_CONNECTION",
    attribute_list
)

# Trend pen definition component.
PEN = component(
    "PEN",
    pp.Word(pp.printables)  # Can be I/O modules, structure, and array members.
    + attribute_list
)

# Trend definition component.
TREND = component(
    "TREND",
    pp.common.identifier
    + attribute_list

    # Template data. Reference documentation indicates this is always
    # present, however, it is actually optional.
    + prop_list

    + pp.ZeroOrMore(PEN)
)

# Statement defining a single quick watch tag.
WATCH_TAG = (
    pp.Suppress(pp.Keyword("WATCH_TAG"))
    + attribute_list
    + terminator
)

# Watchlist definition component.
QUICK_WATCH = component(
    "QUICK_WATCH",
    attribute_list

    # Reference documentation indicates there will always be at least one
    # tag, however, it is possible to have an empty quick watch.
    + pp.ZeroOrMore(WATCH_TAG)
)

# Safety signature authentication code.
AUTHENTICATION_CODE = component(
    "AUTHENTICATION_CODE",
    pp.common.identifier
    + attribute_list
)

# Controller configuration component.
CONFIG = component(
    "CONFIG",
    pp.common.identifier
    + attribute_list
)

# Controller definition component.
CONTROLLER = component(
    "CONTROLLER",
    pp.common.identifier("name")
    + attribute_list("attributes")
    + pp.Dict(pp.ZeroOrMore(DATATYPE), asdict=True)("datatypes")
    + pp.ZeroOrMore(MODULE)
    + pp.Dict(pp.ZeroOrMore(aoi_definition), asdict=True)("aois")
    + pp.Dict(TAG, asdict=True)("tags")
    + pp.Dict(pp.ZeroOrMore(PROGRAM), asdict=True)("programs")
    + pp.ZeroOrMore(TASK)
    + pp.ZeroOrMore(PARAMETER_CONNECTION)
    + pp.ZeroOrMore(TREND)
    + pp.ZeroOrMore(QUICK_WATCH)

    # This component is not listed in the main L5K controller structure
    # definition; it's location is defined in the Define Safety Signatures
    # chapter.
    + pp.Opt(AUTHENTICATION_CODE)

    + pp.ZeroOrMore(CONFIG)
)
CONTROLLER.set_parse_action(controller.convert)

# Top-level expression for the entire L5K export.
prj = header + version + CONTROLLER("controller")
