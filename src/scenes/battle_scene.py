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
            self.attack = randint(int(self.level * 0.8), int(self.level * 1.2))
            self.defence = randint(int(self.level * 0.4), int(self.level * 0.6))
            self.sprite = Sprite(data['sprite_path'], sprite_size)
            self.sprite_path = data['sprite_path']

        def take_damage(self, amount: int):
            self.hp -= amount
            if self.hp < 0:
                self.hp = 0







    def __init__(self, game_manager: GameManager | None = None):
        super().__init__()

        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = game_manager
        # path = "saves/temp.json"
        # new_gm = self.game_manager.load(path)
        # self.game_manager = new_gm
        self.monster_index = -1
        self.bag = self.game_manager.bag
        self.monster_chosen = False
        self.chosen_monster: BattleScene.Combatant | None = None
        self.temp_buttons = []
        self.enemy = None
        self.choosing_enemy()
        self.going_back = False
        


        self.my_turn = True
        self.in_attack = False
        self.using_item = False
        self.doing_action = False

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

    def action(self):
        self.doing_action = True
        

  
       



    def normal_attack(self, attacker, receiver):
        damage = attacker.attack - receiver.defence
        receiver.take_damage(damage)
        
        return


    def commit_suicide(self):
        self.suicide(self.chosen_monster)
        self.doing_action = False
        return

    def suicide(self, user):
        user.take_damage(9999)
        return

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
        self.enemy = None
        self.temp_buttons = []         
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
                            "UI/button_play.png", "UI/button_play_hover.png",
                            mon_start_x + 220, y_button + 15,
                            60, 60,
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
            

            if self.my_turn:
                if self.in_attack:
                    pass
                elif self.using_item:
                    self.return_button.draw(screen)
                elif self.doing_action:
                    self.suicide_button.draw(screen)
                    self.return_button.draw(screen)
                else:
                    self.attack_button.draw(screen)
                    self.item_button.draw(screen)
                    self.action_button.draw(screen)

            


            screen.blit(self.chosen_monster.sprite.image, (GameSettings.SCREEN_WIDTH // 2 - 450, GameSettings.SCREEN_HEIGHT // 2 - 50))
            
            font = pg.font.Font(None, 42)
            name_text = font.render(f"{self.chosen_monster.name} Lv{self.chosen_monster.level}", True, (0, 0, 0))
            hp_text = font.render(f"HP: {self.chosen_monster.hp}/{self.chosen_monster.max_hp}", True, (0, 0, 0))
            screen.blit(name_text, (GameSettings.SCREEN_WIDTH // 2 - 530, GameSettings.SCREEN_HEIGHT // 2 + 250))
            screen.blit(hp_text, (GameSettings.SCREEN_WIDTH // 2 - 240, GameSettings.SCREEN_HEIGHT // 2 + 250))


            screen.blit(self.enemy.sprite.image, (GameSettings.SCREEN_WIDTH // 2 + 250, GameSettings.SCREEN_HEIGHT // 2 - 250))
            
            name_text = font.render(f"{self.enemy.name} Lv{self.enemy.level}", True, (0, 0, 0))
            hp_text = font.render(f"HP: {self.enemy.hp}/{self.enemy.max_hp}", True, (0, 0, 0))
            screen.blit(name_text, (GameSettings.SCREEN_WIDTH // 2 + 50, GameSettings.SCREEN_HEIGHT // 2 - 50 ))
            screen.blit(hp_text, (GameSettings.SCREEN_WIDTH // 2 + 50, GameSettings.SCREEN_HEIGHT // 2 ))

            if self.going_back:
                return_font = pg.font.Font("assets/fonts/Minecraft.ttf", 62)
                return_text = return_font.render("Click anywhere to return", True, (self.alpha, self.alpha, self.alpha))
                screen.blit(return_text, (GameSettings.SCREEN_WIDTH // 2 - 570, GameSettings.SCREEN_HEIGHT // 2 - 250))



    def update(self, dt):
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
                            "sprite_path": self.chosen_monster.sprite_path
                        }
                sound_manager.stop_all_sounds()
                sound_manager.play_sound("toby fox - UNDERTALE Soundtrack - 11 Determination.ogg", int(self.game_manager.music_slider_value) / 100)
            
            elif self.enemy.hp <= 0:
                self.enemy.hp = 0
                self.going_back = True
                for idx, mon in enumerate(self.game_manager.bag._monsters_data):
                    if mon['name'] == self.chosen_monster.name and idx == self.monster_index:
                        # Convert Combatant back to dict before saving
                        self.game_manager.bag._monsters_data[idx] = {
                            "name": self.chosen_monster.name,
                            "level": self.chosen_monster.level,
                            "hp": self.chosen_monster.hp,
                            "max_hp": self.chosen_monster.max_hp,
                            "sprite_path": self.chosen_monster.sprite_path
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