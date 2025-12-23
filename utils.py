import math
from colorsys import rgb_to_hsv, hsv_to_rgb
import config


def rgb_to_hex(rgb):
    return f"{min(255, max(0, rgb[0])):02X}{min(255, max(0, rgb[1])):02X}{min(255, max(0, rgb[2])):02X}"


def color_distance(c1, c2):
    """Расстояние между двумя цветами в RGB"""
    return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)


def generate_color_transition(start_color, end_color, steps):
    """Генерация промежуточных цветов для плавного перехода"""
    if start_color is None:
        return [end_color]

    transitions = []
    for i in range(steps):
        ratio = i / (steps - 1)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        transitions.append((r, g, b))
    return transitions


def is_color_allowed(rgb):
    """Фильтр цветов"""
    r, g, b = rgb

    if r < 10 and g < 10 and b < 10:
        return False

    h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)
    return (
        config.MIN_BRIGHTNESS <= v <= config.MAX_BRIGHTNESS
        and s >= config.MIN_SATURATION
    )
