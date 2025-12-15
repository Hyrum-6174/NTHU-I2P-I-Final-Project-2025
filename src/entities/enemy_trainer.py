from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from src.sprites import Animation
from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera
from src.entities.player import Player
from random import randint

class EnemyTrainerClassification(Enum):
    STATIONARY = "stationary"

@dataclass
class IdleMovement:
    def __init__(self):
        self.timer = 0
    def update(self, enemy: "EnemyTrainer", dt: float) -> None:
        directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        idx = randint(0, 3)
        self.timer += 1
        if self.timer > 300:
            self.timer = 0
            enemy._set_direction(directions[idx])

class EnemyTrainer(Entity):
    classification: EnemyTrainerClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    detected: bool
    los_direction: Direction

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        classification: EnemyTrainerClassification = EnemyTrainerClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
        sprite: Sprite | None = "character/ow1.png"
    ) -> None:
        super().__init__(x, y, game_manager)
        self.classification = classification
        self.max_tiles = max_tiles
        self.game_manager = game_manager
        self.player = self.game_manager.player
        self.animation = Animation(
            sprite, ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE),
        )
        self.sprite = sprite

        if classification == EnemyTrainerClassification.STATIONARY:
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.detected = False


    def save__temp_game(self):
        if not self.game_manager:
            return
        
        path = "saves/temp.json"
        self.game_manager.save(path)


    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            print("enter battle")
            
            self.save__temp_game()
            scene_manager.change_scene("battle")
        self.animation.update_pos(self.position)

    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected:
            self.warning_sign.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:
        '''
        TODO: Create hitbox to detect line of sight of the enemies towards the player
        '''
        if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
            wh_mode = 0
            if self.direction == Direction.RIGHT:
                x = self.position.x + GameSettings.TILE_SIZE
                y = self.position.y - GameSettings.TILE_SIZE
            else:
                x = self.position.x - 5 * GameSettings.TILE_SIZE
                y = self.position.y - GameSettings.TILE_SIZE             
        else:
            wh_mode = 1
            if self.direction == Direction.UP:
                x = self.position.x - GameSettings.TILE_SIZE
                y = self.position.y - 5 * GameSettings.TILE_SIZE
            else:
                x = self.position.x - GameSettings.TILE_SIZE
                y = self.position.y + GameSettings.TILE_SIZE                
        
        # x = self.position.x - mode * GameSettings.TILE_SIZE + abs(mode - 1) * GameSettings.TILE_SIZE * 1
        # y = self.position.y + mode * GameSettings.TILE_SIZE - abs(mode - 1) * GameSettings.TILE_SIZE * 1

        enemy_sight_width = wh_mode * GameSettings.TILE_SIZE * 3 + abs(wh_mode - 1) * GameSettings.TILE_SIZE * 5
        enemy_sight_height = wh_mode * GameSettings.TILE_SIZE * 5 + abs(wh_mode - 1) * GameSettings.TILE_SIZE * 3

        enemy_sight_rect = pygame.Rect(x, y, enemy_sight_width, enemy_sight_height)
        return enemy_sight_rect

    def _has_los_to_player(self) -> None:
        player = self.game_manager.player
        player_rect = pygame.Rect(player.position.x, player.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        if player is None:
            self.detected = False
            return
        los_rect = self._get_los_rect()
        if los_rect is None:
            self.detected = False
            return
        '''
        TODO: Implement line of sight detection
        If it's detected, set self.detected to True
        '''
        if los_rect.colliderect(player_rect):
            self.detected = True
            # print("detected")
        else:
            self.detected = False

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "EnemyTrainer":
        classification = EnemyTrainerClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == EnemyTrainerClassification.STATIONARY:
            facing = Direction.DOWN
        the_sprite = data.get("sprite")
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            classification,
            max_tiles,
            facing,
            the_sprite
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        base["sprite"] = self.sprite
        return base