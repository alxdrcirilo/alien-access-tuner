from dataclasses import dataclass

FPS = 60


@dataclass
class Resolution:
    WIDTH: int = 420
    HEIGHT: int = 380


@dataclass
class Colors:
    BLACK: tuple = (0, 0, 0)
    BLUE: tuple = (24, 168, 241)
    DARK_GRAY: tuple = (40, 40, 40)
    DARK_GREEN: tuple = (31, 94, 11)
    GRAY: tuple = (200, 200, 200)
    GREEN: tuple = (55, 251, 56)
    LIGHT_BLUE: tuple = (162, 218, 245)
    LIGHT_GRAY: tuple = (230, 230, 230)
    RED: tuple = (255, 75, 31)
    YELLOW: tuple = (251, 173, 8)
    WHITE: tuple = (240, 242, 241)

