import pygame as pg
import generator
from player import Player
import ui
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
TILE_SIZE = (20, 20)
HUNIT = 50  # how many pixels a single height unit occupies


class Game:
    state = 'booting up'
    stage1 = generator.Stage()
    tiles_group = pg.sprite.Group()
    platforms_group = pg.sprite.Group()
    player = Player()

    black_screen = pg.Surface(win_rect.size).convert_alpha()
    black_screen.fill('black')
    ground_y = win_rect.bottom - 200
    current_height = 0
    best_height = 0
    height_label = ui.Label('Height: 0', 'Consolas', 30, 'black', topleft=(win_rect.left + 10, win_rect.top + 10))
    best_height_line = pg.Rect(0, win_rect.bottom, win_rect.width, 3)
    best_height_label = ui.Label('YOUR BEST', 'Consolas', 15, 'deepskyblue4', bottomleft=(5, best_height_line.top - 3))
    lowest_ordinate = win_rect.bottom  # the bottom bound of the screen which the current visible screen should scroll to
    generator.handle_rendering(stage1, current_height, [], tiles_group, platforms_group)

    def __init__(self, difficulty):
        self.difficulty = difficulty

    def handle_state(self, surface):
        if self.state == 'running' and self.player.rect.top > win_rect.bottom:
            self.state = 'restarting'
        if self.state == 'restarting':
            black_screen_alpha = self.black_screen.get_alpha()
            if black_screen_alpha < 255:
                black_screen_alpha += 10
                self.black_screen.set_alpha(black_screen_alpha)
                surface.blit(self.black_screen, (0, 0))
            else:
                self.state = 'booting up'
                self.restart()
        if self.state == 'booting up':
            black_screen_alpha = self.black_screen.get_alpha()
            if black_screen_alpha > 0:
                black_screen_alpha -= 5
                self.black_screen.set_alpha(black_screen_alpha)
                surface.blit(self.black_screen, (0, 0))
            else:
                self.state = 'running'

    def update_objects(self):
        if self.state == 'running':
            self.player.update(self.platforms_group)

    def update_height(self):
        self.current_height = int((self.ground_y - self.player.rect.top) / HUNIT)
        self.height_label.update_text(f'Height: {self.current_height}')
        if self.current_height > self.best_height:
            self.best_height = self.current_height

    def draw_objects(self, surface):
        pg.draw.rect(surface, 'deepskyblue4', self.best_height_line)
        self.best_height_label.draw(surface)
        self.platforms_group.draw(surface)
        self.player.draw(surface)
        self.height_label.draw(surface)

    def restart(self):
        self.stage1.restart()
        self.tiles_group.empty()
        generator.tile_map.clear()
        generator.occupied_tiles.clear()
        self.platforms_group.empty()
        self.player.__init__()
        self.ground_y = win_rect.bottom - 200
        self.current_height = 0
        self.best_height_line.top = self.ground_y - HUNIT * self.best_height
        self.best_height_label.rect.bottom = self.best_height_line.top - 3
        generator.handle_rendering(self.stage1, self.current_height, [], self.tiles_group, self.platforms_group)
        self.lowest_ordinate = win_rect.bottom

    def draw_tiles(self, surface, grid_type=1):
        """
        Utility function that allows to draw tiles on the screen
        """
        if grid_type == 1:
            for tile in self.tiles_group:
                pg.draw.circle(surface, 'gray70', tile.rect.topleft, 1)
                if tile.id in generator.occupied_tiles:
                    pg.draw.rect(surface, 'red', tile.rect)
        if grid_type == 2:
            for col_num in range(int(win_rect.width / TILE_SIZE[0]) + 1):
                pg.draw.line(surface, 'gray70', (TILE_SIZE[0] * col_num, 0), (TILE_SIZE[0] * col_num, win_rect.bottom))
            for line_num in range(int(win_rect.height / TILE_SIZE[1]) + 1):
                pg.draw.line(surface, 'gray70', (0, TILE_SIZE[1] * line_num), (win_rect.right, TILE_SIZE[1] * line_num))

    def check_scroll_need(self):
        # check if the player is too close to the top bound
        top_lim_offset = 100 - self.player.rect.top
        if top_lim_offset > 0:
            self.lowest_ordinate = win_rect.bottom - top_lim_offset
        if self.difficulty == 'easy':
            # check if the player is about to fall
            bottom_lim_offset = self.player.rect.bottom - (win_rect.bottom - 200)
            if bottom_lim_offset > 0:
                self.lowest_ordinate = win_rect.bottom + bottom_lim_offset
        # check if the player has landed on a platform
        if self.player.is_on_platform is True:
            self.lowest_ordinate = self.player.rect.bottom + 200

        offset = win_rect.bottom - self.lowest_ordinate
        if offset > 0:
            scroll_step = min(offset, 5)
            self.lowest_ordinate += scroll_step
            self.scroll_objects(scroll_step)
            generator.handle_rendering(self.stage1, self.current_height, pg.sprite.spritecollide(self.player, self.tiles_group, False), self.tiles_group, self.platforms_group)
        elif self.difficulty == 'easy' and offset < 0:
            scroll_step = offset
            self.lowest_ordinate += scroll_step
            self.scroll_objects(scroll_step)

    def scroll_objects(self, step):
        # tiles
        for tile in self.tiles_group:
            tile.pos[1] += step
            tile.rect.y = round(tile.pos[1])
            if tile.rect.top >= win_rect.bottom:
                generator.tile_map.pop(tile.id)
                generator.occupied_tiles.discard(tile.id)
                tile.kill()
        # platforms
        for platform in self.platforms_group:
            platform.pos[1] += step
            platform.rect.y = round(platform.pos[1])
            if self.difficulty != 'easy' and platform.rect.top >= win_rect.bottom:
                platform.kill()
        # player
        self.player.pos[1] += step
        self.player.rect.centery = round(self.player.pos[1])
        # height-related objects
        self.ground_y += step
        self.best_height_line.y += step
        self.best_height_label.rect.y += step
