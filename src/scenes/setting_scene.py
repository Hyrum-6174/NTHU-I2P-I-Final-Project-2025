import pygame as pg
import json
import os
from typing import override

from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from src.utils import GameSettings
from src.scenes.menu_scene import MenuScene  # import MenuScene class
from src.sprites import Sprite
from src.interface.components.slider import Slider
from src.core.managers import GameManager
from src.entities.player import Player
from src.maps.map import Map
from src.scenes.battle_scene import BattleScene
from src.scenes.catch_scene import CatchScene
from src.scenes.game_scene import GameScene

class SettingScene(Scene):
    music_toggle_button: Button
    sfx_toggle_button: Button
    back_button: Button
    save_button: Button
    load_button: Button
    music_on: bool
    sfx_on: bool
    music_slider: Slider
    sfx_slider: Slider
    game_manager: GameManager | None
    player: Player

    def __init__(self, game_manager: GameManager | None = None):
        super().__init__()

        
        self.previous_scene_name = None
        self.game_manager = game_manager
        self.player = self.game_manager.player
        self.game_manager.just_load = False
        self.enter_count = 0

        # Reference to menu scene
        self.menu_scene = scene_manager._scenes.get("menu")  # access the registered menu scene

        # Default toggle states
        self.game_manager.music_on = True
        self.sfx_on = True

        # Button positions (relative to board center)
        center_x = GameSettings.SCREEN_WIDTH // 2
        start_y = GameSettings.SCREEN_HEIGHT // 2 - 100
        gap_y = 100

        # Music toggle
        self.music_toggle_button = Button(
            "UI/raw/UI_Flat_ToggleRightOff01a.png",
            "UI/raw/UI_Flat_ToggleRightOn01a.png",
            center_x - 155, start_y - 50,
            60, 60,
            self.toggle_music
        )

        # SFX toggle
        self.sfx_toggle_button = Button(
            "UI/raw/UI_Flat_ToggleRightOff01a.png",
            "UI/raw/UI_Flat_ToggleRightOn01a.png",
            center_x - 155, start_y - 50 + gap_y,
            60, 60,
            self.toggle_sfx
        )

        # Back button
        self.back_button = Button(
            "UI/button_back.png",
            "UI/button_back_hover.png",
            center_x - 185, start_y - 50 + 2 * gap_y,
            100, 80,
            self.back
        )

        # Save button
        self.save_button = Button(
            "UI/button_save.png",
            "UI/button_save_hover.png",
            center_x + 125, start_y - 50 + 2 * gap_y,
            100, 80,
            self.save_game
            )
        
        # Load button
        self.load_button = Button(
            "UI/button_load.png",
            "UI/button_load_hover.png",
            center_x - 25, start_y - 50 + 2 * gap_y,
            100, 80,
            self.load_game
            )

        # Music slider
        self.music_slider = Slider(
            center_x - 85, start_y - 35,
            300, 20,
        )

        # SFX slider
        self.sfx_slider = Slider(
            center_x - 85, start_y + 65,
            300, 20,
        )

        # Settings board
        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot02a.png",  # your PNG
            (500, 400)                      # scale to board size
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 225,
            GameSettings.SCREEN_HEIGHT // 2 - 200
        )


    def back(self):
        if self.game_manager.music_on:
            # if self.previous_scene_name == None:
            #     sound_manager.play_sound("RBY 101 Opening (Part 1).ogg", int(self.music_slider.value) / 100)
            pass
        scene_manager.change_scene(
        self.previous_scene_name if self.previous_scene_name else "menu")

    def toggle_music(self):
        self.game_manager.music_on = not self.game_manager.music_on
        if self.game_manager.music_on:
            self.music_toggle_button.img_button = Sprite("UI/raw/UI_Flat_ToggleRightOn01a.png", (60, 60))
            sound_manager.resume_all()
        else:
            self.music_toggle_button.img_button = Sprite("UI/raw/UI_Flat_ToggleRightOff01a.png", (60, 60))
            sound_manager.pause_all()

    def toggle_sfx(self):
        self.sfx_on = not self.sfx_on
        if self.sfx_on:
            self.sfx_toggle_button.img_button = Sprite("UI/raw/UI_Flat_ToggleRightOn01a.png", (60, 60))
        else:
            self.sfx_toggle_button.img_button = Sprite("UI/raw/UI_Flat_ToggleRightOff01a.png", (60, 60))


    def save_game(self):
        path = "saves/save.json"
        self.game_manager.save(path)

        

    def load_game(self):
        # self.game_manager = new_gm
        self.game_manager.just_load = True
        sound_manager.stop_all_sounds()

        # for m in self.game_manager.maps.values():
        #     if isinstance(m, Map):
        #         m.game_manager = self.game_manager

        with open("saves/save.json", "r") as f:
            game_data1 = json.load(f)

        # if game_data["current_map"] != game_data1["current_map"]:
        des = game_data1["current_map"]
        self.game_manager.switch_map(des, False)
        
        # path = "saves/save.json"
        # new_gm = self.game_manager.load(path)

        # print(game_data1["player"]['x'], type(game_data1["player"]['x']))       
        scene_manager.change_scene("game")

        # self.game_manager.player.position.x = game_data1["player"]['x'] * GameSettings.TILE_SIZE
        # self.game_manager.player.position.y = game_data1['player']['y'] * GameSettings.TILE_SIZE
        self.game_manager.save("saves/temp.json")
        gm = GameManager.load("saves/save.json")  # Load once
        gm.save("saves/temp.json")
        game_scene = GameScene(gm)
        setting_scene = SettingScene(gm)
        battle_scene = BattleScene(gm)
        catch_scene = CatchScene(gm)
        scene_manager.register_scene("game", game_scene)
        scene_manager.register_scene("settings", setting_scene)
        scene_manager.register_scene("battle", battle_scene)
        scene_manager.register_scene("catch", catch_scene)


    @override
    def enter(self) -> None:
        # self.enter_count += 1
        # if self.enter_count > 1:
        #     sound_manager.stop_all_sounds()
        #     self.enter_count = 1
        pass
          

    @override
    def exit(self) -> None:
        # sound_manager.stop_all_sounds()
        pass


    @override
    def update(self, dt: float) -> None:
        self.music_toggle_button.update(dt)
        self.sfx_toggle_button.update(dt)
        self.back_button.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.music_slider.update(dt)
        self.sfx_slider.update(dt)
        self.game_manager.player.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        # 1. If previous scene is the menu, draw it directly
        if self.menu_scene and (self.previous_scene_name == "menu" or self.previous_scene_name is None):
            self.menu_scene.background.draw(screen)
            self.menu_scene.play_button.draw(screen)
            self.menu_scene.settings_button.draw(screen)
            dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 150))
            screen.blit(dark_overlay, (0, 0))

        # 2. Otherwise, draw the previous scene if exists
        elif self.previous_scene_name and self.previous_scene_name in scene_manager._scenes:
            prev_scene = scene_manager._scenes[self.previous_scene_name]

            if hasattr(prev_scene, "current_map"):
                prev_scene.current_map.draw(screen, prev_scene.game_manager.player.camera)
                prev_scene.game_manager.player.draw(screen, prev_scene.game_manager.player.camera)
                for enemy in prev_scene.game_manager.current_enemy_trainers:
                    enemy.draw(screen, prev_scene.game_manager.player.camera)

                # Apply dark overlay for map/game
                dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
                dark_overlay.fill((0, 0, 0, 150))
                screen.blit(dark_overlay, (0, 0))

            # Fallback
            elif hasattr(prev_scene, "draw"):
                prev_scene.draw(screen)
                dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
                dark_overlay.fill((0, 0, 0, 150))
                screen.blit(dark_overlay, (0, 0))

        # 3. Draw the settings board
        #board_rect = pg.Rect(
        #    GameSettings.SCREEN_WIDTH // 2 - 250,
        #    GameSettings.SCREEN_HEIGHT // 2 - 200,
        #    500, 400
        #)
        #board_surface = pg.Surface((board_rect.width, board_rect.height), pg.SRCALPHA)
        #board_surface.fill((50, 50, 50, 200))
        #screen.blit(board_surface, (board_rect.x, board_rect.y))
        screen.blit(self.board_sprite.image, self.board_pos)

        # 4. Draw the buttons on top
        self.music_toggle_button.draw(screen)
        self.sfx_toggle_button.draw(screen)

        music_sprite = (
            Sprite("UI/raw/UI_Flat_ToggleRightOn01a.png", (60, 60))
            if self.game_manager.music_on else
            Sprite("UI/raw/UI_Flat_ToggleRightOff01a.png", (60, 60))
        )
        screen.blit(music_sprite.image, self.music_toggle_button.hitbox.topleft)
        
        # Same for SFX
        sfx_sprite = (
            Sprite("UI/raw/UI_Flat_ToggleRightOn01a.png", (60, 60))
            if self.sfx_on else
            Sprite("UI/raw/UI_Flat_ToggleRightOff01a.png", (60, 60))
        )
        screen.blit(sfx_sprite.image, self.sfx_toggle_button.hitbox.topleft)

        # Draw other buttons normally
        self.back_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)

        # Draw sliders
        self.music_slider.draw(screen)
        self.sfx_slider.draw(screen)
