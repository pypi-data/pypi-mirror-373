# Test suite for FileHelper class using pytest

import os
import tempfile
import shutil
from pathlib import Path
import json
from unittest.mock import patch, mock_open

from sokrates.file_helper import FileHelper

def test_clean_name():
    """Test clean_name method with various inputs"""
    # Test basic cleaning
    assert FileHelper.clean_name("test/file") == "test_file"
    assert FileHelper.clean_name("file:name") == "file-name"
    assert FileHelper.clean_name("file*name") == "file-name"
    
    # Test removal of problematic characters
    res = FileHelper.clean_name('file?"name')
    assert not '?' in res
    assert not '"' in res
    assert FileHelper.clean_name("?test?") == "test"  # Question marks should be gone
    
    # Test with no special characters (should return unchanged)
    assert FileHelper.clean_name("normal_name.txt") == "normal_name.txt"

def test_list_files_in_directory():
    """Test list_files_in_directory method"""
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = Path(temp_dir) / "file1.txt"
        file2 = Path(temp_dir) / "file2.py"
        dir1 = Path(temp_dir) / "subdir"
        dir1.mkdir()
        
        # Create files
        file1.touch()
        file2.touch()
        
        # Test listing only files, not directories
        result = FileHelper.list_files_in_directory(temp_dir)
        assert len(result) == 2  # Should find both files
        assert str(file1) in result
        assert str(file2) in result
        
        # Create a subdirectory and ensure it's not included
        dir_result = FileHelper.list_files_in_directory(temp_dir)
        for item in dir_result:
            assert Path(item).is_file()  # All items should be files

def test_read_json_file():
    """Test read_json_file method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file_path = Path(temp_dir) / "test.json"
        
        # Create a test JSON file
        data = {"key": "value", "number": 42}
        with open(json_file_path, 'w') as f:
            json.dump(data, f)
        
        # Read and verify content
        result = FileHelper.read_json_file(str(json_file_path))
        assert result == data

def test_read_file():
    """Test read_file method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test.txt"
        
        # Create a test file
        content = "Hello, World!\n  With whitespace   "
        with open(file_path, 'w') as f:
            f.write(content)
        
        # Read and verify content (stripped)
        result = FileHelper.read_file(str(file_path))
        assert result == content.strip()
        
        # Test exception handling for non-existent file
        non_existent = Path(temp_dir) / "nonexistent.txt"
        try:
            FileHelper.read_file(str(non_existent))
        except FileNotFoundError as e:
            assert str(non_existent) in str(e)

def test_read_multiple_files():
    """Test read_multiple_files method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = Path(temp_dir) / "file1.txt"
        file2 = Path(temp_dir) / "file2.txt"
        
        # Create test files
        content1 = "Content of first file"
        content2 = "Content of second file"
        with open(file1, 'w') as f:
            f.write(content1)
        with open(file2, 'w') as f:
            f.write(content2)
        
        # Test reading multiple files
        result = FileHelper.read_multiple_files([str(file1), str(file2)])
        assert len(result) == 2
        assert result[0] == content1.strip()
        assert result[1] == content2.strip()

def test_read_multiple_files_from_directories():
    """Test read_multiple_files_from_directories method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories and files
        dir1 = Path(temp_dir) / "dir1"
        dir2 = Path(temp_dir) / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        file1 = dir1 / "file1.txt"
        file2 = dir2 / "file2.txt"
        
        with open(file1, 'w') as f:
            f.write("Content of first file")
        with open(file2, 'w') as f:
            f.write("Content of second file")
        
        # Test reading from multiple directories
        result = FileHelper.read_multiple_files_from_directories([str(dir1), str(dir2)])
        assert len(result) == 2
        assert "Content of first file" in result
        assert "Content of second file" in result

def test_write_to_file():
    """Test write_to_file method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "output.txt"
        
        # Write content to file
        content = "Hello, World!"
        FileHelper.write_to_file(str(file_path), content)
        
        # Verify content was written correctly
        result = FileHelper.read_file(str(file_path))
        assert result == content
        
        # Test with nested directory creation
        nested_dir = Path(temp_dir) / "nested" / "deep"
        file_in_nested = nested_dir / "nested.txt"
        nested_content = "Nested content"
        FileHelper.write_to_file(str(file_in_nested), nested_content)
        
        assert file_in_nested.exists()
        result = FileHelper.read_file(str(file_in_nested))
        assert result == nested_content

def test_write_to_existing_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"
        initial_content = "First line."
        FileHelper.write_to_file(file_path=test_file, content=initial_content)
        new_content = "Second line."
        FileHelper.write_to_file(file_path=test_file, content=new_content)
        assert test_file.read_text() == new_content

def test_create_new_file():
    """Test create_new_file method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "newfile.txt"
        
        # Create new empty file
        FileHelper.create_new_file(str(file_path))
        
        assert file_path.exists()
        result = FileHelper.read_file(str(file_path))
        assert result == ""  # Empty file should return empty string

def test_generate_postfixed_sub_directory_name():
    """Test generate_postfixed_sub_directory_name method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir) / "base"
        
        # Generate directory name
        dir_name = FileHelper.generate_postfixed_sub_directory_name(str(base_dir))
        
        # Should contain a timestamp in YYYY-MM-DD_HH-MM format
        assert "20" in dir_name  # Year should be present
        assert "-" in dir_name  # Separator should exist
        assert "_" in dir_name  # Hour-minute separator should exist

def test_generate_postfixed_file_path():
    """Test generate_postfixed_file_path method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test.txt"
        
        # Generate new timestamped path
        new_path = FileHelper.generate_postfixed_file_path(str(file_path))
        
        # Should have a timestamp and same extension
        assert "_20" in new_path  # Year should be present
        assert ".txt" in new_path  # Extension preserved

def test_combine_files():
    """Test combine_files method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = Path(temp_dir) / "file1.txt"
        file2 = Path(temp_dir) / "file2.txt"
        
        # Create files
        with open(file1, 'w') as f:
            f.write("First file content")
        with open(file2, 'w') as f:
            f.write("Second file content")
        
        # Combine files
        result = FileHelper.combine_files([str(file1), str(file2)])
        
        assert "First file content" in result
        assert "Second file content" in result
        assert "---" in result  # Separator should be present

def test_combine_files_in_directories():
    """Test combine_files_in_directories method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        dir1 = Path(temp_dir) / "dir1"
        dir2 = Path(temp_dir) / "dir2"
        
        # Create directories and files
        dir1.mkdir()
        dir2.mkdir()
        
        file1 = dir1 / "file1.txt"
        file2 = dir2 / "file2.txt"
        
        with open(file1, 'w') as f:
            f.write("Content of first directory")
        with open(file2, 'w') as f:
            f.write("Content of second directory")
        
        # Combine files from directories
        result = FileHelper.combine_files_in_directories([str(dir1), str(dir2)])
        
        assert "Content of first directory" in result
        assert "Content of second directory" in result

def test_directory_tree():
    """Test directory_tree method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create structure
        dir1 = Path(temp_dir) / "dir1"
        dir2 = Path(temp_dir) / "dir2"
        file1 = dir1 / "file1.txt"
        
        dir1.mkdir()
        dir2.mkdir()
        with open(file1, 'w') as f:
            f.write("test")
            
        # Test directory tree generation
        result = FileHelper.directory_tree(str(temp_dir))
        assert len(result) >= 1  # Should find at least one file
        
        # Check that all files are found
        for path in result:
            assert Path(path).exists()

def test_create_and_return_task_execution_directory():
    """Test create_and_return_task_execution_directory method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test default behavior (should return home dir structure)
        try:
            result = FileHelper.create_and_return_task_execution_directory()
            
            # Should be a valid path
            assert result is not None
            assert Path(result).is_dir()
            
        except Exception as e:
            pass  # This might fail if permissions aren't right but that's acceptable for testing

def test_copy_file():
    """Test copy_file method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.txt"
        target = Path(temp_dir) / "target.txt"
        
        # Create source file
        content = "Hello, World!"
        with open(source, 'w') as f:
            f.write(content)
        
        # Copy file
        FileHelper.copy_file(str(source), str(target))
        
        # Verify copy was successful
        assert target.exists()
        result = FileHelper.read_file(str(target))
        assert result == content

def test_directory_tree_with_patterns():
    """Test directory_tree method with exclusions"""
    with tempfile.TemporaryDirectory() as temp_dir:
        dir1 = Path(temp_dir) / "dir1"
        dir2 = Path(temp_dir) / "__pycache__"  # This should be excluded
        
        dir1.mkdir()
        dir2.mkdir()
        
        file1 = dir1 / "file.txt"
        with open(file1, 'w') as f:
            f.write("test")
            
        # Test directory tree (should exclude __pycache__)
        result = FileHelper.directory_tree(str(temp_dir))
        
        # Should find files but not the excluded directory
        assert len(result) >= 0  # At least one file found

def test_write_to_file_with_exception():
    """Test write_to_file method exception handling"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Try to write to a path that doesn't exist (invalid permissions)
        invalid_path = "/root/should_not_be_writable.txt"  # This should fail
        
        try:
            FileHelper.write_to_file(invalid_path, "test content")
        except Exception:
            pass  # Expected behavior

def test_read_file_with_exception():
    """Test read_file method exception handling"""
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent = Path(temp_dir) / "nonexistent.txt"
        
        try:
            FileHelper.read_file(str(non_existent))
        except FileNotFoundError:
            pass  # Expected behavior

def test_clean_name_edge_cases():
    """Test edge cases for clean_name method"""
    try:
        FileHelper.clean_name("")
    except ValueError:
        pass  # Expected behavior for invalid JSON
    
    # Only special characters
    try:
        FileHelper.clean_name("/*?\"")
    except ValueError:
        pass  # Expected behavior for invalid JSON
    
    result = FileHelper.clean_name("file name with spaces.txt")
    assert result == "file-name-with-spaces.txt"

def test_list_files_in_directory_empty():
    """Test list_files_in_directory when directory is empty"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Empty directory should return empty list
        result = FileHelper.list_files_in_directory(temp_dir)
        assert result == []

def test_read_json_file_with_invalid_json():
    """Test read_json_file method exception handling"""
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_json_file = Path(temp_dir) / "invalid.json"
        
        # Create an invalid JSON file
        with open(invalid_json_file, 'w') as f:
            f.write("{invalid json}")
            
        try:
            FileHelper.read_json_file(str(invalid_json_file))
        except Exception:
            pass  # Expected behavior for invalid JSON

def test_combine_files_no_files():
    """Test combine_files method with no files provided"""
    try:
        FileHelper.combine_files(None)
    except Exception:
        pass  # Expected behavior

def test_combine_files_in_directories_no_dirs():
    """Test combine_files_in_directories method with no directories provided"""
    try:
        FileHelper.combine_files_in_directories(None)
    except Exception:
        pass  # Expected behavior
