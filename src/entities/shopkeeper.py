from __future__ import annotations
import pygame as pg
from enum import Enum
from dataclasses import dataclass
from typing import override

import math
import json
from src.sprites import Animation
from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera
from src.entities.player import Player
from src.interface.components import Button

class ShopKeeper(Entity):
    def __init__(self, x, y, game_manager, facing, sprite, items):
        super().__init__(x, y, game_manager)
        self.animation = Animation(
            sprite, ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE),
        )

        self.items = items
        self.item_to_buy = None
        self.item_name = None
        self.item_index = -1
        self.current_money = 0
        self.no_money = False

        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2 

        self.shop_button = Button(
            "UI/button_shop.png",
            "UI/button_shop_hover.png",
            center_x,
            center_y + 150,
            80, 80,
            self.open_shop
        )

        self.leave_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            center_x + 360, center_y - 280,
            80, 80,
            self.open_shop
        )

        self.buy_button = Button(
            "UI/button_buy.png",
            "UI/button_buy_hover.png",
            center_x - 620, center_y - 230,
            280, 160,
            self.buying
        )

        self.sell_button = Button(
            "UI/button_sell.png",
            "UI/button_sell_hover.png",
            center_x -620, center_y - 60,
            280, 160,
            self.selling
        )

        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot01a.png",
            (700, 550)
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 285,
            GameSettings.SCREEN_HEIGHT // 2 - 260
        )

        self.monster = None
        self.index = None
        self.value = 0
        self.temp_buttons_monster_sell = []
        self.temp_buttons_item_buy = []
        self.val_dict = dict()
        self.shop_open = False
        self.sprite = sprite
        self.buy = False
        self.sell = False
        self.is_buying_item = False
        self.is_selling_monster = False


    def open_shop(self):
        self.game_manager.shop_open = not self.game_manager.shop_open
        self.shop_open = not self.shop_open
        self.buy = False
        self.sell = False

    def buying(self):
        self.buy = True
        self.sell = False

    def selling(self):
        self.buy = False
        self.sell = True

    def detect(self):
        player = self.game_manager.player
        player_rect = pg.Rect(player.position.x, player.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
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

    def _get_los_rect(self):
        x = self.position.x
        y = self.position.y + 1 * GameSettings.TILE_SIZE
        enemy_sight_rect = pg.Rect(x, y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        return enemy_sight_rect        

    def draw_item_for_sell(self, screen: pg.Surface):
        board_x, board_y = self.board_pos
        item_start_x = board_x + 40
        item_start_y = board_y + 70
        item_gap_y = 65
        for i, item in enumerate(self.items):
            img_path = f"assets/images/{item['sprite_path']}"
            try:
                img = pg.image.load(img_path).convert_alpha()
                img = pg.transform.scale(img, (60, 60))
            except Exception:
                img = pg.Surface((60, 60))
                img.fill((150, 150, 150))        
            y = item_start_y + i * item_gap_y
            screen.blit(img, (item_start_x, y))
            font = pg.font.Font(None, 24)
            name_text = font.render(f"{item['name']}", True, (255, 255, 255))
            screen.blit(name_text, (item_start_x + 60, y + 15))
            value_count_text = font.render(f"Value: {item["value"]}   Stock: {item["count"]}", True, (0, 0, 0))
            self.val_dict[item["name"]] = self.val_dict.get(item["name"], item["value"])
            screen.blit(value_count_text, (item_start_x + 140, y + 35))
            if not self.temp_buttons_item_buy:
                for i, item in enumerate(self.items):
                    y_button = item_start_y + i * item_gap_y
                    
                    temp_button = Button(
                        "UI/button_shop.png", "UI/button_shop_hover.png",
                        item_start_x + 320, y_button + 15,
                        60, 60,
                        lambda itm=item, num = i: self.buying_item(itm, num)
                    )
                    self.temp_buttons_item_buy.append(temp_button)

    def draw_backpack_monster(self, screen: pg.Surface):
        board_x, board_y = self.board_pos
        mon_start_x = board_x + 40
        mon_start_y = board_y + 70
        mon_gap_y = 65
        for i, mon in enumerate(self.game_manager.bag._monsters_data):
            img_path = f"assets/images/{mon['sprite_path']}"
            try:
                img = pg.image.load(img_path).convert_alpha()
                img = pg.transform.scale(img, (60, 60))
            except Exception:
                img = pg.Surface((60, 60))
                img.fill((150, 150, 150))

            y = mon_start_y + i * mon_gap_y
            screen.blit(img, (mon_start_x, y))
            font = pg.font.Font(None, 24)
            name_text = font.render(f"{mon['name']} Lv{mon['level']}", True, (255, 255, 255))
            hp_text = font.render(f"HP: {mon['hp']}/{mon['max_hp']}", True, (255, 255, 255))
            screen.blit(name_text, (mon_start_x + 60, y + 15))
            screen.blit(hp_text, (mon_start_x + 60, y + 35))
            value = math.ceil((((math.ceil(1000 * mon["hp"] / mon["max_hp"])) / 1000) * 3 * mon["level"]) ** 1.12)
            self.val_dict[mon["name"]] = self.val_dict.get(mon["name"], value)
            value_text = font.render(f"Value: {value}", True, (0, 0, 0))
            screen.blit(value_text, (mon_start_x + 200, y + 25))
            if not self.temp_buttons_monster_sell:
                for i, mon in enumerate(self.game_manager.bag._monsters_data):
                    y_button = mon_start_y + i * mon_gap_y
                    
                    temp_button = Button(
                        "UI/button_money_sign.png", "UI/button_money_sign_hover.png",
                        mon_start_x + 290, y_button + 15,
                        60, 60,
                        lambda m=mon, num = i: self.selling_monster(m, num)
                    )
                    self.temp_buttons_monster_sell.append(temp_button)

    def buying_item(self, item, item_index):
        self.item_to_buy = item
        self.item_name = item["name"]
        self.item_index = item_index
        self.value = self.val_dict[self.item_name]
        self.temp_buttons_item_buy = []
        self.is_buying_item = True

    def selling_monster(self, monster, index):
        self.monster = monster["name"]
        self.index = index
        self.value = self.val_dict[self.monster]
        self.temp_buttons_monster_sell = []
        self.is_selling_monster = True

    def money_checking(self, amount):
        for stuff in self.game_manager.bag._items_data:
            if stuff["name"] == "Coins":
                self.current_money = stuff["count"]
                if self.current_money + amount < 0:
                    self.no_money = True
                    return

    def money_changing(self, amount):
        for stuff in self.game_manager.bag._items_data:
            if stuff["name"] == "Coins":
                self.current_money = stuff["count"]
                if self.current_money + amount < 0:
                    return
                stuff["count"] += amount
                self.value = 0
                break

    def item_changing(self, amount):
        for stuff in self.game_manager.bag._items_data:
            if stuff["name"] == self.item_name:
                stuff["count"] += amount
                break
        else:
            stuff = {
                "name": self.item_name,
                "count": 1,  "sprite_path": self.item_to_buy["sprite_path"], 
                "value": self.value, "stock": 99, "usable": self.item_to_buy["usable"]
            }
            self.game_manager.bag._items_data.append(stuff)

    @override
    def update(self, dt):
        # self._movement.update(self, dt)
        self.animation.update_pos(self.position)
        self.detect()
        if self.detected and not self.shop_open:
            self.shop_button.update(dt)

        if self.shop_open:
            self.leave_button.update(dt)
            self.buy_button.update(dt)
            self.sell_button.update(dt)
            if self.buy:
                for btn in self.temp_buttons_item_buy:
                    btn.update(dt)
            if self.sell:
                for btn in self.temp_buttons_monster_sell:
                    btn.update(dt)
            if self.is_buying_item:
                for idx, item in enumerate(self.items):
                    if item["name"] == self.item_name and idx == self.item_index:
                        self.money_checking(-self.value)
                        if not self.no_money:
                            self.money_changing(-self.value)                            
                            item["count"] -= 1
                            self.item_changing(1)
                        self.no_money = False
                        self.is_buying_item = False
            if self.is_selling_monster:
                for idx, mon in enumerate(self.game_manager.bag._monsters_data):
                    if mon['name'] == self.monster and idx == self.index:
                        self.game_manager.bag._monsters_data.pop(idx)
                        self.money_changing(self.value)
                        self.is_selling_monster = False


    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pg.draw.rect(screen, (20, 120, 0), camera.transform_rect(los_rect), 1)

        if self.detected and not self.shop_open:
            self.shop_button.draw(screen)

        if self.shop_open:
            board_x, board_y = self.board_pos
            dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 150))
            screen.blit(dark_overlay, (0, 0))
            screen.blit(self.board_sprite.image, (board_x, board_y))
            self.leave_button.draw(screen)
            self.buy_button.draw(screen)
            self.sell_button.draw(screen)
            if self.buy:
                self.draw_item_for_sell(screen)
                for btn in self.temp_buttons_item_buy:
                    btn.draw(screen)
            if self.sell:
                self.draw_backpack_monster(screen)
                for btn in self.temp_buttons_monster_sell:
                    btn.draw(screen)

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager):
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None:
            facing = Direction.DOWN
        the_sprite = data.get("sprite")
        the_items = data.get("items")
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            facing,
            the_sprite,
            the_items
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["facing"] = self.direction.name
        base["sprite"] = self.sprite
        base["items"] = self.items
        return base