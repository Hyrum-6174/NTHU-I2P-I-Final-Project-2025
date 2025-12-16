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

        self.minimap_tile_radius = 16
        self.minimap_view = pg.Surface(
            (
                GameSettings.TILE_SIZE // 6 * 2 * self.minimap_tile_radius,
                GameSettings.TILE_SIZE // 6 * 2 * self.minimap_tile_radius
            ),
            pg.SRCALPHA
        )


        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot02a.png",
            (625, 500)
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 325,
            GameSettings.SCREEN_HEIGHT // 2 - 300
        )



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
        screen.blit(self.minimap_view, (0, 0))
        center_x = self.minimap_view.get_width() // 2
        center_y = self.minimap_view.get_height() // 2
        pg.draw.circle(screen, (0, 0, 0), (center_x, center_y), 6)
        pg.draw.circle(screen, (255, 255, 255), (center_x, center_y), 5)

    def update_minimap_view(self, player_pos: Position):
        tile_size = GameSettings.TILE_SIZE // 6
        radius = self.minimap_tile_radius

        center_x = (player_pos.x // GameSettings.TILE_SIZE) * tile_size
        center_y = (player_pos.y // GameSettings.TILE_SIZE) * tile_size

        view_px = radius * tile_size
        view_size = radius * 2 * tile_size

        src_rect = pg.Rect(
            center_x - view_px,
            center_y - view_px,
            view_size,
            view_size
        )

        self.minimap_view.fill((0, 0, 0, 0))

        self.minimap_view.blit(self.minimap, (0, 0), src_rect)

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
            image = pg.transform.scale(image, (GameSettings.TILE_SIZE // 6, GameSettings.TILE_SIZE // 6))
            target.blit(image, (x * (GameSettings.TILE_SIZE // 6), y * (GameSettings.TILE_SIZE // 6)))

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
