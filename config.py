DEVICE_ADDRESS = "BA1B6ED2-2302-6DA0-4917-647BEF98FBE2"
CHARACTERISTIC_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"

DOWNSCALE_FACTOR = 16  # Коэфициент уменьшения скриншота
MIN_BRIGHTNESS = 0.15
MAX_BRIGHTNESS = 0.95
MIN_SATURATION = 0.2
DOWNSCALE_COLOR_FACTOR = 8

# Параметры переходов
COLOR_CHANGE_THRESHOLD = 15  # Порог изменения цвета для начала перехода
TRANSITION_STEPS = 15  # Количество шагов перехода между цветами
TRANSITION_DELAY = 0.001  # Задержка между шагами перехода /cек

# Включить/выключить улучшение цвета
ENHANCE_COLOR = False  # Поставьте True, если нужно улучшение цвета
