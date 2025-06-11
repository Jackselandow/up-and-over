import pygame as pg
import utilities
from scaler import Scaler
pg.init()

screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
# screen = pg.display.set_mode((720, 540))
screen.fill('black')
screen_size = screen.get_size()
scaler = Scaler()
scaled_win = pg.Surface(scaler.scaled_win_size)
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
        game.draw_objects(scaled_win, mouse_pos)
        screen.blit(scaled_win, scaler.scaled_win_rect)
        pg.display.update()


def debug():
    from game import Game
    game = Game('easy')
    show_info = False
    hitbox_view = True
    while True:
        clock.tick(FPS)
        mouse_pos = scaler.get_virtual_mouse_pos()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.KEYUP:
                if event.key == pg.K_r:
                    game.state = 'restarting'
                elif event.key == pg.K_h:
                    hitbox_view = not hitbox_view
                elif event.key == pg.K_i:
                    show_info = not show_info
        game.handle_state()
        # game.check_scroll_need()
        game.update_objects(mouse_pos)
        game.update_height()
        if not hitbox_view:
            game.draw_objects(scaled_win, mouse_pos)
        else:
            game.draw_hitboxes(scaled_win)
            pg.draw.line(scaled_win, 'red', scaler.scale_pos(game.player.rect.center), scaler.scale_pos(game.player.rect.center + game.player.vel * 5), 3)
            game.draw_tiles(scaled_win)
        utilities.debug(f'FPS: {round(clock.get_fps(), 1)}', scaled_win, 2)
        if show_info:
            utilities.debug(f'active pattern: {game.stage1.active_spawn_pattern.name}', scaled_win, 3)
            utilities.debug(f'pattern countdown: {game.stage1.pattern_switch_countdown}', scaled_win, 4)
            utilities.debug(f'player vel: {round(game.player.vel)}', scaled_win, 5)
            utilities.debug(f'mouse pos: {mouse_pos}', scaled_win, 6)
            utilities.debug(f'height: {round(game.player.rect.height, 2)}', scaled_win, 7)
            utilities.debug(f'bounce vel: {round(game.player.bounce_vel, 2)}', scaled_win, 8)
        screen.blit(scaled_win, scaler.scaled_win_rect)
        pg.display.update()


if __name__ == "__main__":
    debug()
