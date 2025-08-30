# pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportArgumentType=false, reportAssignmentType=false, reportOperatorIssue=false
import typing
from dataclasses import dataclass
from functools import cache, cached_property
from typing import Callable, final

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype, is_object_dtype
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if typing.TYPE_CHECKING:
    from ..dataexplorer import DataExplorer

from ..guihelper import build_layout, get_dynamic_scroll_area
from .base import Dtype, DtypeOperation, NaNOperation, NumericConverter
from .filterwidget import FilterStore, FilterWidget, InvalidFilterWidgetError
from .numcatwidget import NumCatWidget


@dataclass
class FilterGUI:
    filter_page: QWidget
    filter_layout: QGridLayout
    shape_label: QLabel
    filter_widgets: list[FilterWidget]


@dataclass
class NumCatGUI:
    num_to_cat_page: QWidget
    num_to_cat_layout: QGridLayout
    num_to_cat_widgets: list[NumCatWidget]


@final
class DataStore:
    name: str
    # Maps type of cleaning (ex: Nan) to dict of column names
    # to operation performed.
    cleaning_operations: dict[str, dict[str, str]]
    cleaned_data: pd.DataFrame
    # Maps column names to a filter operation
    # For datetimes and continuous variables,
    # this is a less than, greater than comparison.
    # For categorical variables,
    # this is a value in/value equal to comparison.
    filters: dict[str, list[FilterStore]]
    filterGUI: FilterGUI
    on_filter_change_callbacks: dict[int, Callable[[], None]]
    callback_id: int
    filtered_data: pd.DataFrame
    numeric_to_categorical: dict[str, NumericConverter]

    def __init__(
        self,
        cl_ops: dict[str, dict[str, str]],
        data: pd.DataFrame,
        name: str,
        dataexplorer: "DataExplorer",
    ):
        self.name = name
        self.cleaning_operations = cl_ops
        self.cleaned_data = data
        self.dataexplorer = dataexplorer
        self.debug = dataexplorer.debug
        self.error = dataexplorer.error
        self.filters = {}
        self.filterGUI = self._get_filter_GUI(name)
        self.numCatGUI = self._get_num_cat_GUI(name)
        self.filtered_data = data.copy()
        self.callback_id = 1
        self.on_filter_change_callbacks = {}
        self.numeric_to_categorical = {}

    def apply_filters(self):
        init_len = len(self.filtered_data)
        self.filtered_data = self.cleaned_data.copy()
        for column in self.filters:
            for filterstore in self.filters[column]:
                if not filterstore.active:
                    continue
                starting_length = len(self.filtered_data)
                self.debug(filterstore)
                self.filtered_data = apply_filter(
                    self.filtered_data, column, filterstore
                )
                self.debug(
                    f"{starting_length - len(self.filtered_data)} "
                    "rows removed by filter "
                    f"{column} {filterstore.dtype} {filterstore.filter_value}"
                )

        delta = init_len - len(self.filtered_data)
        if delta > 0:
            self.dataexplorer.status_message(
                f"{delta} rows removed by newly applied filters"
            )
        elif delta == 0:
            self.dataexplorer.status_message(
                "Newly applied filters have not changed the data."
            )
        else:
            self.dataexplorer.status_message(
                f"{-delta} rows added by newly applied filters"
            )

        self.filterGUI.shape_label.setText(
            f"Filtered - Rows: {self.filtered_data.shape[0]},"
            f"Columns: {self.filtered_data.shape[1]}"
        )

        self.replot_callbacks()

    def add_filter_change_callback(self, callback: Callable[[], None]) -> int:
        callback_id = self.callback_id
        self.on_filter_change_callbacks[callback_id] = callback
        self.callback_id += 1
        return callback_id

    def remove_filter_change_callback(self, callback_id: int):
        _ = self.on_filter_change_callbacks.pop(callback_id)

    def _get_filter_GUI(self, name: str) -> FilterGUI:
        gui = FilterGUI(
            filter_page=self.dataexplorer.get_widget(),
            filter_layout=QGridLayout(),
            shape_label=QLabel(),
            filter_widgets=[],
        )
        vbox_layout = QVBoxLayout(gui.filter_page)
        vbox_layout.setSpacing(10)

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        unfiltered_shape_label = QLabel(
            f"Unfiltered - Rows: {self.cleaned_data.shape[0]}, "
            f"Columns: {self.cleaned_data.shape[1]}"
        )
        unfiltered_shape_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        gui.shape_label = QLabel(
            f"Filtered - Rows: {self.cleaned_data.shape[0]}, "
            f"Columns: {self.cleaned_data.shape[1]}"
        )
        gui.shape_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        add_widget_button = QPushButton("Add Filter...")
        _ = add_widget_button.clicked.connect(self._filter_widget_dialog)

        apply_filter_button = QPushButton("Apply Filters")
        _ = apply_filter_button.clicked.connect(self.apply_filters)

        scroll_area, content_widget = get_dynamic_scroll_area(
            self.dataexplorer.get_widget
        )

        content_widget.setLayout(gui.filter_layout)

        build_layout(vbox_layout, [name_label, unfiltered_shape_label, gui.shape_label])
        vbox_layout.addWidget(scroll_area, 1)
        build_layout(vbox_layout, [add_widget_button, apply_filter_button])

        gui.filter_page.setLayout(vbox_layout)
        return gui

    def _filter_widget_dialog(self):
        self._select_column = self.dataexplorer.get_widget(detached=True)
        self._select_column.setWindowTitle("Select column to filter")
        layout = QVBoxLayout()
        self._select_column.resize(500, 300)
        label = QLabel("Choose a column")
        self._column_chosen = QComboBox()
        self._column_chosen.addItems(self.columns)
        ok_button = QPushButton("Ok")
        _ = ok_button.clicked.connect(self._add_filter_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widg_list = [label, self._column_chosen, ok_button]
        build_layout(layout, widg_list)
        self._select_column.setLayout(layout)
        self._select_column.show()

    def _add_filter_widget(self):
        column = self._column_chosen.currentText()
        self._select_column.deleteLater()
        self.debug(f"Trying to create filter widget for {column}")
        try:
            filter_widget = FilterWidget(self, column, self.dataexplorer)
        except InvalidFilterWidgetError:
            return
        n = len(self.filterGUI.filter_widgets)
        self.filterGUI.filter_layout.addWidget(
            filter_widget, self._row(n), self._col(n)
        )
        if column in self.filters:
            self.filters[column].append(filter_widget.filterstore)
        else:
            self.filters[column] = [filter_widget.filterstore]
        self.filterGUI.filter_widgets.append(filter_widget)

    def _row(self, n: int) -> int:
        grid_max_col: int = self.dataexplorer.config["Grid"]["grid_max_col"]
        return int(n / grid_max_col)

    def _col(self, n: int) -> int:
        grid_max_col: int = self.dataexplorer.config["Grid"]["grid_max_col"]
        return n % grid_max_col

    def on_filter_widget_delete(self, widget: FilterWidget):
        layout = self.filterGUI.filter_layout
        ws = self.filterGUI.filter_widgets

        if len(ws) > 1 and widget != ws[-1]:
            for widg in ws:
                layout.removeWidget(widg)
            ws.remove(widget)
            self.debug("Widget Removed!")
            for i, widg in enumerate(ws):
                layout.addWidget(widg, self._row(i), self._col(i))
            layout.update()
            self.debug("Layout Updated!")
        else:
            layout.removeWidget(widget)
            self.debug("Last Widget Removed!")
            ws.remove(widget)

        self.filters[widget.column].remove(widget.filterstore)
        if len(self.filters[widget.column]) == 0:
            _ = self.filters.pop(widget.column)
        self.apply_filters()

    def _get_num_cat_GUI(self, name: str) -> NumCatGUI:
        gui = NumCatGUI(
            num_to_cat_page=self.dataexplorer.get_widget(),
            num_to_cat_layout=QGridLayout(),
            num_to_cat_widgets=[],
        )
        vbox_layout = QVBoxLayout(gui.num_to_cat_page)
        vbox_layout.setSpacing(10)

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        add_widget_button = QPushButton("Add numeric to categorical rule...")
        _ = add_widget_button.clicked.connect(self._num_cat_dialog)

        scroll_area, content_widget = get_dynamic_scroll_area(
            self.dataexplorer.get_widget
        )

        content_widget.setLayout(gui.num_to_cat_layout)

        build_layout(vbox_layout, [name_label])
        vbox_layout.addWidget(scroll_area, 1)
        build_layout(vbox_layout, [add_widget_button])

        gui.num_to_cat_page.setLayout(vbox_layout)
        return gui

    def _num_cat_dialog(self):
        self._select_column_nc = self.dataexplorer.get_widget(detached=True)
        self._select_column_nc.setWindowTitle("Select numeric column")
        layout = QVBoxLayout()
        self._select_column_nc.resize(200, 200)
        label = QLabel("Choose a column")
        self._column_chosen_nc = QComboBox()
        self.debug(self.numeric_columns)
        self._column_chosen_nc.addItems(self.numeric_columns)
        ok_button = QPushButton("Ok")
        _ = ok_button.clicked.connect(self._add_num_cat_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widg_list = [label, self._column_chosen_nc, ok_button]
        build_layout(layout, widg_list)
        self._select_column_nc.setLayout(layout)
        self._select_column_nc.show()

    def _add_num_cat_widget(self):
        column = self._column_chosen_nc.currentText()
        self._select_column_nc.deleteLater()
        self.debug(f"Trying to create num_cat widget for {column}")
        if column in self.numeric_to_categorical:
            self.error(
                "Cannot convert a numerical column to a categorical column twice"
            )
            return
        num_cat_widget = NumCatWidget(self, column, self.dataexplorer)
        n = len(self.numCatGUI.num_to_cat_widgets)
        self.numCatGUI.num_to_cat_layout.addWidget(
            num_cat_widget, self._row(n), self._col(n)
        )
        self.numeric_to_categorical[column] = num_cat_widget.numeric_converter
        self.numCatGUI.num_to_cat_widgets.append(num_cat_widget)

    def on_num_cat_widget_delete(self, widget: NumCatWidget):
        layout = self.numCatGUI.num_to_cat_layout
        ws = self.numCatGUI.num_to_cat_widgets

        if len(ws) > 1 and widget != ws[-1]:
            for widg in ws:
                layout.removeWidget(widg)
            ws.remove(widget)
            self.debug("Widget Removed!")
            for i, widg in enumerate(ws):
                layout.addWidget(widg, self._row(i), self._col(i))
            layout.update()
            self.debug("Layout Updated!")
        else:
            layout.removeWidget(widget)
            self.debug("Widget Removed!")
            _ = ws.pop()

        _ = self.numeric_to_categorical.pop(widget.column)
        self.replot_callbacks()

    def replot_callbacks(self):
        callbacks: dict[int, Callable[[], None]] = self.on_filter_change_callbacks
        for callback in callbacks.values():
            callback()
            self.debug("Replotting!")

    @cached_property
    def columns(self) -> list[str]:
        return [column for column in self.cleaned_data.columns]

    @cached_property
    def numeric_columns(self) -> list[str]:
        return [
            column
            for column in self.cleaned_data.columns
            if numeric_comparator(self.cleaned_data[column])
        ]

    @cached_property
    def categorical_columns(self) -> list[str]:
        return [
            column
            for column in self.cleaned_data.columns
            if categorical_comparator(self.cleaned_data[column])
        ]

    @cached_property
    def datetime_columns(self) -> list[str]:
        return [
            column
            for column in self.cleaned_data.columns
            if datetime_comparator(self.cleaned_data[column])
        ]

    @cache
    def get_column_dtype(self, column: str) -> Dtype:
        if numeric_comparator(self.cleaned_data[column]):
            return Dtype.NUMERIC
        elif categorical_comparator(self.cleaned_data[column]):
            return Dtype.CATEGORICAL
        else:
            return Dtype.DATETIME


@final
class DataModel:
    # Maps name of dataset to a DataStore
    datasets: dict[str, DataStore]
    active: str = ""

    def __init__(self, dataexplorer: "DataExplorer"):
        self.datasets = {}
        self.dataexplorer: "DataExplorer" = dataexplorer
        self.debug = dataexplorer.debug
        self.error = dataexplorer.error

    def add_dataset_to_model(
        self,
        dataset: pd.DataFrame,
        name: str,
        cleaning_operations: dict[str, dict[str, str]],
    ):
        self.debug(dataset.head())
        self.debug(dataset.shape)
        valid_name = name
        num = 1
        while valid_name in self.datasets:
            valid_name = f"{name} {num}"
            num += 1
        self.datasets[valid_name] = DataStore(
            cl_ops=cleaning_operations,
            data=dataset,
            name=valid_name,
            dataexplorer=self.dataexplorer,
        )
        self.dataexplorer.gui.add_filter_GUI_to_page(
            self.datasets[valid_name].filterGUI, valid_name
        )
        self.dataexplorer.gui.add_num_cat_GUI_to_page(
            self.datasets[valid_name].numCatGUI, valid_name
        )
        self.debug(f"Name used {valid_name}")
        self.dataexplorer.status_message(f"Data from {name} read!")
        self.dataexplorer.gui.update_data_list(valid_name)

    def set_active_dataset(self, name: str):
        self.active = name

    @property
    def active_dataset(self) -> DataStore | None:
        if self.active == "":
            self.error("No valid active dataset!")
            return None
        else:
            return self.datasets[self.active]

    @property
    def active_cleaned_data(self) -> pd.DataFrame | None:
        if self.active_dataset:
            return self.active_dataset.cleaned_data
        else:
            return None

    @property
    def active_filtered_data(self) -> pd.DataFrame | None:
        if self.active_dataset:
            return self.active_dataset.filtered_data
        else:
            return None


def handle_dtype_operation(
    series: pd.Series, operation: str, debug_callback: Callable[[str], None]
) -> pd.Series:
    debug_callback(operation)
    match operation:
        case DtypeOperation.CATEGORICAL.value:
            series = series.astype(str)
        case DtypeOperation.NUMERIC.value:
            series = pd.to_numeric(series, errors="coerce")  # pyright: ignore[reportUnknownMemberType, reportAssignmentType]
        case DtypeOperation.DATETIME.value:
            series = pd.to_datetime(series, errors="coerce")
        case _:
            raise RuntimeError("Invalid dtype cleaning operation.")

    assert isinstance(series, pd.Series)
    return series


def handle_nan_operation(
    df: pd.DataFrame,
    operation: str,
    column: str,
    debug_callback: Callable[[str], None],
) -> pd.DataFrame:
    debug_callback(operation)
    match operation:
        case NaNOperation.REPLACE_WITH_0.value:
            return df.fillna({column: 0})
        case NaNOperation.DROP_ROWS.value:
            return df.dropna(subset=column)
        case NaNOperation.KEEP_AS_NaN.value:
            return df
        case NaNOperation.REPLACE_WITH_NO_DATA.value:
            return df.fillna({column: "No Data"})
        case _:
            raise RuntimeError("Invalid nan cleaning operation.")


def numeric_comparator(df_column: pd.Series) -> bool:
    return is_numeric_dtype(df_column)


def categorical_comparator(df_column: pd.Series) -> bool:
    return is_object_dtype(df_column)


def datetime_comparator(df_column: pd.Series) -> bool:
    return is_datetime64_any_dtype(df_column)


def apply_filter(
    data: pd.DataFrame, column: str, filterstore: FilterStore
) -> pd.DataFrame:
    match filterstore.dtype:
        case Dtype.CATEGORICAL:
            if len(filterstore.filter_value) > 0:
                data = data[data[column].astype(str).isin(filterstore.filter_value)]
        case Dtype.NUMERIC:
            data = data[
                (data[column].values >= filterstore.filter_value[0])
                & (data[column].values <= filterstore.filter_value[1])
            ]
        case Dtype.DATETIME:
            data = data[
                (data[column].values >= filterstore.filter_value[0])
                & (data[column].values <= filterstore.filter_value[1])
            ]
    assert isinstance(data, pd.DataFrame)
    return data
