import pygame as pg
pg.init()


class Label:

    def __init__(self, text, font_name, font_size, fg, bg=None, **pos):
        self.win = pg.display.get_surface()
        self.text = text
        self.fg = fg
        self.bg = bg
        self.font = pg.font.SysFont(font_name, font_size)
        self.surface = self.font.render(text, True, fg, bg).convert_alpha()
        self.rect = self.surface.get_rect(**pos)

    def update_text(self, new_text):
        self.text = new_text
        self.surface = self.font.render(self.text, True, self.fg, self.bg).convert_alpha()
        self.rect.size = self.surface.get_size()

    def draw(self, surface):
        surface.blit(self.surface, self.rect)
