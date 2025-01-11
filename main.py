import os
import random
import time
from typing import Tuple

import cv2
import numpy as np
import pyautogui as pg
import pytesseract.pytesseract

from Imports.tesseract import setup_tesseract
from core.gate.gate_status import GateStatus


def delay(a: float = 1, b: float = 2) -> float:
    return random.uniform(a, b)


def get_random_coordinate(region: Tuple[int, int, int, int]) -> Tuple[int, int]:
    x1, y1, x2, y2 = region
    random_x = random.randint(x1, x2)
    random_y = random.randint(y1, y2)
    return random_x, random_y


def real_click(region: Tuple[int, int, int, int]) -> None:
    x, y = get_random_coordinate(region)
    pg.moveTo(x, y, delay())
    time.sleep(delay())
    # pg.click(x, y)


def go_in_city(city_number: int) -> None:
    """
    Open the city list and go to the specified city.

    Args:
        city_number (int): Order number of the city (1 to 7).
    """
    real_click(city_menu)
    # ToDo Replace the loop if possible, remove .items()
    for city, cords in CITIES.items():
        if cords["city_number"] == city_number:
            real_click(cords["region"])
            break


def scan_area_and_extract_text(region: tuple[int, int, int, int]) -> str:
    screenshot = pg.screenshot(region=region)
    text = pytesseract.image_to_string(screenshot, config=config)
    return text


def check_is_free(region: tuple[int, int, int, int]) -> int:
    numbers_in_missions = scan_area_and_extract_text(region)
    x, y = map(int, numbers_in_missions.split('/'))
    return y - x


def scan_one_cell(
        region: tuple[int, int, int, int],
        missions: int,
        researchers: int,
        target_color: tuple[int] = (255, 255, 255),
        tolerance: int = 10,
        required_percentage: int = 90
) -> tuple[int, int]:
    """
        ToDo
            Найти значения для цвета, маски и процентного соотношения нужного цвета в одной клетке.
            Цвет текста (22-43 ячейки / Нельзя основать город)
        Сканирует одну клетку на экране и определяет, пустая она или занята.

    Args:
        region (Tuple[int, int, int, int]): Coordinates of the cell on the screen.
        missions (int): Number of available missions.
        researchers (int): Number of available researchers.
        target_color (Tuple[int, int, int]): Target color in RGB format.
        tolerance (int): Allowed deviation of the color.
        required_percentage (int): Percentage of the target color to consider the cell empty.

    Returns:
        Tuple[int, int]: Updated counts of missions and researchers.
    """
    screenshot = np.array(pg.screenshot(region=region))

    lower_bound = np.array([c - tolerance for c in target_color])
    upper_bound = np.array([c + tolerance for c in target_color])

    mask = cv2.inRange(screenshot, lower_bound, upper_bound)

    matching_percentage = (np.sum(mask) / 255) / mask.size * 100
    if matching_percentage >= required_percentage:
        send_explorer(region)
        missions -= 1
        researchers -= 1
    return missions, researchers


def scan_all_cells(city_number, start_x=384, start_y=164, cell_width=123, cell_height=84, grid_width=9, grid_height=7):
    """
        ToDo:
            Добавить проверку давности исследования клетки.
            Например если срок давности более 3-ех дней, отправить исследователя
            Иначе пропустить и идти дальше
        Проходит по всем клеткам поля размером 9x7 и выводит 111 внутри каждой клетки.
        1107 * 588  -- Размеры карты
        384, 164    -- Начальная точка (карта)
        123 * 84    -- Размеры 1 клетки
        Args:
            city_number (int): Первый город из которого начинаем отправлять исследователей
            start_x, start_y (int): Начальные координаты первой клетки (верхний левый угол).
            cell_width, cell_height (int): Ширина и высота каждой клетки в пикселях.
            grid_width, grid_height (int): Количество клеток по горизонтали и вертикали.
    """

    for row in range(grid_height):
        for col in range(grid_width):
            x1 = start_x + col * cell_width
            y1 = start_y + row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            pg.moveTo(x1 + cell_width / 2, y1 + cell_height / 2)  # клик четко по центру клетки
            time.sleep(0.2)
        #     missions, researchers = send_a_researchers(city_number, x1, y1, x2, y2)
        #
        #     if missions > 0 and researchers == 0:
        #         city_number += 1
        #         go_in_city(city_number)
        #     elif missions == 0:
        #         break
        # else:
        #     continue  # Выполняется только если внутренний цикл не был прерван
        # break


def send_explorer(region: tuple[int, int, int, int]):
    """
        Функция для отправки исследователя.
        Args:
            x1, y1, x2, y2 координаты клетки в которую нужно отправить исследователя
        ToDo: Примечания:
            Кликать нужно в случайные места конкретных целей:
                1. В центре клетки
                2. По кнопке действия отправки исследователя
                3. По кнопке отправки исследователя
    """
    # координаты для открытия панели действий
    # выбрать действие отправить исследователя
    # отправить исследователя
    print("Исследователь отправлен!")


def send_a_researchers(
        city_number: int,
        region: tuple[int, int, int, int]
)->tuple[int, int]:
    missions = check_is_free(MISSIONS)
    go_in_city(city_number)
    researchers = check_is_free(RESEARCHERS)

    missions, researchers = scan_one_cell(
        region=region,
        missions=missions,
        researchers=researchers,
    )
    # TODO: return координат заменить на отправку исследователей
    return missions, researchers


def check_gates(
        region: tuple[int, int, int, int],
        status_now: GateStatus.now,
        threshold: float=0.92
) -> tuple[int, int] | None:
    """
        status_now (str): "close" or "open"
        :return top_left (int, int)
    """
    NAMES = [i for i in os.listdir("Images/gates_status/") if i.startswith(status_now)]
    for name in NAMES:
        template_path = f"Images/gates_status/{name}"
        (x1, y1, x2, y2) = region
        screenshot = np.array(pg.screenshot(region=(x1, y1, x2 - x1, y2 - y1)))
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(f"Template image not found: {template_path}")

        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            top_left = (max_loc[0] + region[0], max_loc[1] + region[1])
            return top_left
    return None


def open_or_close_gates(
        find_gates:tuple[int, int],
) -> None:
    """
        Клик по найденным воротам на кусочке экрана
        Подтверждение действия (кнопка Да)
    """
    find_gates_region = (find_gates[0] - 10, find_gates[1] - 10, find_gates[0] + 10, find_gates[1] + 10)
    real_click(find_gates_region)
    real_click(gate_YES)


def all_gates_open_or_close(
        status_now: GateStatus.now
) -> None:
    """
    "Открыть" или "Закрыть" ворота во всех городах
    """
    for i in range(CITY_NUMERICS):
        go_in_city(CITIES[f"City_{i}"]['city_number'])
        find_gates = check_gates(
            region=gate_here,
            status_now=status_now,
        )
        if find_gates:
            open_or_close_gates(find_gates)


def main():
    print("Start Main\n")
    # scan_all_cells(1)

    # all_gates_open_or_close(status_now="close")
    # time.sleep(5*60)     # Ждем пока откроются все ворота
    # all_gates_open_or_close(status_now="open")

    print("\nEnd Main")


if __name__ == '__main__':
    MISSIONS = (429, 976, 464, 992)
    RESEARCHERS = (832, 664, 868, 681)
    CITY_NUMERICS = 7
    CITIES = {
        "City_0": {
            "city_number": 1,
            "region": (833, 219, 1037, 232),
        },

        "City_1": {
            "city_number": 2,
            "region": (833, 237, 1037, 252),
        },

        "City_2": {
            "city_number": 3,
            "region": (833, 261, 1037, 277),
        },

        "City_3": {
            "city_number": 4,
            "region": (833, 283, 1037, 297),
        },

        "City_4": {
            "city_number": 5,
            "region": (833, 306, 1037, 322),
        },

        "City_5": {
            "city_number": 6,
            "region": (833, 325, 1037, 344),
        },

        "City_6": {
            "city_number": 7,
            "region": (833, 347, 1037, 368),
        },

    }

    gate_YES = (841, 613, 926, 646)
    gate_here = (1227, 541, 1338, 636)
    city_menu = (820, 157, 1038, 213)

    setup_tesseract()
    config = r'--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789/'

    main()

# Перевезти ресурсы

# Автоматически нанять купцов и исследователей

# Нанять армию согласно ресурсам

# Отправить на клановый замок носильщиков

# При полной проверки клетки с карты мира, сделать переход на следующую клетку.
# Для начала можно просто вводить координаты для этой клетки.
