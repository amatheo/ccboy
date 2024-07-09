import os

# Configuration de l'émulateur
ROM_FILE = os.environ.get('ROM_FILE', 'default.gbc')
ROM_PATH = os.environ.get('ROM_PATH', '/app/roms')

# Configuration du serveur WebSocket
WEBSOCKET_HOST = os.environ.get('WEBSOCKET_HOST', 'localhost')
WEBSOCKET_PORT = int(os.environ.get('WEBSOCKET_PORT', 8081))

# Configuration de l'émulation
EMULATION_FPS = int(os.environ.get('EMULATION_FPS', 60))
SCREEN_UPDATE_RATE = int(os.environ.get('SCREEN_UPDATE_RATE', 15))

# Autres configurations
COMPRESSION_ENABLED = os.environ.get('COMPRESSION_ENABLED', 'True').lower() == 'true'

COLOR_MAP = {
    (0xF0, 0xF0, 0xF0): '0',
    (0xF2, 0xB2, 0x33): '1',
    (0xE5, 0x7F, 0xD8): '2',
    (0x99, 0xB2, 0xF2): '3',
    (0xDE, 0xDE, 0x6C): '4',
    (0x7F, 0xCC, 0x19): '5',
    (0xF2, 0xB2, 0xCC): '6',
    (0x4C, 0x4C, 0x4C): '7',
    (0x99, 0x99, 0x99): '8',
    (0x4C, 0x99, 0xB2): '9',
    (0xB2, 0x66, 0xE5): 'a',
    (0x33, 0x66, 0xCC): 'b',
    (0x7F, 0x66, 0x4C): 'c',
    (0x57, 0xA6, 0x4E): 'd',
    (0xCC, 0x4C, 0x4C): 'e',
    (0x19, 0x19, 0x19): 'f'
}

ACTION_MAP = {
    "a": "a",
    "b": "b",
    "start": "start",
    "select": "select",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right"
}
