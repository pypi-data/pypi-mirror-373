# pyright: reportArgumentType=false, reportUnknownMemberType=false, reportMissingTypeStubs=false
from pathlib import Path

import pandas as pd
from spoofs import debug_error_spoof as debug_spoof

from data_explorer_qt.data.dataenums import Dtype
from data_explorer_qt.data.datamodel import (
    FilterStore,
    apply_filter,
    categorical_comparator,
    datetime_comparator,
    handle_dtype_operation,
    handle_nan_operation,
    numeric_comparator,
)


def test_dtype_conversion():
    # 6 possible conversions, but only 3 valid conversions
    # Any -> Categorical, Numeric -> Categorical, Categorical -> Datetime.
    path_to_data = str(Path(__file__).parent / "Test.xlsx")
    data = pd.read_excel(path_to_data, engine="calamine")
    # Dates column is default read as categorical in this case.
    assert not datetime_comparator(data["Dates"])
    # Categorical -> Datetime
    assert datetime_comparator(
        handle_dtype_operation(data["Dates"], "Datetime", debug_spoof)
    )
    # Numeric -> Categorical
    assert categorical_comparator(
        handle_dtype_operation(data["Header 1"], "Categorical", debug_spoof)
    )
    # Categorical (empty column) -> Numeric
    assert numeric_comparator(
        handle_dtype_operation(data["Header 2"], "Numeric", debug_spoof)
    )


def test_nan_handling():
    path_to_data = str(Path(__file__).parent / "TestNaN.xlsx")
    data = pd.read_excel(path_to_data, engine="calamine")
    data["Dates"] = handle_dtype_operation(data["Dates"], "Datetime", debug_spoof)
    data = handle_nan_operation(data, "Keep as NaN", "Dates", debug_spoof)
    assert data["Dates"].isna().sum() == 2
    data = handle_nan_operation(data, "Replace with No Data", "Header 3", debug_spoof)
    assert data["Header 3"].str.contains("No Data").sum() == 3
    data = handle_nan_operation(data, "Replace with 0", "Header 2", debug_spoof)
    assert (data["Header 2"] == 0).sum() == len(data)


def test_filtering():
    path_to_data = str(Path(__file__).parent / "Test.xlsx")
    filter = FilterStore(dtype=Dtype.CATEGORICAL, filter_value=["Hello"])
    data = pd.read_excel(path_to_data, engine="calamine")
    data = apply_filter(data, column="Header 3", filterstore=filter)
    assert len(data) == 4
    data = pd.read_excel(path_to_data, engine="calamine")
    filter = FilterStore(dtype=Dtype.NUMERIC, filter_value=(10, 100))
    data = apply_filter(data, column="Header 1", filterstore=filter)
    assert len(data) == 2
