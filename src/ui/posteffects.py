import random

import pygame

from ..config import Colors, Resolution


class PostEffects:
    """
    The PostEffects class provides various visual effects that can be applied to the screen.
    These effects include static noise, tracking lines, horizontal shifts, color distortions,
    dropouts, bloom effects, and an LCD-like surface rendering.

    Attributes:
        _screen (pygame.Surface): The pygame surface representing the screen where effects are applied.
        noise (float): The density of the static noise effect.
        dropout (float): The probability of applying the dropout effect.
    """

    _screen: pygame.Surface

    # TODO:
    # def __init__(self) -> None:
    #     self.noise = 0.0002
    #     self.dropout = 0.05

    def add_static(self) -> None:
        """
        Applies a static noise effect to the screen.

        This method randomly sets pixels on the screen to a gray color to simulate static noise.
        The density of the noise can be controlled by the `noise` parameter.

        Returns:
            None
        """
        noise = random.uniform(self.noise / 2, self.noise)
        for _ in range(int(Resolution.WIDTH * Resolution.HEIGHT * noise)):
            x = random.randint(0, Resolution.WIDTH - 1)
            y = random.randint(0, Resolution.HEIGHT - 1)
            self._screen.set_at(
                (x, y),
                random.choice(
                    [Colors.GRAY, Colors.DARK_GRAY, Colors.LIGHT_GRAY, Colors.WHITE]
                ),
            )

            if random.random() < 0.02:
                length = int(random.normalvariate(8, 4))
                if length > 0:
                    for i in range(length):
                        if x + i < Resolution.WIDTH:
                            self._screen.set_at(
                                (x + i, y),
                                random.choice(
                                    [
                                        Colors.GRAY,
                                        Colors.DARK_GRAY,
                                        Colors.LIGHT_GRAY,
                                        Colors.WHITE,
                                    ]
                                ),
                            )

    def add_tracking(self) -> None:
        """
        Apply random horizontal tracking lines to the screen.

        This method randomly draws horizontal lines across the screen with varying
        thickness and color. There is a 10% chance that the method will draw between
        0 to 3 lines. The lines are drawn at random vertical positions with random
        thickness and color chosen from a predefined set of colors.

        Colors used:
            - BLUE
            - GREEN
            - RED
            - WHITE

        The lines are drawn using the pygame library.

        Returns:
            None
        """
        colors = [Colors.BLUE, Colors.GREEN, Colors.WHITE]
        if random.random() < self.tracking:
            for _ in range(random.randint(0, 3)):
                y = random.randint(0, Resolution.HEIGHT)
                line_thickness = random.randint(1, 40)
                pygame.draw.line(
                    self._screen,
                    random.choice(colors),
                    (0, y),
                    (Resolution.WIDTH, y),
                    line_thickness,
                )

    def add_shifting(self):
        """
        Applies a horizontal shift effect to the screen with a small probability.

        This method randomly decides whether to apply a horizontal shift effect to the screen.
        If the effect is applied, it shifts horizontal slices of the screen by a random amount.
        The shift amount is a random integer between -10% and +10% of the screen width.
        The effect is applied to slices of the screen with a height of 10 pixels.
        After applying the shift, a random glitch sound is played.

        Returns:
            None
        """
        if random.random() < self.shift:
            shift_amount = random.randint(
                -Resolution.WIDTH // 10, Resolution.WIDTH // 10
            )
            for y in range(0, Resolution.HEIGHT, 10):
                slice_rect = pygame.Rect(0, y, Resolution.WIDTH, 10)
                slice_surface = self._screen.subsurface(slice_rect).copy()
                self._screen.blit(slice_surface, (shift_amount, y))
            random.choice(self._glitches).play()

    def add_distortion(self):
        """
        Apply a distortion effect to the screen by randomly shifting the green color channel.

        This method has a 5% chance to apply a distortion effect to the screen. The effect
        involves shifting the green color channel of each pixel by a random amount between
        -20 and 20, while ensuring the green value stays within the range of 100 to 255.

        Returns:
            None
        """
        if random.random() < self.distortion:
            color_shift = random.randint(-20, 20)
            for y in range(Resolution.HEIGHT):
                for x in range(Resolution.WIDTH):
                    r, g, b, a = self._screen.get_at((x, y))
                    g = max(100, min(255, g + color_shift))
                    self._screen.set_at((x, y), (r, g, b, a))

    def add_dropout(self):
        if random.random() < self.dropout:
            blackout = pygame.Surface((Resolution.WIDTH, Resolution.HEIGHT))
            blackout.fill(random.choice([Colors.BLACK, Colors.BLUE]))
            blackout.set_alpha(random.randint(0, 255))
            self._screen.blit(blackout, (0, 0))

    def add_bloom(self):
        """
        Applies a bloom effect to the current screen.
        The bloom effect highlights bright areas of the screen by creating a glowing effect.
        This is achieved by identifying pixels above a certain brightness threshold and
        applying a blur to these areas.

        Steps:
        1. Create a new surface for the bloom effect.
        2. Identify bright pixels on the screen using a threshold.
        3. Copy these bright pixels to the bloom surface.
        4. Scale down the bloom surface to create a blur effect.
        5. Scale the bloom surface back up to the original size.
        6. Blend the bloom surface back onto the original screen.

        Attributes:
            threshold (int): The brightness threshold to consider a pixel as bright.
            bloom_factor (float): The factor by which the bloom surface is scaled down to create the blur effect.

        Returns:
            None
        """
        threshold = 200
        bloom_surface = pygame.Surface(self._screen.get_size()).convert_alpha()
        bloom_surface.fill((0, 0, 0, 0))

        pixels = pygame.surfarray.pixels3d(self._screen)
        alpha = pygame.surfarray.pixels_alpha(self._screen)
        bloom_pixels = pygame.surfarray.pixels3d(bloom_surface)
        bloom_alpha = pygame.surfarray.pixels_alpha(bloom_surface)

        bright_mask = (
            (pixels[:, :, 0] > threshold)
            & (pixels[:, :, 1] > threshold)
            & (pixels[:, :, 2] > threshold)
        )
        bloom_pixels[bright_mask] = pixels[bright_mask]
        bloom_alpha[bright_mask] = alpha[bright_mask]

        del pixels, alpha, bloom_pixels, bloom_alpha

        bloom_factor = 0.75
        small_bloom_surface = pygame.transform.smoothscale(
            bloom_surface,
            (
                int(Resolution.WIDTH * bloom_factor),
                int(Resolution.HEIGHT * bloom_factor),
            ),
        )
        bloom_surface = pygame.transform.smoothscale(
            small_bloom_surface, (Resolution.WIDTH, Resolution.HEIGHT)
        )
        self._screen.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
