import asyncio
from pyboy import PyBoy


class GameBoyEmulator:
    def __init__(self, rom_path, fps=60):
        self.pyboy = PyBoy(rom_path, window="null")
        self.button_press = []
        self.fps = fps

    async def run(self):
        while True:
            for button in self.button_press:
                self.pyboy.button(button)
            self.button_press.clear()
            self.pyboy.tick()
            await asyncio.sleep(1 / self.fps)

    def get_screen(self):
        return self.pyboy.screen.ndarray[:, :, :3]

    def press_button(self, button):
        self.button_press.append(button)

    def stop(self):
        self.pyboy.stop()
