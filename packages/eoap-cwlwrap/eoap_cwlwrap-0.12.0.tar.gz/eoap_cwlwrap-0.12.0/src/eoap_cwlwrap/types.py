"""
EOAP CWLWrap (c) 2025

EOAP CWLWrap is licensed under
Creative Commons Attribution-ShareAlike 4.0 International.

You should have received a copy of the license along with this work.
If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""

import sys
from cwl_utils.parser.cwl_v1_2 import (
    CommandInputArraySchema,
    CommandOutputArraySchema,
    Directory,
    File,
    InputArraySchema,
    OutputArraySchema,
    Workflow
)
from loguru import logger
from typing import (
    Any,
    get_args,
    get_origin,
    Union
)
import sys

Workflows = Union[Workflow, list[Workflow]]
'''A single CWL Workflow or a list of Workflows union type.'''

Directory_or_File = Union[Directory, File]
'''A Directory Workflow or a File union type.'''

URL_SCHEMA = 'https://raw.githubusercontent.com/eoap/schemas/main/string_format.yaml'
'''The URL of the string-format schema'''

URL_TYPE = f"{URL_SCHEMA}#URI"
'''The fully qualified name URI CWL type'''

# CWLtype utility methods

def is_nullable(typ: Any) -> bool:
    '''
    Detects if the input type can be nullable.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `bool`: `True`, if the input type can be nullable, `False` otherwise.
    '''    
    return isinstance(typ, list) and 'null' in typ

def is_type_assignable_to(
    actual: Any,
    expected: Any
) -> bool:
    '''
    Detects if the actual type can be assignable to the expected type.

    Args:
        `actual` (`Any`): Any CWL type
        `actual` (`expected`): Any CWL type

    Returns:
        `bool`: `True`, if the actual type can be assignable to the expected type, `False` otherwise.
    '''
    if get_origin(expected) is Union:
        return any(is_type_assignable_to(actual, typ) for typ in get_args(expected))

    # Case 0: Direct string reference
    if isinstance(actual, str):
        return expected == actual if isinstance(expected, str) else actual == expected.__name__

    # Case 1: Direct match with Directory class
    if actual == expected or isinstance(actual, expected):
        return True

    # Case 2: Union type (list of types)
    if isinstance(actual, list):
        return any(is_type_assignable_to(actual=t, expected=expected) for t in actual)

    # Case 3: Array type (recursive item type check)
    if hasattr(actual, "items"):
        return is_type_assignable_to(actual=actual.items, expected=expected)

    # Case 4: Possibly a CWLType or raw class — extract and test
    if isinstance(actual, expected):
        return issubclass(actual, expected)

    return False

def get_assignable_type(
    actual: Any,
    expected: Any
) -> Any:
    if get_origin(expected) is Union:
        for typ in get_args(expected):
            if (is_type_assignable_to(actual=actual, expected=typ)):
                return typ

    if is_type_assignable_to(actual=actual, expected=expected):
        return expected

    return None

def is_directory_compatible_type(typ: Any) -> bool:
    '''
    Detects if the actual type can be assignable to `Directory` type.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `bool`: `True`, if the input type can be assignable to the `Directory` type, `False` otherwise.
    '''
    return is_type_assignable_to(typ, Directory)

def is_file_compatible_type(typ: Any) -> bool:
    '''
    Detects if the actual type can be assignable to `File` type.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `bool`: `True`, if the input type can be assignable to the `File` type, `False` otherwise.
    '''
    return is_type_assignable_to(typ, File)

def is_directory_or_file_compatible_type(typ: Any) -> bool:
    '''
    Detects if the actual type can be assignable to `Directory` or `File` types.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `bool`: `True`, if the input type can be assignable to the `Directory` or `File` types, `False` otherwise.
    '''
    return is_type_assignable_to(typ, Directory_or_File)

def is_uri_compatible_type(typ: Any) -> bool:
    '''
    Detects if the actual type can be assignable to `https://raw.githubusercontent.com/eoap/schemas/refs/heads/main/string_format.yaml#URI` type.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `bool`: `True`, if the input type can be assignable to `https://raw.githubusercontent.com/eoap/schemas/refs/heads/main/string_format.yaml#URI` type, `False` otherwise.
    '''
    return is_type_assignable_to(typ, URL_TYPE)

def is_array_type(typ: Any) -> bool:
    '''
    Detects if the actual type can be assignable to `array` type.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `bool`: `True`, if the input type can be assignable to the `array` type, `False` otherwise.
    '''
    if isinstance(typ, list):
        return any(is_array_type(type_item) for type_item in list(typ))

    return hasattr(typ, "items")

def replace_type_with_url(
    source: Any,
    to_be_replaced: Any
) -> Any:
    '''
    Deep replaces any CWL type in the source type with the `https://raw.githubusercontent.com/eoap/schemas/refs/heads/main/string_format.yaml#URI` type.

    Args:
        `source` (`Any`): Any CWL type
        `to_be_replaced` (`Any`): The CWL type that has to be replaced

    Returns:
        `Any`: The new type.
    '''
    if get_origin(to_be_replaced) is Union:
        for typ in get_args(to_be_replaced):
            if is_type_assignable_to(source, typ):
                return replace_type_with_url(source=source, to_be_replaced=typ)
        return None

    # case 0: Direct match with class name
    if isinstance(source, str) and (isinstance(to_be_replaced, str) and source == to_be_replaced or source == to_be_replaced.__name__):
        return URL_TYPE

    # Case 1: Direct match with class
    if source == to_be_replaced or isinstance(source, to_be_replaced):
        return URL_TYPE

    # Union: list of types
    if isinstance(source, list):
        return [replace_type_with_url(source=t, to_be_replaced=to_be_replaced) for t in source]

    # Array types
    if isinstance(source, InputArraySchema) or isinstance(source, CommandInputArraySchema):
        return InputArraySchema(
            extension_fields=source.extension_fields,
            items=replace_type_with_url(source=source.items, to_be_replaced=to_be_replaced),
            type_=source.type_,
            label=source.label,
            doc=source.doc
        )

    if isinstance(source, OutputArraySchema) or isinstance(source, CommandOutputArraySchema):
        return OutputArraySchema(
            extension_fields=source.extension_fields,
            items=replace_type_with_url(source=source.items, to_be_replaced=to_be_replaced),
            type_=source.type_,
            label=source.label,
            doc=source.doc
        )

    # Return original type if no match
    return source

def replace_directory_with_url(typ: Any) -> Any:
    '''
    Deep replaces the `Directory` type in the source type with the `https://raw.githubusercontent.com/eoap/schemas/refs/heads/main/string_format.yaml#URI` type.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `Any`: The new type.
    '''
    return replace_type_with_url(source=typ, to_be_replaced=Directory)

# CWLtype to string methods

def type_to_string(typ: Any) -> str:
    '''
    Serializes a CWL type to a human-readable string.

    Args:
        `typ` (`Any`): Any CWL type

    Returns:
        `str`: The human-readable string representing the input CWL type.
    '''
    if get_origin(typ) is Union:
        return " or ".join([type_to_string(inner_type) for inner_type in get_args(typ)])

    if isinstance(typ, list):
        return f"[ {', '.join([type_to_string(t) for t in typ])} ]"

    if hasattr(typ, "items"):
        return f"{type_to_string(typ.items)}[]"

    if isinstance(typ, str):
        return typ

    return typ.__name__

def _create_error_message(parameters: list[Any]) -> str:
    return 'no' if 0 == len(parameters) else str(list(map(lambda parameter: parameter.id, parameters)))

# Validation methods

def _validate_stage_in(
    stage_in: Workflow,
    expected_output_type: Any
):
    logger.info(f"Validating stage-in '{stage_in.id}'...")

    url_inputs = list(
        filter(
            lambda input: is_uri_compatible_type(input.type_),
            stage_in.inputs
        )
    )

    if len(url_inputs) != 1:
        sys.exit(f"stage-in '{stage_in.id}' not valid, {_create_error_message(url_inputs)} URL-compatible input found, please specify one.")

    directory_outputs = list(
        filter(
            lambda output: is_type_assignable_to(output.type_, expected_output_type),
            stage_in.outputs
        )
    )

    if len(directory_outputs) != 1:
        sys.exit(f"stage-in '{stage_in.id}' not valid, {_create_error_message(directory_outputs)} Directory-compatible output found, please specify one.")

    logger.info(f"stage-in '{stage_in.id}' is valid")

def validate_directory_stage_in(directory_stage_in: Workflow):
    '''
    Checks if a CWL stage-in document is a `URI`-compatible input and `Directory`-compatible output `Workflow`.

    Args:
        `directory_stage_in` (`Workflow`): Any CWL `Workflow`

    Returns:
        `None`: none.
    '''
    _validate_stage_in(stage_in=directory_stage_in, expected_output_type=Directory)

def validate_file_stage_in(file_stage_in: Workflow):
    '''
    Checks if a CWL stage-in document is a `URI`-compatible input and `File`-compatible output `Workflow`.

    Args:
        `file_stage_in` (`Workflow`): Any CWL `Workflow`

    Returns:
        `None`: none.
    '''
    _validate_stage_in(stage_in=file_stage_in, expected_output_type=File)

def validate_stage_out(stage_out: Workflow):
    '''
    Checks if a CWL stage-out document is a `Directory`-compatible input and `URI`-compatible output `Workflow`.

    Args:
        `stage_out` (`Workflow`): Any CWL `Workflow`

    Returns:
        `None`: none.
    '''
    logger.info(f"Validating stage-out '{stage_out.id}'...")

    directory_inputs = list(
        filter(
            lambda input: is_directory_compatible_type(input.type_),
            stage_out.inputs
        )
    )

    if len(directory_inputs) != 1:
        sys.exit(f"stage-out '{stage_out.id}' not valid, {_create_error_message(directory_inputs)} Directory-compatible input found, please specify one.")

    url_outputs = list(
        filter(
            lambda output: is_uri_compatible_type(output.type_),
            stage_out.outputs
        )
    )

    if len(url_outputs) != 1:
        sys.exit(f"stage-out '{stage_out.id}' not valid, {_create_error_message(url_outputs)} URL-compatible output found, please specify one.")

    logger.info(f"stage-out '{stage_out.id}' is valid")
