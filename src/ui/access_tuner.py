import random
import time

import pygame
from pygame.locals import QUIT

from src.config import FPS, Colors, Resolution

from ..helpers.utils import resource_path
from .posteffects import PostEffects


class AccessTuner(PostEffects):
    def __init__(self) -> None:
        super().__init__()

        pygame.init()
        pygame.display.set_caption("Access Tuner")

        self._load_fonts()
        self._load_sounds()
        self._post_init()

        # Game loop
        self._running = True
        self._started = False

        # Game state
        self._validation_ranges = {i: self._get_random_ranges(0.3) for i in range(3)}
        self._validated = {i: False for i in range(3)}

    def _post_init(self):
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((Resolution.WIDTH, Resolution.HEIGHT))

        self.noise = 0.00005
        self.dropout = 0.0005
        self.tracking = 0.01
        self.shift = 0.01
        self.distortion = 0.01

    def _load_fonts(self):
        self._font_file = "../../assets/fonts/Sevastopol-Interface.ttf"

    def _load_sounds(self):
        pygame.mixer.music.load("assets/sounds/static.wav")
        pygame.mixer.music.play(-1)
        self._glitches = (
            pygame.mixer.Sound("assets/sounds/glitch.wav"),
            pygame.mixer.Sound("assets/sounds/glitch_2.wav"),
        )
        for glitch in self._glitches:
            glitch.set_volume(0.1)

    def _get_random_ranges(self, max_length):
        start = random.uniform(0, 1 - max_length)
        end = start + random.uniform(0.1, max_length)
        return (start, end)

    def draw(self) -> None:
        # Background
        self._screen.fill(Colors.BLUE)

        # Container
        v_offset = 10
        border_width = 3
        border_radius = 2
        inner_padding = border_width + 2

        outer_rect = pygame.Rect(
            v_offset,
            Resolution.HEIGHT // 5,
            Resolution.WIDTH - 2 * v_offset,
            Resolution.HEIGHT - 2 * Resolution.HEIGHT // 5,
        )
        inner_rect = outer_rect.inflate(-2 * inner_padding, -2 * inner_padding)

        pygame.draw.rect(
            self._screen, Colors.WHITE, outer_rect, border_width, border_radius
        )
        pygame.draw.rect(
            self._screen, Colors.WHITE, inner_rect, border_width, border_radius
        )

        container = inner_rect.inflate(-4 * inner_padding, -4 * inner_padding)

        # Subrects
        subrect_height = container.height // 3
        texts = [
            "ESTABLISHING CONNECTION",
            "SENDING PACKETS",
            "OVERRIDING PROTOCOL",
        ]
        subrects = [
            pygame.Rect(
                container.left,
                container.top + i * subrect_height,
                container.width,
                subrect_height,
            )
            for i in range(3)
        ]

        # Text and progress bars
        for n, (message, subrect) in enumerate(zip(texts, subrects)):
            # Text
            font = pygame.font.Font(resource_path(self._font_file), 20)
            text = font.render(message, True, Colors.LIGHT_GRAY)
            self._screen.blit(text, (subrect.left, subrect.top))

            # Scale to progress bar
            border_width = 4
            border_radius = 2
            subrect.scale_by_ip(1, 0.4)

            if position := self._validation_ranges.get(n):
                allowed_range = pygame.Rect(
                    subrect.left + position[0] * subrect.width,
                    subrect.top,
                    (position[1] - position[0]) * subrect.width,
                    subrect.height,
                )
                pygame.draw.rect(
                    self._screen,
                    Colors.LIGHT_BLUE,
                    allowed_range,
                )

            # Progress bar content
            if n == list(self._validated.values()).index(False):
                progress_length = 10
                progress_position = (pygame.time.get_ticks() // 10) % (
                    2 * subrect.width - 2 * progress_length
                )
                if progress_position >= subrect.width - progress_length:
                    progress_position = (
                        2 * (subrect.width - progress_length) - progress_position
                    )
                current_position = pygame.Rect(
                    subrect.left + progress_position,
                    subrect.top,
                    progress_length,
                    subrect.height,
                )
                pygame.draw.rect(
                    self._screen,
                    Colors.WHITE,
                    current_position,
                    border_radius=border_radius,
                )

            # If first not validated, save state
            if n == list(self._validated.values()).index(False):
                self.allowed_range = allowed_range
                self.current_position = current_position

            # Progress bar
            pygame.draw.rect(
                self._screen, Colors.WHITE, subrect, border_width, border_radius
            )

        # Title
        font = pygame.font.Font(resource_path(self._font_file), 38)
        text = font.render("SYSTEM OVERRIDE", True, Colors.WHITE)
        text_rect = text.get_rect(
            center=(
                Resolution.WIDTH // 2,
                Resolution.HEIGHT // 10,
            )
        )
        self._screen.blit(text, text_rect)

        # Bottom text
        font = pygame.font.Font(resource_path(self._font_file), 22)
        text = font.render("SECURITY FREQUENCY MATCH", True, Colors.WHITE)
        text_rect = text.get_rect(
            center=(
                Resolution.WIDTH // 2,
                Resolution.HEIGHT * 0.9,
            )
        )
        self._screen.blit(text, text_rect)
        font = pygame.font.Font(resource_path(self._font_file), 12)
        text = font.render("V0.34 - SEEGSON SYSTEMS", True, Colors.WHITE)
        text_rect = text.get_rect(
            center=(
                Resolution.WIDTH // 2,
                Resolution.HEIGHT * 0.95,
            )
        )
        self._screen.blit(text, text_rect)

    def add_posteffects(self):
        self.add_static()
        self.add_tracking()
        self.add_shifting()
        self.add_distortion()
        self.add_dropout()

    def draw_screen_border(self):
        border_rect = pygame.Rect(0, 0, Resolution.WIDTH, Resolution.HEIGHT)
        pygame.draw.rect(self._screen, Colors.DARK_GRAY, border_rect, 8)
        pygame.draw.rect(self._screen, Colors.DARK_GRAY, border_rect, 8, 12)

    def play(self) -> None:
        while self._running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()

            if not self._started:
                self._screen.fill(Colors.DARK_GRAY)
                self.noise = 0.4
                self.add_static()

                self.draw_screen_border()

                # Draw "No Signal" box
                box_width, box_height = Resolution.WIDTH * 0.8, 80
                box_rect = pygame.Rect(
                    (Resolution.WIDTH - box_width) // 2,
                    (Resolution.HEIGHT - box_height) // 2,
                    box_width,
                    box_height,
                )
                pygame.draw.rect(self._screen, Colors.BLACK, box_rect)
                pygame.draw.rect(self._screen, Colors.YELLOW, box_rect, 6, 4)

                font = pygame.font.Font(resource_path(self._font_file), 32)
                text = font.render("NO SIGNAL", True, Colors.WHITE)
                text_rect = text.get_rect(center=box_rect.center)
                self._screen.blit(text, text_rect)

                self._clock.tick(FPS)
                pygame.display.update()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] and not self._started:
                print("Game started!")
                pygame.mixer.music.stop()
                self._started = True
                self.noise = 0.00005

            if self._started:
                self.draw()
                self.add_posteffects()
                self.add_bloom()

                self.draw_screen_border()

                if keys[pygame.K_SPACE] and self._started:
                    if self.allowed_range.contains(self.current_position):
                        pygame.mixer.Sound("assets/sounds/blip.wav").play()
                        self._validated[list(self._validated.values()).index(False)] = (
                            True
                        )

                        # Show green screen with "ACCESS GRANTED"
                        if all(self._validated.values()):
                            self._screen.fill(Colors.DARK_GREEN)
                            font = pygame.font.Font(resource_path(self._font_file), 46)
                            text = font.render("ACCESS GRANTED", True, Colors.DARK_GRAY)
                            text_rect = text.get_rect(
                                center=(Resolution.WIDTH // 2, Resolution.HEIGHT // 2)
                            )
                            self._screen.blit(text, text_rect)
                            self.draw_screen_border()
                            pygame.display.update()
                            time.sleep(3)


                    # Show red screen with "ACCESS DENIED"
                    else:
                        self.noise *= 2
                        self.dropout *= 2
                        self.tracking *= 2
                        self.shift *= 2
                        self.distortion *= 2

                        self._screen.fill(Colors.RED)
                        font = pygame.font.Font(resource_path(self._font_file), 46)
                        text = font.render("ACCESS DENIED", True, Colors.DARK_GRAY)
                        text_rect = text.get_rect(
                            center=(Resolution.WIDTH // 2, Resolution.HEIGHT // 2)
                        )
                        self._screen.blit(text, text_rect)
                        self.draw_screen_border()
                        pygame.display.update()
                        time.sleep(0.5)

                    # To prevent consecutive key presses
                    pygame.time.wait(200)

                self._clock.tick(FPS)
                pygame.display.update()
