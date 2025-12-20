import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.utils.evo_dict import EvoDict
from src.utils.destination_dict import DestinationDict
from src.core.services import scene_manager, sound_manager, input_manager
from src.sprites import Sprite
from src.sprites import Animation
from src.interface.components import Button
from src.interface.components.chat_overlay import ChatOverlay
from typing import override
import json

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    animation_online: Animation

    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.game_manager = game_manager
        self.showing_bag = False
        self.nav_open = False
        self.navigating = False
        temp = DestinationDict()
        self.destination_dict = temp.destination_dict
        self.navigate_to_buttons = []
        temp1 = EvoDict()
        self.evo_dict = temp1.evo_dict

        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
            self.chat_overlay = ChatOverlay(self.online_manager.send_chat, self.online_manager.get_recent_chat)
        else:
            self.online_manager = None
            self.chat_overlay = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self.animation_online = Animation(
            "character/ow1.png", ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE),
        )
        button_width = 75
        button_height = 75

        center_x = GameSettings.SCREEN_WIDTH // 2
        play_y = GameSettings.SCREEN_HEIGHT * 3 // 4

        settings_x = center_x - button_width + 600
        settings_y = play_y - 520
        self.settings_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            settings_x, settings_y,
            button_width, button_height,
            self.open_settings
        )

        self.backpack_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            settings_x - 80, settings_y,
            button_width, button_height,
            self.open_backpack
        )

        start_y = GameSettings.SCREEN_HEIGHT // 2 - 100
        gap_y = 100

        self.back_button = Button(
            "UI/button_back.png",
            "UI/button_back_hover.png",
            center_x - 255, start_y + 2 * gap_y,
            100, 80,
            self.open_backpack
        )

        self.navigation_button = Button(
            "UI/button_location.png",
            "UI/button_location_hover.png",
            settings_x - 160, settings_y,
            button_width, button_height,
            self.open_navigation_ui
        )

        self.navigation_back_button = Button(
            "UI/button_back.png",
            "UI/button_back_hover.png",
            center_x - 295, start_y + 2 * gap_y,
            100, 80,
            self.open_navigation_ui
        )

        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot02a.png",
            (625, 500)
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 325,
            GameSettings.SCREEN_HEIGHT // 2 - 300
        )

    def open_backpack(self):
        self.showing_bag = not self.showing_bag

    def open_settings(self):
        settings_scene = scene_manager._scenes["settings"]
        for key, scene in scene_manager._scenes.items():
            if scene is scene_manager._current_scene:
                settings_scene.previous_scene_name = key
                break
        else:
            settings_scene.previous_scene_name = "menu"
        scene_manager.change_scene("settings")

    def open_navigation_ui(self):
        self.nav_open = not self.nav_open

    def navigate_to(self, place):
        self.destination = self.destination_dict[place][1]
        start = (int(self.game_manager.player.position.x / GameSettings.TILE_SIZE), int(self.game_manager.player.position.y / GameSettings.TILE_SIZE))
        self.grid = self.game_manager.current_map.create_map_for_navigation()
        self.path = self.game_manager.current_map.bfs_path(self.grid, start, self.destination)
        self.navigating = not self.navigating

    @override
    def enter(self) -> None:
        if self.game_manager.music_on and not self.game_manager.repeated_enter:
            sound_manager.play_sound("RBY 103 Pallet Town.ogg", int(self.game_manager.music_slider_value) / 100)
        if self.online_manager:
            self.online_manager.enter()
        self.game_manager.repeated_enter = True

        
    @override
    def exit(self) -> None:
        sound_manager.stop_all_sounds()
        self.game_manager.repeated_enter = False
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        if self.game_manager.stop_navigation:
            self.navigating = False
            self.game_manager.stop_navigation = False
        self.info_open = self.game_manager.bag.info_check()
        if self.showing_bag:
            self.game_manager.bag.update(dt)
            if not self.info_open:
                self.back_button.update(dt)

        elif self.nav_open:
            self.navigation_back_button.update(dt)
            for btn in self.navigate_to_buttons:
                btn.update(dt)

        elif self.game_manager.shop_open:
            for shopkeeper in self.game_manager.current_shopkeeper:
                shopkeeper.update(dt)

        else:
            self.game_manager.current_map.update(dt)
            if self.game_manager.change_bgm:
                if self.game_manager.current_map_key == "desert.tmx":
                    sound_manager.stop_all_sounds()
                    sound_manager.play_sound("RBY 130 Mt. Moon.ogg", int(self.game_manager.music_slider_value) / 100)
                    self.game_manager.change_bgm = False
                elif self.game_manager.current_map_key == "map.tmx":
                    sound_manager.stop_all_sounds()
                    sound_manager.play_sound("RBY 103 Pallet Town.ogg", int(self.game_manager.music_slider_value) / 100)
                    self.game_manager.change_bgm = False
                elif self.game_manager.current_map_key == "gym.tmx":
                    sound_manager.stop_all_sounds()
                    sound_manager.play_sound("RBY 126 Pokemon Gym.ogg", int(self.game_manager.music_slider_value) / 100)
                    self.game_manager.change_bgm = False

            # Update player and other data
            try:
                if not self.chat_overlay.is_open:
                    if self.game_manager.player:
                        self.game_manager.player.update(dt)
                        if self.game_manager.player.is_moving:
                            self.game_manager.current_map.update_minimap_view(self.game_manager.player.position)
            except:
                if self.game_manager.player:
                    self.game_manager.player.update(dt)
                    if self.game_manager.player.is_moving:
                        self.game_manager.current_map.update_minimap_view(self.game_manager.player.position)               
            for enemy in self.game_manager.current_enemy_trainers:
                enemy.update(dt)
            for shopkeeper in self.game_manager.current_shopkeeper:
                shopkeeper.update(dt)

            self.settings_button.update(dt)
            self.backpack_button.update(dt)
            self.navigation_button.update(dt)
            self.navigate_to_buttons = []

        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name,
                self.game_manager.player.direction.name
            )
            self.animation_online.update(dt)
            self.chat_overlay.update(dt)
            if not self.chat_overlay.is_open and input_manager.key_pressed(pg.K_t):
                self.chat_overlay.open()

    @override
    def draw(self, screen: pg.Surface):
        if self.game_manager.player:
            '''
            [TODO HACKATHON 3]
            Implement the camera algorithm logic here
            Right now it's hard coded, you need to follow the player's positions
            you may use the below example, but the function still incorrect, you may trace the entity.py

            camera = self.game_manager.player.camera
            '''
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
            self.game_manager.current_map.draw_ruin(screen, camera)
            self.game_manager.current_map.draw_mini_map(screen)
            
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        for shopkeeper in self.game_manager.current_shopkeeper:
            shopkeeper.draw(screen, camera)

        if not self.game_manager.shop_open:
            self.settings_button.draw(screen)
            self.backpack_button.draw(screen)
            self.navigation_button.draw(screen)

        camera = self.game_manager.player.camera

        if self.navigating and self.path:
            start = (int(self.game_manager.player.position.x / GameSettings.TILE_SIZE), int(self.game_manager.player.position.y / GameSettings.TILE_SIZE))
            self.path = self.game_manager.current_map.bfs_path(self.grid, start, self.destination)            
            for i in range(len(self.path) - 1):
                x0, y0 = self.path[i]
                x1, y1 = self.path[i + 1]
                dx, dy = x1 - x0, y1 - y0

                self.game_manager.current_map.draw_direction_triangle(
                    screen, camera, x0, y0, (dx, dy)
                )

        if self.nav_open:
            board_x, board_y = self.board_pos
            dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 150))
            screen.blit(dark_overlay, (0, 0))
            screen.blit(self.board_sprite.image, (board_x, board_y))
            self.navigation_back_button.draw(screen)
            gap_y = 70
            skip = 0
            for i, (place, stats) in enumerate(self.destination_dict.items()):
                if stats[0] == self.game_manager.current_map_key:
                    font = pg.font.Font("assets/fonts/Minecraft.ttf", 42)
                    place_text = font.render(f"{place}", True, (0, 0, 0))
                    pos_text = font.render(f"X: {stats[1][0]} Y: {stats[1][1]}", True, (0, 0, 0))
                    screen.blit(place_text, (board_x + 140, board_y + 45 + (i - skip) * gap_y))
                    screen.blit(pos_text, (board_x + 320, board_y + 45 + (i - skip) * gap_y))
                    if not self.navigate_to_buttons:
                        ndic = 0
                        for i, (place, stats) in enumerate(self.destination_dict.items()):
                            if stats[0] == self.game_manager.current_map_key:
                                y_button = board_y + 25 + (i - ndic) * gap_y
                                
                                temp_button = Button(
                                    "UI/choose.png", "UI/choose_hover.png",
                                    board_x + 40, y_button,
                                    550, 70,
                                    lambda there = place: self.navigate_to(there)
                                )
                                self.navigate_to_buttons.append(temp_button)
                            else:
                                ndic += 1
                else:
                    skip += 1
            for btn in self.navigate_to_buttons:
                btn.draw(screen)

        if self.showing_bag:
            board_x, board_y = self.board_pos
            dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 150))
            screen.blit(dark_overlay, (0, 0))
            screen.blit(self.board_sprite.image, (board_x, board_y))
            self.game_manager.bag.draw(screen, (board_x, board_y))
            if not self.info_open:
                self.back_button.draw(screen)

        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    # self.sprite_online.update_pos(pos)
                    # self.sprite_online.draw(screen)
                    self.animation_online.update_pos(pos)
                    self.animation_online.switch(player['direction'].lower())
                    self.animation_online.draw(screen)
            self.chat_overlay.draw(screen)