"""Tests for novus_pytils.types.lists module."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from novus_pytils.types.lists import (
    remove_empty_lines_from_list, print_list, write_list_to_file, read_list_from_file,
    flatten_list, remove_duplicates, chunk_list, filter_list, sort_list_of_dicts,
    group_by_key, find_in_list, list_intersection, list_union, list_difference,
    rotate_list, partition_list, merge_sorted_lists, get_list_statistics
)


class TestRemoveEmptyLinesFromList:
    """Test the remove_empty_lines_from_list function."""
    
    def test_remove_empty_lines(self):
        input_list = ["line1", "", "line2", "   ", "line3", ""]
        result = remove_empty_lines_from_list(input_list)
        # Function only removes falsy values (empty strings), not whitespace-only strings
        assert result == ["line1", "line2", "   ", "line3"]
    
    def test_no_empty_lines(self):
        input_list = ["line1", "line2", "line3"]
        result = remove_empty_lines_from_list(input_list)
        assert result == input_list
    
    def test_all_empty_lines(self):
        input_list = ["", "   ", "\t", ""]
        result = remove_empty_lines_from_list(input_list)
        # Only empty strings are removed, whitespace strings remain
        assert result == ["   ", "\t"]
    
    def test_empty_input_list(self):
        result = remove_empty_lines_from_list([])
        assert result == []


class TestPrintList:
    """Test the print_list function."""
    
    @patch('builtins.print')
    def test_print_list_basic(self, mock_print):
        test_list = ["item1", "item2", "item3"]
        print_list(test_list)
        assert mock_print.call_count == len(test_list)
    
    @patch('builtins.print')
    def test_print_empty_list(self, mock_print):
        print_list([])
        mock_print.assert_not_called()
    
    @patch('builtins.print')
    def test_print_list_with_mixed_types(self, mock_print):
        test_list = ["string", 42, 3.14, True]
        print_list(test_list)
        assert mock_print.call_count == len(test_list)


class TestWriteListToFile:
    """Test the write_list_to_file function."""
    
    def test_write_list_to_file(self, temp_dir):
        test_list = ["line1", "line2", "line3"]
        file_path = temp_dir / "output.txt"
        
        write_list_to_file(str(file_path), test_list)
        
        assert file_path.exists()
        content = file_path.read_text().strip().split('\n')
        assert content == test_list
    
    def test_write_empty_list(self, temp_dir):
        file_path = temp_dir / "empty.txt"
        write_list_to_file(str(file_path), [])
        
        assert file_path.exists()
        assert file_path.stat().st_size == 0
    
    def test_write_mixed_types(self, temp_dir):
        test_list = ["string", 42, 3.14, True]
        file_path = temp_dir / "mixed.txt"
        
        # Function doesn't handle non-string types, will raise TypeError
        with pytest.raises(TypeError):
            write_list_to_file(str(file_path), test_list)


class TestReadListFromFile:
    """Test the read_list_from_file function."""
    
    def test_read_list_from_file(self, temp_dir):
        file_path = temp_dir / "input.txt"
        test_content = "line1\nline2\nline3\n"
        file_path.write_text(test_content)
        
        result = read_list_from_file(str(file_path))
        assert result == ["line1", "line2", "line3"]
    
    def test_read_empty_file(self, temp_dir):
        file_path = temp_dir / "empty.txt"
        file_path.write_text("")
        
        result = read_list_from_file(str(file_path))
        assert result == []
    
    def test_read_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            read_list_from_file("/nonexistent/file.txt")
    
    def test_read_file_with_empty_lines(self, temp_dir):
        file_path = temp_dir / "with_empty.txt"
        file_path.write_text("line1\n\nline2\n\nline3")
        
        result = read_list_from_file(str(file_path))
        assert result == ["line1", "", "line2", "", "line3"]


class TestFlattenList:
    """Test the flatten_list function."""
    
    def test_flatten_nested_list(self):
        nested_list = [1, [2, 3], [4, [5, 6]], 7]
        result = flatten_list(nested_list)
        assert result == [1, 2, 3, 4, 5, 6, 7]
    
    def test_flatten_already_flat_list(self):
        flat_list = [1, 2, 3, 4, 5]
        result = flatten_list(flat_list)
        assert result == flat_list
    
    def test_flatten_empty_list(self):
        result = flatten_list([])
        assert result == []
    
    def test_flatten_deeply_nested(self):
        nested_list = [1, [2, [3, [4, [5]]]]]
        result = flatten_list(nested_list)
        assert result == [1, 2, 3, 4, 5]
    
    def test_flatten_mixed_types(self):
        nested_list = ["a", [1, "b"], [2.5, [True, "c"]]]
        result = flatten_list(nested_list)
        assert result == ["a", 1, "b", 2.5, True, "c"]


class TestRemoveDuplicates:
    """Test the remove_duplicates function."""
    
    def test_remove_duplicates_basic(self):
        input_list = [1, 2, 2, 3, 3, 3, 4]
        result = remove_duplicates(input_list)
        assert result == [1, 2, 3, 4]
    
    def test_remove_duplicates_preserve_order(self):
        input_list = [3, 1, 2, 1, 3, 2]
        result = remove_duplicates(input_list)
        assert result == [3, 1, 2]
    
    def test_remove_duplicates_no_duplicates(self):
        input_list = [1, 2, 3, 4]
        result = remove_duplicates(input_list)
        assert result == input_list
    
    def test_remove_duplicates_empty_list(self):
        result = remove_duplicates([])
        assert result == []
    
    def test_remove_duplicates_strings(self):
        input_list = ["a", "b", "a", "c", "b"]
        result = remove_duplicates(input_list)
        assert result == ["a", "b", "c"]


class TestChunkList:
    """Test the chunk_list function."""
    
    def test_chunk_list_even_division(self):
        input_list = [1, 2, 3, 4, 5, 6]
        result = chunk_list(input_list, 2)
        assert result == [[1, 2], [3, 4], [5, 6]]
    
    def test_chunk_list_uneven_division(self):
        input_list = [1, 2, 3, 4, 5]
        result = chunk_list(input_list, 2)
        assert result == [[1, 2], [3, 4], [5]]
    
    def test_chunk_list_chunk_size_larger_than_list(self):
        input_list = [1, 2, 3]
        result = chunk_list(input_list, 5)
        assert result == [[1, 2, 3]]
    
    def test_chunk_list_chunk_size_one(self):
        input_list = [1, 2, 3]
        result = chunk_list(input_list, 1)
        assert result == [[1], [2], [3]]
    
    def test_chunk_list_empty_list(self):
        result = chunk_list([], 2)
        assert result == []
    
    def test_chunk_list_invalid_chunk_size(self):
        with pytest.raises(ValueError):
            chunk_list([1, 2, 3], 0)
        
        with pytest.raises(ValueError):
            chunk_list([1, 2, 3], -1)


class TestFilterList:
    """Test the filter_list function."""
    
    def test_filter_list_basic(self):
        input_list = [1, 2, 3, 4, 5, 6]
        result = filter_list(input_list, lambda x: x % 2 == 0)
        assert result == [2, 4, 6]
    
    def test_filter_list_strings(self):
        input_list = ["apple", "banana", "cherry", "date"]
        result = filter_list(input_list, lambda x: len(x) > 5)
        assert result == ["banana", "cherry"]
    
    def test_filter_list_no_matches(self):
        input_list = [1, 3, 5, 7]
        result = filter_list(input_list, lambda x: x % 2 == 0)
        assert result == []
    
    def test_filter_list_all_matches(self):
        input_list = [2, 4, 6, 8]
        result = filter_list(input_list, lambda x: x % 2 == 0)
        assert result == input_list
    
    def test_filter_list_empty_list(self):
        result = filter_list([], lambda x: True)
        assert result == []


class TestSortListOfDicts:
    """Test the sort_list_of_dicts function."""
    
    def test_sort_by_string_key(self):
        input_list = [
            {"name": "Charlie", "age": 25},
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 20}
        ]
        result = sort_list_of_dicts(input_list, "name")
        expected_names = ["Alice", "Bob", "Charlie"]
        assert [item["name"] for item in result] == expected_names
    
    def test_sort_by_numeric_key(self):
        input_list = [
            {"name": "Charlie", "age": 25},
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 20}
        ]
        result = sort_list_of_dicts(input_list, "age")
        expected_ages = [20, 25, 30]
        assert [item["age"] for item in result] == expected_ages
    
    def test_sort_reverse(self):
        input_list = [
            {"name": "Alice", "score": 85},
            {"name": "Bob", "score": 92},
            {"name": "Charlie", "score": 78}
        ]
        result = sort_list_of_dicts(input_list, "score", reverse=True)
        expected_scores = [92, 85, 78]
        assert [item["score"] for item in result] == expected_scores
    
    def test_sort_missing_key(self):
        input_list = [
            {"name": "Alice", "age": 25},
            {"name": "Bob"},  # Missing age key
            {"name": "Charlie", "age": 30}
        ]
        with pytest.raises(KeyError):
            sort_list_of_dicts(input_list, "age")
    
    def test_sort_empty_list(self):
        result = sort_list_of_dicts([], "name")
        assert result == []


class TestGroupByKey:
    """Test the group_by_key function."""
    
    def test_group_by_string_key(self):
        input_list = [
            {"category": "fruit", "name": "apple"},
            {"category": "vegetable", "name": "carrot"},
            {"category": "fruit", "name": "banana"},
            {"category": "vegetable", "name": "spinach"}
        ]
        result = group_by_key(input_list, "category")
        
        assert "fruit" in result
        assert "vegetable" in result
        assert len(result["fruit"]) == 2
        assert len(result["vegetable"]) == 2
    
    def test_group_by_numeric_key(self):
        input_list = [
            {"grade": 90, "name": "Alice"},
            {"grade": 85, "name": "Bob"},
            {"grade": 90, "name": "Charlie"}
        ]
        result = group_by_key(input_list, "grade")
        
        assert 90 in result
        assert 85 in result
        assert len(result[90]) == 2
        assert len(result[85]) == 1
    
    def test_group_by_missing_key(self):
        input_list = [
            {"name": "Alice"},
            {"name": "Bob", "category": "test"}
        ]
        with pytest.raises(KeyError):
            group_by_key(input_list, "category")
    
    def test_group_empty_list(self):
        result = group_by_key([], "key")
        assert result == {}


class TestFindInList:
    """Test the find_in_list function."""
    
    def test_find_in_list_found(self):
        input_list = [1, 2, 3, 4, 5]
        result = find_in_list(input_list, lambda x: x > 3)
        assert result == 4
    
    def test_find_in_list_not_found(self):
        input_list = [1, 2, 3]
        result = find_in_list(input_list, lambda x: x > 5)
        assert result is None
    
    def test_find_in_list_first_match(self):
        input_list = [1, 2, 3, 4, 5]
        result = find_in_list(input_list, lambda x: x % 2 == 0)
        assert result == 2  # First even number
    
    def test_find_in_list_strings(self):
        input_list = ["apple", "banana", "cherry"]
        result = find_in_list(input_list, lambda x: x.startswith("b"))
        assert result == "banana"
    
    def test_find_in_empty_list(self):
        result = find_in_list([], lambda x: True)
        assert result is None


class TestListIntersection:
    """Test the list_intersection function."""
    
    def test_list_intersection_basic(self):
        list1 = [1, 2, 3, 4, 5]
        list2 = [3, 4, 5, 6, 7]
        result = list_intersection(list1, list2)
        assert set(result) == {3, 4, 5}
    
    def test_list_intersection_no_common(self):
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        result = list_intersection(list1, list2)
        assert result == []
    
    def test_list_intersection_identical(self):
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        result = list_intersection(list1, list2)
        assert set(result) == {1, 2, 3}
    
    def test_list_intersection_with_duplicates(self):
        list1 = [1, 2, 2, 3]
        list2 = [2, 2, 3, 4]
        result = list_intersection(list1, list2)
        assert set(result) == {2, 3}
    
    def test_list_intersection_empty_lists(self):
        assert list_intersection([], []) == []
        assert list_intersection([1, 2], []) == []
        assert list_intersection([], [1, 2]) == []


class TestListUnion:
    """Test the list_union function."""
    
    def test_list_union_basic(self):
        list1 = [1, 2, 3]
        list2 = [3, 4, 5]
        result = list_union(list1, list2)
        assert set(result) == {1, 2, 3, 4, 5}
    
    def test_list_union_no_overlap(self):
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        result = list_union(list1, list2)
        assert set(result) == {1, 2, 3, 4, 5, 6}
    
    def test_list_union_identical(self):
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        result = list_union(list1, list2)
        assert set(result) == {1, 2, 3}
    
    def test_list_union_empty_lists(self):
        assert list_union([], []) == []
        assert set(list_union([1, 2], [])) == {1, 2}
        assert set(list_union([], [1, 2])) == {1, 2}


class TestListDifference:
    """Test the list_difference function."""
    
    def test_list_difference_basic(self):
        list1 = [1, 2, 3, 4, 5]
        list2 = [3, 4, 5]
        result = list_difference(list1, list2)
        assert set(result) == {1, 2}
    
    def test_list_difference_no_common(self):
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        result = list_difference(list1, list2)
        assert set(result) == {1, 2, 3}
    
    def test_list_difference_identical(self):
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        result = list_difference(list1, list2)
        assert result == []
    
    def test_list_difference_empty_lists(self):
        assert list_difference([], []) == []
        assert set(list_difference([1, 2], [])) == {1, 2}
        assert list_difference([], [1, 2]) == []


class TestRotateList:
    """Test the rotate_list function."""
    
    def test_rotate_list_positive(self):
        input_list = [1, 2, 3, 4, 5]
        result = rotate_list(input_list, 2)
        assert result == [4, 5, 1, 2, 3]
    
    def test_rotate_list_negative(self):
        input_list = [1, 2, 3, 4, 5]
        result = rotate_list(input_list, -2)
        assert result == [3, 4, 5, 1, 2]
    
    def test_rotate_list_zero(self):
        input_list = [1, 2, 3, 4, 5]
        result = rotate_list(input_list, 0)
        assert result == input_list
    
    def test_rotate_list_full_rotation(self):
        input_list = [1, 2, 3, 4, 5]
        result = rotate_list(input_list, 5)
        assert result == input_list
    
    def test_rotate_list_larger_than_length(self):
        input_list = [1, 2, 3]
        result = rotate_list(input_list, 4)  # 4 % 3 = 1
        assert result == [3, 1, 2]
    
    def test_rotate_empty_list(self):
        result = rotate_list([], 3)
        assert result == []


class TestPartitionList:
    """Test the partition_list function."""
    
    def test_partition_list_basic(self):
        input_list = [1, 2, 3, 4, 5, 6]
        true_list, false_list = partition_list(input_list, lambda x: x % 2 == 0)
        assert true_list == [2, 4, 6]
        assert false_list == [1, 3, 5]
    
    def test_partition_list_all_true(self):
        input_list = [2, 4, 6, 8]
        true_list, false_list = partition_list(input_list, lambda x: x % 2 == 0)
        assert true_list == input_list
        assert false_list == []
    
    def test_partition_list_all_false(self):
        input_list = [1, 3, 5, 7]
        true_list, false_list = partition_list(input_list, lambda x: x % 2 == 0)
        assert true_list == []
        assert false_list == input_list
    
    def test_partition_empty_list(self):
        true_list, false_list = partition_list([], lambda x: True)
        assert true_list == []
        assert false_list == []


class TestMergeSortedLists:
    """Test the merge_sorted_lists function."""
    
    def test_merge_sorted_lists_basic(self):
        list1 = [1, 3, 5]
        list2 = [2, 4, 6]
        result = merge_sorted_lists(list1, list2)
        assert result == [1, 2, 3, 4, 5, 6]
    
    def test_merge_sorted_lists_different_lengths(self):
        list1 = [1, 3, 5, 7, 9]
        list2 = [2, 4]
        result = merge_sorted_lists(list1, list2)
        assert result == [1, 2, 3, 4, 5, 7, 9]
    
    def test_merge_sorted_lists_one_empty(self):
        list1 = [1, 2, 3]
        list2 = []
        result = merge_sorted_lists(list1, list2)
        assert result == list1
        
        result = merge_sorted_lists([], list1)
        assert result == list1
    
    def test_merge_sorted_lists_both_empty(self):
        result = merge_sorted_lists([], [])
        assert result == []
    
    def test_merge_sorted_lists_duplicates(self):
        list1 = [1, 2, 3]
        list2 = [2, 3, 4]
        result = merge_sorted_lists(list1, list2)
        assert result == [1, 2, 2, 3, 3, 4]


class TestGetListStatistics:
    """Test the get_list_statistics function."""
    
    def test_get_statistics_basic(self):
        input_list = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = get_list_statistics(input_list)
        
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["min"] == 1.0
        assert result["max"] == 5.0
        assert result["sum"] == 15.0
        assert result["count"] == 5
    
    def test_get_statistics_single_value(self):
        input_list = [42.0]
        result = get_list_statistics(input_list)
        
        assert result["mean"] == 42.0
        assert result["median"] == 42.0
        assert result["min"] == 42.0
        assert result["max"] == 42.0
        assert result["sum"] == 42.0
        assert result["count"] == 1
    
    def test_get_statistics_even_length(self):
        input_list = [1.0, 2.0, 3.0, 4.0]
        result = get_list_statistics(input_list)
        
        assert result["mean"] == 2.5
        assert result["median"] == 2.5  # Average of 2.0 and 3.0
        assert result["min"] == 1.0
        assert result["max"] == 4.0
    
    def test_get_statistics_empty_list(self):
        result = get_list_statistics([])
        assert result["count"] == 0
        assert result["sum"] == 0
        assert result["min"] is None
        assert result["max"] is None
        assert result["mean"] is None
        assert result["median"] is None
    
    def test_get_statistics_mixed_numbers(self):
        input_list = [1.5, 2, 3.7, 4.2, 5]
        result = get_list_statistics(input_list)
        
        assert isinstance(result["mean"], float)
        assert isinstance(result["median"], float)
        assert result["count"] == 5