import asyncio
import websockets
import zlib

import config
from screen_converter import ScreenConverter
from button_handler import ButtonHandler

class WebSocketServer:
    def __init__(self, emulator, host='localhost', port=8081):
        self.emulator = emulator
        self.host = host
        self.port = port
        self.server = None

    async def start(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        print(f"WebSocket server started on {self.host}:{self.port}")
        await self.server.wait_closed()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def handler(self, websocket, path):
        print("Client connected")
        send_task = asyncio.create_task(self.send_game_data(websocket))
        try:
            while True:
                command = await websocket.recv()
                ButtonHandler.handle_command(command, self.emulator)
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            send_task.cancel()

    async def send_game_data(self, websocket):
        try:
            while True:
                screen_buffer = self.emulator.get_screen()
                header_bytes = ScreenConverter.generate_header_bytes(screen_buffer)
                nfp_data_str = ScreenConverter.convert_screen_to_nfp(screen_buffer)
                nfp_image = header_bytes + nfp_data_str.encode('utf-8')

                nfp_image = zlib.compress(nfp_image, level=9)

                await websocket.send(nfp_image)
                await asyncio.sleep(1 / config.SCREEN_UPDATE_RATE)
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
