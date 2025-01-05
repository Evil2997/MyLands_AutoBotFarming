import time

import cv2
import numpy as np
import pyautogui as pg


def scan_one_cell(region, TARGET_COLORS, missions=0, researchers=0):
    """
        Сканирует одну клетку на экране и определяет, пустая она или занята.

        Args:
            x1, y1, x2, y2 (int): Координаты области клетки на экране.

        Returns:
            missions (int): количество свободных миссий
            researchers (int): количество свободных исследователей в городе
    """
    (x1, y1, x2, y2) = region
    screenshot = np.array(pg.screenshot(region=(x1, y1, x2 - x1, y2 - y1)))

    tolerance = 10
    MATCH_PERCENTAGE = []
    for target_color in TARGET_COLORS:
        lower_bound = np.array([c - tolerance for c in target_color])
        upper_bound = np.array([c + tolerance for c in target_color])

        mask = cv2.inRange(screenshot, lower_bound, upper_bound)

        matching_percentage = (np.sum(mask) / 255) / mask.size * 100
        MATCH_PERCENTAGE.append(matching_percentage)
        if MATCH_PERCENTAGE.count(0) >= 3:
            "ЗАНЯТО"
            return True
    return False


# if matching_percentage >= required_percentage:
#     send_explorer(x1, y1, x2, y2)
#     missions -= 1
#     researchers -= 1
#     return missions, researchers
# else:
#     return missions, researchers

# TODO: Заменить одинаковые цвета на другие по названию клеток.
#       Еще раз проставить все цвета заново.

TARGET_COLORS = [
    (1, 96, 211),
    (157, 231, 255),
    (2, 167, 226),
    (116, 215, 248),
    (116, 215, 248),
    (116, 215, 248),
    (116, 214, 248),
    (3, 167, 227)
]

Constants_Maps = {

}

grid_height = 7
grid_width = 9
cell_width = 123
cell_height = 84
start_x = 384
start_y = 164
i = 1
a = []
time.sleep(2)
for row in range(grid_height):
    for col in range(grid_width):
        x1 = start_x + col * cell_width
        y1 = start_y + row * cell_height
        region = (x1, y1, x1 + cell_width, y1 + cell_height)
        res = scan_one_cell(region, TARGET_COLORS)
        if res:
            a.append(i)
        i += 1
print(a)
