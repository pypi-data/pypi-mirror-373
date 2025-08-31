"""
Basic import tests for all qufe modules
"""
import pytest


def test_main_package_import():
    """Test main package import"""
    import qufe
    assert hasattr(qufe, '__version__')
    assert hasattr(qufe, '__author__')
    assert qufe.__version__ == "0.1.2"


def test_base_module_import():
    """Test base module import"""
    try:
        import qufe.base
        from qufe.base import TS, diff_codes, import_script, flatten, flatten_gen
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import base module: {e}")


def test_dbhandler_module_import():
    """Test dbhandler module import"""
    try:
        import qufe.dbhandler
        from qufe.dbhandler import PostGreSQLHandler
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import dbhandler module: {e}")


def test_excludebracket_module_import():
    """Test excludebracket module import"""
    try:
        import qufe.excludebracket
        from qufe.excludebracket import eb2, check_eb
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import excludebracket module: {e}")


def test_filehandler_module_import():
    """Test filehandler module import"""
    try:
        import qufe.filehandler
        from qufe.filehandler import FileHandler, PathFinder
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import filehandler module: {e}")


def test_interactionhandler_module_import():
    """Test interactionhandler module import"""
    try:
        import qufe.interactionhandler
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import interactionhandler module: {e}")


def test_pdhandler_module_import():
    """Test pdhandler module import"""
    try:
        import qufe.pdhandler
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import pdhandler module: {e}")


def test_texthandler_module_import():
    """Test texthandler module import"""
    try:
        import qufe.texthandler
        from qufe.texthandler import print_dict, print_in_columns, list_to_doku_wiki_table
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import texthandler module: {e}")


def test_wbhandler_module_import():
    """Test wbhandler module import"""
    try:
        import qufe.wbhandler
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import wbhandler module: {e}")


def test_all_imports_from_init():
    """Test that all imports work from __init__.py"""
    try:
        from qufe import (
            base, dbhandler, excludebracket, filehandler,
            interactionhandler, pdhandler, texthandler, wbhandler,
            TS, FileHandler, PathFinder, PostGreSQLHandler,
            diff_codes, import_script, flatten, flatten_gen,
            print_dict, print_in_columns, list_to_doku_wiki_table,
            eb2, check_eb
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import from qufe.__init__: {e}")