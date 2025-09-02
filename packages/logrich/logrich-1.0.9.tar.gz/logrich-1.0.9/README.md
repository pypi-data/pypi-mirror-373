# Логгер

[Screenshot logger](https://disk.yandex.ru/i/JexFefETxnJavA)  
[Screenshot logger2](https://disk.yandex.ru/i/ubvT0kZbfS-Guw)

![Screenshot logger](wiki/logrich_screenshot.png?raw=True "Screenshot")
----
![Screenshot logger too](wiki/logrich_screenshot2.png?raw=True "Screenshot")

Уровень вывода исключений определяется в переменных окружения.
Цвета, ширины и шаблоны вывода также могут быть определены в окружении.

## Использование

смотри [тест](tests/test_1.py) 

```sh
LOGURU_DIAGNOSE=NO
LOGURU_DATETIME_SHOW=1

# условие работы логрича, int, default = 1
LGR_LOGRICH_ON=1
# наибольшая ширина плашки, int, default = 15
LGR_LEVEL_MAX_WITH=15
# наименьшая ширина плашки, int, default = 9
LGR_LEVEL_MIN_WITH=9
# доля ширины имени файла в общей ширине, int, default = 55
LGR_RATIO_FILE_NAME=55
# доля ширины основного сообщения в общей ширине, int, default = 100
LGR_RATIO_MESSAGE=100
# насколько нужно уменьшить разделитель - это прерывистая черта отделяющая
# вывод не помещающийся в одной строке с плашкой, int, default = 25
LGR_REDUCE_DEVIDER_LEN=25
# ширина консоли richlog, ее можно установить менее ширины консоли, int, default = COLUMNS
LGR_CONSOLE_WITH=COLUMNS
# точная ширина контента колонки с именем файла, int, default = 20
LGR_LEN_FILE_NAME_SECTION=20

# пример установки шаблона
LOG_LEVEL_START_TPL="[reverse i dark_orange] START  [/]"
# установить в пустоту, чтобы отключить только определенный вывод
LOG_LEVEL_DEBUG_TPL=''
```

## Запустить тест(ы):

```shell
pytest
# монитор тестов
ptw
```
