import pygame as pg
import generator
from player import Player
import ui
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
state = 'booting up'
stage1 = generator.Stage()
tiles_group = pg.sprite.Group()
platforms_group = pg.sprite.Group()
player = Player()

TILE_SIZE = (20, 20)
HEIGHT_COEFFICIENT = 50  # how many pixels a single height unit occupies

black_screen = pg.Surface(win_rect.size).convert_alpha()
black_screen.fill('black')
ground_y = win_rect.bottom - 200
best_height = 0
height_label = ui.Label('Height: 0', 'Consolas', 30, 'black', topleft=(win_rect.left + 10, win_rect.top + 10))
best_height_line = pg.Rect(0, win_rect.bottom, win_rect.width, 3)
best_height_label = ui.Label('YOUR BEST', 'Consolas', 15, 'deepskyblue4', bottomleft=(5, best_height_line.top - 3))
lowest_ordinate = win_rect.bottom  # the bottom bound of the screen which the current visible screen should scroll to
generator.handle_rendering(stage1, [], tiles_group, platforms_group)


def handle_state(surface):
    global state
    if state == 'running' and player.rect.top > win_rect.bottom:
        state = 'restarting'
    if state == 'restarting':
        black_screen_alpha = black_screen.get_alpha()
        if black_screen_alpha < 255:
            black_screen_alpha += 10
            black_screen.set_alpha(black_screen_alpha)
            surface.blit(black_screen, (0, 0))
        else:
            state = 'booting up'
            restart()
    if state == 'booting up':
        black_screen_alpha = black_screen.get_alpha()
        if black_screen_alpha > 0:
            black_screen_alpha -= 5
            black_screen.set_alpha(black_screen_alpha)
            surface.blit(black_screen, (0, 0))
        else:
            state = 'running'


def update_objects():
    if state == 'running':
        player.update(platforms_group)


def update_height():
    global best_height
    current_height = int((ground_y - player.rect.top) / HEIGHT_COEFFICIENT)
    height_label.update_text(f'Height: {current_height}')
    if current_height > best_height:
        best_height = current_height


def draw_objects(surface):
    pg.draw.rect(surface, 'deepskyblue4', best_height_line)
    best_height_label.draw(surface)
    platforms_group.draw(surface)
    player.draw(surface)
    height_label.draw(surface)


def restart():
    global ground_y, lowest_ordinate
    stage1.restart()
    tiles_group.empty()
    generator.tile_map.clear()
    generator.occupied_tiles.clear()
    platforms_group.empty()
    player.__init__()
    ground_y = win_rect.bottom - 200
    best_height_line.top = ground_y - HEIGHT_COEFFICIENT * best_height
    best_height_label.rect.bottom = best_height_line.top - 3
    generator.handle_rendering(stage1, [], tiles_group, platforms_group)
    lowest_ordinate = win_rect.bottom


def draw_tiles(surface, grid_type=1):
    """
    Utility function that allows to draw tiles on the screen
    """
    if grid_type == 1:
        for tile in tiles_group:
            pg.draw.circle(surface, 'gray70', tile.rect.topleft, 1)
            if tile.id in generator.occupied_tiles:
                pg.draw.rect(surface, 'red', tile.rect)
    if grid_type == 2:
        for col_num in range(int(win_rect.width / TILE_SIZE[0]) + 1):
            pg.draw.line(surface, 'gray70', (TILE_SIZE[0] * col_num, 0), (TILE_SIZE[0] * col_num, win_rect.bottom))
        for line_num in range(int(win_rect.height / TILE_SIZE[1]) + 1):
            pg.draw.line(surface, 'gray70', (0, TILE_SIZE[1] * line_num), (win_rect.right, TILE_SIZE[1] * line_num))


def check_scroll_need():
    global lowest_ordinate
    # check if the player is too close to the top bound
    top_lim_offset = 100 - player.rect.top
    if top_lim_offset > 0:
        lowest_ordinate = win_rect.bottom - top_lim_offset
    # check if the player has landed on a platform
    if player.is_on_platform is True:
        lowest_ordinate = player.rect.bottom + 200

    offset = win_rect.bottom - lowest_ordinate
    if offset > 0:
        scroll_step = min(offset, 5)
        lowest_ordinate += scroll_step
        scroll_objects(scroll_step)
        generator.handle_rendering(stage1, pg.sprite.spritecollide(player, tiles_group, False), tiles_group, platforms_group)


def scroll_objects(step):
    global ground_y
    # tiles
    for tile in tiles_group:
        tile.pos[1] += step
        tile.rect.y = round(tile.pos[1])
        if tile.rect.top >= win_rect.bottom:
            generator.tile_map.pop(tile.id)
            generator.occupied_tiles.discard(tile.id)
            tile.kill()
    # platforms
    for platform in platforms_group:
        platform.pos[1] += step
        platform.rect.y = round(platform.pos[1])
        if platform.rect.top >= win_rect.bottom:
            platform.kill()
    # player
    player.pos[1] += step
    player.rect.centery = round(player.pos[1])
    # height-related objects
    ground_y += step
    best_height_line.y += step
    best_height_label.rect.y += step
