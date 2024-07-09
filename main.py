import asyncio
from emulator import GameBoyEmulator
from websocket_server import WebSocketServer
from screen_converter import ScreenConverter
import config


async def main():
    ScreenConverter.initialize()

    emulator = GameBoyEmulator(rom_path=f"{config.ROM_PATH}/{config.ROM_FILE}", fps=config.EMULATION_FPS)
    server = WebSocketServer(emulator, host=config.WEBSOCKET_HOST, port=config.WEBSOCKET_PORT)

    emulator_task = asyncio.create_task(emulator.run())
    server_task = asyncio.create_task(server.start())

    try:
        await asyncio.gather(emulator_task, server_task)
    finally:
        emulator.stop()
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
