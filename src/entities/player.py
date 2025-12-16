from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager, scene_manager
from src.utils import Position, Direction, PositionCamera, GameSettings
from src.core import GameManager
import math
from typing import override
import time

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)
        self.just_tp = False
        self.draw_player_under = False
        self.is_moving = False

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        ''' 
        [TODO HACKATHON 2] Calculate the distance change based on input, 
        and then normalize diagonal movement 
        '''
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1 
            self.animation.switch("left")
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1
            self.animation.switch("right")
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1
            self.animation.switch("up")
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1
            self.animation.switch("down")
        


        # Normalize diagonal movement
        length = math.hypot(dis.x, dis.y)
        if length > 0:
            dis.x = (dis.x / length) * self.speed * dt
            dis.y = (dis.y / length) * self.speed * dt
            self.is_moving = True
        else:
            self.is_moving = False

        ''' [TODO HACKATHON 4] Check if there is collision with map or NPCs. 
        Update X and Y separately to prevent glitchy teleportation 
        '''

        # --- Update X first ---
        self.position.x += dis.x
        player_rect = pg.Rect(int(self.position.x), int(self.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)

        # Map collision check (X)
        if self.game_manager.current_map.check_collision(player_rect):
            self.position.x = self._snap_to_grid(self.position.x)

        # NPC collision check (X)
        for npc in self.game_manager.current_enemy_trainers:
            npc_rect = pg.Rect(int(npc.position.x), int(npc.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
            if player_rect.colliderect(npc_rect):
                self.position.x = self._snap_to_grid(self.position.x)
                break

        # shopkeeper collision check (X)
        for npc in self.game_manager.current_shopkeeper:
            npc_rect = pg.Rect(int(npc.position.x), int(npc.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
            if player_rect.colliderect(npc_rect):
                self.position.x = self._snap_to_grid(self.position.x)
                break

        # --- Update Y next ---
        self.position.y += dis.y
        player_rect = pg.Rect(int(self.position.x), int(self.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)

        # Map collision check (Y)
        if self.game_manager.current_map.check_collision(player_rect):
            self.position.y = self._snap_to_grid(self.position.y)

        # NPC collision check (Y)
        for npc in self.game_manager.current_enemy_trainers:
            npc_rect = pg.Rect(int(npc.position.x), int(npc.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
            if player_rect.colliderect(npc_rect):
                self.position.y = self._snap_to_grid(self.position.y)
                break

        # shopkeeper collision check (Y)
        for npc in self.game_manager.current_shopkeeper:
            npc_rect = pg.Rect(int(npc.position.x), int(npc.position.y), GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
            if player_rect.colliderect(npc_rect):
                self.position.y = self._snap_to_grid(self.position.y)
                break

        # overlap check
        # if self.game_manager.current_map.check_ruin_collision(player_rect):
        #     self.draw_player_under = True
        # else:
        #     self.draw_player_under = False

        # --- Teleportation check ---
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            ''' 
            [TODO HACKATHON 6] Move player to the teleport's pixel position 
            first so first-time return lands at the door, then switch map
            '''
            current_time = time.time()
            if self.just_tp and current_time < self.tp_cooldown_end:
                return None
            elif self.just_tp and current_time >= self.tp_cooldown_end:
                self.just_tp = False
            self.just_tp = False  # cooldown finished
            self.game_manager.maps[self.game_manager.current_map_key].spawn = self.position
            self.game_manager.switch_map(tp.destination) # switch map normally
            # self.position = tp.pos.copy()  # manually set player to teleport position
            self.just_tp = True 
            self.tp_cooldown_end = current_time + 3
        
        # bush check
        if self.game_manager.current_map.check_bush(player_rect) and input_manager.key_pressed(pg.K_SPACE):        
            scene_manager.change_scene("catch")
            

        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)

    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
        # return {
        #     "x": self.position.x / GameSettings.TILE_SIZE,
        #     "y": self.position.y / GameSettings.TILE_SIZE,
        #     # Add other Player-specific info here if needed
        # }

    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)
