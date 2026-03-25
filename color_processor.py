import numpy as np
from PIL import Image, ImageGrab
from colorsys import hsv_to_rgb
import pyautogui
import config
from multiprocessing import Process, Queue
import queue
import time
import traceback


def process_color_worker(screenshot_queue, color_queue):
    """Рабочий процесс для обработки скриншотов"""
    print("[Worker] Запущен рабочий процесс")
    while True:
        try:
            # Получаем numpy array вместо PIL Image
            pixels_data = screenshot_queue.get(timeout=1)
            if pixels_data is None:
                print("[Worker] Получен сигнал выхода")
                break

            # pixels_data это уже обработанный и масштабированный массив
            pixels = pixels_data

            # Если RGBA, берём только RGB
            if pixels.shape[2] == 4:
                pixels = pixels[:, :, :3]

            pixels_flat = pixels.reshape(-1, 3).astype(np.float32) / 255.0
            r, g, b = pixels_flat[:, 0], pixels_flat[:, 1], pixels_flat[:, 2]

            # Быстрый расчёт HSV
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
                color_queue.put((0, 0, 0), block=False)
                continue

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

            color_queue.put(dominant_color, block=False)

        except queue.Empty:
            continue
        except Exception as e:
            print(f"[Worker] Ошибка в рабочем процессе: {e}")
            print(f"[Worker] Traceback: {traceback.format_exc()}")


class ColorProcessor:
    def __init__(self):
        self.last_color = None
        self.setup_screen_capture()

        # Инициализируем multiprocessing queues
        self.screenshot_queue = Queue(maxsize=2)
        self.color_queue = Queue(maxsize=2)

        # Запускаем рабочий процесс
        self.worker_process = Process(
            target=process_color_worker,
            args=(self.screenshot_queue, self.color_queue),
            daemon=True,
        )
        self.worker_process.start()

    def setup_screen_capture(self):
        """Настройка захвата экрана"""
        screen_width, screen_height = pyautogui.size()
        self.screen_region = (0, 0, screen_width, screen_height)

    async def get_dominant_color(self):
        """Получить доминирующий цвет (асинхронно с обработкой в отдельном процессе)"""
        try:
            # Захватываем скриншот в главном процессе
            screenshot = ImageGrab.grab(bbox=self.screen_region)

            # Масштабируем в главном процессе (быстрее, чем передавать PIL Image)
            small_img = screenshot.resize(
                (
                    screenshot.width // config.DOWNSCALE_FACTOR,
                    screenshot.height // config.DOWNSCALE_FACTOR,
                ),
                Image.Resampling.NEAREST,
            )

            # Конвертируем в numpy array (легко сериализуется)
            pixels = np.array(small_img, dtype=np.uint8)

            # Отправляем только numpy array в рабочий процесс (неблокирующее)
            try:
                self.screenshot_queue.put(pixels, block=False)
            except:
                pass  # Если очередь полная, пропустим кадр

            # Получаем уже обработанный цвет
            try:
                dominant_color = self.color_queue.get(block=False)
                self.last_color = dominant_color
                return dominant_color
            except:
                # Если нет результата - возвращаем последний цвет
                return self.last_color if self.last_color else (128, 128, 128)

        except Exception as e:
            print(f"Ошибка при получении цвета: {e}")
            return (128, 128, 128)

    def cleanup(self):
        """Остановить рабочий процесс"""
        if hasattr(self, "worker_process") and self.worker_process.is_alive():
            self.screenshot_queue.put(None)
            self.worker_process.join(timeout=2)
            if self.worker_process.is_alive():
                self.worker_process.terminate()
        return (r, g, b)
        # h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)
        # s = min(s * 1.0, 1.0)
        # v = min(v * 1.2, 1.0)
        # r, g, b = hsv_to_rgb(h, s, v)
        # return (int(r * 255), int(g * 255), int(b * 255))
