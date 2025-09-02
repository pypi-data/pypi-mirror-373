import os

import pytest
from rich.style import Style

from logrich import log
from logrich.app import console

obj = {
    "name": "Имя, фамилия " * 5,
    "slug": 759933327936,
    "slug1": 13,
    "slug2": 51,
    "slug-test": 198,
    "slug3": 951,
    "href": "http://0.0.0.0:8000/downloads/pf-pf4-2050596-e4b8eff7.xlsx",
    "digest": "e4b8eff72593c54e40a3f0dfa3aff156",
    "message": "File pf-pf4-2050596-e4b8eff7 created now",
    "score": 123456,
    "elapsed_time": "0.060 seconds",
    "version": "2.14.3",
    "access": "eyJ0XAiiJKV1QiLCJhbGciOiJIUzI1NiJ912.eyJ0btlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjUzNTUwMTY1LCJqdGkiOiJmNzFhYjg5OWE5MDY0Y2EwODgwMzY1NzQ1NjYwNzdjOSIsInVzZXJfaWQiOjF9.KES3fhmBTXy8AwDSJTseNsLFC3xSh1J_slndgmSwp08",
    "id": 1234561,
}


# @rich.repr.auto
# декоратор формирует __repr_rich__ на основе __init__ объекта
class Bird:
    def __init__(self, name, eats=None, fly=True, extinct=False):
        self.name = name
        self.eats = list(eats) if eats else []
        self.fly = fly
        self.extinct = extinct

    def __repr__(self):
        return f"Bird({self.name}, eats={self.eats!r}, fly={self.fly!r}, extinct={self.extinct!r})"


BIRDS = {
    "gull": Bird("gull", eats=["fish", "chips", "ice cream", "sausage rolls"]),
    "penguin": Bird("penguin", eats=["fish"], fly=False),
    "dodo": Bird("dodo", eats=["fruit"], fly=False, extinct=True),
}

temp_reason = "\033[38;5;196mВременно отключен, должен быть включен."

skip = False
# skip = True
skip_item = False
# skip_item = True
skipmark = pytest.mark.skipif(skip, reason=temp_reason)
skipmark_item = pytest.mark.skipif(skip_item, reason=temp_reason)


@skipmark
def test_one():
    log.trace("Сообщение уровня TRACE: 5")
    log.debug("Сообщение уровня DEBUG: 10")
    log.info("Сообщение уровня INFO: 20")
    log.success("Сообщение уровня SUCCESS: 25")
    log.warning("Сообщение уровня WARNING: 30")
    log.error("Сообщение уровня ERROR: 40; " * 10)
    log.fatal("Это катастрофа, парень шел к успеху, но не фартануло..:-(\nСообщение уровня CRITICAL: 50")
    log.debug(BIRDS, title="Объект птички")
    log.info(obj, title="Словарь")
    # return
    log.success("SUCCESS [#FF1493]SUCCESS[/] [#00FFFF]SUCCESS[/] " * 10)
    log.debug("=" * 70)

    title = "Это Спарта!!"
    console.rule(f"[green]{title}[/]", style=Style(color="magenta"))

    num_dict = {
        1: {2: {2: 111}, 3: {3: 111}},
        2: {3: {3: 111}},
        3: {2: {2: 111}, 3: {3: 111}},
    }
    log.debug(num_dict, title="неверно раскрашивает первые числа")
    num_dict = {
        1: {2: {2: "здесь будут стили"}, 3: {3: "здесь будут стили"}},
        2: {3: {3: "здесь будут стили"}},
        3: {2: {2: "здесь будут стили"}, 3: {3: "здесь будут стили"}},
    }
    log.debug(num_dict, title="неверно раскрашивает первые двойки")

    context = {"clientip": "192.168.0.1", "user": "fbloggs1"}  # noqa F841

    # logger.info("Protocol problem", extra=context)  # Standard logging
    # logger.bind(**context).info("Protocol problem")  # Loguru


def test_too():
    # TEST = log.level("TEST")
    # TST = "<red>TST"
    # TST = "TST"
    # TST = "[reverse gray70] TST      [/]"
    # TST = "[reverse yellow] TST      [/]"
    # log.level(TST, no=15)
    # log.level(TST, no=15, style="red")
    # log.log(TST, "Тестовый лог")
    # log.tst = lambda msg: log.log(TST, msg)
    log.test("Тестовый лог")
    log.start("Тестовый лог")
    log.pprint("Тестовый лог PPRINT")
    log.debug((1, 2))
    log.trace(os.get_terminal_size())
    # assert None, "--"
    log.debug(3, 4)
    log.trace()
    log.success("foo", "bar")
    log.trace(*["baz2", "bar"])
    log.success("foo", "bar", title="Заголовок сообщения")
    log.info("foo bar", title="Заголовок сообщения")
    log.debug("*8" * 10)
