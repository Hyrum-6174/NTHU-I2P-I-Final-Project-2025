import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item
from src.sprites import Sprite

class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

    def update(self, dt: float):
        pass

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