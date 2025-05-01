import pygame as pg
pg.init()


class Element:

    def __init__(self, pos: list, size, color):
        self.pos = pos
        self.size = size
        self.rect = pg.Rect(self.pos, self.size)
        self.surface = pg.Surface(self.size)
        self.surface.fill(color)

    def draw(self, canvas):
        canvas.blit(self.surface, self.rect)

    def scroll(self, scroll_value):
        self.pos[1] += scroll_value
        self.rect.y = round(self.pos[1])

    def update_pos(self, new_pos: list):
        self.pos = new_pos
        self.rect.topleft = (round(self.pos[0]), round(self.pos[1]))


class Label:

    def __init__(self, text: str, font_name, font_size, fg, bg, pos_attr: str, pos_value: tuple):
        self.text = text
        self.fg = fg
        self.bg = bg
        self.font = pg.font.SysFont(font_name, font_size)
        self.surface = self.font.render(text, False, fg, bg).convert_alpha()
        self.rect = self.surface.get_rect()
        setattr(self.rect, pos_attr, pos_value)
        self.pos = list(self.rect.topleft)

    def draw(self, canvas):
        canvas.blit(self.surface, self.rect)

    def scroll(self, scroll_value):
        self.pos[1] += scroll_value
        self.rect.y = round(self.pos[1])

    def update_pos(self, new_pos_attr: str, new_pos_value: tuple):
        setattr(self.rect, new_pos_attr, new_pos_value)
        self.pos = list(self.rect.topleft)

    def update_text(self, new_text):
        self.text = new_text
        self.surface = self.font.render(self.text, False, self.fg, self.bg).convert_alpha()
        self.rect.size = self.surface.get_size()
