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
            await self.client.connect()
            self.is_connected = True
            print("Успешное подключение...")
            return True
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
        if not self.is_connected:
            return

        color_hex = utils.rgb_to_hex(color)
        cmd = bytes.fromhex(f"7E000503{color_hex}00EF")
        await self.client.write_gatt_char(config.CHARACTERISTIC_UUID, cmd)

    async def run_color_stream(self):
        """Отправка цветов"""
        last_color = None

        while self.is_connected:
            try:
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

                await asyncio.sleep(0)

            except Exception as e:
                print(f"Ошибка в потоке цветов: {e}")
                break
