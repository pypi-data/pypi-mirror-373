# pyright: reportUninitializedInstanceVariable=false, reportUnknownMemberType=false, reportMissingTypeStubs=false

import ctypes
import sys
import threading
import typing
from functools import partial
from pathlib import Path
from typing import final

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QDragEnterEvent, QDropEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from qframelesswindow import FramelessMainWindow

from .data.datamodel import DataModel, FilterGUI, NumCatGUI
from .data.importexportGUI import DataImporter, export_data
from .data.tableGUI import TableViewer
from .guihelper import (
    CustomTitleBar,
    build_grid_layout,
    build_layout,
    get_label_widget_row,
)

if typing.TYPE_CHECKING:
    from .dataexplorer import DataExplorer


@final
class DataExplorerGUI(FramelessMainWindow):
    pages: list[QWidget] = []

    def __init__(self, dataexplorer: "DataExplorer"):
        super().__init__()

        self.dataexplorer: DataExplorer = dataexplorer
        self.config = self.dataexplorer.config
        self.debug = self.dataexplorer.debug
        self.error = self.dataexplorer.error
        window_dimensions: list[int] = self.config["General"]["window_dimensions"]

        self.data: dict[str, pd.DataFrame] = {}
        self.clear_message_timeout = None
        self.setWindowTitle("Data Explorer")
        title_bar = CustomTitleBar(self)
        self.setTitle = title_bar.changeTitle
        self.setTitleBar(title_bar)
        self.setMenuWidget(self.titleBar)  # pyright: ignore[reportUnknownArgumentType]
        self.debug(sys.platform)
        if sys.platform == "win32":
            (
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "Data.Explorer"
                )
            )
        self.setWindowIcon(QIcon(self.dataexplorer.icon_path))

        self.setGeometry(100, 100, *window_dimensions)  # x, y, width, height

        self.current_theme = self.config["General"]["default_theme"].casefold()
        self.current_theme_index = self._get_current_theme_index()
        self.debug(self.current_theme)

        self.central_widget = self.dataexplorer.get_widget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(
            0, 0, 0, 0
        )  # No margins for the main layout
        self.main_layout.setSpacing(0)  # No spacing between sidebar and content
        statusbar = self.statusBar()
        if not statusbar:
            self.debug("Unable to load status bar!")
        else:
            self.QStatusBar: QStatusBar = statusbar

        self.content_area_container = QFrame()
        self.content_area_container.setObjectName("ContentArea")
        self.content_layout = QVBoxLayout(self.content_area_container)

        self._generate_pages()
        self._generate_sidebar()

        # Add sidebar and content area to the main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area_container, 1)

        self.set_theme()
        self.write_to_status_bar("Initialisation complete!")

    def _generate_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")  # For QSS styling
        self.sidebar.setFixedWidth(240)  # Adjust width as needed
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(5)  # Spacing between sidebar items
        self.sidebar_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )

        idx: int = 0

        # Navigation Buttons
        self.nav_button1 = QPushButton("Manage Data")
        self.nav_button1.setCheckable(True)  # Allows it to stay "pressed"
        self.nav_button1.setChecked(True)  # Default selected
        f = partial(self.switch_content_page, index=idx)
        _ = self.nav_button1.clicked.connect(f)
        idx += 1

        self.nav_button2 = QPushButton("Filter Data")
        self.nav_button2.setCheckable(True)
        f = partial(self.switch_content_page, index=idx)
        _ = self.nav_button2.clicked.connect(f)
        idx += 1

        self.nav_button3 = QPushButton("Convert Numeric to Categorical")
        self.nav_button3.setCheckable(True)
        f = partial(self.switch_content_page, index=idx)
        _ = self.nav_button3.clicked.connect(f)
        idx += 1

        self.nav_button4 = QPushButton("Plot Data")
        self.nav_button4.setCheckable(True)
        f = partial(self.switch_content_page, index=idx)
        _ = self.nav_button4.clicked.connect(f)
        idx += 1

        self.nav_button5 = QPushButton("Plot Settings")
        self.nav_button5.setCheckable(True)
        f = partial(self.switch_content_page, index=idx)
        _ = self.nav_button5.clicked.connect(f)
        idx += 1

        self.nav_button6 = QPushButton("App Settings")
        self.nav_button6.setCheckable(True)
        f = partial(self.switch_content_page, index=idx)
        _ = self.nav_button6.clicked.connect(f)
        idx += 1

        self.sidebar_nav_buttons = [
            self.nav_button1,
            self.nav_button2,
            self.nav_button3,
            self.nav_button4,
            self.nav_button5,
            self.nav_button6,
        ]

        for btn_name in self.plugin_button_names:
            btn = QPushButton(btn_name)
            btn.setCheckable(True)
            f = partial(self.switch_content_page, index=idx)
            _ = btn.clicked.connect(f)
            self.sidebar_nav_buttons.append(btn)
            idx = idx + 1
            self.debug(btn)

        build_layout(self.sidebar_layout, self.sidebar_nav_buttons)

        # Spacer to push nav items to the top
        self.sidebar_layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

    def _generate_pages(self):
        # Page 1: Data Import/Export/View
        self.pages.append(self._manage_data_page())

        # Page 2: Filtering
        self.pages.append(self._filter_data_page())

        # Page 3: Numeric -> Categorical
        self.pages.append(self._num_to_cat_page())

        # Page 4: Plotting
        self.pages.append(self._plotting_page())

        # Page 5: Plot Settings
        self.pages.append(self.plot_settings_page())

        # Page 6: App Settings
        self.pages.append(self.app_settings_page())

        self.pages.extend(self.load_plugin_pages())

        # Add initial page to content layout
        for page_widget in self.pages:
            self.content_layout.addWidget(page_widget)
            page_widget.setVisible(False)

        # Show the first page
        if self.pages:
            self.pages[0].setVisible(True)
            self.current_page_index = 0

    def _manage_data_page(self) -> QWidget:
        manage_data_page = self.dataexplorer.get_widget()
        manage_data_page_layout = QVBoxLayout(manage_data_page)
        manage_data_page.setObjectName("ContentArea")

        top_spacer = QSpacerItem(
            10, 30, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )

        import_button = QPushButton("Import Data from File")
        _ = import_button.clicked.connect(self._on_import_data_from_file)

        mid_spacer = QSpacerItem(
            10, 10, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )

        active_dataset_label = QLabel("Set Active Dataset")
        active_dataset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        mid_spacer_2 = QSpacerItem(
            10, 10, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )

        self.active_dataset_combobox = QComboBox()
        self.active_dataset_combobox.setEditable(True)

        le = self.active_dataset_combobox.lineEdit()
        if le is None:
            self.debug("Unable to get lineEdit property of QComboBox.")
        else:
            le.setAlignment(Qt.AlignmentFlag.AlignCenter)
            le.setReadOnly(True)
        _ = self.active_dataset_combobox.currentTextChanged.connect(
            self.set_active_dataset
        )

        mid_spacer_3 = QSpacerItem(
            10, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.filter_viewexport_checkbox = QCheckBox(
            "Apply filter for exporting/viewing"
        )
        self.filter_viewexport_checkbox.setChecked(True)

        export_data_button = QPushButton("Export Dataset")
        _ = export_data_button.clicked.connect(self._export_data)

        bottom_spacer = QSpacerItem(
            10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        view_data_button = QPushButton("View Dataset")
        _ = view_data_button.clicked.connect(self._view_data)

        view_data_statistics_button = QPushButton("View Data Statistics")
        _ = view_data_statistics_button.clicked.connect(self._view_data_statistics)
        widg_list = [
            top_spacer,
            import_button,
            mid_spacer,
            active_dataset_label,
            mid_spacer_2,
            self.active_dataset_combobox,
            mid_spacer_3,
            self.filter_viewexport_checkbox,
            export_data_button,
            bottom_spacer,
            view_data_button,
            bottom_spacer,
            view_data_statistics_button,
        ]

        build_layout(manage_data_page_layout, widg_list)
        manage_data_page_layout.addStretch()
        manage_data_page.setAcceptDrops(True)
        manage_data_page.dragEnterEvent = self.manage_data_dragEnterEvent
        manage_data_page.dropEvent = self.manage_data_dropEvent
        return manage_data_page

    def manage_data_dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def manage_data_dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            event.accept()
            if Path(file_path).exists():
                self._importer = DataImporter(self.dataexplorer, file_path)
            else:
                self.error("That file did not work! It does not exist.")
        else:
            event.ignore()

    def _view_data(self):
        datamodel: DataModel = self.dataexplorer.datamodel
        if self.filter_viewexport_checkbox.isChecked():
            active = datamodel.active_filtered_data
        else:
            active = datamodel.active_cleaned_data
        if active is None:
            self.write_to_status_bar("No Active Data to view")
        else:
            self.table_viewer = TableViewer(self.dataexplorer, active, datamodel.active)

    def _view_data_statistics(self):
        datamodel: DataModel = self.dataexplorer.datamodel
        if self.filter_viewexport_checkbox.isChecked():
            active = datamodel.active_filtered_data
        else:
            active = datamodel.active_cleaned_data
        if active is None:
            self.write_to_status_bar("No Active Data to view")
        else:
            active = active.describe(include="all")
            self.table_viewer = TableViewer(
                self.dataexplorer, active, f"{datamodel.active} Statistics"
            )

    def _on_import_data_from_file(self):
        self._importer = DataImporter(self.dataexplorer)

    def set_active_dataset(self):
        self.dataexplorer.datamodel.set_active_dataset(
            self.active_dataset_combobox.currentText()
        )
        for dataset in self.filter_pages:
            self.filter_pages[dataset].setVisible(False)
            self.num_to_cat_pages[dataset].setVisible(False)
        self.filter_pages[self.dataexplorer.datamodel.active].setVisible(True)
        self.num_to_cat_pages[self.dataexplorer.datamodel.active].setVisible(True)
        self.setTitle(f"Current dataset: {self.dataexplorer.datamodel.active}")
        self.debug("Active dataset changed to: " + self.dataexplorer.datamodel.active)

    def update_data_list(self, name: str):
        datalist: QComboBox = self.active_dataset_combobox
        datalist.addItem(name)

    def _export_data(self):
        datamodel: DataModel = self.dataexplorer.datamodel
        if self.filter_viewexport_checkbox.isChecked():
            active = datamodel.active_filtered_data
        else:
            active = datamodel.active_cleaned_data
        if active is None:
            self.write_to_status_bar("No Active Data to view")
        else:
            export_data(self.dataexplorer, active)

    def _filter_data_page(self) -> QFrame:
        filter_data_page = QFrame()
        self.filter_data_page_layout = QVBoxLayout(filter_data_page)
        self.filter_pages: dict[str, QWidget] = {}
        self.filter_pages["__empty__"] = QLabel("No active datasets to filter")
        self.filter_data_page_layout.addWidget(self.filter_pages["__empty__"])
        return filter_data_page

    def add_filter_GUI_to_page(self, filterGUI: FilterGUI, name: str):
        self.filter_data_page_layout.addWidget(filterGUI.filter_page)
        filterGUI.filter_page.setObjectName("ContentArea")
        self.filter_pages[name] = filterGUI.filter_page
        self.filter_pages[name].setVisible(False)

    def _num_to_cat_page(self) -> QFrame:
        num_to_cat_page = QFrame()
        self.num_to_cat_page_layout = QVBoxLayout(num_to_cat_page)
        self.num_to_cat_pages: dict[str, QWidget] = {}
        self.num_to_cat_pages["__empty__"] = QLabel("No active datasets")
        self.num_to_cat_page_layout.addWidget(self.num_to_cat_pages["__empty__"])
        return num_to_cat_page

    def add_num_cat_GUI_to_page(self, numCatGUI: NumCatGUI, name: str):
        self.num_to_cat_page_layout.addWidget(numCatGUI.num_to_cat_page)
        numCatGUI.num_to_cat_page.setObjectName("ContentArea")
        self.num_to_cat_pages[name] = numCatGUI.num_to_cat_page
        self.num_to_cat_pages[name].setVisible(False)

    def _plotting_page(self) -> QWidget:
        plotting_page = self.dataexplorer.get_widget()
        plotting_page.setObjectName("ContentArea")
        plotting_page_layout = QVBoxLayout(plotting_page)

        histogram_button = QPushButton("Histogram")
        _ = histogram_button.clicked.connect(
            lambda: self.dataexplorer.plotter.histogram_plotter()
        )

        scatter_plot_button = QPushButton("Scatter")
        _ = scatter_plot_button.clicked.connect(
            lambda: self.dataexplorer.plotter.scatterplot_plotter()
        )
        line_plot_button = QPushButton("Line")
        _ = line_plot_button.clicked.connect(
            lambda: self.dataexplorer.plotter.lineplot_plotter()
        )

        categorical_plot_button = QPushButton("Categorical")
        _ = categorical_plot_button.clicked.connect(
            lambda: self.dataexplorer.plotter.catplot_plotter()
        )
        count_plot_button = QPushButton("Categorical Count")
        _ = count_plot_button.clicked.connect(
            lambda: self.dataexplorer.plotter.countplot_plotter()
        )

        correl_matrix = QPushButton("Correlation Matrix")
        _ = correl_matrix.clicked.connect(
            lambda: self.dataexplorer.plotter.correlmatrix_plotter()
        )

        regression_plot_button = QPushButton("Linear Regression")
        _ = regression_plot_button.clicked.connect(
            lambda: self.dataexplorer.plotter.regression_plotter()
        )

        pair_grid_button = QPushButton("Pair Grid")
        _ = pair_grid_button.clicked.connect(
            lambda: self.dataexplorer.plotter.pair_grid_plotter()
        )

        build_grid_layout(
            plotting_page_layout,
            [
                [histogram_button, scatter_plot_button],
                [line_plot_button, categorical_plot_button],
                [count_plot_button, correl_matrix],
                [regression_plot_button, pair_grid_button],
            ],
        )

        plotting_page_layout.addStretch()

        return plotting_page

    def plot_settings_page(self) -> QWidget:
        plot_settings_page = self.dataexplorer.get_widget()
        plot_settings_page.setObjectName("ContentArea")
        self.plot_settings_layout = QVBoxLayout(plot_settings_page)
        return plot_settings_page

    def app_settings_page(self) -> QWidget:
        app_settings_page = self.dataexplorer.get_widget()
        app_settings_page.setObjectName("ContentArea")
        app_settings_layout = QVBoxLayout(app_settings_page)
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(self.config["Themes"].keys())
        self.theme_combobox.setCurrentIndex(self.current_theme_index)
        _ = self.theme_combobox.currentTextChanged.connect(self.set_theme)
        theme_combobox = get_label_widget_row("Theme", self.theme_combobox)
        build_layout(app_settings_layout, [theme_combobox])
        app_settings_layout.addStretch()
        return app_settings_page

    def write_to_status_bar(self, message: str):
        if self.clear_message_timeout is not None:
            self.clear_message_timeout.cancel()
        self.QStatusBar.showMessage(message)
        self.clear_message_timeout = threading.Timer(30, self.clear_status_bar)
        self.clear_message_timeout.start()

    def clear_status_bar(self):
        self.QStatusBar.clearMessage()
        self.clear_message_timeout = None

    def _get_current_theme_index(self) -> int:
        for i, theme_name in enumerate(self.config["Themes"].keys()):
            if self.current_theme.casefold() == theme_name.casefold():
                return i
        self.debug("Could not get current theme index!")
        return 0

    def set_theme(self):
        self.current_theme = self.theme_combobox.currentText()
        for theme_name in self.config["Themes"].keys():
            if self.current_theme.casefold() == theme_name.casefold():
                self.dataexplorer.stylesheet = self.config["Themes"][theme_name]
                self.debug(self.dataexplorer.stylesheet)
                self.setStyleSheet(self.dataexplorer.stylesheet)
                break

    def load_plugin_pages(self) -> list[QWidget]:
        plugin_loaders = self.dataexplorer.plugin_list
        self.plugin_button_names: list[str] = []
        plugin_widgets: list[QWidget] = []
        for plugin_loader in plugin_loaders:
            widg, btn_name = plugin_loader(self.dataexplorer)
            self.plugin_button_names.append(btn_name)
            plugin_widgets.append(widg)

        return plugin_widgets

    def switch_content_page(self, index: int):
        self.debug(f"Switch to page {index}")
        if 0 <= index < len(self.pages):
            self.pages[self.current_page_index].setVisible(False)
            self.sidebar_nav_buttons[self.current_page_index].setChecked(False)
            self.pages[index].setVisible(True)
            self.sidebar_nav_buttons[index].setChecked(True)
            self.current_page_index = index

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        if self.clear_message_timeout is not None:
            self.clear_message_timeout.cancel()
        self.dataexplorer.closeEvent()
        return super().closeEvent(event)

    def _not_implemented(self):
        _ = QMessageBox.warning(
            self, "Not Implemented", "This functionality has not yet been implemented."
        )

    def error_msg(self, message: str):
        _ = QMessageBox.warning(self, "Error", message)
