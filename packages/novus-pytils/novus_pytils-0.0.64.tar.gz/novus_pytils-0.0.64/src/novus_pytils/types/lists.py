"""List manipulation utility functions.

This module provides functions for working with lists and performing common list operations.
"""
from typing import List, Dict, Any, Callable, Tuple
from collections import defaultdict
import statistics

def remove_empty_lines_from_list(list):
    """
    Removes empty lines from a list of strings.

    :param list: List of strings.
    :return: List of strings with empty lines removed.
    """
    return [x for x in list if x]

def print_list(list):
    """
    Prints a list of items.

    :param list: List of items to print.
    """
    for item in list:
        print(item)

def write_list_to_file(file_name, lines):
    """
    Writes lines to a file, adding a newline to the end of each line.

    :param str file_name: Name of the file to write.
    :param List[str] lines: List of strings to write to the file.
    """
    
    with open(file_name, 'w') as file:
        for line in lines:
            file.write(line + '\n')

def read_list_from_file(file_name):
    """
    Reads lines from a file, stripping whitespace from each.

    :param str file_name: Name of the file to read.
    :return: List of strings, each line from the file with whitespace stripped.
    :rtype: List[str]
    """
    
    with open(file_name, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    Flatten a nested list into a single level list.

    Args:
        nested_list: A list that may contain nested lists.

    Returns:
        A flattened list.
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.

    Args:
        lst: The input list.

    Returns:
        A list with duplicates removed.
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        lst: The input list.
        chunk_size: The size of each chunk.

    Returns:
        A list of chunks.
        
    Raises:
        ValueError: If chunk_size is less than or equal to 0.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def filter_list(lst: List[Any], predicate: Callable[[Any], bool]) -> List[Any]:
    """
    Filter a list using a predicate function.

    Args:
        lst: The input list.
        predicate: A function that returns True for items to keep.

    Returns:
        A filtered list.
    """
    return [item for item in lst if predicate(item)]

def sort_list_of_dicts(lst: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Sort a list of dictionaries by a specific key.

    Args:
        lst: List of dictionaries.
        key: The key to sort by.
        reverse: Whether to sort in descending order.

    Returns:
        A sorted list of dictionaries.
        
    Raises:
        KeyError: If any dictionary is missing the specified key.
    """
    # Check that all dictionaries have the key
    for item in lst:
        if key not in item:
            raise KeyError(f"Key '{key}' not found in dictionary")
    
    return sorted(lst, key=lambda x: x[key], reverse=reverse)

def group_by_key(lst: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Group a list of dictionaries by a specific key.

    Args:
        lst: List of dictionaries.
        key: The key to group by.

    Returns:
        A dictionary with grouped items.
        
    Raises:
        KeyError: If any dictionary is missing the specified key.
    """
    # Check that all dictionaries have the key
    for item in lst:
        if key not in item:
            raise KeyError(f"Key '{key}' not found in dictionary")
    
    groups = defaultdict(list)
    for item in lst:
        groups[item[key]].append(item)
    return dict(groups)

def find_in_list(lst: List[Any], predicate: Callable[[Any], bool]) -> Any:
    """
    Find the first item in a list that matches a predicate.

    Args:
        lst: The input list.
        predicate: A function that returns True for the desired item.

    Returns:
        The first matching item, or None if not found.
    """
    for item in lst:
        if predicate(item):
            return item
    return None

def list_intersection(list1: List[Any], list2: List[Any]) -> List[Any]:
    """
    Find the intersection of two lists.

    Args:
        list1: First list.
        list2: Second list.

    Returns:
        A list containing items present in both lists.
    """
    return list(set(list1) & set(list2))

def list_union(list1: List[Any], list2: List[Any]) -> List[Any]:
    """
    Find the union of two lists.

    Args:
        list1: First list.
        list2: Second list.

    Returns:
        A list containing all unique items from both lists.
    """
    return list(set(list1) | set(list2))

def list_difference(list1: List[Any], list2: List[Any]) -> List[Any]:
    """
    Find items in list1 that are not in list2.

    Args:
        list1: First list.
        list2: Second list.

    Returns:
        A list containing items in list1 but not in list2.
    """
    return list(set(list1) - set(list2))

def rotate_list(lst: List[Any], positions: int) -> List[Any]:
    """
    Rotate a list by the specified number of positions.

    Args:
        lst: The input list.
        positions: Number of positions to rotate (positive = right, negative = left).

    Returns:
        A rotated list.
    """
    if not lst:
        return lst
    positions = positions % len(lst)
    return lst[-positions:] + lst[:-positions]

def partition_list(lst: List[Any], predicate: Callable[[Any], bool]) -> Tuple[List[Any], List[Any]]:
    """
    Partition a list into two lists based on a predicate.

    Args:
        lst: The input list.
        predicate: A function that returns True/False for each item.

    Returns:
        A tuple of (items_matching_predicate, items_not_matching_predicate).
    """
    true_items = []
    false_items = []
    for item in lst:
        if predicate(item):
            true_items.append(item)
        else:
            false_items.append(item)
    return true_items, false_items

def merge_sorted_lists(list1: List[Any], list2: List[Any]) -> List[Any]:
    """
    Merge two sorted lists into one sorted list.

    Args:
        list1: First sorted list.
        list2: Second sorted list.

    Returns:
        A merged sorted list.
    """
    result = []
    i = j = 0
    
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    
    result.extend(list1[i:])
    result.extend(list2[j:])
    return result

def get_list_statistics(lst: List[float]) -> Dict[str, float]:
    """
    Calculate statistics for a list of numbers.

    Args:
        lst: List of numbers.

    Returns:
        A dictionary containing various statistics.
    """
    if not lst:
        return {
            'count': 0,
            'sum': 0,
            'min': None,
            'max': None,
            'mean': None,
            'median': None
        }
    
    return {
        'count': len(lst),
        'sum': sum(lst),
        'min': min(lst),
        'max': max(lst),
        'mean': statistics.mean(lst),
        'median': statistics.median(lst),
        'mode': statistics.mode(lst) if len(set(lst)) != len(lst) else None,
        'stdev': statistics.stdev(lst) if len(lst) > 1 else 0
    }
