import numpy as np
from PIL import Image, ImageGrab
from colorsys import rgb_to_hsv, hsv_to_rgb
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
                return (128, 128, 128)  # Серый по умолчанию

            median_color = np.median(filtered_pixels, axis=0).astype(int)
            dominant_color = (
                int(median_color[0]),
                int(median_color[1]),
                int(median_color[2]),
            )

            # Коррекция цвета
            dominant_color = self._enhance_color(dominant_color)
            return dominant_color

        except Exception as e:
            print(f"Ошибка при обработке цвета: {e}")
            return (128, 128, 128)

    def _enhance_color(self, color):
        """Улучшение цвета"""
        r, g, b = color
        h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)
        s = min(s * 1.2, 1.0)
        v = min(v * 1.5, 1.0)
        r, g, b = hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
