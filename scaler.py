import pygame as pg
from PIL import Image
pg.init()


class Scaler:

    def __init__(self):
        self.screen_size = pg.display.get_window_size()
        self.base_win_size = (720, 540)
        scale_x = self.screen_size[0] / self.base_win_size[0]
        scale_y = self.screen_size[1] / self.base_win_size[1]
        self.scale_factor = min(scale_x, scale_y)
        self.scaled_win_size = (self.base_win_size[0] * self.scale_factor, self.base_win_size[1] * self.scale_factor)
        self.scaled_win_offset = ((self.screen_size[0] - self.scaled_win_size[0]) // 2, (self.screen_size[1] - self.scaled_win_size[1]) // 2)
        self.scaled_win_rect = pg.Rect(self.scaled_win_offset, self.scaled_win_size)

    def scale_surface(self, surface, fast=False):
        if fast:
            return pg.transform.scale_by(surface, self.scale_factor).convert_alpha()
        else:
            surf_size = surface.get_size()
            scaled_surf_size = (round(surf_size[0] * self.scale_factor), round(surf_size[1] * self.scale_factor))
            surf_bytes = pg.image.tobytes(surface, 'RGBA')
            pil_img = Image.frombytes('RGBA', surf_size, surf_bytes)
            pil_img = pil_img.resize(scaled_surf_size, Image.Resampling.NEAREST)
            scaled_surface = pg.image.frombytes(pil_img.tobytes(), scaled_surf_size, 'RGBA').convert_alpha()
            return scaled_surface

    def scale_rect(self, rect):
        scaled_rect = rect.copy()
        scaled_rect.topleft = (rect.left * self.scale_factor, rect.top * self.scale_factor)
        scaled_rect.size = (rect.width * self.scale_factor, rect.height * self.scale_factor)
        return scaled_rect

    def scale_pos(self, pos):
        return round(pos[0] * self.scale_factor), round(pos[1] * self.scale_factor)

    def get_virtual_mouse_pos(self):
        real_x, real_y = pg.mouse.get_pos()
        virtual_x = (real_x - self.scaled_win_offset[0]) // self.scale_factor
        virtual_y = (real_y - self.scaled_win_offset[1]) // self.scale_factor
        return virtual_x, virtual_y
