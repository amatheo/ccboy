import numpy as np
from config import COLOR_MAP


class ScreenConverter:
    color_lookup = {}

    @classmethod
    def initialize(cls):
        for (r, g, b), hex_val in COLOR_MAP.items():
            color_15bit = cls.to_15bit(r, g, b)
            cls.color_lookup[color_15bit] = hex_val

    @staticmethod
    def to_15bit(r, g, b):
        return ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3)

    @classmethod
    def find_closest_color(cls, color_15bit):
        if color_15bit in cls.color_lookup:
            return cls.color_lookup[color_15bit]

        r = (color_15bit >> 10) & 0x1F
        g = (color_15bit >> 5) & 0x1F
        b = color_15bit & 0x1F

        min_diff = float('inf')
        closest_color = 'f'  # Default to white if no match found

        for (kr, kg, kb), hex_val in COLOR_MAP.items():
            kr_15 = kr >> 3
            kg_15 = kg >> 3
            kb_15 = kb >> 3
            diff = abs(int(r) - int(kr_15)) + abs(int(g) - int(kg_15)) + abs(int(b) - int(kb_15))
            if diff < min_diff:
                min_diff = diff
                closest_color = hex_val

        return closest_color

    @classmethod
    def convert_screen_to_nfp(cls, screen):
        # Convertir l'image en format 15-bit en utilisant un type de données plus grand
        screen_15bit = (screen[:, :, 0].astype(np.uint16) << 7) & 0x7C00 | \
                       (screen[:, :, 1].astype(np.uint16) << 2) & 0x03E0 | \
                       (screen[:, :, 2].astype(np.uint16) >> 3)

        # Trouver les couleurs uniques et les plus fréquentes
        unique_colors, counts = np.unique(screen_15bit, return_counts=True)
        top_colors = dict(sorted(zip(unique_colors, counts), key=lambda x: x[1], reverse=True)[:56])

        # Créer un dictionnaire de lookup pour les couleurs les plus fréquentes
        color_map = {color: cls.find_closest_color(color) for color in top_colors}

        # Convertir l'image
        nfp_image = np.vectorize(color_map.get)(screen_15bit)

        # Convertir les couleurs restantes
        mask = ~np.isin(screen_15bit, list(color_map.keys()))
        if np.any(mask):
            remaining_colors = screen_15bit[mask]
            for color in np.unique(remaining_colors):
                nfp_image[screen_15bit == color] = cls.find_closest_color(color)

        # Convertir l'image en une chaîne de caractères
        nfp_image_str = '\n'.join([''.join(map(str, row)) for row in nfp_image])

        return nfp_image_str

    @staticmethod
    def generate_header_bytes(screen):
        height, width = screen.shape[:2]
        return bytes([width, height])
