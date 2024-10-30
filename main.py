import pygame as pg
from classes import Game
from debug import output
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
win = pg.display.set_mode(win_rect.size)
pg.display.set_caption('SkyJump')
# pg.display.set_icon(pg.image.load(''))
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
        win.fill('lightskyblue1')
        game.check_scroll_need()
        # game.draw_grid(win)
        if not key_pressed[pg.K_q]:
            game.platforms_group.draw(win)
        game.energy_waves_group.update()
        game.energy_waves_group.draw(win)
        game.player.update()
        game.player.show()
        # mouse_pos = pg.mouse.get_pos()
        # for tile in game.tiles_group:
        #     if tile.rect.collidepoint(mouse_pos):
        #         output(tile.id, 4)
        # for platform in game.platforms_group:
        #     if platform.rect.collidepoint(mouse_pos):
        #         output(platform.occupied_tiles, 5)
        output(f'player.vel: {game.player.vel}', 1)
        output(f'altitude: {game.player.altitude}', 2)
        output(f'energy: {game.player.energy}', 3)
        pg.display.update()


if __name__ == "__main__":
    run()
