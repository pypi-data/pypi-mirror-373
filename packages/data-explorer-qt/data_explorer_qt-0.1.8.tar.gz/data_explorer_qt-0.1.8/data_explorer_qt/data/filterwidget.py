import typing
from dataclasses import dataclass

import pandas as pd
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDateTimeEdit,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from superqt import QLabeledDoubleRangeSlider

from ..guihelper import MultiSelectComboBox, build_layout

if typing.TYPE_CHECKING:
    from ..dataexplorer import DataExplorer
    from .datamodel import DataStore
from .base import Dtype


@dataclass
class FilterStore:
    dtype: Dtype
    filter_value: tuple[float, float] | tuple[pd.Timestamp, pd.Timestamp] | list[str]
    active: bool = True


class InvalidFilterWidgetError(RuntimeError):
    pass


@typing.final
class FilterWidget(QWidget):
    filterstore: FilterStore

    def __init__(
        self, datastore: "DataStore", column: str, dataexplorer: "DataExplorer"
    ):
        super().__init__()
        self.setStyleSheet(dataexplorer.stylesheet)
        self.debug = dataexplorer.debug
        self.error = dataexplorer.error
        self.dtype = column_type = datastore.get_column_dtype(column)
        self.column = column
        self.datastore = datastore

        self._layout = QVBoxLayout()
        self.setMaximumHeight(150)  # To prevent detaching of title and filter.
        self.setMinimumWidth(275)  # To prevent squishing of certain filters

        self.column_label = QLabel(column)
        self.column_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.column_label.setObjectName("FilterWidgetLabel")
        self.active_checkbox = QCheckBox()
        self.active_checkbox.setChecked(True)
        _ = self.active_checkbox.toggled.connect(lambda: self.on_state_change())
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.active_checkbox)
        header_layout.addWidget(self.column_label, stretch=1)

        delete_button = QPushButton("Delete Filter")
        delete_button.setObjectName("DeleteFilter")
        _ = delete_button.clicked.connect(self.onDelete)
        match column_type:
            case Dtype.NUMERIC:
                minimum, maximum = (  # pyright: ignore[reportUnknownVariableType]
                    datastore.cleaned_data[column].min(),
                    datastore.cleaned_data[column].max(),
                )
                if maximum == minimum:
                    self.deleteLater()
                    self.debug("Unable to create a filter widget for this.")
                    self.error(
                        f"Unable to create filter widget for {column} because max=min"
                    )
                    raise InvalidFilterWidgetError()

                self.filter_widget = QLabeledDoubleRangeSlider()
                self.filter_widget.setObjectName("LabeledRangeSlider")
                self.debug(f"min: {minimum} max: {maximum}")
                self.filter_widget.setRange(minimum, maximum)  # noqa # pyright: ignore[reportUnknownArgumentType]
                self.filter_widget.setValue((minimum, maximum))
                self.filter_widget._min_label.setMaximumWidth(40)
                self.filter_widget._max_label.setMaximumWidth(40)
                # self.filter_widget.setEdgeLabelMode(
                #     QLabeledDoubleRangeSlider.EdgeLabelMode.LabelIsValue
                # )
                _ = self.filter_widget.valueChanged.connect(self.on_numeric_change)
                self.filterstore = FilterStore(self.dtype, (minimum, maximum))  # pyright: ignore[reportUnknownArgumentType]
                build_layout(
                    self._layout, [header_layout, self.filter_widget, delete_button]
                )
                # TODO: Figure out a better workaround for this code.
                self.filter_widget._min_label.editingFinished.emit()
                self.filter_widget._max_label.editingFinished.emit()
            case Dtype.CATEGORICAL:
                self.filter_widget = MultiSelectComboBox()
                self.filter_widget.addItems(  # pyright: ignore[reportUnknownMemberType]
                    list(datastore.cleaned_data[column].astype(str).unique())
                )
                _ = self.filter_widget.dataChanged.connect(self.on_categorical_change)
                self.filterstore = FilterStore(
                    self.dtype, list(datastore.cleaned_data[column].unique())
                )
                build_layout(
                    self._layout, [header_layout, self.filter_widget, delete_button]
                )
            case Dtype.DATETIME:
                minimum, maximum = (
                    datastore.cleaned_data[column].min(),
                    datastore.cleaned_data[column].max(),
                )
                if not isinstance(maximum, pd.Timestamp) or not isinstance(
                    minimum, pd.Timestamp
                ):
                    self.deleteLater()
                    self.debug(f"Datetime values are of wrong type for column {column}")
                    self.error(
                        f"Unable to create a filter widget for {column}"
                        "due to a type issue."
                    )
                    raise InvalidFilterWidgetError()

                def get_time(x: pd.Timestamp) -> QDateTime:
                    return QDateTime(x.year, x.month, x.day, x.hour, x.minute, x.second)

                hbox_min = QHBoxLayout()
                min_value_label = QLabel("Min")
                self.min_value = QDateTimeEdit()
                self.min_value.setMinimumDateTime(get_time(minimum))
                self.min_value.setMaximumDateTime(get_time(maximum))
                self.min_value.setDateTime(get_time(minimum))
                self.min_value.setCalendarPopup(True)
                _ = self.min_value.dateTimeChanged.connect(self.on_datetime_change)
                build_layout(hbox_min, [min_value_label, self.min_value])

                hbox_max = QHBoxLayout()
                max_value_label = QLabel("Max")
                self.max_value = QDateTimeEdit()
                self.max_value.setMinimumDateTime(get_time(minimum))
                self.max_value.setMaximumDateTime(get_time(maximum))
                self.max_value.setDateTime(get_time(maximum))
                self.max_value.setCalendarPopup(True)
                _ = self.max_value.dateTimeChanged.connect(self.on_datetime_change)
                build_layout(hbox_max, [max_value_label, self.max_value])

                self.filterstore = FilterStore(self.dtype, (minimum, maximum))

                build_layout(
                    self._layout, [header_layout, hbox_min, hbox_max, delete_button]
                )
        self.setLayout(self._layout)
        self.update_label_style()

    def on_state_change(self):
        self.filterstore.active = self.active_checkbox.isChecked()
        self.debug(f"{self.filterstore} state toggled")
        self.update_label_style()

    def update_label_style(self):
        _ = self.column_label.setProperty("active", self.filterstore.active)
        self.column_label.style().unpolish(self.column_label)
        self.column_label.style().polish(self.column_label)

    def on_numeric_change(self):
        if isinstance(self.filter_widget, QLabeledDoubleRangeSlider):
            self.filterstore.filter_value = self.filter_widget.value()
            self.debug(self.filterstore.filter_value)
        else:
            self.debug("Wrong instance calling wrong function on_numeric_change")

    def on_categorical_change(self):
        if isinstance(self.filter_widget, MultiSelectComboBox):
            self.filterstore.filter_value = self.filter_widget.currentData()
            self.debug(self.filterstore.filter_value)
        else:
            self.debug("Wrong instance calling wrong function on_categorical_change")

    def on_datetime_change(self):
        try:
            self.filterstore.filter_value = (
                pd.to_datetime(self.min_value.dateTime().toPython()),  # pyright: ignore[reportCallIssue, reportUnknownMemberType, reportArgumentType]
                pd.to_datetime(self.max_value.dateTime().toPython()),  # pyright: ignore[reportCallIssue, reportUnknownMemberType, reportArgumentType]
            )
            self.debug(self.filterstore.filter_value)
        except AttributeError:
            self.debug("Wrong instance calling wrong function on_datetime_change")

    def onDelete(self):
        self.datastore.on_filter_widget_delete(self)
        _ = self.close()
