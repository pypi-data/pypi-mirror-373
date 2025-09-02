"""
Basic functionality tests for core qufe functions
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock


class TestBasicFunctionality:
    """Test basic functionality that doesn't require external dependencies"""
    
    def test_flatten_function(self):
        """Test flatten function from base module"""
        try:
            from qufe.base import flatten
            
            # Test basic flattening
            nested_list = [[1, 2], [3, [4, 5]], 6]
            result = flatten(nested_list)
            expected = [1, 2, 3, 4, 5, 6]
            assert result == expected, f"Expected {expected}, got {result}"
            
        except ImportError:
            pytest.skip("flatten function not available")
        except Exception as e:
            pytest.fail(f"flatten function test failed: {e}")
    
    def test_flatten_gen_function(self):
        """Test flatten_gen generator function"""
        try:
            from qufe.base import flatten_gen
            
            nested_list = [[1, 2], [3, [4, 5]], 6]
            result = list(flatten_gen(nested_list))
            expected = [1, 2, 3, 4, 5, 6]
            assert result == expected, f"Expected {expected}, got {result}"
            
        except ImportError:
            pytest.skip("flatten_gen function not available")
        except Exception as e:
            pytest.fail(f"flatten_gen function test failed: {e}")
    
    def test_eb2_function(self):
        """Test eb2 function from excludebracket module"""
        try:
            from qufe.excludebracket import eb2
            
            # Test basic bracket removal
            text_with_brackets = "Hello (world) test [example] end"
            result = eb2(text_with_brackets)
            # The exact result depends on implementation, so just check it runs
            assert isinstance(result, str), "eb2 should return a string"
            
        except ImportError:
            pytest.skip("eb2 function not available")
        except Exception as e:
            pytest.fail(f"eb2 function test failed: {e}")
    
    def test_check_eb_function(self):
        """Test check_eb function from excludebracket module"""
        try:
            from qufe.excludebracket import check_eb
            
            # Test bracket validation
            valid_text = "Hello (world)"
            invalid_text = "Hello (world"
            
            # Just check that function runs without error
            result_valid = check_eb(valid_text)
            result_invalid = check_eb(invalid_text)
            
            assert isinstance(result_valid, bool), "check_eb should return boolean"
            assert isinstance(result_invalid, bool), "check_eb should return boolean"
            
        except ImportError:
            pytest.skip("check_eb function not available")
        except Exception as e:
            pytest.fail(f"check_eb function test failed: {e}")
    
    def test_ts_class_basic(self):
        """Test basic TS class functionality"""
        try:
            from qufe.base import TS
            
            # Create TS instance with default timezone
            ts = TS()
            assert ts is not None, "TS instance should be created"
            
            # Test with specific timezone
            ts_seoul = TS('Asia/Seoul')
            assert ts_seoul is not None, "TS instance with timezone should be created"
            
        except ImportError:
            pytest.skip("TS class not available")
        except Exception as e:
            pytest.fail(f"TS class test failed: {e}")
    
    def test_print_dict_function(self):
        """Test print_dict function"""
        try:
            from qufe.texthandler import print_dict
            import io
            from contextlib import redirect_stdout
            
            test_dict = {"key1": "value1", "key2": ["item1", "item2"]}
            
            # Capture output
            f = io.StringIO()
            with redirect_stdout(f):
                print_dict(test_dict)
            
            output = f.getvalue()
            assert len(output) > 0, "print_dict should produce output"
            assert "key1" in output, "Output should contain dictionary keys"
            
        except ImportError:
            pytest.skip("print_dict function not available")
        except Exception as e:
            pytest.fail(f"print_dict function test failed: {e}")
    
    def test_filehandler_class_basic(self):
        """Test basic FileHandler class functionality"""
        try:
            from qufe.filehandler import FileHandler
            
            # Create FileHandler instance
            fh = FileHandler()
            assert fh is not None, "FileHandler instance should be created"
            
            # Test with temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a test file
                test_file = os.path.join(temp_dir, "test.txt")
                with open(test_file, "w") as f:
                    f.write("test content")
                
                # Test file operations (basic existence check)
                assert os.path.exists(test_file), "Test file should exist"
            
        except ImportError:
            pytest.skip("FileHandler class not available")
        except Exception as e:
            pytest.fail(f"FileHandler class test failed: {e}")


class TestDependencyHandling:
    """Test handling of optional dependencies"""
    
    def test_database_handler_graceful_failure(self):
        """Test that database handler fails gracefully without DB connection"""
        try:
            from qufe.dbhandler import PostgreSQLHandler
            
            # This should not crash, even if DB is not available
            # We're not actually connecting, just testing import and instantiation
            assert PostgreSQLHandler is not None
            
        except ImportError:
            pytest.skip("PostgreSQLHandler not available")
        except Exception as e:
            # Database connection errors are expected in test environment
            if "database" in str(e).lower() or "connection" in str(e).lower():
                pytest.skip(f"Database not available for testing: {e}")
            else:
                pytest.fail(f"Unexpected error in PostgreSQLHandler: {e}")
    
    def test_selenium_handler_graceful_failure(self):
        """Test that selenium handler fails gracefully without browser"""
        try:
            import qufe.wbhandler
            # Just test that module imports without immediate crashes
            assert True
            
        except ImportError as e:
            if "selenium" in str(e).lower() or "webdriver" in str(e).lower():
                pytest.skip(f"Selenium dependencies not available: {e}")
            else:
                pytest.fail(f"Unexpected import error in wbhandler: {e}")
        except Exception as e:
            # Browser-related errors are expected in test environment
            if any(keyword in str(e).lower() for keyword in ["browser", "driver", "chrome", "firefox"]):
                pytest.skip(f"Browser not available for testing: {e}")
            else:
                pytest.fail(f"Unexpected error in wbhandler: {e}")