# pyright: reportUnknownMemberType=false
import pprint
import traceback
import typing
from dataclasses import dataclass
from itertools import product
from typing import Callable, Literal, override

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget
from qframelesswindow import FramelessWindow
from seaborn import FacetGrid, PairGrid

from ..data.base import NumericConversion
from ..guihelper import CustomTitleBar, MultiSelectComboBox, build_layout

if typing.TYPE_CHECKING:
    from ..data.datamodel import DataStore
    from ..dataexplorer import DataExplorer

FILTER_DISPLAY_STARTING_TEXT = "Filters: "

MARKERS = [
    " ",
    ".",
    ",",
    "o",
    "v",
    "^",
    "<",
    ">",
    "1",
    "2",
    "3",
    "4",
    "8",
    "s",
    "p",
    "P",
    "*",
    "h",
    "H",
    "+",
    "x",
    "X",
    "D",
    "d",
]

LINE_STYLES = ["-", "--", "-.", ":", "None"]

VIOLIN_INNER = ["box", "quart", "point", "stick"]

HIST_PLOT_STATISTICS = ["count", "frequency", "proportion", "percent", "density"]

HIST_MULTIPLE = ["layer", "dodge", "stack", "fill"]

COUNT_PLOT_STATISTICS = ["count", "proportion", "percent"]

CORREL_STATISTICS = ["pearson", "kendall", "spearman"]

COLOR_PALETTES = {
    "qualitative": [
        "tab10",
        "deep",
        "muted",
        "pastel",
        "bright",
        "dark",
        "colorblind",
        "tab20",
        "tab20b",
        "tab20c",
    ],
    "circular": ["hls", "husl"],
    "perceptually_uniform": [
        "rocket",
        "mako",
        "flare",
        "crest",
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "cividis",
    ],
    "diverging": ["vlag", "icefire", "coolwarm", "bwr", "seismic"],
}

PALETTE_TYPES = ["qualitative", "circular", "perceptually_uniform", "diverging"]

SORT_CATEGORIES = [
    "First Occurence",
    "Alphabetical",
]

REGRESSION_MIN_DEGREE = 1
REGRESSION_MAX_DEGREE = 4


@typing.final
@dataclass
class TickParams:
    axis: Literal["x", "y"]
    rotation: int
    grid_colour: str
    grid_alpha: float

    def to_kwargs(self) -> dict[str, int | str | float]:
        return {
            "axis": self.axis,
            "labelrotation": self.rotation,
            "grid_color": self.grid_colour,
            "grid_alpha": self.grid_alpha,
        }


@typing.final
class EmbeddedDynamicPlot(QWidget):
    filter_display: QTextEdit
    plot: QWidget
    figure: Figure

    def __init__(
        self,
        dataexplorer: "DataExplorer",
        datastore: "DataStore",
        name: str,
        parent: "PlottingDialog",
    ):
        super().__init__()
        self.setWindowTitle(name)
        self.debug = dataexplorer.debug
        self.error = dataexplorer.error
        self.dataexplorer = dataexplorer
        self._parent = parent
        self.name = name
        self.resize(1200, 1200)
        self.setObjectName("DynamicPlot")
        self.setStyleSheet(dataexplorer.stylesheet)
        self.datastore = datastore
        self.filter_display = QTextEdit()
        self.filter_display.setReadOnly(True)
        self.filter_display.setText(self._generate_filter_text())
        self.dataexplorer.owned_widgets.append(self)
        self.setWindowIcon(QIcon(self.dataexplorer.icon_path))

        self.plot_subwidget = self.dataexplorer.get_widget()
        self.figure = plt.figure()
        self.plot = FigureCanvas(plt.figure())

        self.plot_toolbar: QWidget = NavigationToolbar2QT(self.plot)

        self.plot_vbox = QVBoxLayout(self.plot_subwidget)

        build_layout(self.plot_vbox, [self.plot_toolbar, self.plot])

        self._layout = QHBoxLayout(self)
        build_layout(self._layout, [(self.plot_subwidget, 1), self.filter_display])

        self.show()

    def update_dynamic_widget(self, plot: Figure | FacetGrid):
        self._draw_plot(plot)
        self.filter_display.setText(self._generate_filter_text())

    def _draw_plot(self, plot: Figure | FacetGrid):
        old_plot = self.plot
        old_toolbar = self.plot_toolbar
        old_figure = self.figure
        old_plot_subwidget = self.plot_subwidget
        if isinstance(plot, Figure):
            self.figure = plot
        else:
            self.figure = plot.figure

        plt.close(old_figure)
        old_plot.close()
        old_toolbar.close()
        self.plot = FigureCanvas(self.figure)
        self.plot_toolbar = NavigationToolbar2QT(self.plot)

        self.plot_subwidget = self.dataexplorer.get_widget()
        self.plot_vbox = QVBoxLayout(self.plot_subwidget)
        build_layout(self.plot_vbox, [self.plot_toolbar, self.plot])
        _ = self._layout.replaceWidget(old_plot_subwidget, self.plot_subwidget)
        old_plot_subwidget.close()
        self.update()
        self.debug(f"{self.name} updated!")

    def _generate_filter_text(self) -> str:
        filter_text = FILTER_DISPLAY_STARTING_TEXT
        for column in self.datastore.filters:
            filter_text += f"<br>- {column}"  # Newline + bullet list start
            for fs in self.datastore.filters[column]:
                if fs.active:
                    filter_text += pprint.pformat(fs.filter_value)
        return filter_text

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        self.dataexplorer.owned_widgets.remove(self)
        self._parent.delete_dynamic_plot()
        return super().closeEvent(event)


class PlottingDialog(FramelessWindow):
    dynamic_plot_widget: EmbeddedDynamicPlot | None = None
    dynamic_callback_id: int = -1
    plotting_data: pd.DataFrame
    palette_type: Literal[*PALETTE_TYPES] = PALETTE_TYPES[0]  # pyright: ignore

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore", name: str):
        super().__init__()
        self.setWindowTitle(f"{name} Plotting Dialog")
        cust_title = CustomTitleBar(self)
        self.setTitleBar(cust_title)
        self.setObjectName("StandardWidget")
        cust_title.changeTitle(f"{name} Plotting Dialog")
        self.dataexplorer: "DataExplorer" = dataexplorer
        self.debug: Callable[[str], None] = dataexplorer.debug
        self.error: Callable[[str], None] = dataexplorer.error
        self.datastore: "DataStore" = datastore
        self.setWindowIcon(QIcon(self.dataexplorer.icon_path))

        self._generate_plotting_data()
        self.dataexplorer.owned_widgets.append(self)
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self.setStyleSheet(dataexplorer.stylesheet)
        self.resize(600, 800)

    def setup_column_combobox(self, mandatory: bool, multi_variable: bool = False):
        if multi_variable:
            box = MultiSelectComboBox()
        else:
            box = QComboBox()
            box.setSizeAdjustPolicy(
                QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
            )
        if mandatory:
            box.addItems(self.datastore.columns)
        else:
            box.addItem("")
            box.addItems(self.datastore.columns)
        return box

    def cat_name(self, col_name: str):
        return col_name + "_categorical_"

    def _generate_plotting_data(self):
        self.plotting_data = self.datastore.filtered_data.copy()
        cat_name = self.cat_name

        for column, nc in self.datastore.numeric_to_categorical.items():
            self.debug(f"{column} {nc.conversion} {nc.value}")
            match nc.conversion:
                case NumericConversion.AS_CATEGORY:
                    self.plotting_data[cat_name(column)] = self.plotting_data[column]
                case NumericConversion.BINNED:
                    if not isinstance(nc.value, int):
                        self.error("Incorrect type for numeric->categorical bin_N")
                        return
                    self.plotting_data[cat_name(column)] = pd.cut(
                        self.plotting_data[column], nc.value
                    )
                case NumericConversion.BIN_WIDTH:
                    if not isinstance(nc.value, list):
                        self.error("Incorrect type for numeric->categorical bin edges")
                        return
                    self.plotting_data[cat_name(column)] = pd.cut(
                        self.plotting_data[column], nc.value
                    )

    def get_categorical_column_name(self, col_name: str):
        if col_name == "":
            return None
        else:
            cat_name = self.cat_name(col_name)
            if cat_name in self.plotting_data.columns:
                return cat_name
            else:
                return col_name

    def get_category_order(self, col_name: str | None):
        if col_name is None or col_name.endswith("_categorical_"):
            return None
        match self.dataexplorer.plotter.sort_category_by:
            case "First Occurence":
                return None
            case "Alphabetical":
                return sorted(self.plotting_data[col_name].unique())

    def get_palette(self):
        match self.palette_type:
            case "qualitative":
                return self.dataexplorer.plotter.qualitative_palette
            case "circular":
                return self.dataexplorer.plotter.circular_palette
            case "perceptually_uniform":
                return self.dataexplorer.plotter.perceptually_uniform_palette
            case "diverging":
                return self.dataexplorer.plotter.diverging_palette

    def on_plot(self):
        self._generate_plotting_data()

    def plotter(self) -> Figure | FacetGrid | PairGrid: ...

    def plot(self):
        self.on_plot()
        try:
            fig_or_fg = self.plotter()
            if isinstance(fig_or_fg, Figure):
                fig_or_fg.show()
            else:
                fig_or_fg.figure.show()
        except TimeoutError:
            self.error("Plot took too long. Check your variables")
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())

    def dynamic_plot(self): ...

    def redraw_dynamic_plot(self): ...

    def delete_dynamic_plot(self):
        self.debug("Dynamic Plot Widget Deleted")
        self.dynamic_plot_widget = None
        self.datastore.remove_filter_change_callback(self.dynamic_callback_id)
        self.dynamic_callback_id = -1

    def on_widget_change(self):
        if self.dynamic_plot_widget is not None:
            self.redraw_dynamic_plot()

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        self.dataexplorer.owned_widgets.remove(self)
        return super().closeEvent(event)


def get_dataframe_X_for_degree(
    df: pd.DataFrame, degree: int
) -> tuple[pd.DataFrame, list[str]]:
    generated_columns = []
    columns = list(df.columns)
    for deg in range(2, degree + 1):  # 2, 3, 4, ...
        cols_this_iter = []
        new_cols_this_iter = []
        for col in columns:
            new_col_name = f"{col}^{deg}"
            assert new_col_name not in columns
            cols_this_iter.append(col)
            new_cols_this_iter.append(new_col_name)
        df[new_cols_this_iter] = df[cols_this_iter] ** deg
        generated_columns.extend(new_cols_this_iter)
    return (df, generated_columns)


def get_dataframe_X_with_interaction(
    df: pd.DataFrame, generated_columns: list[str]
) -> pd.DataFrame:
    columns = set(df.columns) - set(generated_columns)
    generated_columns = []
    for col_A, col_B in product(columns, columns):
        if col_A != col_B:
            new_col_name = f"{col_A}*{col_B}"
            if new_col_name in generated_columns:
                continue
            assert new_col_name not in columns
            df[new_col_name] = df[col_A] * df[col_B]
            generated_columns.extend([new_col_name, f"{col_B}*{col_A}"])

    return df
