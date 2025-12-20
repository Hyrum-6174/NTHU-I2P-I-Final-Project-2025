import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item
from src.sprites import Sprite
from src.interface.components import Button
from src.utils.evo_dict import EvoDict

class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []
        
        for stuff in self._items_data:
            if stuff["name"] == "Coins":
                self.money = stuff["count"]
                break

        self.monster_info_buttons = []
        self.info_open = False
        self.monster = None
        self.index = -1
        self.can_evo = False
        temp = EvoDict()
        self.evo_dict = temp.evo_dict
        self.to_evo = False
        self.no_evo = False
        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot02a.png",
            (825, 550)
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 325,
            GameSettings.SCREEN_HEIGHT // 2 - 300
        )

        self.back_button = Button(
            "UI/button_back.png",
            "UI/button_back_hover.png",
            GameSettings.SCREEN_WIDTH // 2 - 255, GameSettings.SCREEN_HEIGHT // 2 + 2 * 80,
            100, 80,
            self.toggle_info
        )

        self.evlove_button = Button(
            "UI/button_evolve.png",
            "UI/button_evolve_hover.png",
            GameSettings.SCREEN_WIDTH // 2 + 155, GameSettings.SCREEN_HEIGHT // 2 + 2 * 60,
            240, 130,
            self.check_evo
        )

    def toggle_info(self):
        self.info_open = not self.info_open

    def check_evo(self):
        lvl_req = self.evo_dict[self.monster["name"]][2]
        money_req = self.evo_dict[self.monster["name"]][3]
        self.check_money()
        if self.monster["level"] >= lvl_req and self.money >= money_req:
            self.to_evo = True
        else:
            self.no_evo = True

    def check_money(self):
        for stuff in self._items_data:
            if stuff["name"] == "Coins":
                self.money = stuff["count"]
                break

    def update(self, dt: float):
        for btn in self.monster_info_buttons:
            btn.update(dt)
        if len(self.monster_info_buttons) > len(self._monsters_data) or len(self.monster_info_buttons) < len(self._monsters_data):
            self.monster_info_buttons = []
        if self.info_open:
            self.back_button.update(dt)
            if self.monster["name"] in self.evo_dict:
                self.evlove_button.update(dt)
            if self.to_evo:
                self.toggle_info()
                for i, mon in enumerate(self._monsters_data):
                    if mon['name'] == self.monster["name"] and i == self.index:
                        # Convert Combatant back to dict before saving
                        self._monsters_data[i] = {
                            "name": self.evo_dict[self.monster["name"]][0],
                            "level": self.monster["level"],
                            "hp": self.monster["hp"],
                            "max_hp": self.monster["max_hp"] + self.evo_dict[self.monster["name"]][4],
                            "sprite_path": self.evo_dict[self.monster["name"]][1],
                            "element": self.monster["element"],
                            "exp": self.monster["exp"],
                            "evo": self.monster["evo"] + 1
                        }
                        self.to_evo = False
                        self.monster_info_buttons = []
                        for stuff in self._items_data:
                            if stuff["name"] == "Coins":
                                stuff["count"] =  self.money


    def draw(self, screen: pg.Surface, pos: tuple[int, int]):
        item_start_x = pos[0] + 60
        item_start_y = pos[1] + 50
        item_gap_y = 50
        for i, item in enumerate(self._items_data):
            img_path = f"assets/images/{item['sprite_path']}"
            try:
                img = pg.image.load(img_path).convert_alpha()
                img = pg.transform.scale(img, (40, 40))
            except Exception:
                img = pg.Surface((40, 40))
                img.fill((200, 200, 200))

            y = item_start_y + i * item_gap_y
            screen.blit(img, (item_start_x, y))
            font = pg.font.Font(None, 24)
            text = font.render(f"{item['name']} x{item['count']}", True, (255, 255, 255))
            screen.blit(text, (item_start_x + 50, y + 10))
        mon_start_x = pos[0] + 270
        mon_start_y = pos[1] + 50
        mon_gap_y = 70
        for i, mon in enumerate(self._monsters_data):
            img_path = f"assets/images/{mon['sprite_path']}"
            try:
                img = pg.image.load(img_path).convert_alpha()
                img = pg.transform.scale(img, (50, 50))
            except Exception:
                img = pg.Surface((50, 50))
                img.fill((150, 150, 150))

            y = mon_start_y + i * mon_gap_y
            screen.blit(img, (mon_start_x, y))
            font = pg.font.Font(None, 22)
            name_text = font.render(f"{mon['name']} Lv{mon['level']}", True, (255, 255, 255))
            hp_text = font.render(f"HP: {mon['hp']}/{mon['max_hp']}", True, (255, 255, 255))
            screen.blit(name_text, (mon_start_x + 60, y + 5))
            screen.blit(hp_text, (mon_start_x + 60, y + 25))
            if not self.monster_info_buttons:
                for i, mon in enumerate(self._monsters_data):
                    y_button = mon_start_y + i * mon_gap_y
                    
                    temp_button = Button(
                        "UI/button_info.png", "UI/button_info_hover.png",
                        mon_start_x + 190, y_button,
                        60, 60,
                        lambda m=mon, num = i: self.open_info(m, num)
                    )
                    self.monster_info_buttons.append(temp_button)
            for btn in self.monster_info_buttons:
                btn.draw(screen)
            if self.info_open:
                board_x, board_y = self.board_pos
                screen.blit(self.board_sprite.image, (board_x, board_y))
                img_path = f"assets/images/{self.monster['sprite_path']}"
                img = pg.image.load(img_path).convert_alpha()
                img = pg.transform.scale(img, (250, 250))
                screen.blit(img, (board_x + 50, board_y+ 50))
                self.back_button.draw(screen)
                font = pg.font.Font(None, 42)
                lvl_text = font.render(f"level: {self.monster["level"]}", True, (0, 0, 0))
                hp_text = font.render(f"HP: {self.monster["hp"]}/{self.monster["max_hp"]}", True, (0, 0, 0))
                screen.blit(lvl_text, (board_x + 420, board_y+ 180))
                screen.blit(hp_text, (board_x + 420, board_y+ 210))
                if self.monster["name"] in self.evo_dict:
                    self.evlove_button.draw(screen)
                    evo_text = font.render(f"Evolve to {self.evo_dict[self.monster["name"]][0]} lvl req {self.evo_dict[self.monster["name"]][2]} money req {self.evo_dict[self.monster["name"]][3]}",True, (0,0,0))
                    screen.blit(evo_text, (board_x + 50, board_y+ 350))
                    self.can_evo = True
                else:
                    evo_text = font.render("nope", True, (0, 0, 0))
                    screen.blit(evo_text, (board_x + 50, board_y+ 350))

    def open_info(self, monster, index):
        self.info_open = True
        self.monster = monster
        self.index = index

    def info_check(self):
        return self.info_open

    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        bag = cls(monsters, items)
        return bag