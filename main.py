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
game = Game()

black_screen = pg.Surface(win.get_size()).convert_alpha()
black_screen.fill('black')
black_screen.set_alpha(0)


def run():
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
            game.state = 'losing'
        win.fill('lightskyblue1')
        game.check_scroll_need()
        # game.draw_grid(win)
        game.update_objects()
        game.update_height()
        game.draw_objects(win)
        handle_game_state()
        # mouse_pos = pg.mouse.get_pos()
        # for tile in game.tiles_group:
        #     if tile.rect.collidepoint(mouse_pos):
        #         output(tile.id, 4)
        # for platform in game.platforms_group:
        #     if platform.rect.collidepoint(mouse_pos):
        #         output(platform.occupied_tiles, 5)
        # output(f'player.vel: {game.player.vel}', 1)
        # output(f'height: {game.height}', 2)
        # output(f'best height: {game.best_height}', 3)
        # output(f'game state: {game.state}', 4)
        pg.display.update()


def handle_game_state():
    if game.state == 'running' and game.player.rect.top > win_rect.bottom:
        game.state = 'losing'
    if game.state == 'losing':
        black_screen_alpha = black_screen.get_alpha()
        if black_screen_alpha < 255:
            black_screen_alpha += 10
            black_screen.set_alpha(black_screen_alpha)
            win.blit(black_screen, (0, 0))
        else:
            game.state = 'restarting'
            game.restart()
    if game.state == 'restarting':
        black_screen_alpha = black_screen.get_alpha()
        if black_screen_alpha > 0:
            black_screen_alpha -= 5
            black_screen.set_alpha(black_screen_alpha)
            win.blit(black_screen, (0, 0))
        else:
            game.state = 'running'


if __name__ == "__main__":
    run()
