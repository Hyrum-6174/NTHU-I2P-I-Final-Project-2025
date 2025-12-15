from __future__ import annotations
from src.utils import Logger, GameSettings, Position, Teleport
import json, os
import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maps.map import Map
    from src.entities.player import Player
    from src.entities.enemy_trainer import EnemyTrainer
    from src.entities.shopkeeper import ShopKeeper
    from src.data.bag import Bag

class GameManager:
    # Entities
    player: Player | None
    enemy_trainers: dict[str, list[EnemyTrainer]]
    shopkeepers: dict[str, list[ShopKeeper]]
    bag: "Bag"
    
    
    # Map properties
    current_map_key: str
    maps: dict[str, Map]
    
    # Changing Scene properties
    should_change_scene: bool
    next_map: str
    
    def __init__(self, maps: dict[str, Map], start_map: str, 
                 player: Player | None,
                 enemy_trainers: dict[str, list[EnemyTrainer]], 
                 shopkeepers: dict[str, list[ShopKeeper]],
                 bag: Bag | None = None,
                 enemy: Bag | None = None,
                 ):
                     
        from src.data.bag import Bag
        # Game Properties
        self.maps = maps
        self.current_map_key = start_map
        self.player = player
        self.enemy_trainers = enemy_trainers
        self.shopkeepers = shopkeepers
        self.bag = bag if bag is not None else Bag([], [])
        self.enemy = enemy if enemy is not None else Bag([], [])

        self.change_bgm = False
        self.music_on = True
        self.music_slider_value = 50
        self.repeated_enter = False
        self.saving = False
        self.just_load = False
        self.shop_open = False

        # Check If you should change scene
        self.should_change_scene = False
        self.next_map = ""
        
    @property
    def current_map(self) -> Map:
        return self.maps[self.current_map_key]
        
    @property
    def current_enemy_trainers(self) -> list[EnemyTrainer]:
        return self.enemy_trainers[self.current_map_key]
        
    @property
    def current_teleporter(self) -> list[Teleport]:
        return self.maps[self.current_map_key].teleporters

    @property
    def current_shopkeeper(self) -> list[ShopKeeper]:
        return self.shopkeepers[self.current_map_key]

    def switch_map(self, target: str, record_spawn: bool = True) -> None:
        if target not in self.maps:
            Logger.warning(f"Map '{target}' not loaded; cannot switch.")
            return

        self.next_map = target
        self.should_change_scene = True
            
    def try_switch_map(self) -> None:
        
        if self.should_change_scene:
            # print(self.current_map_key)
            # print(self.just_load)
            self.current_map_key = self.next_map
            self.next_map = ""
            self.should_change_scene = False
            if self.player and not self.just_load:
                self.player.position = self.maps[self.current_map_key].spawn
                self.change_bgm = True
            # else:
            #     with open("saves/save.json", "r") as f:
            #         game_data1 = json.load(f)    
            #     self.player.position.x = game_data1["player"]['x'] * GameSettings.TILE_SIZE
            #     self.player.position.y = game_data1['player']['y'] * GameSettings.TILE_SIZE
            #     print(self.current_map_key, 1)
            #     self.just_load = False
            
    def check_collision(self, rect: pg.Rect) -> bool:
        if self.maps[self.current_map_key].check_collision(rect):
            return True
        for entity in self.enemy_trainers[self.current_map_key]:
            if rect.colliderect(entity.animation.rect):
                return True
        for entity in self.shopkeepers[self.current_map_key]:
            if rect.colliderect(entity.animation.rect):
                return True
        return False

    def save(self, path: str) -> None:
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            Logger.info(f"Game saved to {path}")
        except Exception as e:
            Logger.warning(f"Failed to save game: {e}")
             
    @classmethod
    def load(cls, path: str) -> "GameManager | None":
        if not os.path.exists(path):
            Logger.error(f"No file found: {path}, ignoring load function")
            return None

        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, object]:
        map_blocks: list[dict[str, object]] = []
        for key, m in self.maps.items():
            # block = m.to_dict(player_position=self.player.position if self.current_map_key == key else None)
            if self.current_map_key == key:
                px = {
                    "x": self.player.position.x / GameSettings.TILE_SIZE,
                    "y": self.player.position.y / GameSettings.TILE_SIZE,
                }
            else:
                px = None
            # print(">>> Saving:", type(self.player.position.x), self.player.position.x)
            # print(">>> Current map spawn:", type(self.current_map.spawn.x), self.current_map.spawn.x)
            block = m.to_dict()
            block["enemy_trainers"] = [t.to_dict() for t in self.enemy_trainers.get(key, [])]
            block["shopkeepers"] = [c.to_dict() for c in self.shopkeepers.get(key, [])]
            # spawn = self.player_spawns.get(key)
            # block["player"] = {
            #     "x": spawn["x"] / GameSettings.TILE_SIZE,
            #     "y": spawn["y"] / GameSettings.TILE_SIZE
            # }
            map_blocks.append(block)
        
        return {
            "map": map_blocks,
            "current_map": self.current_map_key,
            "player": self.player.to_dict() if self.player is not None else None,
            "bag": self.bag.to_dict(),
            "enemy": self.enemy.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "GameManager":
        from src.maps.map import Map
        from src.entities.player import Player
        from src.entities.enemy_trainer import EnemyTrainer
        from src.entities.shopkeeper import ShopKeeper
        from src.data.bag import Bag
        
        Logger.info("Loading maps")
        maps_data = data["map"]
        maps: dict[str, Map] = {}
        player_spawns: dict[str, Position] = {}
        trainers: dict[str, list[EnemyTrainer]] = {}
        shopkeepers: dict[str, list[ShopKeeper]] = {}

        for entry in maps_data:
            path = entry["path"]
            maps[path] = Map.from_dict(entry)
            sp = entry.get("player")
            if sp:
                player_spawns[path] = Position(
                    sp["x"] * GameSettings.TILE_SIZE,
                    sp["y"] * GameSettings.TILE_SIZE
                )
        current_map = data["current_map"]
        gm = cls(
            maps, current_map,
            None, # Player
            trainers,
            shopkeepers,
            bag=None,
            enemy=None,
        )
        gm.current_map_key = current_map
        
        Logger.info("Loading enemy trainers")
        Logger.info("Loading shopkeepers")
        for m in data["map"]:
            raw_data = m["enemy_trainers"]
            gm.enemy_trainers[m["path"]] = [EnemyTrainer.from_dict(t, gm) for t in raw_data]
            shopkeepers_data = m["shopkeepers"]
            gm.shopkeepers[m["path"]] = [ShopKeeper.from_dict(t, gm) for t in shopkeepers_data]
        
        Logger.info("Loading Player")
        if data.get("player"):
            gm.player = Player.from_dict(data["player"], gm)
        
        Logger.info("Loading bag")
        from src.data.bag import Bag as _Bag
        gm.bag = Bag.from_dict(data.get("bag", {})) if data.get("bag") else _Bag([], [])

        Logger.info("Loading enemy")
        from src.data.bag import Bag as _Bag
        gm.enemy = Bag.from_dict(data.get("enemy", {})) if data.get("enemy") else _Bag([], [])

        return gm