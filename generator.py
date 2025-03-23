import pygame as pg
import random
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
tile_map = {}  # {tile index: tile}
occupied_tiles = set()  # a set of occupied tile ids
TILE_SIZE = (20, 20)
WIN_TSIZE = (int(win_rect.width / TILE_SIZE[0]), int(win_rect.height / TILE_SIZE[1]))  # (50, 40)
GROUND_GAP = 250  # gap between the ground's top and the bottom of the first tile row


def handle_rendering(overlap_tiles: list, tiles_group, platforms_group):
    overlap_rows = [tile.id[1] for tile in overlap_tiles]
    overlap_rows.append(-1)  # provides the lowest row value when no tile has been generated yet
    tile_render_range = 60  # determines how many tiles up from the player's position should be generated
    highest_needed_row = max(overlap_rows) + tile_render_range
    render_tiles(highest_needed_row, tiles_group)
    render_platforms(highest_needed_row, platforms_group)


def render_tiles(highest_needed_row, tiles_group):
    if len(tiles_group) == 0:
        ground_y = win_rect.bottom - 200
        highest_generated_tile = Tile((0, -1), (0, ground_y - GROUND_GAP))
        highest_generated_row = -1
    else:
        highest_generated_tile = tiles_group.sprites()[-1]
        highest_generated_row = list(tile_map.keys())[-1][1]
    tile_rows_needed = highest_needed_row - highest_generated_row
    for _ in range(tile_rows_needed):  # generate a needed number of tile rows
        tile_row_id = highest_generated_row + 1
        tile_row_y = highest_generated_tile.rect.y - TILE_SIZE[1]
        for column in range(int(win_rect.width / TILE_SIZE[0])):
            new_tile = Tile((column, tile_row_id), [column * TILE_SIZE[0], tile_row_y])
            tile_map.update({new_tile.id: new_tile})
            tiles_group.add(new_tile)
        highest_generated_tile = new_tile
        highest_generated_row += 1


def render_platforms(highest_generated_row, platforms_group):
    if len(platforms_group) == 0:
        ground_y = win_rect.bottom - 200
        generate_platform((50, 10), [win_rect.left, win_rect.bottom - 200], (0, -1), 'ground', platforms_group)
        generate_platform((12, 2), [380, ground_y - GROUND_GAP - 2 * TILE_SIZE[1]], (19, 1), 'default', platforms_group)
    outline_tiles = 6  # how many unoccupied tiles in all directions a new platform should have
    max_gap_x = 15
    min_offset_x = 4  # at least how many x ids of the last platform mustn't be occupied by a new one
    max_offset_y = 12  # max allowed difference between the new platform's tpos[1] and the last one's
    last_platform = platforms_group.sprites()[-1]
    new_platform_tsize = (12, 2)
    while highest_generated_row - last_platform.tpos[1] >= max_offset_y:
        left_lim_x = max(0, last_platform.tpos[0] - max_gap_x - new_platform_tsize[0])
        right_lim_x = min(WIN_TSIZE[0] - new_platform_tsize[0], last_platform.tpos[0] + last_platform.tsize[0] + max_gap_x)
        x_ids = [x_id for x_id in range(left_lim_x, right_lim_x + 1)]
        overhang_x_ids = {x_id for x_id in range(last_platform.tpos[0] + last_platform.tsize[0] - min_offset_x - new_platform_tsize[0] + 1, last_platform.tpos[0] + min_offset_x)}
        x_ids = [x_id for x_id in x_ids if x_id not in overhang_x_ids]
        y_ids = [y_id for y_id in range(last_platform.tpos[1], last_platform.tpos[1] + max_offset_y + 1)]
        while True:
            tpos = (random.choice(x_ids), random.choice(y_ids))
            platform_outline_ids = {(x_id, y_id) for y_id in range(tpos[1], tpos[1] - new_platform_tsize[1] - outline_tiles, -1) for x_id in range(tpos[0] - outline_tiles, tpos[0] + new_platform_tsize[0] + outline_tiles)}
            if not platform_outline_ids & occupied_tiles:
                break
        toffset_y = tpos[1] - last_platform.tpos[1]
        pos = [tpos[0] * TILE_SIZE[0], last_platform.rect.y - toffset_y * TILE_SIZE[1]]
        last_platform = generate_platform(new_platform_tsize, pos, tpos, 'default', platforms_group)


def generate_platform(platform_tsize, pos, tpos, type, platforms_group):
    new_platform = Platform(pos, tpos, platform_tsize, type)
    seized_ids = {(x_id, y_id) for y_id in range(tpos[1], tpos[1] - platform_tsize[1], -1) for x_id in range(tpos[0], tpos[0] + platform_tsize[0])}
    occupied_tiles.update(seized_ids)
    platforms_group.add(new_platform)
    return new_platform


class Tile(pg.sprite.Sprite):

    def __init__(self, id: tuple, pos: list, size=TILE_SIZE):
        super().__init__()
        self.id = id  # (column number, row number)
        self.pos = pos
        self.size = size
        self.rect = pg.Rect(self.pos, self.size)
        # self.content = None


class Platform(pg.sprite.Sprite):

    def __init__(self, pos: list, tpos: tuple, tsize: tuple, type: str):
        super().__init__()
        self.pos = pos
        self.tpos = tpos  # id of the most top left occupied tile
        self.tsize = tsize  # how many tiles a platform occupies in both dimensions
        self.size = (self.tsize[0] * TILE_SIZE[0], self.tsize[1] * TILE_SIZE[1])
        self.rect = pg.Rect(self.pos, self.size)
        self.type = type
        if self.type == 'default':
            # self.image = pg.image.load('resources/platform.png').convert_alpha()
            self.image = pg.Surface(self.size).convert()
            self.image.fill('white')
        elif self.type == 'ground':
            self.image = pg.Surface(self.size).convert()
            self.image.fill('forestgreen')

    # NOT A RECTANGULAR-SHAPED PLATFORM
    # def __init__(self, occupied_tiles, type):
    #     self.occupied_tiles = occupied_tiles
    #     self.type = type
    #     self.pos = [float('inf'), float('inf')]
    #     bottomright_corner = [float('-inf'), float('-inf')]
    #     for tile in self.occupied_tiles:
    #         self.pos = [min(self.pos[0], tile.pos[0]), min(self.pos[1], tile.pos[1])]
    #         bottomright_corner = [max(bottomright_corner[0], tile.rect.right), max(bottomright_corner[1], tile.rect.bottom)]
    #     self.rect = pg.Rect(self.pos, (bottomright_corner[0] - self.pos[0], bottomright_corner[1] - self.pos[1]))
    #     self.image = pg.Surface(self.rect.size, pg.SRCALPHA)
    #     for tile in self.occupied_tiles:
    #         self.image.fill('white', ((tile.pos[0] - self.pos[0], tile.pos[1] - self.pos[1]), tile.size))
    #
    # def draw(self, surface):
    #     for tile in self.occupied_tiles:
    #         surface.blit(tile.image, tile.rect)
