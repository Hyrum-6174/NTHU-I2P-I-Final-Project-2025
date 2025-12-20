import pygame as pg
from src.sprites import Sprite
from .component import UIComponent

class Slider(UIComponent):
    def __init__(self, x, y, width, height, min_val=0, max_val=100, value=50, on_change=None):
        # Bar as sprite
        self.bar_sprite = Sprite("UI/raw/UI_Flat_Bar06a.png", (width, height))
        self.bar_rect = pg.Rect(x, y, width, height)

        # Handle as sprite
        self.handle_sprite = Sprite("UI/raw/UI_Flat_Handle06a.png", (20, height))
        self.handle_rect = pg.Rect(x, y, 20, height)

        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.on_change = on_change
        self.dragging = False

        # Initial handle position based on value
        self.handle_rect.x = x + (value - min_val) / (max_val - min_val) * width

    def update(self, dt):
        mouse = pg.mouse.get_pos()
        pressed = pg.mouse.get_pressed()[0]

        if pressed and self.handle_rect.collidepoint(mouse):
            self.dragging = True
        if not pressed:
            self.dragging = False

        if self.dragging:
            self.handle_rect.x = max(self.bar_rect.x,
                                    min(mouse[0], self.bar_rect.right - self.handle_rect.width))
            relative_x = self.handle_rect.x - self.bar_rect.x
            handle_range = self.bar_rect.width - self.handle_rect.width
            self.value = self.min_val + (relative_x / handle_range) * (self.max_val - self.min_val)
            if self.on_change:
                self.on_change(self.value)
                

    def draw(self, screen):
        # Draw bar sprite
        screen.blit(self.bar_sprite.image, self.bar_rect.topleft)
        # Draw handle sprite
        screen.blit(self.handle_sprite.image, self.handle_rect.topleft)
