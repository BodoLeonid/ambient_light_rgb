import asyncio
import platform
from color_processor import ColorProcessor
from ble_client import BLEClient


async def main():
    print("Запуск отслеживания цветов...")

    color_processor = ColorProcessor()
    ble_client = BLEClient(color_processor)

    # Подключение к устройству
    try:
        if await ble_client.connect():
            await ble_client.run_color_stream()
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
    finally:
        await ble_client.disconnect()
        color_processor.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
