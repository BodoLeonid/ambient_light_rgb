import asyncio
from bleak import BleakClient
import config
import utils


class BLEClient:
    def __init__(self, color_processor):
        self.client = None
        self.color_processor = color_processor
        self.is_connected = False

    async def connect(self):
        """Подключение к устройству"""
        try:
            self.client = BleakClient(config.DEVICE_ADDRESS)
            await asyncio.wait_for(self.client.connect(), timeout=10.0)
            # Даём время на service discovery
            await asyncio.sleep(1.0)
            self.is_connected = True
            print("Успешное подключение...")
            return True
        except asyncio.TimeoutError:
            print("Ошибка подключения: таймаут подключения")
            return False
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    async def disconnect(self):
        """Отключение от устройства"""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            print("Отключено от устройства")

    async def send_color_command(self, color):
        """Отправка на устройство"""
        if not self.is_connected or not self.client:
            return

        try:
            color_hex = utils.rgb_to_hex(color)
            cmd = bytes.fromhex(f"7E000503{color_hex}00EF")
            # Используем write_gatt_char с правильным UUID
            await self.client.write_gatt_char(
                config.CHARACTERISTIC_UUID, cmd, response=False
            )
        except Exception as e:
            print(f"Ошибка отправки цвета: {e}")
            self.is_connected = False

    async def run_color_stream(self):
        """Отправка цветов"""
        last_color = None
        frame_skip_count = 0

        while self.is_connected:
            try:
                # Пропускаем некоторые кадры для ускорения
                frame_skip_count += 1
                if frame_skip_count < config.SKIP_FRAMES:
                    await asyncio.sleep(config.POLL_DELAY)
                    continue
                frame_skip_count = 0

                new_color = await self.color_processor.get_dominant_color()

                if last_color is None:
                    last_color = new_color
                    await self.send_color_command(new_color)
                else:
                    if (
                        utils.color_distance(new_color, last_color)
                        >= config.COLOR_CHANGE_THRESHOLD
                    ):
                        transition_colors = utils.generate_color_transition(
                            last_color, new_color, config.TRANSITION_STEPS
                        )

                        for color in transition_colors:
                            await self.send_color_command(color)
                            await asyncio.sleep(config.TRANSITION_DELAY)

                        last_color = new_color
                    else:
                        await self.send_color_command(last_color)

                await asyncio.sleep(config.POLL_DELAY)

            except Exception as e:
                print(f"Ошибка в потоке цветов: {e}")
                break
