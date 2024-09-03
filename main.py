import pygame as pg
from classes import Game
from debug import output
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
win = pg.display.set_mode(win_rect.size)
pg.display.set_caption('SkyJump')
# pg.display.set_icon(pg.image.load('resources/heart.jpg'))
clock = pg.time.Clock()
FPS = 60


def run():
    game = Game()
    while True:
        clock.tick(FPS)
        events = pg.event.get()
        # globs = globals()
        # locs = locals()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_r]:
            run()
        win.fill('white')
        game.check_scroll_need()
        game.platforms_group.draw(win)
        game.player.update()
        game.player.show()
        output(f'player.vel: {game.player.vel}', 1)
        output(f'charges: {game.player.charges}', 2)
        pg.display.update()


if __name__ == "__main__":
    run()
