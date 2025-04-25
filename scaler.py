import pygame as pg

pg.init()


class Scaler:

    def __init__(self, screen_size, win_size):
        scale_x = screen_size[0] / win_size[0]
        scale_y = screen_size[1] / win_size[1]
        self.scale_factor = min(scale_x, scale_y)
        scaled_win_size = (int(win_size[0] * self.scale_factor), int(win_size[1] * self.scale_factor))
        self.scaled_win_offset = ((screen_size[0] - scaled_win_size[0]) // 2, (screen_size[1] - scaled_win_size[1]) // 2)
        self.scaled_win_rect = pg.Rect(self.scaled_win_offset, scaled_win_size)

    def scale(self, surface):
        surf_size = surface.get_size()
        scaled_surf_size = (int(surf_size[0] * self.scale_factor), int(surf_size[1] * self.scale_factor))
        return pg.transform.smoothscale(surface, scaled_surf_size)

    def directdraw(self, surface, canvas, dest):
        """Draw a surface directly in the correct size and proportions"""
        scaled_surf = self.scale(surface)
        canvas.blit(scaled_surf, dest)

    def display_win(self, win, screen):
        scaled_win = pg.transform.smoothscale(win, self.scaled_win_rect.size)
        screen.blit(scaled_win, self.scaled_win_rect)

    def get_virtual_mouse_pos(self):
        real_x, real_y = pg.mouse.get_pos()
        virtual_x = (real_x - self.scaled_win_offset[0]) // self.scale_factor
        virtual_y = (real_y - self.scaled_win_offset[1]) // self.scale_factor
        return virtual_x, virtual_y
