import pygame as pg
from scaler import Scaler
pg.init()

scaler = Scaler()


class Element:

    def __init__(self, pos, size, color):
        self.size = size
        self.rect = pg.FRect(pos, self.size)
        self.surface = pg.Surface(self.size)
        self.surface.fill(color)
        self.surface = scaler.scale_surface(self.surface)

    def draw(self, canvas):
        canvas.blit(self.surface, scaler.scale_pos(self.rect.topleft))

    def scroll(self, scroll_value):
        self.rect.move_ip(0, scroll_value)

    def update_pos(self, new_pos):
        self.rect.topleft = new_pos


class Label:

    def __init__(self, text: str, font_name, font_size, fg, bg, pos_attr: str, pos_value: tuple):
        self.text = text
        self.fg = fg
        self.bg = bg
        self.font = pg.font.SysFont(font_name, font_size)
        self.surface = self.font.render(text, False, fg, bg).convert_alpha()
        self.rect = self.surface.get_frect()
        setattr(self.rect, pos_attr, pos_value)
        self.surface = scaler.scale_surface(self.surface)

    def draw(self, canvas):
        canvas.blit(self.surface, scaler.scale_pos(self.rect.topleft))

    def scroll(self, scroll_value):
        self.rect.move_ip(0, scroll_value)

    def update_pos(self, new_pos_attr: str, new_pos_value: tuple):
        setattr(self.rect, new_pos_attr, new_pos_value)

    def update_text(self, new_text):
        self.text = new_text
        self.surface = self.font.render(self.text, False, self.fg, self.bg).convert_alpha()
        self.rect.size = self.surface.get_size()
        self.surface = scaler.scale_surface(self.surface)
