import decimal
import inspect
import logging
import re
from collections import deque
from collections.abc import Callable
from datetime import datetime
from functools import lru_cache
from types import FrameType
from typing import Any

from rich.console import Console
from rich.table import Table

from logrich.config import config_main, console, console_dict, get_main_config, get_style


@lru_cache
class Log:
    """Extension log, use in tests."""

    def __init__(
        self,
        config: config_main,
        **kwargs,
    ) -> None:
        self.deque: deque = deque()
        self.config = config
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def print(
        self,
        # вызов логгера без параметров выведет текущую дату
        *args,
        frame: FrameType | None = None,
        **kwargs,
    ) -> None:
        """Extension log."""

        if not self.config.LGR_LOGRICH_ON:
            return

        try:
            if args and len(args) == 1:
                msg = args[0]
            elif not args:
                msg = datetime.now().strftime("%H:%M:%S")
            else:
                msg = args

            if not (level := self.deque.pop()):
                return

            level_key = f"LOG_LEVEL_{level.upper()}_TPL"
            level_style = get_style(level_key)

            # если стиль определяется как пустая строка, то вывода не будет
            if not level_style:
                return

            # фрейм с исходными данными для вывода, иногда,
            # может быть передан на вход
            frame = frame or inspect.currentframe()

            if isinstance(frame, FrameType):
                frame = frame.f_back

            if not frame:
                logging.warning("Frame undefined")
                return

            len_file_name_section = self.config.LGR_LEN_FILE_NAME_SECTION
            file_name = kwargs.get("file_name", frame.f_code.co_filename)[-len_file_name_section:]
            line = kwargs.get("line", frame.f_lineno)
            divider = self.config.LGR_CONSOLE_WITH - len_file_name_section - self.config.LGR_REDUCE_DEVIDER_LEN
            title = kwargs.get("title", "-" * divider)

            if isinstance(msg, str | int | float | bool | type(decimal) | type(None)):
                self.print_tbl(
                    message=str(msg),
                    file=file_name,
                    line=line,
                    level=level,
                    level_style=level_style,
                )
            elif isinstance(msg, (dict | tuple | list)):
                # TODO add message for dict, tuple etc.
                self.print_tbl(
                    message=title,
                    file=file_name,
                    line=line,
                    level=level,
                    level_style=level_style,
                )
                self.format_extra_obj(message=msg)
            else:
                self.print_tbl(
                    message=msg,
                    file=file_name,
                    line=frame.f_lineno,
                    level=level,
                    level_style=level_style,
                )
        except Exception as err:
            logging.warning(err)

    def print_tbl(
        self,
        level_style: str,
        level: str,
        file: str,
        line: int,
        message: str = "",
    ) -> str:
        """Форматирует вывод логгера в табличном виде"""
        table = Table(
            highlight=True,
            show_header=False,
            padding=0,
            collapse_padding=True,
            show_footer=False,
            expand=True,
            box=None,
        )
        stamp = f"{level_style:<9}"
        # LEVEL
        table.add_column(
            justify="left",
            min_width=self.config.LGR_LEVEL_MIN_WITH,
            max_width=self.config.LGR_LEVEL_MAX_WITH,
        )
        try:
            style = getattr(self, f"{level}_style")
        except AttributeError:
            style = re.match(r"^\[(.*)].", level_style)
            style = style and style.group(1)
            if style:
                style = style.replace("reverse", "")
        # MESSAGE
        table.add_column(ratio=self.config.LGR_RATIO_MESSAGE, overflow="fold", style=style)
        # FILE
        table.add_column(justify="right", ratio=self.config.LGR_RATIO_FILE_NAME, overflow="fold")
        # LINE
        table.add_column(ratio=2, overflow="crop")  # для паддинга справа
        msg = f"{message}"
        file_info = f"[grey42]{file}...[/][red]{line}[/]"

        table.add_row(stamp, msg, file_info)

        with console.capture() as capture:
            console_dict.print(table, markup=True)
        return capture.get()

    def __getattr__(self, *args, **kwargs) -> Callable:
        """
        метод __getattr__ определяет поведение,
        когда наш атрибут, который мы пытаемся получить, не найден
        """
        name = args[0]
        if name.endswith(("style",)):
            return object.__getattribute__(self, name)
        self.deque.append(name)
        return self.print

    def print_message_for_table(self, message: Any) -> str:
        # инстанс консоли rich
        console_ = Console(
            no_color=True,
            markup=False,
            safe_box=True,
            highlight=False,
        )

        with console_.capture() as capture:
            console_.print(
                message,
                markup=False,
                width=self.config.LGR_CONSOLE_WITH,
            )
        return capture.get()

    def format_extra_obj(self, message: Any) -> None:
        """форматирует вывод исключений в цвете и в заданной ширине, исп-ся rich"""
        table = Table(
            padding=(0, 2),
            highlight=True,
            show_footer=False,
            box=None,
        )

        table.add_column()

        # MESSAGE
        table.add_row(self.print_message_for_table(message=message))

        console_dict.print(table, markup=True)


log = Log(config=get_main_config())
