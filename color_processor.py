import numpy as np
from PIL import Image, ImageGrab
from colorsys import rgb_to_hsv, hsv_to_rgb
from collections import defaultdict
import pyautogui
import config
import utils


class ColorProcessor:
    def __init__(self):
        self.last_color = None
        self.setup_screen_capture()

    def setup_screen_capture(self):
        """Настройка захвата экрана"""
        screen_width, screen_height = pyautogui.size()
        self.screen_region = (0, 0, screen_width, screen_height)

    async def get_dominant_color(self):
        """Доминирующий цвет на экрана"""
        try:
            screenshot = ImageGrab.grab(bbox=self.screen_region)
            small_img = screenshot.resize(
                (
                    screenshot.width // config.DOWNSCALE_FACTOR,
                    screenshot.height // config.DOWNSCALE_FACTOR,
                ),
                Image.Resampling.LANCZOS,
            )

            pixels = np.array(small_img).reshape(-1, 3)
            filtered_pixels = [
                tuple(pixel) for pixel in pixels if utils.is_color_allowed(pixel)
            ]

            if not filtered_pixels:
                return (0, 0, 0)

            pixels_per_color = defaultdict(list)
            pixels_per_color_count = defaultdict(int)
            dominant_hue = (0, 0)  # (count, hue)
            for pixel in filtered_pixels:
                h, s, v = rgb_to_hsv(pixel[0] / 255, pixel[1] / 255, pixel[2] / 255)
                h = round(h, 2)
                pixels_per_color[h].append((s, v))
                pixels_per_color_count[h] += 1
                temp_count = pixels_per_color_count[h]
                if dominant_hue[0] < temp_count:
                    dominant_hue = (temp_count, h)

            target_list = pixels_per_color[dominant_hue[1]]
            if target_list:
                median_sv = np.median(target_list, axis=0)
                h = dominant_hue[1]
                s = float(median_sv[0])
                v = float(median_sv[1])
                r, g, b = hsv_to_rgb(h, s, v)
                dominant_color = (int(r * 255), int(g * 255), int(b * 255))
            else:
                dominant_color = (0, 0, 0)

            dominant_color = self._enhance_color(dominant_color)
            return dominant_color

        except Exception as e:
            print(f"Ошибка при обработке цвета: {e}")
            return (128, 128, 128)

    def _enhance_color(self, color):
        """Улучшение цвета"""
        r, g, b = color
        return (r, g, b)
        # h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)
        # s = min(s * 1.0, 1.0)
        # v = min(v * 1.2, 1.0)
        # r, g, b = hsv_to_rgb(h, s, v)
        # return (int(r * 255), int(g * 255), int(b * 255))
