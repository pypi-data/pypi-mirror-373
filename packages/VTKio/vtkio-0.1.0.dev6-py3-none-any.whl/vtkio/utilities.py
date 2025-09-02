#!/usr/bin/env python
"""
Module for generic helper functions used in VTKio.

This module contains the following functions:


Functions
---------
get_recursively()
    Search a dictionary recursively.

"""

from __future__ import annotations

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

import os
import subprocess
# Standard Library
from collections.abc import MutableMapping


def is_numeric_array(obj):
    """
    Check if the provided object behaves like a numeric array.

    This function determines if the given object has specific attributes that are generally associated with numeric
    array-like objects. The attributes checked include addition, subtraction, multiplication, division, and power
    operations. Objects lacking these attributes are not considered numeric arrays.

    Parameters
    ----------
    obj : object
        The object to check for numeric array-like behaviour.

    Returns
    -------
    bool
        Returns True if the object meets the required criteria for being
        a numeric array-like object; otherwise, it returns False.
    """
    attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
    return all(hasattr(obj, attr) for attr in attrs)


def flatten(dictionary, parent_key='', separator='_'):
    """
    Flattens a nested dictionary into a single-depth dictionary.

    The function takes a nested dictionary and transforms it into a flattened dictionary
    with a single level. Each key in the resulting dictionary is a concatenation of the
    hierarchical keys from the original dictionary, separated by the provided separator.
    This is particularly useful for simplifying nested structures for certain operations,
    such as data serialization or storage.

    Parameters
    ----------
    dictionary : dict
        A dictionary that may contain nested dictionaries as values.
    parent_key : str, optional
        A string to prefix the keys of the flattened dictionary with. Defaults to an
        empty string, meaning no prefix is added.
    separator : str, optional
        A string used to separate concatenated keys in the flattened dictionary. Defaults
        to an underscore ('_').

    Returns
    -------
    dict
        A flattened dictionary where all keys are made unique by combining their
        hierarchical keys using the specified separator.
    """
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


def dict_extract_generator(key, var):
    """
    Generate values from a nested dictionary or list structure that match the specified key.

    This generator function recursively traverses dictionaries and lists in search of values
    associated with a specified key. The function yields these values when the matching key
    is found.

    Parameters
    ----------
    key : str
        The key to search for in the nested structure.
    var : dict or list
        The nested dictionary or list structure to traverse.

    Yields
    ------
    Any
        Values associated with the specified key in the nested structure. The type of
        the yielded value depends on the contents of the input structure.
    """
    if hasattr(var,'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in dict_extract_generator(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in dict_extract_generator(key, d):
                        yield result


def get_recursively(search_dict, field):
    """
    Search a dictionary recursively.

    Takes a dictionary with nested lists and dictionaries, and searches all dictionaries for a key of the field provided.

    Parameters
    ----------
    search_dict : Dict [Any, Any]
        Dictionary to be searched. It can contain nested dictionaries and lists as well as basic types such as strings, ints and floats.
    field : key [Any]
        Dictionary key to be searched for. Typically, a string, integer or float.

    Returns
    -------
    result : List[Any]
        The values associated with the key provided. If the key is not found, an empty list is returned.


    Examples
    --------
    >>> d = {'a': 1, 'b': 2, 'c': {'da': 4, 'db': 5, 'dc': {'dda': 8, 'ddb': 9}}}
    >>> get_recursively(d, 'da')
    [4]
    >>> get_recursively(d, 'ddb')
    [9]
    >>> get_recursively(d, 'missing_key')
    []

    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


def flatten_list(nested_list):
    """
    Flattens a nested list into a single list.

    The function takes a nested list of arbitrary depth and recursively flattens
    it into a single list containing all the elements. Any nested sub-lists are
    converted into their constituent elements and appended to the resulting list.

    Parameters
    ----------
    nested_list : list
        A possibly nested list of elements to be flattened. The input can consist
        of multiple levels of lists.

    Returns
    -------
    list
        A flattened list containing all elements from the input `nested_list`,
        including elements from any nested sub-lists.
    """
    def flatten_helper(sublist, result):
        for item in sublist:
            if isinstance(item, list):  # Improved type checking
                flatten_helper(item, result)  # Recursive call
            else:
                result.append(item)
        return result

    return flatten_helper(nested_list, [])  # Extracted recursive logic into helper


def first_key(dict):
    """
    Retrieve the first key from a given dictionary that is for integer or float data.

    This function iterates over a dictionary and retrieves the first key it
    encounters. If the dictionary is empty, it returns None.

    Parameters
    ----------
    dict : dict
        The dictionary from which the first key will be retrieved.

    Returns
    -------
    Hashable or None
        The first key encountered in the dictionary. If the dictionary is empty,
        returns None.
    """
    for key in dict:
        if isinstance(dict[key][0], (int, float)):
            return key
    return None


def is_git_repo(dir: str) -> bool:
    """Is the given directory version-controlled with git?"""
    return os.path.exists(os.path.join(dir, '.git'))


def have_git() -> bool:
    """Can we run the git executable?"""
    try:
        subprocess.check_output(['git', '--help'])
        return True
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def git_revision(dir: str) -> str:
    """Get the SHA-1 of the HEAD of a git repository."""
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=dir).decode('utf-8').strip()
