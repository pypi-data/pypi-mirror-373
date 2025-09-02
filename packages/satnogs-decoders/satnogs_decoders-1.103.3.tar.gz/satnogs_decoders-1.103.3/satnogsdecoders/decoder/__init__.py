"""
SatNOGS Decoder subpackage initialization
"""
from __future__ import absolute_import, division, print_function

import enum
import functools
import importlib
import os
import re

from kaitaistruct import KaitaiStruct

# Add all decoders automatically to the current namespace
for file in os.listdir(os.path.dirname(__file__)):
    if not file.endswith('.py') or file.startswith('__'):
        continue
    module_name = file[:-3]

    module = importlib.import_module(f'.{module_name}', package=__package__)
    class_name = module_name.capitalize().replace('_', '')

    try:
        globals()[class_name] = getattr(module, class_name)
    except AttributeError as ex:
        print(f'WARNING: Import of decoder class {class_name} failed.\n'
              ' Did you compile modified Kaitai structs to Python code yet? \n'
              f'AttributeError: {ex}')

FIELD_REGEX = re.compile(
    r':field (?P<field>[\*\w]+): (?P<attribute>.*?)'
    r'(?:(?=:field)|\Z|\n)', re.S)

UNKNOWN_SIZE_NOTATION = '___'


def get_attribute(obj, name):
    """
    Get element by index in case of list
    Get attribute of object by namein case of non-list object
    """
    if isinstance(obj, list):
        try:
            return obj[int(name)]
        except ValueError:
            return getattr(obj, name).name
    if isinstance(getattr(obj, name), enum.Enum):
        return getattr(obj, name).name
    return getattr(obj, name)


def get_dynamic_fields(obj, path_list, indexes, inframe_index, key):
    """
    Get element by recusion in case of unknown sized list
    """
    if inframe_index == len(path_list):
        pos = 1
        for k in indexes:
            key = key.replace(UNKNOWN_SIZE_NOTATION,
                              '_' + str(indexes[k][0] - 1) + '_', pos)
            pos += 1

        return obj, key

    name = path_list[inframe_index]
    if isinstance(obj, list):
        try:
            if name == UNKNOWN_SIZE_NOTATION:
                index_key = indexes[path_list[inframe_index - 1]][0]
                indexes[path_list[inframe_index - 1]][0] += 1
                if indexes[path_list[inframe_index - 1]][1] is None:
                    indexes[path_list[inframe_index - 1]][1] = len(obj)
                return get_dynamic_fields(obj[index_key], path_list, indexes,
                                          inframe_index + 1, key)

            return get_dynamic_fields(obj[int(name)], path_list, indexes,
                                      inframe_index + 1, key)
        except ValueError:
            return get_dynamic_fields(
                getattr(obj, name).name, path_list, indexes, inframe_index + 1,
                key)
    if isinstance(getattr(obj, name), enum.Enum):
        return get_dynamic_fields(
            getattr(obj, name).name, path_list, indexes, inframe_index + 1,
            key)
    return get_dynamic_fields(getattr(obj, name), path_list, indexes,
                              inframe_index + 1, key)


def get_fields(struct: KaitaiStruct, empty=False):
    """
    Extract fields from Kaitai Struct as defined in the Struct docstring
    and return as dictionary.

    Args:
        struct: Satellite Decoder object
        empty (bool): If True, fields with invalid paths get None value.
                      If False, fields with invalid paths are omitted.

    Returns:
        dict: Field values mapped to field names
    """
    fields = {}
    dynamic_fields = {}

    try:
        doc_fields = FIELD_REGEX.findall(struct.__doc__)
    except TypeError:
        return fields

    for key, value in doc_fields:
        try:
            if UNKNOWN_SIZE_NOTATION not in key:
                fields[key] = functools.reduce(get_attribute, value.split('.'),
                                               struct)
            else:
                key_values = key.split(UNKNOWN_SIZE_NOTATION)
                for i in range(0, len(key_values) - 1):
                    dynamic_fields[key_values[i]] = [0, None]

                path_list = value.split('.')
                while True:
                    value, generated_key = get_dynamic_fields(
                        struct, path_list, dynamic_fields, 0, key)
                    fields[generated_key] = value
                    first_dynamic_field_key = next(iter(dynamic_fields))
                    if dynamic_fields[first_dynamic_field_key][
                            0] == dynamic_fields[first_dynamic_field_key][1]:
                        break

        except AttributeError:
            if empty:
                fields[key] = None

    return fields


def kaitai_to_dict(struct):
    """
    Convert a Kaitai Struct parsed object to a nested dictionary.
    Handles nested objects, arrays, and primitive types.

    Args:
        struct: A Kaitai Struct parsed object

    Returns:
        dict: A nested dictionary representation of the Kaitai object / frame
    """
    if isinstance(struct, (int, float, str, bool)) or struct is None:
        return struct
    if isinstance(struct, bytes):
        return struct.hex()
    if isinstance(struct, list):
        return [kaitai_to_dict(item) for item in struct]
    if hasattr(struct, '__dict__'):
        result = {}
        # Get all public attributes (not starting with '_')
        for key in dir(struct):
            # Skip private attributes
            if key.startswith('_'):
                continue

            value = getattr(struct, key)

            # Skip callable methods
            if callable(value):
                continue

            result[key] = kaitai_to_dict(value)
        return result
    raise ValueError('struct must be a valid kaitai struct'
                     'or recursive sub-member.')
