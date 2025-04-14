import pygame as pg
from debug import output
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
win = pg.display.set_mode(win_rect.size)
pg.display.set_caption('Up & Over')
pg.display.set_icon(pg.image.load('resources/icon.png'))

clock = pg.time.Clock()
FPS = 60


def run():
    import game
    game = game.Game('normal')
    while True:
        clock.tick(FPS)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        game.check_scroll_need()
        game.update_objects()
        game.update_height()
        win.fill('lightskyblue1')
        game.draw_objects(win)
        game.handle_state(win)
        pg.display.update()


def debug():
    import game
    game = game.Game('easy')
    while True:
        clock.tick(FPS)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        key_pressed = pg.key.get_pressed()
        mouse_pos = pg.mouse.get_pos()
        if key_pressed[pg.K_r]:
            game.state = 'restarting'
        game.check_scroll_need()
        game.update_objects()
        game.update_height()
        win.fill('lightskyblue1')
        game.draw_tiles(win)
        if not key_pressed[pg.K_q]:
            game.draw_objects(win)
        game.handle_state(win)
        output(f'FPS: {round(clock.get_fps(), 1)}', 2)
        output(f'active pattern: {game.stage1.active_spawn_pattern.name}', 3)
        output(f'pattern countdown: {game.stage1.pattern_switch_countdown}', 4)
        output(f'player vel: {round(game.player.vel)}', 5)
        for tile in game.tiles_group:
            if tile.rect.collidepoint(mouse_pos):
                output(f'tile id: {tile.id}', 6)
        pg.display.update()


if __name__ == "__main__":
    debug()
