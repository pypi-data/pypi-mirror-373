"""Tests for novus_pytils.types.pandas module."""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from novus_pytils.types.pandas import to_frame, write_csv


class TestToFrame:
    """Test the to_frame function."""
    
    def test_to_frame_from_dict(self):
        input_data = {"name": ["Alice", "Bob"], "age": [25, 30]}
        result = to_frame(input_data)
        
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["name", "age"]
        assert len(result) == 2
        assert result.iloc[0]["name"] == "Alice"
        assert result.iloc[0]["age"] == 25
    
    def test_to_frame_from_list_of_dicts(self):
        input_data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ]
        result = to_frame(input_data)
        
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["name", "age"]
        assert len(result) == 2
    
    def test_to_frame_from_list_of_lists(self):
        input_data = [["Alice", 25], ["Bob", 30]]
        result = to_frame(input_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert len(result.columns) == 2
    
    def test_to_frame_from_existing_dataframe(self):
        original_df = pd.DataFrame({"name": ["Alice"], "age": [25]})
        result = to_frame(original_df)
        
        assert isinstance(result, pd.DataFrame)
        assert result.equals(original_df)
    
    def test_to_frame_from_series(self):
        input_series = pd.Series([1, 2, 3, 4], name="values")
        result = to_frame(input_series)
        
        assert isinstance(result, pd.DataFrame)
        assert "values" in result.columns
        assert len(result) == 4
    
    def test_to_frame_from_list(self):
        input_data = [1, 2, 3, 4]
        result = to_frame(input_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert len(result.columns) == 1
    
    def test_to_frame_from_tuple(self):
        input_data = (1, 2, 3, 4)
        result = to_frame(input_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert len(result.columns) == 1
    
    def test_to_frame_empty_dict(self):
        result = to_frame({})
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert len(result.columns) == 0
    
    def test_to_frame_empty_list(self):
        result = to_frame([])
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_to_frame_nested_dict(self):
        input_data = {
            "users": {
                "name": ["Alice", "Bob"],
                "age": [25, 30]
            }
        }
        # This might raise an error or handle differently depending on implementation
        try:
            result = to_frame(input_data)
            assert isinstance(result, pd.DataFrame)
        except (ValueError, TypeError):
            # Some nested structures might not be directly convertible
            pass
    
    def test_to_frame_mixed_data_types(self):
        input_data = {
            "name": ["Alice", "Bob"],
            "age": [25, 30],
            "is_active": [True, False],
            "score": [95.5, 87.2]
        }
        result = to_frame(input_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert len(result.columns) == 4
        
        # Check data types are preserved
        assert result["name"].dtype == object
        assert result["age"].dtype in [int, "int64"]
        assert result["is_active"].dtype == bool
        assert result["score"].dtype == float
    
    def test_to_frame_with_nan_values(self):
        input_data = {
            "name": ["Alice", "Bob", None],
            "age": [25, None, 35]
        }
        result = to_frame(input_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert pd.isna(result.iloc[2]["name"])
        assert pd.isna(result.iloc[1]["age"])


class TestWriteCsv:
    """Test the write_csv function."""
    
    def test_write_csv_basic(self, temp_dir):
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["NYC", "LA", "Chicago"]
        })
        file_path = temp_dir / "output.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        
        # Read back and verify (no index_col since we wrote with index=False)
        result_df = pd.read_csv(file_path)
        pd.testing.assert_frame_equal(df, result_df)
    
    def test_write_csv_empty_dataframe(self, temp_dir):
        df = pd.DataFrame()
        file_path = temp_dir / "empty.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        # Empty DataFrame should still create a file
        assert file_path.stat().st_size >= 0
    
    def test_write_csv_single_row(self, temp_dir):
        df = pd.DataFrame({"name": ["Alice"], "age": [25]})
        file_path = temp_dir / "single.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        result_df = pd.read_csv(file_path)
        pd.testing.assert_frame_equal(df, result_df)
    
    def test_write_csv_single_column(self, temp_dir):
        df = pd.DataFrame({"values": [1, 2, 3, 4, 5]})
        file_path = temp_dir / "single_col.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        result_df = pd.read_csv(file_path)
        pd.testing.assert_frame_equal(df, result_df)
    
    def test_write_csv_with_special_characters(self, temp_dir):
        df = pd.DataFrame({
            "name": ["Alice,Smith", "Bob\"Jones", "Charlie\nBrown"],
            "description": ["Line1\nLine2", "Quote\"Test", "Comma,Test"]
        })
        file_path = temp_dir / "special.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        # CSV should handle special characters properly
        result_df = pd.read_csv(file_path)
        pd.testing.assert_frame_equal(df, result_df)
    
    def test_write_csv_with_nan_values(self, temp_dir):
        df = pd.DataFrame({
            "name": ["Alice", None, "Charlie"],
            "age": [25, 30, None],
            "score": [95.5, None, 87.2]
        })
        file_path = temp_dir / "with_nan.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        result_df = pd.read_csv(file_path)
        # NaN values should be preserved
        assert pd.isna(result_df.iloc[1]["name"])
        assert pd.isna(result_df.iloc[2]["age"])
        assert pd.isna(result_df.iloc[1]["score"])
    
    def test_write_csv_mixed_data_types(self, temp_dir):
        df = pd.DataFrame({
            "string_col": ["a", "b", "c"],
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "bool_col": [True, False, True],
            "datetime_col": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
        })
        file_path = temp_dir / "mixed_types.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        # Should be able to write mixed data types
        content = file_path.read_text()
        assert "string_col" in content
        assert "int_col" in content
        assert "float_col" in content
        assert "bool_col" in content
        assert "datetime_col" in content
    
    def test_write_csv_overwrite_existing(self, temp_dir):
        df1 = pd.DataFrame({"col1": [1, 2, 3]})
        df2 = pd.DataFrame({"col2": [4, 5, 6]})
        file_path = temp_dir / "overwrite.csv"
        
        # Write first DataFrame
        write_csv(df1, str(file_path))
        assert file_path.exists()
        
        # Overwrite with second DataFrame
        write_csv(df2, str(file_path))
        
        # Verify second DataFrame was written
        result_df = pd.read_csv(file_path)
        pd.testing.assert_frame_equal(df2, result_df)
    
    def test_write_csv_invalid_path(self):
        df = pd.DataFrame({"col": [1, 2, 3]})
        
        # Should raise an exception for invalid path
        with pytest.raises((OSError, IOError, PermissionError)):
            write_csv(df, "/invalid/path/file.csv")
    
    def test_write_csv_directory_path(self, temp_dir):
        df = pd.DataFrame({"col": [1, 2, 3]})
        
        # Should raise an exception when trying to write to directory
        with pytest.raises((OSError, IOError, IsADirectoryError)):
            write_csv(df, str(temp_dir))
    
    def test_write_csv_large_dataframe(self, temp_dir):
        # Test with a larger DataFrame
        import numpy as np
        
        size = 1000
        df = pd.DataFrame({
            "id": range(size),
            "value": np.random.rand(size),
            "category": [f"cat_{i % 10}" for i in range(size)]
        })
        file_path = temp_dir / "large.csv"
        
        write_csv(df, str(file_path))
        
        assert file_path.exists()
        assert file_path.stat().st_size > 0
        
        # Verify we can read it back
        result_df = pd.read_csv(file_path)
        assert len(result_df) == size
        assert list(result_df.columns) == ["id", "value", "category"]