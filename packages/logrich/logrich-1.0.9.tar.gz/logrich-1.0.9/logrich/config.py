import logging
import os
from collections import namedtuple
from collections.abc import Callable
from functools import lru_cache

from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.theme import Theme

__all__ = ["theme", "config_tpl", "config_main", "console", "console_dict"]


@lru_cache
def get_style(
    style: str,
    LOGRICH_DEFAULT_FORMAT: str | None = None,
) -> str:
    LOGRICH_DEFAULT_FORMAT = LOGRICH_DEFAULT_FORMAT or os.environ.get(
        "LOGRICH_DEFAULT_FORMAT", "[reverse color(245)] DEF    [/]"
    )
    resp = config_tpl.get(style, LOGRICH_DEFAULT_FORMAT.strip('"'))
    return resp


config_main = namedtuple(
    "config_main",
    # ширина всего вывода
    # ширина вывода имени файла
    (
        "LGR_LOGRICH_ON",
        "LGR_RATIO_FILE_NAME",
        "LGR_LEVEL_MIN_WITH",
        "LGR_LEVEL_MAX_WITH",
        "LGR_RATIO_MESSAGE",
        "LGR_CONSOLE_WITH",
        "LGR_REDUCE_DEVIDER_LEN",
        "LGR_LEN_FILE_NAME_SECTION",
    ),
)


@lru_cache
def get_main_config() -> config_main:
    """
    формирует объект с параметрами

    :return: Именованный кортеж с параметрами
    :rtype: config_main
    """

    def get_env_value(name: str, type_: Callable, default: int | str | bool) -> bool | str | int | None:
        try:
            val = type_(os.environ.get(name, default=default))
            return val
        except Exception as err:
            logging.warning(
                f"Ошибка в начальных параметрах: {err}\nБудет использовано значение по-умолчанию: {default}."
            )

    try:
        # in docker without tty
        LGR_CONSOLE_WITH = get_env_value("LGR_CONSOLE_WITH", int, os.get_terminal_size()[0])
    except OSError:
        LGR_CONSOLE_WITH = 100

    resp = config_main(
        # условие работы логрича
        LGR_LOGRICH_ON=get_env_value("LGR_LOGRICH_ON", int, True),
        # наибольшая ширина плашки
        LGR_LEVEL_MAX_WITH=get_env_value("LGR_LEVEL_MAX_WITH", int, 15),
        # наименьшая ширина плашки
        LGR_LEVEL_MIN_WITH=get_env_value("LGR_LEVEL_MIN_WITH", int, 9),
        # доля ширины имени файла в общей ширине
        LGR_RATIO_FILE_NAME=get_env_value("LGR_RATIO_FILE_NAME", int, 55),
        # доля ширины основного сообщения в общей ширине
        LGR_RATIO_MESSAGE=get_env_value("LGR_RATIO_MESSAGE", int, 100),
        # насколько нужно уменьшить разделитель - это прерывистая черта отделяющая
        # вывод не помещающийся в одной строке с плашкой
        LGR_REDUCE_DEVIDER_LEN=get_env_value("LGR_REDUCE_DEVIDER_LEN", int, 25),
        # ширина консоли richlog, ее можно установить менее ширины консоли
        LGR_CONSOLE_WITH=LGR_CONSOLE_WITH,
        # точная ширина контента колонки с именем файла
        LGR_LEN_FILE_NAME_SECTION=get_env_value("LGR_LEN_FILE_NAME_SECTION", int, 20),
    )

    return resp


config_tpl = dict(
    # https://rich.readthedocs.io/en/stable/appendix/colors.html
    # здесь значения по-умолчанию, для того, чтобы не загромождать
    # файл с переменными окружения
    LOG_LEVEL_ELAPCE_TPL="[reverse turquoise2] ELAPCE [/]",
    LOG_LEVEL_START_TPL="[reverse i aquamarine1] START  [/]",
    LOG_LEVEL_END_TPL="[reverse i green4] END    [/reverse i green4]",
    LOG_LEVEL_TEST_TPL="[reverse grey70] TEST   [/]",
    LOG_LEVEL_DATA_TPL="[reverse cornflower_blue] DATA   [/]",
    LOG_LEVEL_DEV_TPL="[reverse grey70] DEV    [/]",
    LOG_LEVEL_INFO_TPL="[reverse blue] INFO   [/]",
    LOG_LEVEL_TRACE_TPL="[reverse dodger_blue2] TRACE  [/]",
    LOG_LEVEL_RUN_TPL="[reverse yellow] RUN    [/]",
    LOG_LEVEL_GO_TPL="[reverse royal_blue1] GO     [/]",
    LOG_LEVEL_LIST_TPL="[reverse wheat4] LIST   [/]",
    LOG_LEVEL_DEBUG_TPL="[reverse #9f2844] DEBUG  [/]",
    LOG_LEVEL_SUCCESS_TPL="[reverse green] SUCCS  [/]",
    LOG_LEVEL_LOG_TPL="[reverse chartreuse4] LOG    [/]",
    LOG_LEVEL_TIME_TPL="[reverse spring_green4] TIME   [/]",
    LOG_LEVEL_WARN_TPL="[reverse yellow] WARN   [/]",
    LOG_LEVEL_WARNING_TPL="[reverse yellow] WARN   [/]",
    LOG_LEVEL_FATAL_TPL="[reverse bright_red] FATAL  [/]",
    LOG_LEVEL_ERR_TPL="[reverse #ff5252] ERR    [/]",
    LOG_LEVEL_ERROR_TPL="[reverse #ff5252] ERROR  [/]",
)

config_tpl.update(
    **os.environ,  # override loaded values with environment variables
)

color_of_digit = "bold magenta"

theme = Theme(
    # https://www.w3schools.com/colors/colors_picker.asp
    # https://htmlcolorcodes.com/color-names/
    # https://colorscheme.ru/
    {
        "repr.brace": "bold black",
        "repr.str": "green",
        "repr.attrib_name": "#0099ff",
        "repr.equal": "red dim",
        "repr.digit": color_of_digit,
        "repr.digit2": color_of_digit,
        "repr.colon": "#D2691E",
        "repr.quotes": "#778899",
        "repr.comma": "#778899",
        "repr.key": "#08e8de",
        "repr.bool_true": "bold blue",
        "repr.none": "blue",
        "repr.bool_false": "yellow",
        "repr.class_name": "magenta bold",
        "repr.string_list_tuple": "green",
        "trace_msg": "#05a7f7",
        "debug_msg": "#e64d00",
        "info_msg": "#33ccff",
        "success_msg": "green",
        "warning_msg": "yellow",
        "error_msg": "#ff5050",
        "critical_msg": "#de0b2e",
    },
)


def combine_regex(*regexes: str) -> str:
    """Combine a number of regexes in to a single regex.

    Returns:
        str: New regex with all regexes ORed together.
    """
    return "|".join(regexes)


class MyReprHighlighter(ReprHighlighter):
    """подсветка вывода на основе регул. выражений"""

    # https://regex101.com/r/zR2hP5/1
    base_style = "repr."
    highlights = [
        r"'(?P<str>[\S\s]*)'",
        r":\s\'(?P<value>.+)\'",
        r"['](?P<string_list_tuple>\w+)[']",
        r"(?P<digit2>\d*)[\"\s,[,(](?P<digit>\d*\.?\s?-?\d*-?\.?\d+)",
        combine_regex(
            r"(?P<brace>[][{}()])",  # noqa
            r"\'(?P<key>[\w-]+)\'(?P<colon>:)",
            r"(?P<comma>,)\s",
        ),
        r"(?P<quotes>\')",
        r"(?P<equal>=)",  # noqa
        r"(?P<class_name>[A-Z].*)\(",
        r'(?P<attrib_name>[\w_]{1,50})=(?P<attrib_value>"?[\w_]+"?)?',
        r"\b(?P<bool_true>True)\b|\b(?P<bool_false>False)\b|\b(?P<none>None)\b",
    ]


console = Console()

# инстанс консоли rich
console_dict = Console(
    highlighter=MyReprHighlighter(),
    theme=theme,
    markup=True,
    log_time=False,
    log_path=False,
    safe_box=True,
)
