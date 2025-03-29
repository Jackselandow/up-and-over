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
    while True:
        clock.tick(FPS)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_r]:
            game.state = 'restarting'
        game.check_scroll_need()
        game.update_objects()
        game.update_height()
        win.fill('lightskyblue1')
        game.draw_tiles(win)
        game.draw_objects(win)
        game.handle_state(win)
        # mouse_pos = pg.mouse.get_pos()
        # for tile in game.tiles_group:
        #     if tile.rect.collidepoint(mouse_pos):
        #         print(tile.id)
        output(f'FPS: {round(clock.get_fps(), 1)}', 2)
        # output(f'offset: {win_rect.bottom - game.lowest_ordinate}', 3)
        # output(f'jump power: {game.player.jump_power}', 3)
        output(f'current pattern: {game.stage1.current_pattern.name}', 3)
        pg.display.update()


if __name__ == "__main__":
    run()
