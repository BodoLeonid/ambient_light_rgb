import asyncio
import platform
from color_processor import ColorProcessor
from ble_client import BLEClient


async def main():
    print("Запуск отслеживания цветов...")

    # event loop для macOS
    if platform.system() == "Darwin":
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    color_processor = ColorProcessor()
    ble_client = BLEClient(color_processor)

    try:
        # Подключение к устройству
        if await ble_client.connect():
            # Запуск потока цветов
            await ble_client.run_color_stream()

    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")

    finally:
        # Корректное отключение
        await ble_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
