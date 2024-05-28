from core.service.color import Color as CoreColor


class Color(CoreColor):
    BACKGROUND = (0, 0, 0, 255)
    NORMAL = (30, 30, 30, 255)
    HOVERED = (40, 40, 40, 255)
    PRESSED = (20, 20, 20, 255)
    DISABLED = (50, 50, 50, 255)

    SNAKE_ALIVE = (50, 200, 50, 255)
    SNAKE_DEAD = (50, 100, 40, 255)

    FOOD = (150, 50, 50, 255)

    NEURON_ACTIVE = (50, 200, 50, 255)
    NEURON_SLEEP = (40, 50, 40, 255)
    SYNAPSE_ACTIVE = (200, 200, 200, 255)
    SYNAPSE_SLEEP = (40, 40, 40, 255)

    SURFACE_TILE_NORMAL = (40, 40, 40, 255)
    SURFACE_TILE_ENABLED = (50, 50, 50, 255)
    BORDER_TILE_NORMAL = (20, 20, 20, 255)
    BORDER_TILE_ENABLED = (30, 30, 30, 255)

    TILE_BORDER = (255, 255, 255, 255)

    TEXT = (50, 240, 50, 255)
