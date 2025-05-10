import pygame as pg
from scaler import Scaler
import generator
from player import Player
import ui
pg.init()

scaler = Scaler()
base_win_rect = pg.Rect((0, 0), scaler.base_win_size)
TILE_SIZE = (10, 10)
HUNIT = 30  # how many pixels a single height unit occupies


class Game:
    state = 'booting up'
    stage1 = generator.Stage()
    bg = stage1.bg
    tiles_group = pg.sprite.Group()
    platforms_group = pg.sprite.Group()
    player = Player()

    black_screen = pg.Surface(scaler.scaled_win_size).convert_alpha()
    black_screen.fill('black')
    ground_y = base_win_rect.bottom - TILE_SIZE[1] * 10
    current_height = 0
    reached_height = 0  # best height of the current attempt
    best_height = 0  # best height of all attempts
    height_label = ui.Label('Height: 0', 'Consolas', 26, 'black', None, 'topleft', (base_win_rect.left + 14, base_win_rect.top + 14))
    best_height_line = ui.Element([0, base_win_rect.bottom], (base_win_rect.width, 1), 'deepskyblue4')
    best_height_label = ui.Label('YOUR BEST', 'Consolas', 10, 'deepskyblue4', None, 'bottomleft', (3, best_height_line.rect.top))
    screen_offset_y = 0  # offset > 0 => screen should be scrolled upward; offset < 0 => screen should be scrolled downward
    scroll_speed = 0

    def __init__(self, difficulty):
        self.difficulty = difficulty

    def handle_state(self):
        if self.state == 'running' and self.player.rect.top > base_win_rect.bottom:
            self.state = 'restarting'
        if self.state == 'restarting':
            black_screen_alpha = self.black_screen.get_alpha()
            if black_screen_alpha < 255:
                black_screen_alpha += 10
                self.black_screen.set_alpha(black_screen_alpha)
            else:
                self.state = 'booting up'
                self.restart()
        if self.state == 'booting up':
            black_screen_alpha = self.black_screen.get_alpha()
            if black_screen_alpha > 0:
                black_screen_alpha -= 5
                self.black_screen.set_alpha(black_screen_alpha)
            else:
                self.state = 'running'

    def update_objects(self, mouse_pos):
        if self.state == 'running':
            self.player.update(mouse_pos, self.platforms_group)

    def update_height(self):
        self.current_height = int((self.ground_y - self.player.rect.top) / HUNIT)
        self.height_label.update_text(f'Height: {self.current_height}')
        if self.current_height > self.reached_height:
            self.reached_height = self.current_height
            generator.handle_rendering(self.stage1, self.current_height, self.tiles_group, self.platforms_group)
            if self.current_height > self.best_height:
                self.best_height = self.current_height

    def draw_objects(self, canvas, mouse_pos):
        canvas.blit(self.bg, (0, 0))
        self.best_height_line.draw(canvas)
        self.best_height_label.draw(canvas)
        for platform in self.platforms_group:
            platform.draw(canvas)
        self.player.draw(canvas, mouse_pos)
        self.height_label.draw(canvas)
        canvas.blit(self.black_screen, (0, 0))

    def draw_tiles(self, canvas):
        for tile in self.tiles_group:
            if tile.id in generator.occupied_tiles:
                pg.draw.circle(canvas, 'red', scaler.scale_pos(tile.pos), 2)
            else:
                pg.draw.circle(canvas, 'gray70', scaler.scale_pos(tile.pos), 2)

    def draw_hitboxes(self, canvas):
        canvas.blit(self.bg, (0, 0))
        pg.draw.rect(canvas, 'blue', scaler.scale_rect(self.player.rect))
        for platform in self.platforms_group:
            pg.draw.rect(canvas, 'yellow', scaler.scale_rect(platform.rect))
        canvas.blit(self.black_screen, (0, 0))

    def check_scroll_need(self):
        self.detect_screen_offset()
        if self.screen_offset_y > 0:
            scroll_step = min(self.screen_offset_y, self.scroll_speed)
            self.scroll_objects(scroll_step)
            self.screen_offset_y -= scroll_step
        elif self.difficulty == 'easy' and self.screen_offset_y < 0:
            scroll_step = self.screen_offset_y
            self.scroll_objects(scroll_step)
            self.screen_offset_y -= scroll_step

    def detect_screen_offset(self):
        screen_offset_offers = []
        # check if the player is too close to the top bound
        top_lim_offset = 150 - self.player.rect.top
        if top_lim_offset > 0:
            screen_offset_offers.append(top_lim_offset + 100)
        if self.difficulty == 'easy' and self.reached_height - self.current_height < 50:
            # check if the player is about to fall
            bottom_lim_offset = base_win_rect.bottom - TILE_SIZE[1] * 10 - self.player.rect.bottom
            if bottom_lim_offset < 0:
                self.screen_offset_y = bottom_lim_offset
        # check if the player has landed on a platform
        if self.player.is_on_platform is True:
            screen_offset_offers.append(base_win_rect.bottom - (self.player.rect.bottom + TILE_SIZE[1] * 10))

        if len(screen_offset_offers) > 0 and max(screen_offset_offers) > self.screen_offset_y:
            self.screen_offset_y = max(screen_offset_offers)
            min_scroll_speed = 5
            self.scroll_speed = max(round(self.screen_offset_y / 45), min_scroll_speed)

    def scroll_objects(self, step):
        for tile in self.tiles_group:
            tile.scroll(step)
        for platform in self.platforms_group:
            platform.scroll(step, self.difficulty)
        self.player.scroll(step)
        self.ground_y += step
        self.best_height_line.scroll(step)
        self.best_height_label.scroll(step)

    def restart(self):
        self.stage1.restart()
        self.tiles_group.empty()
        generator.tile_map.clear()
        generator.occupied_tiles.clear()
        generator.generated_tile_rows.clear()
        self.platforms_group.empty()
        self.player.__init__()
        self.ground_y = base_win_rect.bottom - TILE_SIZE[1] * 10
        self.current_height = 0
        self.reached_height = 0
        self.best_height_line.update_pos([0, self.ground_y - HUNIT * self.best_height])
        self.best_height_label.update_pos('bottomleft', (3, self.best_height_line.rect.top))
        self.screen_offset_y = 0
