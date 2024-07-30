import pygame as pg
pg.init()

font = pg.font.Font(None, 30)


def output(info, pos=(10, 10), fg='black', bg=None):
    if type(pos) is int:  # 0, 1, 2... can be assigned to pos instead of coordinates to specify the row of the label
        pos = (10, 10 + (25 * pos))
    win = pg.display.get_surface()
    surf = font.render(str(info), True, fg)
    rect = surf.get_rect(topleft=pos)
    if bg:
        pg.draw.rect(win, bg, rect)
    win.blit(surf, rect)
