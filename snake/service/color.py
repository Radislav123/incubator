from core.service.color import Color as CoreColor


class Color(CoreColor):
    BACKGROUND = (0, 0, 0, 255)
    NORMAL = (30, 30, 30, 255)
    HOVERED = (40, 40, 40, 255)
    PRESSED = (20, 20, 20, 255)
    DISABLED = (50, 50, 50, 255)

    SURFACE_TILE_NORMAL = (40, 40, 40, 255)
    SURFACE_TILE_ENABLED = (50, 50, 50, 255)
    BORDER_TILE_NORMAL = (20, 20, 20, 255)
    BORDER_TILE_ENABLED = (30, 30, 30, 255)

    TILE_BORDER = (255, 255, 255, 255)

    TEXT = (50, 240, 50, 255)
