import pygame as pg
from typing import override

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from src.core.managers import GameManager

class MenuScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    play_button: Button
    settings_button: Button

    def __init__(self, game_manager: GameManager | None = None):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.entering = 0
        self.game_manager = game_manager
        # Button dimensions
        button_width = 100
        button_height = 100
        gap = 20  # Space between buttons

        # Center positions
        center_x = GameSettings.SCREEN_WIDTH // 2
        play_y = GameSettings.SCREEN_HEIGHT * 3 // 4

        # Play button (centered)
        self.play_button = Button(
            "UI/button_play.png", "UI/button_play_hover.png",
            center_x, play_y,
            button_width, button_height,
            lambda: scene_manager.change_scene("game")
        )

        # Settings button (to the left of play button)
        settings_x = center_x - button_width - gap
        settings_y = play_y
        self.settings_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            settings_x, settings_y,
            button_width, button_height,
            lambda: scene_manager.change_scene("settings")
        )

    @override
    def enter(self) -> None:
        if self.game_manager.music_on and not self.game_manager.repeated_enter:
            sound_manager.play_sound("RBY 101 Opening (Part 1).ogg", int(self.game_manager.music_slider_value) / 100)
        self.game_manager.repeated_enter = True

    @override
    def exit(self) -> None:
        sound_manager.stop_all_sounds()
        self.game_manager.repeated_enter = False

    @override
    def update(self, dt: float) -> None:
        self.play_button.update(dt)
        self.settings_button.update(dt)

        if input_manager.key_pressed(pg.K_SPACE):
            scene_manager.change_scene("game")
            return

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.play_button.draw(screen)
        self.settings_button.draw(screen)
