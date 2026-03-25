DEVICE_ADDRESS = "BA1B6ED2-2302-6DA0-4917-647BEF98FBE2"
CHARACTERISTIC_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"

DOWNSCALE_FACTOR = 80  # Еще более агрессивное downscaling
MIN_BRIGHTNESS = 0.15
MAX_BRIGHTNESS = 1.1
MIN_SATURATION = 0.2
DOWNSCALE_COLOR_FACTOR = 8

# Параметры переходов
COLOR_CHANGE_THRESHOLD = 15
TRANSITION_STEPS = 15  # Меньше шагов = быстрее
TRANSITION_DELAY = 0.0001  # Еще меньше задержка
POLL_DELAY = 0.1  # Минимум 50мс между опросами
SKIP_FRAMES = 2  # Пропускаем каждый N-й кадр для анализа

# Включить/выключить улучшение цвета
ENHANCE_COLOR = False  # Поставьте True, если нужно улучшение цвета
