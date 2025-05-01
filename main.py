import pygame as pg
import utilities
from scaler import Scaler
pg.init()

screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
# screen = pg.display.set_mode((640, 360))
screen_size = screen.get_size()
win_size = (640, 360)
win = pg.Surface(win_size)
scaler = Scaler(screen_size, win_size)
pg.display.set_caption('Up & Over')
pg.display.set_icon(pg.image.load('resources/icon.png'))

clock = pg.time.Clock()
FPS = 60


def run():
    from game import Game
    game = Game('normal')
    while True:
        clock.tick(FPS)
        mouse_pos = scaler.get_virtual_mouse_pos()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        game.handle_state()
        game.check_scroll_need()
        game.update_objects(mouse_pos)
        game.update_height()
        win.fill('lightskyblue1')
        game.draw_objects(win, mouse_pos)
        scaler.display_win(win, screen)
        pg.display.update()


def debug():
    from game import Game
    game = Game('easy')
    show_info = True
    hitbox_view = False
    while True:
        clock.tick(FPS)
        mouse_pos = scaler.get_virtual_mouse_pos()
        key_pressed = pg.key.get_pressed()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        if key_pressed[pg.K_r]:
            game.state = 'restarting'
        elif key_pressed[pg.K_q]:
            hitbox_view = not hitbox_view
        game.handle_state()
        game.check_scroll_need()
        game.update_objects(mouse_pos)
        game.update_height()
        win.fill('lightskyblue1')
        game.draw_tiles(win)
        if not hitbox_view:
            game.draw_objects(win, mouse_pos)
        else:
            game.draw_hitboxes(win)
        utilities.debug(f'FPS: {round(clock.get_fps(), 1)}', win, 2)
        if show_info:
            utilities.debug(f'active pattern: {game.stage1.active_spawn_pattern.name}', win, 3)
            utilities.debug(f'pattern countdown: {game.stage1.pattern_switch_countdown}', win, 4)
            utilities.debug(f'player vel: {round(game.player.vel)}', win, 5)
            for tile in game.tiles_group:
                if tile.rect.collidepoint(mouse_pos):
                    utilities.debug(f'tile id: {tile.id}', win, 6)
            utilities.debug(f'mouse pos: {mouse_pos}', win, 7)
        scaler.display_win(win, screen)
        pg.display.update()


if __name__ == "__main__":
    run()
