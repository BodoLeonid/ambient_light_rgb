import numpy as np
from PIL import Image, ImageGrab
from colorsys import hsv_to_rgb
import pyautogui
import config
from numba import jit, vectorize


# JIT компилируемая функция для быстрого расчёта HSV (vectorized)
@vectorize(nopython=True, cache=True)
def fast_hsv_vectorized(rgb_val):
    """Vectorized расчёт HSV через Numba - НЕ ИСПОЛЬЗУЕТСЯ, оставлена для справки"""
    return rgb_val


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
                Image.Resampling.NEAREST,
            )

            # Преобразуем в uint8
            pixels = np.array(small_img, dtype=np.uint8)

            # Если RGBA, берём только RGB
            if pixels.shape[2] == 4:
                pixels = pixels[:, :, :3]

            pixels_flat = pixels.reshape(-1, 3).astype(np.float32) / 255.0

            # Извлекаем R, G, B
            r, g, b = pixels_flat[:, 0], pixels_flat[:, 1], pixels_flat[:, 2]

            # Быстрый расчёт HSV (NumPy optimized)
            max_c = np.maximum(np.maximum(r, g), b)
            min_c = np.minimum(np.minimum(r, g), b)
            delta = max_c - min_c

            v = max_c

            with np.errstate(divide="ignore", invalid="ignore"):
                s = np.where(max_c > 0, delta / max_c, 0)

            h = np.zeros_like(v)
            mask_r = max_c == r
            mask_g = max_c == g
            mask_b = max_c == b

            with np.errstate(divide="ignore", invalid="ignore"):
                h = np.where(mask_r & (delta != 0), ((g - b) / delta) % 6, h)
                h = np.where(mask_g & (delta != 0), (b - r) / delta + 2, h)
                h = np.where(mask_b & (delta != 0), (r - g) / delta + 4, h)

            h = h / 6.0
            h = np.where(h < 0, h + 1, h)

            # Фильтруем пиксели
            valid_mask = (
                (v >= config.MIN_BRIGHTNESS)
                & (v <= config.MAX_BRIGHTNESS)
                & (s >= config.MIN_SATURATION)
            )

            if not np.any(valid_mask):
                return (0, 0, 0)

            h_valid = h[valid_mask]
            s_valid = s[valid_mask]
            v_valid = v[valid_mask]

            h_rounded = (h_valid * 36).astype(int)
            h_counts = np.bincount(h_rounded, minlength=36)
            dominant_h_idx = np.argmax(h_counts)
            dominant_h = dominant_h_idx / 36.0

            mask_dominant = h_rounded == dominant_h_idx
            mean_s = np.mean(s_valid[mask_dominant])
            mean_v = np.mean(v_valid[mask_dominant])

            r, g, b = hsv_to_rgb(dominant_h, mean_s, mean_v)
            dominant_color = (int(r * 255), int(g * 255), int(b * 255))

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
