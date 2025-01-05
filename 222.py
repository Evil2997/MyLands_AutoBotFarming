import numpy as np
import cv2
import pyautogui as pg


def get_unique_colors(image):
    unique_colors = set()
    for row in image:
        for pixel in row:
            unique_colors.add(tuple(pixel))  # Преобразуем массив цвета в кортеж для использования в set
    return list(unique_colors)


def find_color_in_image(image, target_color):
    return np.all(image == target_color, axis=-1)  # Возвращает маску, где цвета совпадают


def match_template(screenshot, template):
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_val, max_loc


def analyze_image(template_image_path, screen_region=(0, 0, 1920, 1080), tolerance=0):
    """
    Анализирует изображение на экране и ищет совпадения с заданным шаблоном.

    Args:
        template_image_path: Путь к шаблону, который нужно найти на экране.
        screen_region: Координаты области экрана для анализа (по умолчанию весь экран).
        tolerance: Допустимое отклонение в цвете (для этого алгоритма = 0).

    Returns:
        Позиция на экране и вероятность совпадения шаблона.
    """
    screenshot = np.array(pg.screenshot(region=screen_region))
    template = cv2.imread(template_image_path)

    # Шаг 1: Извлечение уникальных цветов
    unique_colors = get_unique_colors(template)

    # Шаг 2: Поиск совпадений по цветам
    for color in unique_colors:
        mask = find_color_in_image(screenshot, color)

    # Шаг 3: Поиск шаблона на изображении
    max_val, max_loc = match_template(screenshot, template)

    if max_val > 0.9:  # Порог точности
        print(f"Высокая вероятность совпадения: {max_val} в позиции {max_loc}")

    return max_loc, max_val


# Пример использования
template_image_path = '111.png'  # Путь к файлу шаблона

position, confidence = analyze_image(template_image_path)

print(f"Позиция совпадения: {position}, вероятность: {confidence}")
