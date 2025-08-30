# pyright: reportImportCycles=false, reportUnusedImport=false
import importlib
import logging
import os
import pprint
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, final

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication, QWidget
from qframelesswindow import FramelessWindow

from data_explorer_qt.guihelper import CustomTitleBar

from . import setqtapi  # noqa
from .config import CONFIG
from .data.datamodel import DataModel
from .dataexplorerGUI import DataExplorerGUI
from .plotter.plotter import Plotter


@final
class DataExplorer:
    stylesheet: str = ""
    config = CONFIG
    owned_widgets: list[QWidget] = []
    plugin_list: list[Callable[["DataExplorer"], tuple[QWidget, str]]] = []

    def __init__(self, app: QApplication, debug_mode: bool):
        self.app = app
        self.debug_mode = debug_mode
        self._setup_logging()
        self.icon_path = str(Path(__file__).parent / "resources" / "icon.ico")

        self.construct_plugin_list()

        self.load_custom_font()

        self.gui = DataExplorerGUI(self)
        self.info("GUI Initialised!")

        self.datamodel = DataModel(self)
        self.info("Data Model Initialised!")

        self.plotter = Plotter(self)
        self.info("Plotter Initialised")

    def _setup_logging(self):
        # Parent of this file is the upper directory
        # Parent of that is the upper directory
        log_folder = Path.home() / ".data-explorer-qt" / "Logs"

        log_folder.mkdir(parents=True, exist_ok=True)

        log_file_number = 1
        log_file_path = log_folder / "Log.log"
        while log_file_path.exists():
            log_file_path = log_folder / f"Log {log_file_number}.log"
            log_file_number += 1

        self._logger = logging.getLogger("DataExplorer")
        self._logger.propagate = False
        self._logger.setLevel(logging.DEBUG)

        log_format = logging.Formatter(self.config["Logger"]["log_format"])
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(log_format)
        file = logging.FileHandler(log_file_path)
        file.setFormatter(log_format)
        file.setLevel(logging.DEBUG)
        if self.debug_mode:
            console.setLevel(logging.DEBUG)
        else:
            console.setLevel(logging.INFO)
        self._logger.addHandler(console)
        self._logger.addHandler(file)
        self._logger.info("Logger Setup!")

    def debug(self, msg_or_object: str | Any):
        if isinstance(msg_or_object, str):
            self._logger.debug(msg_or_object)
        else:
            self._logger.debug(pprint.pformat(msg_or_object))

    def error(self, msg_or_object: str | Any):
        if isinstance(msg_or_object, str):
            self.gui.error_msg(msg_or_object)
            self._logger.error(msg_or_object)
        else:
            self._logger.error(pprint.pformat(msg_or_object))
            self.gui.error_msg(pprint.pformat(msg_or_object))

    def info(self, msg_or_object: str | Any):
        if isinstance(msg_or_object, str):
            self._logger.info(msg_or_object)
        else:
            self._logger.info(pprint.pformat(msg_or_object))

    def status_message(self, msg: str):
        self._logger.info(msg)
        self.gui.write_to_status_bar(msg)

    def construct_plugin_list(self):
        plugin_path: str = self.config["General"]["plugins"]
        if not Path(plugin_path).exists():
            self.debug("Plugin Path is invalid.")
            plugin_path_ = Path(__file__).parent.parent / "plugins"
            if not plugin_path_.exists():
                return
            else:
                self.info("Using default plugin path.")
                plugin_path = str(plugin_path_)
        self.debug(plugin_path)
        sys.path.insert(0, plugin_path)
        for filename in os.listdir(plugin_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename.split(".")[0]
                module_name = f"{module_name}"
                try:
                    module = importlib.import_module(module_name)
                    self.plugin_list.append(module.init_plugin)
                    self.info(f"Loaded {module_name}")
                except Exception as e:
                    self.debug(f"Plugin {module_name} not loaded")
                    self.debug(e)

    def load_custom_font(self):
        path_to_font = Path(__file__).parent / "resources" / "PTRootUI.ttf"
        if path_to_font.exists():
            path_to_font = str(path_to_font)
            font_id = QFontDatabase.addApplicationFont(path_to_font)
            if font_id != -1:
                self.debug(QFontDatabase.applicationFontFamilies(font_id)[0])
                self.debug("Loaded Custom Font")
        else:
            return

    def closeEvent(self):
        self.app.quit()

    def get_widget(self, detached: bool = False) -> QWidget:
        if detached:
            widget = FramelessWindow()
            cust_title = CustomTitleBar(widget)
            widget.setTitleBar(cust_title)
        else:
            widget = QWidget()
        widget.setWindowIcon(QIcon(self.icon_path))
        widget.setObjectName("StandardWidget")
        widget.setStyleSheet(self.stylesheet)
        return widget


def run():
    try:
        app = QApplication([])
        app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        argv = sys.argv
        _ = app.setStyle("Fusion")
        debug_mode = False
        if argv is None:
            argv = []
        if "--debug" in argv:
            debug_mode = True
        dataexplorer = DataExplorer(app, debug_mode)
        dataexplorer.gui.show()
        sys.exit(app.exec())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
