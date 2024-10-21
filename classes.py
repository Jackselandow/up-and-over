import pygame as pg
import random
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
DRAG = 0.01
GRAVITY = 0.5


class Game:
    tile_size = (20, 20)

    def __init__(self):
        # self.bg = pg.transform.scale(pg.image.load(f'resources/cover.jpg'), (1000, 800)).convert()
        # platform1 = Platform([600, 600], [200, 20])
        # platform2 = Platform([400, 400], [200, 20])
        # platform3 = Platform([200, 200], [200, 20])
        # platform4 = Platform([0, 0], [200, 20])
        # platform5 = Platform([300, -200], [200, 20])
        # platform6 = Platform([800, -400], [200, 20])
        # platform7 = Platform([400, -600], [200, 20])
        # platform8 = Platform([500, -800], [200, 20])
        self.generator = Generator()
        self.tiles_group, self.ground, self.platforms_group, self.all_sprites_group = self.generator.create_sprite_groups()
        self.player = Player(self)
        self.player.add(self.all_sprites_group)
        self.lowest_ordinate = win_rect.bottom

    def draw_grid(self, win):
        for tile in self.tiles_group:
            pg.draw.circle(win, 'gray70', tile.pos, 1)
            if tile.content:
                pg.draw.rect(win, 'red', tile.rect)

        # for col_num in range(int(win_rect.width / self.tile_size[0]) + 1):
        #     pg.draw.line(win, 'gray70', (self.tile_size[0] * col_num, 0), (self.tile_size[0] * col_num, win_rect.bottom))
        # for line_num in range(int(win_rect.height / self.tile_size[1]) + 1):
        #     pg.draw.line(win, 'gray70', (0, self.tile_size[1] * line_num), (win_rect.right, self.tile_size[1] * line_num))

    def check_scroll_need(self):
        offset = win_rect.bottom - self.lowest_ordinate
        if offset > 0:
            if offset > 5:
                scroll_step = 5
            else:
                scroll_step = offset
            self.lowest_ordinate += scroll_step
            for sprite in self.all_sprites_group:
                sprite.scroll(scroll_step)
            if self.ground not in self.all_sprites_group:
                self.ground.scroll(scroll_step)
            self.generator.update_tiles()


class Generator:
    tile_size = (20, 20)
    rightmost_tile_id = int(win_rect.width / tile_size[0]) - 1
    min_platform_gap = 4
    max_platform_gap = 20

    def __init__(self):
        self.highest_platform_id = -1
        self.tiles_group = pg.sprite.Group()
        self.ground = Platform({'left': 0, 'top': -self.min_platform_gap, 'right': self.rightmost_tile_id, 'bottom': -self.min_platform_gap}, [0, win_rect.bottom - 100], [win_rect.width, 100])
        self.platforms_group = pg.sprite.Group(self.ground)
        self.all_sprites_group = pg.sprite.Group(self.tiles_group, self.platforms_group)
        self.update_tiles()

    def create_sprite_groups(self):
        return self.tiles_group, self.ground, self.platforms_group, self.all_sprites_group

    def update_tiles(self):
        if len(self.tiles_group) == 0:
            highest_row_ordinate = self.ground.rect.top - 200
            tile_id = (None, -1)
        else:
            last_tile = self.tiles_group.sprites()[-1]
            tile_id = last_tile.id
            highest_row_ordinate = last_tile.pos[1]
        tilesless_gap = highest_row_ordinate - -win_rect.bottom
        fitting_rows = int(tilesless_gap / self.tile_size[1])
        for backward_row_num in range(fitting_rows):
            backward_row_num += 1
            tile_id = (0, tile_id[1] + 1)
            tile_y = highest_row_ordinate - backward_row_num * self.tile_size[1]
            tile_row = []
            for col_num in range(int(win_rect.width / self.tile_size[0])):
                new_tile = Tile(tile_id, [col_num * self.tile_size[0], tile_y], self.tile_size)
                tile_id = (tile_id[0] + 1, tile_id[1])
                self.tiles_group.add(new_tile)
                self.all_sprites_group.add(new_tile)
                tile_row.append(new_tile)
            self.update_platform_row(tile_row)

    def update_platform_row(self, tile_row):
        platform_size = [10, 1]  # defines how many tiles on each axis a platform covers
        tiles_row_id = tile_row[0].id[1]
        for tile in tile_row:
            potentially_occupied_tiles = {'left': tile.id[0], 'top': tile.id[1], 'right': tile.id[0] + platform_size[0] - 1, 'bottom': tile.id[1] - platform_size[1] + 1}
            if tile.content is None and self.meets_platform_requirements(potentially_occupied_tiles) is True:
                if random.random() < 0.005:
                    self.generate_platform(platform_size, potentially_occupied_tiles, tile, tiles_row_id)

        if tiles_row_id - self.highest_platform_id > self.max_platform_gap:
            random.shuffle(tile_row)
            for tile in tile_row:
                potentially_occupied_tiles = {'left': tile.id[0], 'top': tile.id[1], 'right': tile.id[0] + platform_size[0] - 1, 'bottom': tile.id[1] - platform_size[1] + 1}
                if self.meets_platform_requirements(potentially_occupied_tiles) is True:
                    self.generate_platform(platform_size, potentially_occupied_tiles, tile, tiles_row_id)
                    break

    def generate_platform(self, platform_size, potentially_occupied_tiles, tile, tiles_row_id):
        new_platform = Platform(potentially_occupied_tiles, list(tile.rect.topleft), [platform_size[0] * self.tile_size[0], platform_size[1] * self.tile_size[1]])
        occupied_tiles = pg.sprite.spritecollide(new_platform, self.tiles_group, False)
        for occ_tile in occupied_tiles:
            occ_tile.content = 'platform'
        self.platforms_group.add(new_platform)
        self.all_sprites_group.add(new_platform)
        if tiles_row_id > self.highest_platform_id:
            self.highest_platform_id = tiles_row_id

    def meets_platform_requirements(self, occupied_tiles):
        passed = True
        # is within screen borders
        if occupied_tiles['right'] <= self.rightmost_tile_id:
            for platform in self.platforms_group:
                if occupied_tiles['bottom'] - platform.occupied_tiles['top'] >= self.min_platform_gap:
                    continue
                elif occupied_tiles['left'] - platform.occupied_tiles['right'] >= self.min_platform_gap or platform.occupied_tiles['left'] - occupied_tiles['right'] >= self.min_platform_gap:
                    continue
                else:
                    passed = False 
                    break
        else:
            passed = False
        return passed


class Tile(pg.sprite.Sprite):

    def __init__(self, id, pos, size):
        super().__init__()
        self.id = id
        self.pos = pos
        self.size = size
        self.content = None
        self.rect = pg.Rect(self.pos, self.size)

    def scroll(self, value):
        self.pos[1] += value
        self.rect.y = round(self.pos[1])
        if self.rect.top >= win_rect.bottom:
            self.kill()


class Player(pg.sprite.Sprite):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.win = pg.display.get_surface()
        self.pos = pg.Vector2(320, 679)  # position of player's center represented as a vector
        self.size = [40, 40]
        self.image = pg.Surface(self.size)
        self.image.fill('red')
        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = self.pos
        self.prerect = self.rect.copy()  # represents the rect on the last frame
        self.vel = pg.Vector2(0, 0)
        self.retention = 0.8  # determines how many percent of the initial velocity will be saved after a bounce
        self.friction = 0.1
        self.altitude = 0
        self.bounce_lim = 3  # lowest speed limit, after reaching which the player won't bounce anymore
        self.accumulating = False
        self.energy = 10
        self.min_energy = 10
        self.max_energy = 35
        self.overcharged = False

    def update(self):
        self.check_energy_level()
        if self.overcharged is False:
            self.handle_player_control()
        self.apply_external_forces()
        self.pos += self.vel
        self.prerect = self.rect.copy()
        self.rect.centerx, self.rect.centery = round(self.pos[0]), round(self.pos[1])
        self.check_bounds_collision()
        self.check_platform_collision()
        self.altitude = int((self.game.ground.pos[1] - self.rect.top) / 50)

    def check_energy_level(self):
        if self.energy < self.min_energy and self.vel.length() == 0:
            self.overcharged = False
            self.energy = min(self.min_energy, self.energy + 0.2)
        elif self.energy > self.max_energy:
            self.overcharged = True
            self.turn_accumulation_off()
            self.release_energy()

    def turn_accumulation_on(self):
        self.accumulating = True
        self.retention = 0.5
        self.friction = 0.3
        self.image.fill('blue')

    def turn_accumulation_off(self):
        self.accumulating = False
        self.retention = 0.8
        self.friction = 0.1
        self.image.fill('red')

    def handle_player_control(self):
        mouse_pressed = pg.mouse.get_pressed()
        if mouse_pressed[0]:
            if self.accumulating is False:
                self.turn_accumulation_on()
            self.cast_ray()
        elif self.accumulating is True:
            self.turn_accumulation_off()
            self.release_energy()

    def cast_ray(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        if mouse_pos != self.pos:
            mouse_dir = (mouse_pos - self.pos).normalize()
            ray_end = self.pos + mouse_dir * self.energy * 5
            pg.draw.line(self.win, 'green', self.rect.center, ray_end, 3)
            return mouse_dir

    def release_energy(self):
        mouse_dir = self.cast_ray()
        self.vel += -mouse_dir * self.energy
        self.energy = 0

    def apply_external_forces(self):
        self.vel -= DRAG * self.vel
        self.rect.bottom += 1
        is_on_surface = pg.sprite.spritecollideany(self, self.game.platforms_group)
        self.rect.bottom -= 1
        if is_on_surface:
            if self.vel[0] > 0:
                self.vel[0] = max(0, self.vel[0] - self.friction)
            elif self.vel[0] < 0:
                self.vel[0] = min(self.vel[0] + self.friction, 0)
            if self.accumulating and self.vel[0] != 0:
                self.energy += self.friction
        else:
            self.vel[1] += GRAVITY

    def check_bounds_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos[0] = self.rect.centerx
            if self.accumulating is True:
                self.energy += abs(self.vel[0])
            self.vel[0] = abs(self.vel[0]) * self.retention
        elif self.rect.right > win_rect.right:
            self.rect.right = win_rect.right
            self.pos[0] = self.rect.centerx
            if self.accumulating is True:
                self.energy += self.vel[0]
            self.vel[0] = -abs(self.vel[0]) * self.retention

    def check_platform_collision(self):
        hit_platforms = pg.sprite.spritecollide(self, self.game.platforms_group, False)
        for hit_platform in hit_platforms:
            if self.vel[1] > 0 and self.prerect.bottom <= hit_platform.rect.top:
                self.rect.bottom = hit_platform.rect.top
                self.pos[1] = self.rect.centery
                if self.accumulating is True:
                    self.energy += self.vel[1]
                if self.vel[1] > self.bounce_lim:
                    self.vel[1] = -abs(self.vel[1]) * self.retention
                else:
                    self.vel[1] = 0
                self.game.lowest_ordinate = hit_platform.rect.top + 100
            elif self.vel[1] < 0 and self.prerect.top >= hit_platform.rect.bottom:
                self.rect.top = hit_platform.rect.bottom
                self.pos[1] = self.rect.centery
                if self.accumulating is True:
                    self.energy += abs(self.vel[1])
                self.vel[1] = abs(self.vel[1]) * self.retention
            if self.vel[0] > 0 and self.prerect.right <= hit_platform.rect.left:
                self.rect.right = hit_platform.rect.left
                self.pos[0] = self.rect.centerx
                if self.accumulating is True:
                    self.energy += self.vel[0]
                self.vel[0] = -abs(self.vel[0]) * self.retention
            elif self.vel[0] < 0 and self.prerect.left >= hit_platform.rect.right:
                self.rect.left = hit_platform.rect.right
                self.pos[0] = self.rect.centerx
                if self.accumulating is True:
                    self.energy += abs(self.vel[0])
                self.vel[0] = abs(self.vel[0]) * self.retention

    def scroll(self, value):
        self.pos[1] += value
        self.rect.centery = round(self.pos[1])

    def show(self):
        self.win.blit(self.image, self.rect)


class Platform(pg.sprite.Sprite):

    def __init__(self, occupied_tiles, pos, size):
        super().__init__()
        self.occupied_tiles = occupied_tiles
        self.pos = pos
        self.size = size
        self.image = pg.transform.scale(pg.image.load(f'resources/platform.png'), self.size).convert_alpha()
        self.rect = pg.Rect(self.pos, self.size)

    def scroll(self, value):
        self.pos[1] += value
        self.rect.y = round(self.pos[1])
        if self.rect.top >= win_rect.bottom:
            self.kill()
            # del self
