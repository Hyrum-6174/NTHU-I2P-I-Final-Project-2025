from __future__ import annotations
import pygame as pg

from typing import override
from src.scenes.scene import Scene
from src.core.managers import GameManager
from src.interface.components import Button
from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.sprites import Sprite
import json
import math
from random import randint
from src.core.services import input_manager, scene_manager, sound_manager

class BattleScene(Scene):
    
    background: BackgroundSprite
    attack_button: Button
    item_button: Button
    action_button: Button



    class Combatant:
        def __init__(self, data: dict, sprite_size: tuple[int, int]):
            self.name = data['name']
            self.level = data['level']
            self.max_hp = data['max_hp']
            self.hp = data['hp']
            self.element = data["element"]
            self.exp = data["exp"]
            self.evo = data["evo"]
            if self.element == "fire":
                self.element_icon = Sprite("ingame_ui/fire_icon.png", (80, 80))
            elif self.element == "water":
                self.element_icon = Sprite("ingame_ui/water_icon.png", (80, 80))
            elif self.element == "nature":
                self.element_icon = Sprite("ingame_ui/nature_icon.png", (80, 80))
            self.attack = randint(int(self.level * 0.8), int(self.level * 1.2)) * (1 + 0.1 * self.evo)
            self.defence = randint(int(self.level * 0.4), int(self.level * 0.6)) * (1 + 0.05 * self.evo)
            self.sprite = Sprite(data['sprite_path'], sprite_size)
            self.sprite_path = data['sprite_path']
            self.weak_against_to = {
                "fire": "water",
                "water": "nature",
                "nature": "fire"
            }

        def take_damage(self, amount: int):
            self.hp -= amount
            if self.hp < 0:
                self.hp = 0







    def __init__(self, game_manager: GameManager | None = None):
        super().__init__()

        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = game_manager
        self.item = self.game_manager.bag._items_data
        # path = "saves/temp.json"
        # new_gm = self.game_manager.load(path)
        # self.game_manager = new_gm
        self.monster_index = -1
        self.bag = self.game_manager.bag
        self.monster_chosen = False
        self.chosen_monster: BattleScene.Combatant | None = None
        self.temp_buttons = []
        self.temp_buttons_item = []
        self.enemy = None
        self.choosing_enemy()
        self.going_back = False

        self.something_timer = 10 ** 20
        self.something_just_happened = False
        self.event_texts = []

        self.my_turn = True
        self.in_attack = False
        self.using_item = False
        self.open_backpack = False
        self.doing_action = False
        self.level_up = False
        self.exp_gain = 0
        self.level_incresed = 0
        self.atk_buff_count = 0
        self.def_buff_count = 0

        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2 
        
        self.alpha = 0
        self.beta = 0

        button_width = 160
        button_height = 90
        gap_x = button_width + 20
        gap_y = button_height + 20

        self.attack_button = Button(
            "UI/button_attack.png",
            "UI/button_attack_hover.png",
            center_x + 240, center_y + 140,
            button_width, button_height,
            self.attack
        )

        self.item_button = Button(
            "UI/button_item.png",
            "UI/button_item_hover.png",
            center_x + 240, center_y + 140 + gap_y,
            button_width, button_height,
            self.use_item
        )

        self.action_button = Button(
            "UI/button_action.png",
            "UI/button_action_hover.png",
            center_x + 240 + gap_x, center_y + 140,
            button_width, button_height,
            self.action
        )

        self.suicide_button = Button(
            "UI/button_suicide.png",
            "UI/button_suicide_hover.png",
            center_x + 240, center_y + 140,
            button_width, button_height,
            self.commit_suicide            
        )

        self.return_button = Button(
            "UI/button_return.png",
            "UI/button_return_hover.png",
            center_x + 240 + gap_x, center_y + 140 + gap_y,
            button_width, button_height,
            self.returning
        )

        self.item_return_button= Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            center_x + 360, center_y - 280,
            80, 80,
            self.return_from_bag
        )



        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot02a.png",
            (625, 500)
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 325,
            GameSettings.SCREEN_HEIGHT // 2 - 300
        )


    def attack(self):
        # print("attack")
        self.in_attack = True
        self.my_turn = False
        self.normal_attack(self.chosen_monster, self.enemy)
        

        self.in_attack = False
        

    def use_item(self):
        self.using_item = True
        self.open_backpack = True

    def using_an_item(self, item, index):
        item_name = item["name"]
        if item["usable"] == "no":
            return

        font = pg.font.Font(None, 42)
        TEXT_COLOR = (0, 0, 0)
        DAMAGE_COLOR = (200, 40, 40)
        BONUS_COLOR  = (40, 120, 200)
        parts = []
        if item_name == "Healing Potion":
            original_hp = self.chosen_monster.hp
            self.chosen_monster.hp += 50
            self.chosen_monster.hp = min(self.chosen_monster.max_hp, self.chosen_monster.hp)
            self.item[index]["count"] -= 1
            sound_manager.play_sound("match-confirm.ogg", int(self.game_manager.music_slider_value) / 100)
            parts = [
                (f"{self.chosen_monster.name} heals for ", TEXT_COLOR),
                (f"{self.chosen_monster.hp - original_hp}", BONUS_COLOR), (f" hp", TEXT_COLOR)
            ]
        elif item_name == "Might Potion":
            original_atk = self.chosen_monster.attack
            self.chosen_monster.attack = original_atk * 1.3
            self.atk_buff_count += 1
            self.item[index]["count"] -= 1
            sound_manager.play_sound("match-confirm.ogg", int(self.game_manager.music_slider_value) / 100)
            parts = [
                (f"{self.chosen_monster.name} increases ", TEXT_COLOR),
                (f"{original_atk * 0.3}", BONUS_COLOR), (f" attack", TEXT_COLOR)
            ]
        elif item_name == "Defense Potion":
            original_def = self.chosen_monster.defence
            self.chosen_monster.defence = original_def * 1.15
            self.def_buff_count += 1
            self.item[index]["count"] -= 1
            sound_manager.play_sound("match-confirm.ogg", int(self.game_manager.music_slider_value) / 100)
            parts = [
                (f"{self.chosen_monster.name} increases ", TEXT_COLOR),
                (f"{original_def * 0.15}", BONUS_COLOR), (f" defense", TEXT_COLOR)
            ]        
        rendered_parts = []
        x_offset = 0
        for text, color in parts:
            surf = font.render(text, True, color)
            rendered_parts.append((surf, x_offset))
            x_offset += surf.get_width()
        self.event_texts.append(rendered_parts)
        self.using_item = False
        self.temp_buttons_item = []
        self.something_just_happened = True
        self.my_turn = False
            

    def action(self):
        self.doing_action = True
        

  
       



    def normal_attack(self, attacker, receiver):
        weak_against = 0
        strong_against = 0
        extra_dmg = 0
        original_dmg = math.ceil(max(attacker.attack - receiver.defence + randint(1, 10), 1))
        if attacker.weak_against_to[attacker.element] == receiver.element:
            weak_against = 1
            extra_dmg = original_dmg * -0.2
        if receiver.weak_against_to[receiver.element] == attacker.element:
            strong_against = 1
            extra_dmg = original_dmg * strong_against * 0.2
        damage = math.ceil(max(original_dmg * (weak_against * -0.2 + 1) * (strong_against * 0.2 + 1), 1))
        receiver.take_damage(damage)
        self.something_just_happened = True
        sound_manager.play_sound("taiko-normal-hitfinish.ogg", int(self.game_manager.music_slider_value) / 100)

        font = pg.font.Font(None, 42)
        # event_text = font.render(f"{attacker.name} deals {original_dmg} + {extra_dmg} damage to {receiver.name}", True, (0, 0, 0))

        TEXT_COLOR = (0, 0, 0)
        DAMAGE_COLOR = (200, 40, 40)
        BONUS_COLOR  = (40, 120, 200) 
        parts = []
        parts = [
            (f"{attacker.name} deals ", TEXT_COLOR),
            (str(original_dmg), DAMAGE_COLOR),
        ]
        if extra_dmg != 0:
            parts.append((" + ", TEXT_COLOR))
            parts.append((str(int(extra_dmg)), BONUS_COLOR))
        parts.append((f" damage to {receiver.name}", TEXT_COLOR))
        rendered_parts = []
        x_offset = 0
        for text, color in parts:
            surf = font.render(text, True, color)
            rendered_parts.append((surf, x_offset))
            x_offset += surf.get_width()
        self.event_texts.append(rendered_parts)
        
        if weak_against == 1:
            extra_text = font.render("It's not very effective.", True, (0, 0, 0))
            self.event_texts.append([(extra_text, 0)])
        elif strong_against == 1:
            extra_text = font.render("It's very effective!", True, (0, 0, 0))
            self.event_texts.append([(extra_text, 0)])
        # self.event_texts.append([(event_text, 0)])
        return


    def commit_suicide(self):
        self.suicide(self.chosen_monster)
        self.doing_action = False
        return

    def suicide(self, user):
        user.take_damage(9999)
        font = pg.font.Font(None, 42)
        event_text = font.render(f"{user.name} deals 9999 damage to itself", True, (0, 0, 0))
        self.event_texts.append([(event_text, 0)])
        return

    def draw_backpack_item(self, screen):
        board_x, board_y = self.board_pos
        item_start_x = board_x + 40
        item_start_y = board_y + 70
        item_gap_y = 65
        no_draw_item_count = 0
        for i, item in enumerate(self.item):
            if item["usable"] == "no":
                no_draw_item_count += 1
                continue
            if item["count"] == 0:
                no_draw_item_count += 1
                continue
            img_path = f"assets/images/{item['sprite_path']}"
            try:
                img = pg.image.load(img_path).convert_alpha()
                img = pg.transform.scale(img, (60, 60))
            except Exception:
                img = pg.Surface((60, 60))
                img.fill((150, 150, 150))        
            y = item_start_y + (i - no_draw_item_count) * item_gap_y
            screen.blit(img, (item_start_x, y))
            font = pg.font.Font(None, 24)
            name_text = font.render(f"{item['name']}", True, (255, 255, 255))
            screen.blit(name_text, (item_start_x + 60, y + 15))
            count_text = font.render(f"count: {item['count']}", True, (0, 0, 0))
            screen.blit(count_text, (item_start_x + 60, y + 35))
            if not self.temp_buttons_item:
                ndic = 0
                for i, item in enumerate(self.item):
                    if item["usable"] == "no":
                        ndic += 1
                        continue
                    if item["count"] == 0:
                        ndic += 1
                        continue
                    y_button = item_start_y + (i - ndic) * item_gap_y
                    
                    temp_button = Button(
                        "UI/choose.png", "UI/choose_hover.png",
                        item_start_x, y_button - 5,
                        220, 70,
                        lambda itm=item, num = (i - ndic): self.using_an_item(itm, num)
                    )
                    self.temp_buttons_item.append(temp_button)

    def return_from_bag(self):
        self.open_backpack = False
        self.using_item = False

    def returning(self):
        self.in_attack = False
        self.using_item = False
        self.doing_action = False
        return





        
    def choosing_enemy(self):
        if self.enemy == None:    
            enemy_data = self.game_manager.enemy._monsters_data[randint(0, len(self.game_manager.enemy._monsters_data) - 1)]
            self.enemy = self.Combatant(enemy_data, sprite_size=(225, 225))


    def choosing_monster(self, monster, index):
        self.monster_chosen = True
        self.chosen_monster = self.Combatant(monster, sprite_size=(300, 300))
        self.monster_index = index
        # print(self.monster_index)
        # print(monster)

    def back(self):
        self.monster_chosen = False
        self.chosen_monster = None
        self.level_up = False
        self.atk_buff_count = 0
        self.def_buff_count = 0
        self.exp_gain = 0
        self.level_incresed = 0
        self.my_turn = True
        self.enemy = None
        self.temp_buttons = []
        self.event_texts = []
        self.game_manager.bag._items_data = self.item
        self.game_manager.save("saves/temp.json")        
        scene_manager.change_scene("game")
        self.going_back = False

    def draw_backpack_monster(self, screen: pg.Surface):
        board_x, board_y = self.board_pos
        screen.blit(self.board_sprite.image, (board_x, board_y))
        mon_start_x = board_x + 200
        mon_start_y = board_y + 45
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

            if not self.temp_buttons:
                for i, mon in enumerate(self.game_manager.bag._monsters_data):
                    if mon["hp"] > 0:
                        y_button = mon_start_y + i * mon_gap_y
                        temp_button = Button(
                            "UI/choose.png", "UI/choose_hover.png",
                            mon_start_x, y_button + 5,
                            220, 60,
                            lambda m=mon, num = i: self.choosing_monster(m, num)
                        )
                        self.temp_buttons.append(temp_button)

            





    def draw(self, screen: pg.Surface):
        self.background.draw(screen)
        if not self.monster_chosen and not self.going_back:
            self.draw_backpack_monster(screen)
            
            for btn in self.temp_buttons:
                btn.draw(screen)
            return
        if not len(self.game_manager.bag._monsters_data) == 0:        
            if not self.enemy:
                self.choosing_enemy()


            screen.blit(self.chosen_monster.element_icon.image, (GameSettings.SCREEN_WIDTH // 2 - 530, GameSettings.SCREEN_HEIGHT // 2 + 150))
            screen.blit(self.chosen_monster.sprite.image, (GameSettings.SCREEN_WIDTH // 2 - 450, GameSettings.SCREEN_HEIGHT // 2 - 50))
            
            font = pg.font.Font(None, 42)
            name_text = font.render(f"{self.chosen_monster.name} Lv{self.chosen_monster.level}", True, (0, 0, 0))
            hp_text = font.render(f"HP: {self.chosen_monster.hp}/{self.chosen_monster.max_hp}", True, (0, 0, 0))
            screen.blit(name_text, (GameSettings.SCREEN_WIDTH // 2 - 530, GameSettings.SCREEN_HEIGHT // 2 + 250))
            screen.blit(hp_text, (GameSettings.SCREEN_WIDTH // 2 - 240, GameSettings.SCREEN_HEIGHT // 2 + 250))

            screen.blit(self.enemy.element_icon.image, (GameSettings.SCREEN_WIDTH // 2 + 50, GameSettings.SCREEN_HEIGHT // 2 - 150 ))
            screen.blit(self.enemy.sprite.image, (GameSettings.SCREEN_WIDTH // 2 + 250, GameSettings.SCREEN_HEIGHT // 2 - 250))
            
            name_text = font.render(f"{self.enemy.name} Lv{self.enemy.level}", True, (0, 0, 0))
            hp_text = font.render(f"HP: {self.enemy.hp}/{self.enemy.max_hp}", True, (0, 0, 0))
            screen.blit(name_text, (GameSettings.SCREEN_WIDTH // 2 + 50, GameSettings.SCREEN_HEIGHT // 2 - 50 ))
            screen.blit(hp_text, (GameSettings.SCREEN_WIDTH // 2 + 50, GameSettings.SCREEN_HEIGHT // 2 ))

            buff_font = pg.font.Font(None, 32)
            if self.atk_buff_count > 0:
                atk_buff_sprite = Sprite("ingame_ui/options1.png", (60, 60))
                atk_buff_count_text = buff_font.render(f"X{self.atk_buff_count}", True, (0, 0, 0))
                screen.blit(atk_buff_sprite.image, (GameSettings.SCREEN_WIDTH // 2 - 40, GameSettings.SCREEN_HEIGHT // 2 + 220))
                screen.blit(atk_buff_count_text, (GameSettings.SCREEN_WIDTH // 2 + 10, GameSettings.SCREEN_HEIGHT // 2 + 260))
            if self.def_buff_count > 0:
                def_buff_sprite = Sprite("ingame_ui/options2.png", (60, 60))
                def_buff_count_text = buff_font.render(f"X{self.def_buff_count}", True, (0, 0, 0))
                screen.blit(def_buff_sprite.image, (GameSettings.SCREEN_WIDTH // 2 - 40, GameSettings.SCREEN_HEIGHT // 2 + 160))
                screen.blit(def_buff_count_text, (GameSettings.SCREEN_WIDTH // 2 + 10, GameSettings.SCREEN_HEIGHT // 2 + 200))

            if self.my_turn:
                if self.in_attack:
                    pass
                elif self.using_item:
                    board_x, board_y = self.board_pos
                    dark_overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
                    dark_overlay.fill((0, 0, 0, 150))
                    screen.blit(dark_overlay, (0, 0))
                    screen.blit(self.board_sprite.image, (board_x, board_y))          
                    self.return_button.draw(screen)
                    self.draw_backpack_item(screen)
                    for btn in self.temp_buttons_item:
                        btn.draw(screen)
                elif self.doing_action:
                    self.suicide_button.draw(screen)
                    self.return_button.draw(screen)
                else:
                    self.attack_button.draw(screen)
                    self.item_button.draw(screen)
                    self.action_button.draw(screen)

            

            event_texts = self.event_texts[-4:]
            text_x = 0
            text_y = 80
            gap_y = 30
            i = 0
            for line in event_texts:
                line_y = text_y + i * gap_y
                for surf, x in line:
                    screen.blit(surf, (text_x + x, line_y))
                i += 1

            if self.going_back:
                return_font = pg.font.Font("assets/fonts/Minecraft.ttf", 62)
                return_text = return_font.render("Click anywhere to return", True, (self.alpha, self.alpha, self.alpha))
                screen.blit(return_text, (GameSettings.SCREEN_WIDTH // 2 - 570, GameSettings.SCREEN_HEIGHT // 2 - 350))
                font = pg.font.Font(None, 42)
                if self.exp_gain > 0:
                    exp_text = font.render(f"{self.chosen_monster.name} gains {self.exp_gain} exp", True, (0, 0, 0))
                    screen.blit(exp_text, (GameSettings.SCREEN_WIDTH // 2 + 230, GameSettings.SCREEN_HEIGHT // 2 + 200))
                if self.level_incresed > 0:
                    lvl_up_text = font.render(f"{self.chosen_monster.name} increases {self.level_incresed} level", True, (0, 0, 0))
                    screen.blit(lvl_up_text, (GameSettings.SCREEN_WIDTH // 2 + 230, GameSettings.SCREEN_HEIGHT // 2 + 250))



    def update(self, dt):
        if self.something_timer < 1:
            self.something_timer += dt
            return
        if self.something_just_happened:
            self.something_timer = 0
            self.something_just_happened = False
            return
        if len(self.game_manager.bag._monsters_data) == 0:
            self.going_back = True
        if self.going_back and input_manager.mouse_pressed(1):
            self.back()
        if not self.going_back:
            if not self.monster_chosen:
                for btn in self.temp_buttons:
                    btn.update(dt)
                return
            
            if not self.enemy:
                self.choosing_enemy()
            
            if self.my_turn:
                if self.in_attack:
                    pass
                elif self.using_item:
                    self.return_button.update(dt)
                    self.item_return_button.update(dt)
                    for btn in self.temp_buttons_item:
                        btn.update(dt)
                elif self.doing_action:
                    self.suicide_button.update(dt)
                    self.return_button.update(dt)
                else:
                    self.attack_button.update(dt)
                    self.item_button.update(dt)
                    self.action_button.update(dt)
            else:
                self.normal_attack(self.enemy, self.chosen_monster)
                self.my_turn = True
            if self.chosen_monster.hp <= 0:
                self.chosen_monster.hp = 0
                self.going_back = True
                for idx, mon in enumerate(self.game_manager.bag._monsters_data):
                    if mon['name'] == self.chosen_monster.name and idx == self.monster_index:
                        # Convert Combatant back to dict before saving
                        self.game_manager.bag._monsters_data[idx] = {
                            "name": self.chosen_monster.name,
                            "level": self.chosen_monster.level,
                            "hp": self.chosen_monster.hp,
                            "max_hp": self.chosen_monster.max_hp,
                            "sprite_path": self.chosen_monster.sprite_path,
                            "element": self.chosen_monster.element,
                            "exp": self.chosen_monster.exp,
                            "evo": self.chosen_monster.evo
                        }
                sound_manager.stop_all_sounds()
                sound_manager.play_sound("toby fox - UNDERTALE Soundtrack - 11 Determination.ogg", int(self.game_manager.music_slider_value) / 100)
            
            elif self.enemy.hp <= 0:
                self.enemy.hp = 0
                self.going_back = True
                exp = self.enemy.level * 2
                self.exp_gain = exp
                while exp >= self.chosen_monster.level:
                    exp -= self.chosen_monster.level
                    self.chosen_monster.level += 1
                    self.level_incresed += 1
                    self.chosen_monster.max_hp += randint(1, 5)
                    self.level_up = True
                self.chosen_monster.exp = exp
                for idx, mon in enumerate(self.game_manager.bag._monsters_data):
                    if mon['name'] == self.chosen_monster.name and idx == self.monster_index:
                        # Convert Combatant back to dict before saving
                        self.game_manager.bag._monsters_data[idx] = {
                            "name": self.chosen_monster.name,
                            "level": self.chosen_monster.level,
                            "hp": self.chosen_monster.hp,
                            "max_hp": self.chosen_monster.max_hp,
                            "sprite_path": self.chosen_monster.sprite_path,
                            "element": self.chosen_monster.element,
                            "exp": self.chosen_monster.exp,
                            "evo": self.chosen_monster.evo
                        }
                sound_manager.stop_all_sounds()
                sound_manager.play_sound("RBY 108 Victory! (Trainer).ogg", int(self.game_manager.music_slider_value) / 100)
        else:
            if self.alpha < 255 and self.beta == 0:
                self.alpha += 1
            if self.alpha == 255:
                self.beta = 1
            if self.beta == 1:
                self.alpha -= 1
                if self.alpha == 0:
                    self.beta = 0
            

    @override
    def enter(self) -> None:
        if self.game_manager.music_on:
            sound_manager.play_sound("RBY 107 Battle! (Trainer).ogg", int(self.game_manager.music_slider_value) / 100)

    @override
    def exit(self):
        sound_manager.stop_all_sounds()
        self.game_manager.repeated_enter = False