from __future__ import annotations
import pygame as pg
import pytmx
from typing import override
from src.utils import load_tmx, Position, GameSettings, PositionCamera, Teleport
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from src.data.bag import Bag
from src.sprites import Sprite
import json
from src.core.managers import GameManager
import math
import time




class Map:
    # Map Properties
    path_name: str
    tmxdata: pytmx.TiledMap
    # Position Argument
    spawn: Position
    teleporters: list[Teleport]
    # Rendering Properties
    _surface: pg.Surface
    _collision_map: list[pg.Rect]
    settings_button: Button
    backpack_button: Button
    game_manager: "GameManager"  # will be attached after load
    
    def open_settings(self):
        # settings_scene = scene_manager._scenes["settings"]
        # for key, scene in scene_manager._scenes.items():
        #     if scene is scene_manager._current_scene:
        #         settings_scene.previous_scene_name = key
        #         break
        # else:
        #     settings_scene.previous_scene_name = "menu"
        # scene_manager.change_scene("settings")
        pass

    def __init__(self, path: str, tp: list[Teleport], spawn: Position):
        

        self.path_name = path
        self.tmxdata = load_tmx(path)
        self.spawn = spawn
        self.teleporters = tp
        self.showing_bag = False
        self.bag = Bag()
        
        self.just_tp = False


        pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE
        pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE

        self._surface = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_layers(self._surface)
        self.minimap = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_minimap_layers(self.minimap)
        self._collision_map = self._create_collision_map()
        self._ruin_map = self._create_ruin_map()
        self._bush_map = self._create_bush_map()

        # button_width = 75
        # button_height = 75

        # center_x = GameSettings.SCREEN_WIDTH // 2
        # play_y = GameSettings.SCREEN_HEIGHT * 3 // 4

        # settings_x = center_x - button_width + 600
        # settings_y = play_y - 520
        # self.settings_button = Button(
        #     "UI/button_setting.png", "UI/button_setting_hover.png",
        #     settings_x, settings_y,
        #     button_width, button_height,
        #     self.open_settings
        # )

        # self.backpack_button = Button(
        #     "UI/button_backpack.png", "UI/button_backpack_hover.png",
        #     settings_x - 80, settings_y,
        #     button_width, button_height,
        #     self.open_backpack
        # )

        # center_x = GameSettings.SCREEN_WIDTH // 2
        # start_y = GameSettings.SCREEN_HEIGHT // 2 - 100
        # gap_y = 100

        # self.back_button = Button(
        #     "UI/button_back.png",
        #     "UI/button_back_hover.png",
        #     center_x - 185, start_y + 2 * gap_y,
        #     100, 80,
        #     self.open_backpack
        # )

        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot02a.png",
            (625, 500)
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 325,
            GameSettings.SCREEN_HEIGHT // 2 - 300
        )

    # def open_backpack(self):
    #     self.showing_bag = not self.showing_bag

    # def draw_backpack(self, screen: pg.Surface):
        
    #     with open("saves/temp.json", "r") as f:
    #         game_data = json.load(f)

    #     self.bag.from_dict(game_data["bag"])
    #     board_x, board_y = self.board_pos
    #     screen.blit(self.board_sprite.image, (board_x, board_y))

    #     item_start_x = board_x + 40
    #     item_start_y = board_y + 20
    #     item_gap_y = 50
    #     for i, item in enumerate(game_data["bag"]["items"]):
    #         img_path = f"assets/images/{item['sprite_path']}"
    #         try:
    #             img = pg.image.load(img_path).convert_alpha()
    #             img = pg.transform.scale(img, (40, 40))
    #         except Exception:
    #             img = pg.Surface((40, 40))
    #             img.fill((200, 200, 200))

    #         y = item_start_y + i * item_gap_y
    #         screen.blit(img, (item_start_x, y))
    #         font = pg.font.Font(None, 24)
    #         text = font.render(f"{item['name']} x{item['count']}", True, (255, 255, 255))
    #         screen.blit(text, (item_start_x + 50, y + 10))

    #     mon_start_x = board_x + 270
    #     mon_start_y = board_y + 20
    #     mon_gap_y = 70
    #     for i, mon in enumerate(game_data["bag"]["monsters"]):
    #         img_path = f"assets/images/{mon['sprite_path']}"
    #         try:
    #             img = pg.image.load(img_path).convert_alpha()
    #             img = pg.transform.scale(img, (50, 50))
    #         except Exception:
    #             img = pg.Surface((50, 50))
    #             img.fill((150, 150, 150))

    #         y = mon_start_y + i * mon_gap_y
    #         screen.blit(img, (mon_start_x, y))
    #         font = pg.font.Font(None, 22)
    #         name_text = font.render(f"{mon['name']} Lv{mon['level']}", True, (255, 255, 255))
    #         hp_text = font.render(f"HP: {mon['hp']}/{mon['max_hp']}", True, (255, 255, 255))
    #         screen.blit(name_text, (mon_start_x + 60, y + 5))
    #         screen.blit(hp_text, (mon_start_x + 60, y + 25))

    @override
    def update(self, dt: float):
        # self.settings_button.update(dt)
        # self.backpack_button.update(dt)
        # if self.showing_bag:
        #     self.bag.update(dt)
        #     self.back_button.update(dt)
        pass

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera):
        screen.blit(self._surface, camera.transform_position(Position(0, 0)))
        if GameSettings.DRAW_HITBOXES:
            for rect in self._collision_map:
                pg.draw.rect(screen, (255, 0, 0), camera.transform_rect(rect), 1)
        
            for rect in self._bush_map:
                pg.draw.rect(screen, (0, 255, 0), camera.transform_rect(rect), 1)

    def draw_ruin(self, screen: pg.Surface, camera: PositionCamera):
        for image, rect in self._ruin_map:
            screen.blit(image, camera.transform_rect(rect))

    def draw_mini_map(self, screen: pg.Surface):
        screen.blit(self.minimap, (0, 0))
        pass

    def check_collision(self, rect: pg.Rect) -> bool:
        for coll_rect in self._collision_map:
            if rect.colliderect(coll_rect):
                return True
        return False

    # def check_ruin_collision(self, rect: pg.Rect):
    #     for coll_rect in self._ruin_map:
    #         if rect.colliderect(coll_rect):
    #             return True
    #     return False       

    def check_teleport(self, pos: Position) -> Teleport | None:
        player_rect = pg.Rect(pos.x, pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)

        current_time = time.time()

        # Only allow teleport if cooldown has passed
        if self.just_tp and current_time < self.tp_cooldown_end:
            return None
        elif self.just_tp and current_time >= self.tp_cooldown_end:
            self.just_tp = False  # cooldown finished

        for tp in self.teleporters:
            tp_rect = pg.Rect(tp.pos.x, tp.pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
            if player_rect.colliderect(tp_rect) and not self.just_tp:
                self.just_tp = True
                self.tp_cooldown_end = current_time + 3  # 3-second cooldown
                return tp

        return None

    def _render_all_layers(self, target: pg.Surface) -> None:
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(target, layer)

    def _render_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer) -> None:
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image is None:
                continue
            image = pg.transform.scale(image, (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
            target.blit(image, (x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE))

    def _render_all_minimap_layers(self, target: pg.Surface) -> None:
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_minimap_tile_layer(target, layer)

    def _render_minimap_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer) -> None:
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image is None:
                continue
            image = pg.transform.scale(image, (GameSettings.TILE_SIZE / 6, GameSettings.TILE_SIZE / 6))
            target.blit(image, (x * GameSettings.TILE_SIZE/6, y * GameSettings.TILE_SIZE/6))

    def _create_collision_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("collision" in layer.name.lower() or "house" in layer.name.lower()):
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(pg.Rect(
                            x * GameSettings.TILE_SIZE,
                            y * GameSettings.TILE_SIZE,
                            GameSettings.TILE_SIZE,
                            GameSettings.TILE_SIZE
                        ))
        return rects

    def _create_ruin_map(self):
        tiles = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and "ruin" in layer.name.lower():
                for x, y, gid in layer:
                    if gid != 0:
                        image = self.tmxdata.get_tile_image_by_gid(gid)
                        if image is None:
                            continue
                        
                        image = pg.transform.scale(
                            image,
                            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
                        )

                        rect = pg.Rect(
                            x * GameSettings.TILE_SIZE,
                            y * GameSettings.TILE_SIZE,
                            GameSettings.TILE_SIZE,
                            GameSettings.TILE_SIZE
                        )

                        tiles.append((image, rect))
        return tiles

    def _create_bush_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("pokemonbush" in layer.name.lower()): 
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(pg.Rect(
                            x * GameSettings.TILE_SIZE,
                            y * GameSettings.TILE_SIZE,
                            GameSettings.TILE_SIZE,
                            GameSettings.TILE_SIZE
                        ))
        return rects
    
    def check_bush(self, rect: pg.Rect) -> bool:
        for bush_rect in self._bush_map:
            if rect.colliderect(bush_rect):
                return True
        return False





    @classmethod
    def from_dict(cls, data: dict) -> "Map":
        tp = [Teleport.from_dict(t) for t in data["teleport"]]
        pos = Position(data["player"]["x"] * GameSettings.TILE_SIZE, data["player"]["y"] * GameSettings.TILE_SIZE)
        return cls(data["path"], tp, pos)

    def to_dict(self):
        return {
            "path": self.path_name,
            "teleport": [t.to_dict() for t in self.teleporters],
            "player": {
                "x": self.spawn.x // GameSettings.TILE_SIZE,
                "y": self.spawn.y // GameSettings.TILE_SIZE,
            }
        }
