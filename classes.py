import pygame as pg
import random
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
TILE_SIZE = (20, 20)
WIN_TSIZE = (int(win_rect.width / TILE_SIZE[0]), int(win_rect.height / TILE_SIZE[1]))  # (50, 40)
GROUND_GAP = 250  # gap between the ground's top and the bottom of the first tile row
HEIGHT_COEFFICIENT = 50  # how many pixels occupies a single height unit
DRAG = 0.012
GRAVITY = 0.45
FRICTION = 0.1


class Label:

    def __init__(self, text, font_name, font_size, fg, bg=None, **pos):
        self.win = pg.display.get_surface()
        self.text = text
        self.fg = fg
        self.bg = bg
        self.font = pg.font.SysFont(font_name, font_size)
        self.surface = self.font.render(text, True, fg, bg).convert_alpha()
        self.rect = self.surface.get_rect(**pos)

    def update_text(self, new_text):
        self.text = new_text
        self.surface = self.font.render(self.text, True, self.fg, self.bg).convert_alpha()
        self.rect.size = self.surface.get_size()

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class Game:

    def __init__(self):
        self.state = 'booting up'
        self.tiles_group = pg.sprite.Group()
        self.tile_map = {}  # {tile index: tile}
        self.occupied_tiles = set()  # a set of occupied tile ids
        self.platforms_group = pg.sprite.Group()
        self.player = Player(self)
        self.energy_waves_group = pg.sprite.Group()

        self.ground_y = win_rect.bottom - 200
        self.height = 0
        self.best_height = 0
        self.height_label = Label('Height: 0', 'Consolas', 30, 'black', topleft=(win_rect.left + 10, win_rect.top + 10))
        self.best_height_line = pg.Rect(0, self.ground_y - HEIGHT_COEFFICIENT * self.best_height, win_rect.width, 3)
        self.best_height_label = Label('YOUR BEST', 'Consolas', 15, 'deepskyblue4', bottomleft=(5, self.best_height_line.top - 3))
        self.lowest_ordinate = win_rect.bottom  # the bottom bound of the screen which the current visible screen should scroll to
        self.handle_rendering()

    def draw_tiles(self, surface, grid_type=1):
        """
        Utility function that allows to draw tiles on the screen
        """
        if grid_type == 1:
            for tile in self.tiles_group:
                pg.draw.circle(surface, 'gray70', tile.rect.topleft, 1)
                if tile.id in self.occupied_tiles:
                    pg.draw.rect(surface, 'red', tile.rect)
        if grid_type == 2:
            for col_num in range(int(win_rect.width / TILE_SIZE[0]) + 1):
                pg.draw.line(surface, 'gray70', (TILE_SIZE[0] * col_num, 0), (TILE_SIZE[0] * col_num, win_rect.bottom))
            for line_num in range(int(win_rect.height / TILE_SIZE[1]) + 1):
                pg.draw.line(surface, 'gray70', (0, TILE_SIZE[1] * line_num), (win_rect.right, TILE_SIZE[1] * line_num))

    def check_scroll_need(self):
        top_lim_offset = 100 - self.player.rect.top
        if top_lim_offset > 0:
            self.lowest_ordinate = win_rect.bottom - top_lim_offset

        offset = win_rect.bottom - self.lowest_ordinate
        if abs(offset) > 0:
            scroll_step = min(abs(offset), 5)
            scroll_step *= offset / abs(offset)
            self.lowest_ordinate += scroll_step
            self.scroll(scroll_step)
            self.handle_rendering()

    def scroll(self, step):
        # tiles
        for tile in self.tiles_group:
            tile.rect.y += step
            if tile.rect.top >= win_rect.bottom:
                self.tile_map.pop(tile.id)
                self.occupied_tiles.discard(tile.id)
                tile.kill()
        # platforms
        for platform in self.platforms_group:
            platform.rect.y += step
            if platform.rect.top >= win_rect.bottom:
                platform.kill()
        # player
        self.player.pos[1] += step
        self.player.rect.centery = round(self.player.pos[1])
        # energy waves
        for wave in self.energy_waves_group:
            wave.pos[1] += step
            wave.rect.y = round(wave.pos[1])
            if wave.rect.top >= win_rect.bottom:
                wave.kill()
        # height-related objects
        self.ground_y += step
        self.best_height_line.y += step
        self.best_height_label.rect.y += step

    def handle_rendering(self):
        overlap_tiles = pg.sprite.spritecollide(self.player, self.tiles_group, False)
        overlap_rows = [tile.id[1] for tile in overlap_tiles]
        overlap_rows.append(-1)  # provides the lowest row value when no tile has been generated yet
        tile_render_range = 60  # determines how many tiles up from the player's position should be generated
        highest_needed_row = max(overlap_rows) + tile_render_range
        self.render_tiles(highest_needed_row)
        self.render_platforms(highest_needed_row)

    def render_tiles(self, highest_needed_row):
        if len(self.tiles_group) == 0:
            highest_generated_tile = Tile((0, -1), (0, self.ground_y - GROUND_GAP))
            highest_generated_row = -1
        else:
            highest_generated_tile = self.tiles_group.sprites()[-1]
            highest_generated_row = list(self.tile_map.keys())[-1][1]
        tile_rows_needed = highest_needed_row - highest_generated_row
        for _ in range(tile_rows_needed):  # generate a needed number of tile rows
            tile_row_id = highest_generated_row + 1
            tile_row_y = highest_generated_tile.rect.y - TILE_SIZE[1]
            for column in range(int(win_rect.width / TILE_SIZE[0])):
                new_tile = Tile((column, tile_row_id), [column * TILE_SIZE[0], tile_row_y])
                self.tile_map.update({new_tile.id: new_tile})
                self.tiles_group.add(new_tile)
            highest_generated_tile = new_tile
            highest_generated_row += 1

    def render_platforms(self, highest_generated_row):
        if len(self.platforms_group) == 0:
            self.generate_platform((50, 10), (win_rect.left, win_rect.bottom - 200), (0, -1), 'ground')
            self.generate_platform((12, 2), (380, self.ground_y - GROUND_GAP - 2 * TILE_SIZE[1]), (19, 1), 'default')
        outline_tiles = 6  # how many unoccupied tiles in all directions a new platform should have
        max_gap_x = 20
        min_offset_x = 3  # at least how many x ids of the last platform mustn't be occupied by a new one
        max_offset_y = 15  # max allowed difference between the new platform's tpos[1] and the last one's
        last_platform = self.platforms_group.sprites()[-1]
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
                if not platform_outline_ids & self.occupied_tiles:
                    break
            toffset_y = tpos[1] - last_platform.tpos[1]
            pos = (tpos[0] * TILE_SIZE[0], last_platform.rect.y - toffset_y * TILE_SIZE[1])
            last_platform = self.generate_platform(new_platform_tsize, pos, tpos, 'default')

    def generate_platform(self, platform_tsize, pos, tpos, type):
        new_platform = Platform(pos, tpos, platform_tsize, type)
        seized_ids = {(x_id, y_id) for y_id in range(tpos[1], tpos[1] - platform_tsize[1], -1) for x_id in range(tpos[0], tpos[0] + platform_tsize[0])}
        self.occupied_tiles.update(seized_ids)
        # for id_y in range(tpos[1], tpos[1] - platform_tsize[1], -1):
        #     for id_x in range(tpos[0], tpos[0] + platform_tsize[0]):
        #         self.tile_map[(id_x, id_y)].content = 'platform'
        self.platforms_group.add(new_platform)
        return new_platform

    def update_objects(self):
        self.energy_waves_group.update()
        if self.state == 'running':
            self.player.update()

    def update_height(self):
        current_height = int((self.ground_y - self.player.rect.top) / HEIGHT_COEFFICIENT)
        if current_height > self.height:
            self.height = current_height
            self.height_label.update_text(f'Height: {self.height}')

    def draw_objects(self, surface):
        if self.best_height > 0:
            pg.draw.rect(surface, 'deepskyblue4', self.best_height_line)
            self.best_height_label.draw(surface)
        self.platforms_group.draw(surface)
        self.energy_waves_group.draw(surface)
        self.player.draw(surface)
        self.height_label.draw(surface)

    def restart(self):
        self.tiles_group.empty()
        self.tile_map.clear()
        self.occupied_tiles.clear()
        self.platforms_group.empty()
        self.energy_waves_group.empty()
        self.player = Player(self)
        self.ground_y = win_rect.bottom - 200
        if self.height > self.best_height:
            self.best_height = self.height
        self.best_height_line.top = self.ground_y - HEIGHT_COEFFICIENT * self.best_height
        self.best_height_label.rect.bottom = self.best_height_line.top - 3
        self.height = 0
        self.handle_rendering()
        self.lowest_ordinate = win_rect.bottom


class Tile(pg.sprite.Sprite):

    def __init__(self, id: tuple, pos: list, size=TILE_SIZE):
        super().__init__()
        self.id = id  # (column number, row number)
        self.size = size
        self.rect = pg.Rect(pos, self.size)
        # self.content = None


class Player(pg.sprite.Sprite):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.pos = pg.Vector2(500, 575)  # position of player's center represented as a vector
        self.size = [50, 50]
        self.state = 'default'
        self.body_types = {'default': pg.image.load('resources/player/body/default.png').convert_alpha(), 'absorbing': pg.image.load('resources/player/body/absorbing.png').convert_alpha(), 'overcharged': pg.image.load('resources/player/body/overcharged.png').convert_alpha()}
        self.eyeball = pg.image.load('resources/player/eyeball.png').convert_alpha()
        self.energy_filling = pg.image.load('resources/player/energy_filling.png').convert_alpha()
        self.pupil_types = {'default': pg.image.load('resources/player/pupil/default.png').convert_alpha(), 'absorbing': pg.image.load('resources/player/pupil/absorbing.png').convert_alpha(), 'overcharged': pg.image.load('resources/player/pupil/overcharged.png').convert_alpha()}
        self.image = self.body_types[self.state].copy()
        self.mask = pg.mask.from_surface(self.image, 0)
        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = self.pos
        self.prerect = self.rect.copy()  # copy of the rect on the last frame
        self.vel = pg.Vector2(0, 0)
        self.retention = 0.75  # determines how many percent of the initial velocity will be saved after a bounce
        self.bounce_lim = 3  # lowest vertical speed limit that prevents the player from bouncing upon reaching
        self.energy = 0
        self.min_energy = 8
        self.max_energy = 25
        self.overcharge_toleration = 5  # amount of energy above self.max_energy limit the player can tolerate and not overcharge

    def update(self):
        self.check_energy_level()
        if self.state != 'overcharged':
            self.handle_player_control()
        self.apply_external_forces()
        self.pos += self.vel
        self.prerect = self.rect.copy()
        self.rect.centerx, self.rect.centery = round(self.pos[0]), round(self.pos[1])
        self.check_bounds_collision()
        self.check_platform_collision()

    def check_energy_level(self):
        if self.energy < self.min_energy and self.vel.length() == 0:
            if self.state == 'overcharged':
                self.state = 'default'
            # self.energy = min(self.min_energy, self.energy + 0.2)
        elif self.energy > self.max_energy + self.overcharge_toleration:
            self.state = 'overcharged'
            self.release_energy()

    def handle_player_control(self):
        mouse_pressed = pg.mouse.get_pressed()
        if mouse_pressed[0]:
            if self.state == 'default':
                self.state = 'absorbing'
            self.energy += 0.4
        elif self.state == 'absorbing':
            self.state = 'default'
            self.release_energy()

    def get_mouse_dir(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        if mouse_pos != self.pos:
            mouse_dir = (mouse_pos - self.pos).normalize()
        else:
            mouse_dir = pg.Vector2(0, 1)
        return mouse_dir

    def release_energy(self):
        if self.energy > 0:
            mouse_dir = self.get_mouse_dir()
            self.produce_energy_wave(mouse_dir)
            self.vel += -mouse_dir * min(self.energy, self.max_energy)
            self.energy = 0

    def apply_external_forces(self):
        self.vel -= DRAG * self.vel
        self.rect.bottom += 1
        is_on_surface = pg.sprite.spritecollideany(self, self.game.platforms_group)
        self.rect.bottom -= 1
        if is_on_surface:
            if self.vel[0] > 0:
                self.vel[0] = max(0, self.vel[0] - FRICTION)
            elif self.vel[0] < 0:
                self.vel[0] = min(self.vel[0] + FRICTION, 0)
            # if self.state == 'absorbing' and self.vel[0] != 0:
            #     self.energy += self.friction
        else:
            self.vel[1] += GRAVITY

    def check_bounds_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos[0] = self.rect.centerx
            # if self.state == 'absorbing':
            #     self.energy += abs(self.vel[0])
            self.vel[0] = abs(self.vel[0]) * self.retention
        elif self.rect.right > win_rect.right:
            self.rect.right = win_rect.right
            self.pos[0] = self.rect.centerx
            # if self.state == 'absorbing':
            #     self.energy += self.vel[0]
            self.vel[0] = -abs(self.vel[0]) * self.retention

    def check_platform_collision(self):
        hit_platforms = pg.sprite.spritecollide(self, self.game.platforms_group, False)
        for hit_platform in hit_platforms:
            # check bottom side collision
            if self.vel[1] > 0 and self.prerect.bottom <= hit_platform.rect.top:
                self.rect.bottom = hit_platform.rect.top
                self.pos[1] = self.rect.centery
                # if self.state == 'absorbing':
                #     self.energy += self.vel[1]
                if self.vel[1] > self.bounce_lim:
                    self.vel[1] = -abs(self.vel[1]) * self.retention
                else:
                    self.vel[1] = 0
                self.game.lowest_ordinate = hit_platform.rect.top + 200
            # check top side collision
            elif self.vel[1] < 0 and self.prerect.top >= hit_platform.rect.bottom:
                self.rect.top = hit_platform.rect.bottom
                self.pos[1] = self.rect.centery
                # if self.state == 'absorbing':
                #     self.energy += abs(self.vel[1])
                self.vel[1] = abs(self.vel[1]) * self.retention
            # check right side collision
            if self.vel[0] > 0 and self.prerect.right <= hit_platform.rect.left:
                self.rect.right = hit_platform.rect.left
                self.pos[0] = self.rect.centerx
                # if self.state == 'absorbing':
                #     self.energy += self.vel[0]
                self.vel[0] = -abs(self.vel[0]) * self.retention
            # check left side collision
            elif self.vel[0] < 0 and self.prerect.left >= hit_platform.rect.right:
                self.rect.left = hit_platform.rect.right
                self.pos[0] = self.rect.centerx
                # if self.state == 'absorbing':
                #     self.energy += abs(self.vel[0])
                self.vel[0] = abs(self.vel[0]) * self.retention

    def produce_energy_wave(self, mouse_dir):
        relative_fullness = self.energy / self.max_energy
        if relative_fullness < 0.3:
            wave_size = 'small'
        elif 0.3 <= relative_fullness <= 0.7:
            wave_size = 'medium'
        elif relative_fullness > 0.7:
            wave_size = 'big'
        wave = EnergyWave(self.game, self.pos, wave_size, mouse_dir)
        self.game.energy_waves_group.add(wave)

    def update_energy_filling(self):
        eyeball = self.eyeball.copy()
        energy_filling = self.energy_filling.copy()
        eyeball_size = eyeball.get_size()
        relative_fullness = self.energy / self.max_energy
        eyeball.blit(energy_filling, (0, eyeball_size[1] - eyeball_size[1] * relative_fullness), (0, eyeball_size[1] - eyeball_size[1] * relative_fullness, eyeball_size[0], eyeball_size[1] * relative_fullness))
        self.image.blit(eyeball, (5, 5))

    def update_pupil(self):
        if self.state != 'overcharged':
            mouse_pos = pg.Vector2(pg.mouse.get_pos())
            if mouse_pos != self.pos:
                vector_to_cursor = mouse_pos - self.pos
                pupil_offset = vector_to_cursor / 5
                pupil_offset.clamp_magnitude_ip(10)
            else:
                pupil_offset = [0, 0]
            self.image.blit(self.pupil_types[self.state], (19 + pupil_offset[0], 19 + pupil_offset[1]))
        else:
            self.image.blit(self.pupil_types['overcharged'], (19, 19))

    def update_visuals(self):
        self.image = self.body_types[self.state].copy()
        self.update_energy_filling()
        self.update_pupil()

    def draw(self, surface):
        self.update_visuals()
        surface.blit(self.image, self.rect)


class EnergyWave(pg.sprite.Sprite):

    def __init__(self, game, pos_center, size: str, mouse_dir):
        super().__init__()
        self.game = game
        self.pos = pg.Vector2(pos_center)  # position of wave's center represented as a vector
        self.size = size
        self.image = pg.image.load(f'resources/energy_wave/{self.size}.png').convert_alpha()
        self.dir = self.determine_move_direction(mouse_dir)
        self.mask = pg.mask.from_surface(self.image, 0)
        self.rect = pg.Rect((0, 0), self.image.get_size())
        self.rect.center = self.pos
        self.speed = 10
        self.vel = self.dir * self.speed
        self.dissipating = False
        self.alpha = 200
        self.image.set_alpha(self.alpha)

    def determine_move_direction(self, mouse_dir):
        default_dir = pg.Vector2(0, 1)
        angle_to_mouse = default_dir.angle_to(mouse_dir)
        self.image = pg.transform.rotate(self.image, -angle_to_mouse)
        return mouse_dir

    def update(self):
        if self.alpha <= 0 or self.rect.colliderect(win_rect) is False:
            self.kill()
            return
        self.check_platform_collision()
        if self.dissipating is True:
            self.alpha -= 20
            self.image.set_alpha(self.alpha)
        self.pos += self.vel
        self.rect.centerx, self.rect.centery = round(self.pos[0]), round(self.pos[1])

    def check_platform_collision(self):
        if self.dissipating is False and pg.sprite.spritecollideany(self, self.game.platforms_group):
            if len(pg.sprite.spritecollide(self, self.game.platforms_group, False, pg.sprite.collide_mask)) > 0:
                self.dissipating = True
        elif self.dissipating is True and len(
                pg.sprite.spritecollide(self, self.game.platforms_group, False, pg.sprite.collide_mask)) == 0:
            self.dissipating = False


class Platform(pg.sprite.Sprite):

    def __init__(self, pos, tpos: tuple, tsize: tuple, type: str):
        super().__init__()
        self.tpos = tpos  # id of the most top left occupied tile
        self.tsize = tsize  # how many tiles a platform occupies in both dimensions
        self.size = (self.tsize[0] * TILE_SIZE[0], self.tsize[1] * TILE_SIZE[1])
        self.rect = pg.Rect(pos, self.size)
        self.type = type
        if self.type == 'default':
            # self.image = pg.image.load('resources/platform.png').convert_alpha()
            self.image = pg.Surface(self.size).convert()
            self.image.fill('white')
        elif self.type == 'ground':
            self.image = pg.Surface(self.size).convert()
            self.image.fill('forestgreen')
        self.mask = pg.mask.from_surface(self.image, 0)

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
