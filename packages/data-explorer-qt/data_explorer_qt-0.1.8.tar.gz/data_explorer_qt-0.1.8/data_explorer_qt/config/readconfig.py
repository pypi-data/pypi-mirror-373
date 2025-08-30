from pathlib import Path
from typing import Any, List
import re

import toml

STARTING_PATH = Path(__file__)
CONFIG_PATH = STARTING_PATH.parent / "config.toml"

FONT_SIZE_REGEX = r"(font-size: )(\d*)"
FONT_WEIGHT_REGEX = r"(font-weight: )(\d*)"


def get_config() -> dict[str, Any]:
    config = toml.load(CONFIG_PATH)
    config = construct_stylesheets(config)
    config = replace_fonts(config)
    config = scale_fonts(config)
    return config


def construct_stylesheets(config: dict[str, Any]) -> dict[str, Any]:
    for key in config["Themes"]:
        assert isinstance(key, str)
        config["Themes"][key] = _theme_constructor(config["Themes"][key])
    return config


def _theme_constructor(theme_input: dict[str, str] | str) -> str:
    if isinstance(theme_input, dict):
        return "\n".join([_theme_constructor(theme_input[key]) for key in theme_input])
    else:
        return theme_input


def get_list_of_themes(config: dict[str, Any]):
    return list(config["Themes"].keys())


def replace_fonts(config: dict[str, Any]) -> dict[str, Any]:
    for key in config["Themes"]:
        stylesheet = config["Themes"][key]
        assert isinstance(stylesheet, str)
        stylesheet = stylesheet.replace("__UI_FONT__", config["General"]["ui_font"])
        stylesheet = stylesheet.replace(
            "__MONOSPACE_FONT__", config["General"]["monospace_font"]
        )
        config["Themes"][key] = stylesheet
    return config


def scale_fonts(config: dict[str, Any]) -> dict[str, Any]:
    font_size = re.compile(FONT_SIZE_REGEX)
    font_weight = re.compile(FONT_WEIGHT_REGEX)
    for key in config["Themes"]:
        stylesheet = config["Themes"][key]
        assert isinstance(stylesheet, str)
        font_sizes = unique(font_size.findall(stylesheet))
        font_weights = unique(font_weight.findall(stylesheet))
        for label, size in font_sizes:
            new_size = str(int(int(size) * config["General"]["font_scale"]))
            stylesheet = stylesheet.replace(label + size, label + new_size)
        for label, weight in font_weights:
            new_weight = str(int(int(weight) * config["General"]["font_weight_scale"]))
            stylesheet = stylesheet.replace(label + weight, label + new_weight)
        config["Themes"][key] = stylesheet
    return config


def unique(list_: List) -> List:
    unique_list = []
    for item in list_:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list


CONFIG = get_config()
CONFIG_STYLESHEET = CONFIG["Themes"]["Light"]
