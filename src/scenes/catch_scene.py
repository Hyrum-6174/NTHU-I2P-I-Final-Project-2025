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
from src.scenes.battle_scene import BattleScene



class CatchScene(Scene):
    
    
    background: BackgroundSprite
    gamble_button: Button


    def __init__(self, game_manager: GameManager | None = None):
        super().__init__()

        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = game_manager
        # path = "saves/temp.json"
        # new_gm = self.game_manager.load(path)
        # self.game_manager = new_gm

        self.target = randint(0, 100)
        self.done_gambling = False
        self.gamble_number = randint(0, 100)
        self.result = 0
        self.win = False

        self.choosing_enemy()

        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2 
        
        
        button_width = 250
        button_height = 190


        self.gamble_button = Button(
            "UI/button_gamble.png",
            "UI/button_gamble_hover.png",
            center_x + 240, center_y + 140,
            button_width, button_height,
            self.gamble
        )

        self.board_sprite = Sprite(
            "UI/raw/UI_Flat_FrameSlot02a.png",
            (625, 500)
        )

        self.board_pos = (
            GameSettings.SCREEN_WIDTH // 2 - 625,
            GameSettings.SCREEN_HEIGHT // 2 - 300
        )
    @override
    def enter(self) -> None:
        if self.game_manager.music_on:
            sound_manager.play_sound("RBY 110 Battle! (Wild Pokemon).ogg", int(self.game_manager.music_slider_value) / 100)

    @override
    def exit(self):
        sound_manager.stop_all_sounds()
        self.game_manager.repeated_enter = False


    def gamble(self):
        self.result = randint(0, 100)
        self.done_gambling = True
        return 

    def choosing_enemy(self):
        self.enemy_data = self.game_manager.enemy._monsters_data[randint(0, len(self.game_manager.enemy._monsters_data) - 1)]
        self.enemy = BattleScene.Combatant(self.enemy_data, sprite_size=(225, 225))






    def draw(self, screen):
        self.background.draw(screen)
        self.gamble_button.draw(screen)
        board_x, board_y = self.board_pos
        screen.blit(self.board_sprite.image, (board_x, board_y))

        font = pg.font.Font(None, 42)
        screen.blit(self.enemy.sprite.image, (GameSettings.SCREEN_WIDTH // 2 + 250, GameSettings.SCREEN_HEIGHT // 2 - 250))
        
        name_text = font.render(f"{self.enemy.name} Lv{self.enemy.level}", True, (0, 0, 0))
        hp_text = font.render(f"HP: {self.enemy.hp}/{self.enemy.max_hp}", True, (0, 0, 0))
        target_font = pg.font.Font("assets/fonts/Minecraft.ttf", 62)
        target_text = target_font.render(f"Gamble {self.target} to win", True, (0, 0, 0))
        
        screen.blit(target_text, (GameSettings.SCREEN_WIDTH // 2 - 570, GameSettings.SCREEN_HEIGHT // 2 - 250))
        
        screen.blit(name_text, (GameSettings.SCREEN_WIDTH // 2 + 50, GameSettings.SCREEN_HEIGHT // 2 - 50 ))
        screen.blit(hp_text, (GameSettings.SCREEN_WIDTH // 2 + 50, GameSettings.SCREEN_HEIGHT // 2 ))
        
        random_number_font = pg.font.Font("assets/fonts/Minecraft.ttf", 262)
        if not self.done_gambling:
            
            random_number = random_number_font.render(f"{self.gamble_number}", True, (0, 0, 0))
            screen.blit(random_number, (GameSettings.SCREEN_WIDTH // 2 - 470, GameSettings.SCREEN_HEIGHT // 2 - 150))    
        else:
            result = random_number_font.render(f"{self.result}", True, (0, 0, 0))
            screen.blit(result, (GameSettings.SCREEN_WIDTH // 2 - 470, GameSettings.SCREEN_HEIGHT // 2 - 150))

    def update(self, dt):
        self.gamble_button.update(dt)
        self.gamble_number = randint(0, 100)
        self.game_manager.bag.update(dt)
        if self.done_gambling:
            if self.result >= self.target:
                self.win = True
                # print(self.game_manager.bag._monsters_data)
                self.game_manager.bag._monsters_data.append(self.enemy_data)
                self.done_gambling = False
                self.win = False
                self.game_manager.save("saves/temp.json")
                scene_manager.change_scene("game")
                self.target = randint(0, 100)
                self.choosing_enemy()
                # print(self.game_manager.bag._monsters_data)               
            else:
                self.win = False
                self.done_gambling = False
                self.game_manager.save("saves/temp.json")
                scene_manager.change_scene("game")             
                self.target = randint(0, 100)
                self.choosing_enemy()


