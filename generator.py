import pygame as pg
import random
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
tile_map = {}  # {tile index: tile}
occupied_tiles = set()  # a set of occupied tile ids
TILE_SIZE = (20, 20)
WIN_TSIZE = (int(win_rect.width / TILE_SIZE[0]), int(win_rect.height / TILE_SIZE[1]))  # (50, 40)
INITIAL_GROUND_Y = win_rect.bottom - 200
GROUND_GAP = 250  # gap between the ground's top and the bottom of the first tile row


def handle_rendering(stage, current_height, overlap_tiles: list, tiles_group, platforms_group):
    tile_rows_needed, highest_needed_row = calculate_render_endpoint(overlap_tiles, len(tiles_group))
    if tile_rows_needed > 0:
        render_tiles(tile_rows_needed, tiles_group)
        render_platforms(stage, highest_needed_row, platforms_group)
        stage.update_spawn_patterns(current_height, tile_rows_needed)


def calculate_render_endpoint(overlap_tiles, tiles_num):
    overlap_rows = [tile.id[1] for tile in overlap_tiles]
    overlap_rows.append(-1)  # provides the lowest row value when no tile has been generated yet
    tile_render_range = WIN_TSIZE[1] * 2  # determines how many tiles up from the player's position should be generated
    highest_needed_row = max(overlap_rows) + tile_render_range
    if tiles_num == 0:
        highest_generated_row = -1
    else:
        highest_generated_row = list(tile_map.keys())[-1][1]
    tile_rows_needed = highest_needed_row - highest_generated_row
    return tile_rows_needed, highest_needed_row


def render_tiles(tile_rows_needed, tiles_group):
    if len(tiles_group) == 0:
        highest_generated_tile = Tile((0, -1), [0, INITIAL_GROUND_Y - GROUND_GAP])
        highest_generated_row = -1
    else:
        highest_generated_tile = tiles_group.sprites()[-1]
        highest_generated_row = list(tile_map.keys())[-1][1]
    for _ in range(tile_rows_needed):  # generate a needed number of tile rows
        tile_row_id = highest_generated_row + 1
        tile_row_y = highest_generated_tile.rect.y - TILE_SIZE[1]
        for column in range(int(win_rect.width / TILE_SIZE[0])):
            new_tile = Tile((column, tile_row_id), [column * TILE_SIZE[0], tile_row_y])
            tile_map.update({new_tile.id: new_tile})
            tiles_group.add(new_tile)
        highest_generated_tile = new_tile
        highest_generated_row += 1


def render_platforms(stage, highest_generated_row, platforms_group):
    if len(platforms_group) == 0:
        GroundPlatform([win_rect.left, INITIAL_GROUND_Y], (0, -1), platforms_group)
        DefaultPlatform([380, INITIAL_GROUND_Y - GROUND_GAP - DefaultPlatform.tsize[1] * TILE_SIZE[1]], (19, 0), platforms_group)
    last_platform = platforms_group.sprites()[-1]
    platform_generation_space = WIN_TSIZE[1]  # how many tile rows should fit between the last tile and the highest generated platform
    while highest_generated_row - last_platform.tpos[1] >= platform_generation_space:
        new_platform_class = stage.active_spawn_pattern.next_platform_type()
        left_lim_x = max(0, last_platform.tpos[0] - new_platform_class.max_gap_x - new_platform_class.tsize[0])
        right_lim_x = min(WIN_TSIZE[0] - new_platform_class.tsize[0], last_platform.tpos[0] + last_platform.tsize[0] + new_platform_class.max_gap_x)
        x_ids = [x_id for x_id in range(left_lim_x, right_lim_x + 1)]
        overhang_x_ids = {x_id for x_id in range(last_platform.tpos[0] + last_platform.tsize[0] - new_platform_class.min_offset_x - new_platform_class.tsize[0] + 1, last_platform.tpos[0] + new_platform_class.min_offset_x)}
        x_ids = [x_id for x_id in x_ids if x_id not in overhang_x_ids]
        y_ids = [y_id for y_id in range(last_platform.tpos[1], last_platform.tpos[1] + new_platform_class.max_offset_y + 1)]
        while True:
            tpos = (random.choice(x_ids), random.choice(y_ids))
            platform_outline_ids = {(x_id, y_id) for y_id in range(tpos[1], tpos[1] - new_platform_class.tsize[1] - new_platform_class.outline_tiles, -1) for x_id in range(tpos[0] - new_platform_class.outline_tiles, tpos[0] + new_platform_class.tsize[0] + new_platform_class.outline_tiles)}
            if not platform_outline_ids & occupied_tiles:
                break
        toffset_y = tpos[1] - last_platform.tpos[1]
        pos = [tpos[0] * TILE_SIZE[0], last_platform.rect.y - toffset_y * TILE_SIZE[1]]
        new_platform = new_platform_class(pos, tpos, platforms_group)
        last_platform = new_platform


class Tile(pg.sprite.Sprite):

    def __init__(self, id: tuple, pos: list, size=TILE_SIZE):
        super().__init__()
        self.id = id  # (column number, row number)
        self.pos = pos
        self.size = size
        self.rect = pg.Rect(self.pos, self.size)
        # self.content = None


class Stage:

    def __init__(self):
        beginner_pattern = SpawnPattern('beginner', 50, 80, 0, 51, {DefaultPlatform: 1})
        rocky_pattern = SpawnPattern('rocky', 50, 80, 50, 101, {SolidPlatform: 2, DefaultPlatform: 1})
        bumpy_pattern = SpawnPattern('bumpy', 50, 80, 100, 151, {DefaultPlatform: 3, BumpyPlatform: 2})
        tricky_pattern = SpawnPattern('tricky', 50, 80, 150, 201, {DefaultPlatform: 3, GhostPlatform: 1})
        bumpy_rocks_pattern = SpawnPattern('bumpy rocks', 50, 100, 200, 1000, {SolidPlatform: 3, BumpyPlatform: 1})
        ghost_pattern = SpawnPattern('ghost', 30, 50, 200, 1000, {GhostPlatform: 1})
        mixed_pattern = SpawnPattern('mixed', 150, 200, 200, 1000, {DefaultPlatform: 3, SolidPlatform: 2, GhostPlatform: 1, BumpyPlatform: 1})
        self.spawn_patterns = [beginner_pattern, rocky_pattern, bumpy_pattern, tricky_pattern, bumpy_rocks_pattern, ghost_pattern, mixed_pattern]
        self.active_spawn_pattern = None
        self.pattern_switch_countdown = 0  # how many more tile rows remain to generate using the current spawn pattern
        self.update_spawn_patterns()

    def update_spawn_patterns(self, current_height=0, generated_tile_rows=0):
        if self.pattern_switch_countdown <= 0:
            self.switch_active_spawn_pattern(current_height)
        self.pattern_switch_countdown -= generated_tile_rows

    def switch_active_spawn_pattern(self, current_height):
        available_patterns = [pattern for pattern in self.spawn_patterns if current_height in pattern.available_height_range]
        if len(available_patterns) > 1 and self.active_spawn_pattern in available_patterns:
            available_patterns.remove(self.active_spawn_pattern)  # avoid selecting the same pattern if other are available
        self.active_spawn_pattern = random.choice(available_patterns)
        self.pattern_switch_countdown = random.randint(self.active_spawn_pattern.row_coverage_limits[0], self.active_spawn_pattern.row_coverage_limits[1])

    def restart(self):
        self.active_spawn_pattern = None
        self.pattern_switch_countdown = 0
        self.update_spawn_patterns()


class SpawnPattern:

    def __init__(self, name: str, min_row_coverage: int, max_row_coverage: int, height_start: int, height_stop: int, platform_types: dict):
        self.name = name
        self.row_coverage_limits = (min_row_coverage, max_row_coverage)  # allowed range of tile rows which the spawn pattern will apply to
        self.available_height_range = range(height_start, height_stop)  # between which height marks the spawn pattern is available
        self.platform_types = platform_types  # {PlatformType: relative weight of the possibility of being chosen}

    def next_platform_type(self):
        return random.choices(list(self.platform_types.keys()), self.platform_types.values())[0]


class Platform(pg.sprite.Sprite):
    """
    outline_tiles - how many unoccupied tiles in all directions a platform should have
    max_gap_x - max number of tiles between this platform and the last one
    min_offset_x - at least how many x ids of the last platform mustn't be occupied by this one
    max_offset_y - max allowed difference between this platform's tpos[1] and the last one's
    """

    def __init__(self, pos: list, tpos: tuple, tsize: tuple, type: str, solid: bool, platforms_group: pg.sprite.Group):
        super().__init__()
        self.pos = pos
        self.tpos = tpos  # id of the most top left occupied tile
        self.tsize = tsize  # how many tiles a platform occupies in both dimensions
        self.size = (self.tsize[0] * TILE_SIZE[0], self.tsize[1] * TILE_SIZE[1])
        self.rect = pg.Rect(self.pos, self.size)
        self.type = type
        self.solid = solid
        self.image = pg.Surface(self.size).convert_alpha()
        seized_ids = {(x_id, y_id) for y_id in range(self.tpos[1], self.tpos[1] - self.tsize[1], -1) for x_id in range(self.tpos[0], self.tpos[0] + self.tsize[0])}
        occupied_tiles.update(seized_ids)
        platforms_group.add(self)

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


class GroundPlatform(Platform):

    def __init__(self, pos: list, tpos: tuple, platforms_group: pg.sprite.Group):
        super().__init__(pos, tpos, (50, 10), 'solid', False, platforms_group)
        self.image.fill('forestgreen')


class DefaultPlatform(Platform):
    outline_tiles = 5
    max_gap_x = 15
    min_offset_x = 0
    max_offset_y = 12
    tsize = (15, 1)

    def __init__(self, pos: list, tpos: tuple, platforms_group: pg.sprite.Group):
        super().__init__(pos, tpos, self.tsize, 'default', False, platforms_group)
        self.image.fill('white')


class SolidPlatform(Platform):
    outline_tiles = 6
    max_gap_x = 10
    min_offset_x = 4
    max_offset_y = 10
    tsize = (12, 2)

    def __init__(self, pos: list, tpos: tuple, platforms_group: pg.sprite.Group):
        super().__init__(pos, tpos, self.tsize, 'solid', True, platforms_group)
        self.image.fill('gray75')


class BumpyPlatform(Platform):
    outline_tiles = 6
    max_gap_x = 10
    min_offset_x = 4
    max_offset_y = 10
    tsize = (4, 4)

    def __init__(self, pos: list, tpos: tuple, platforms_group: pg.sprite.Group):
        super().__init__(pos, tpos, self.tsize, 'bumpy', True, platforms_group)
        self.image.fill('red')
        self.bump_force = 10

    def bump_player(self, platform_side: str, player_vel):
        match platform_side:
            case 'top':
                player_vel[1] -= self.bump_force
            case 'bottom':
                player_vel[1] += self.bump_force
            case 'left':
                player_vel[0] -= self.bump_force
            case 'right':
                player_vel[0] += self.bump_force


class GhostPlatform(Platform):
    outline_tiles = 5
    max_gap_x = 15
    min_offset_x = 0
    max_offset_y = 12
    tsize = (15, 1)

    def __init__(self, pos: list, tpos: tuple, platforms_group: pg.sprite.Group):
        super().__init__(pos, tpos, self.tsize, 'ghost', False, platforms_group)
        self.image.fill('white')
        self.durability = 3
        visible_alpha = 50
        self.alpha_decrement_step = (255 - visible_alpha) / self.durability

    def got_hit(self):
        self.durability -= 1
        if self.durability <= 0:
            self.kill()
        else:
            alpha = self.image.get_alpha()
            self.image.set_alpha(alpha - self.alpha_decrement_step)
