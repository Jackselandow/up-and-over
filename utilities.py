import pygame as pg
pg.init()


def debug(info, canvas, label_row: int, side='left'):
    font = pg.font.Font(None, 30)
    surf = font.render(str(info), True, 'black')
    if side == 'left':
        pos = (10, 10 + 25 * label_row)
        rect = surf.get_rect(topleft=pos)
    elif side == 'right':
        pos = (canvas.get_size()[0] - 10, 10 + 25 * label_row)
        rect = surf.get_rect(topright=pos)
    canvas.blit(surf, rect)
