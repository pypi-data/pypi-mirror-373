def test_import_utils_does_not_import_pandas() -> None:
    import importlib
    import sys

    # Remove potentially cached modules
    pandas_mod = sys.modules.pop("pandas", None)
    sys.modules.pop("arbolab.utils", None)
    sys.modules.pop("arbolab.utils.dataframe", None)

    try:
        importlib.import_module("arbolab.utils")
        assert "pandas" not in sys.modules
    finally:  # restore for any follow-up tests
        if pandas_mod is not None:
            sys.modules["pandas"] = pandas_mod
