import pygame as pg
import random
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
DRAG = 0.01
GRAVITY = 0.5


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

    def scroll(self, value):
        self.rect.y += value

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class Game:

    def __init__(self):
        self.state = 'running'
        # platform1 = Platform([600, 600], [200, 20])
        # platform2 = Platform([400, 400], [200, 20])
        # platform3 = Platform([200, 200], [200, 20])
        # platform4 = Platform([0, 0], [200, 20])
        # platform5 = Platform([300, -200], [200, 20])
        # platform6 = Platform([800, -400], [200, 20])
        # platform7 = Platform([400, -600], [200, 20])
        # platform8 = Platform([500, -800], [200, 20])
        self.generator = Generator()
        self.tiles_group, self.ground, self.platforms_group, self.scrollable_objects = self.generator.get_sprite_groups()
        self.player = Player(self)
        self.energy_waves_group = pg.sprite.Group()
        self.height = 0
        self.best_height = 0
        self.height_coefficient = 50  # determines how many pixels occupies one height unit
        self.height_label = Label('Height: 0', 'Consolas', 30, 'black', topleft=(win_rect.left + 10, win_rect.top + 10))
        self.best_height_line = pg.Rect(0, self.ground.rect.top - self.height_coefficient * self.best_height, win_rect.width, 3)
        self.best_height_label = Label('YOUR BEST', 'Consolas', 15, 'deepskyblue4', bottomleft=(5, self.best_height_line.top - 3))
        self.scrollable_objects.extend((self.player, self.best_height_line, self.best_height_label))
        self.lowest_ordinate = win_rect.bottom

    def draw_grid(self, surface):
        for tile in self.tiles_group:
            pg.draw.circle(surface, 'gray70', tile.pos, 1)
            if tile.content:
                pg.draw.rect(surface, 'red', tile.rect)

        # for col_num in range(int(win_rect.width / self.tile_size[0]) + 1):
        #     pg.draw.line(self.win, 'gray70', (self.tile_size[0] * col_num, 0), (self.tile_size[0] * col_num, win_rect.bottom))
        # for line_num in range(int(win_rect.height / self.tile_size[1]) + 1):
        #     pg.draw.line(self.win, 'gray70', (0, self.tile_size[1] * line_num), (win_rect.right, self.tile_size[1] * line_num))

    def check_scroll_need(self):
        offset = win_rect.bottom - self.lowest_ordinate
        if offset > 0:
            if offset > 5:
                scroll_step = 5
            else:
                scroll_step = offset
            self.lowest_ordinate += scroll_step
            for obj in self.scrollable_objects:
                if hasattr(obj, 'scroll'):
                    obj.scroll(scroll_step)
                else:
                    obj.y += scroll_step
            self.generator.update_tiles()

    def update_objects(self):
        self.energy_waves_group.update()
        if self.state == 'running':
            self.player.update()

    def update_height(self):
        current_height = int((self.ground.pos[1] - self.player.rect.top) / self.height_coefficient)
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
        self.generator.restart()
        self.tiles_group, self.ground, self.platforms_group, self.scrollable_objects = self.generator.get_sprite_groups()
        self.player = Player(self)
        self.energy_waves_group.empty()
        self.scrollable_objects.extend((self.player, self.best_height_line, self.best_height_label))
        if self.height > self.best_height:
            self.best_height = self.height
        self.best_height_line.top = self.ground.rect.top - self.height_coefficient * self.best_height
        self.best_height_label.rect.bottom = self.best_height_line.top - 3
        self.height = 0
        self.lowest_ordinate = win_rect.bottom


class Generator:
    tile_size = (20, 20)
    rightmost_tile_id = int(win_rect.width / tile_size[0]) - 1
    min_platform_gap = 4
    max_platform_gap = 20

    def __init__(self):
        self.highest_platform_id = -1
        self.tiles_group = pg.sprite.Group()
        self.ground = Platform({'left': 0, 'top': -self.min_platform_gap, 'right': self.rightmost_tile_id, 'bottom': -self.min_platform_gap}, [0, win_rect.bottom - 100], [win_rect.width, 100], 'ground')
        self.platforms_group = pg.sprite.Group(self.ground)
        self.scrollable_objects = [self.ground]
        self.update_tiles()

    def get_sprite_groups(self):
        return self.tiles_group, self.ground, self.platforms_group, self.scrollable_objects

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
                self.scrollable_objects.append(new_tile)
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
        new_platform = Platform(potentially_occupied_tiles, list(tile.rect.topleft), [platform_size[0] * self.tile_size[0], platform_size[1] * self.tile_size[1]], 'default')
        occupied_tiles = pg.sprite.spritecollide(new_platform, self.tiles_group, False)
        for occ_tile in occupied_tiles:
            occ_tile.content = 'platform'
        self.platforms_group.add(new_platform)
        self.scrollable_objects.append(new_platform)
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

    def restart(self):
        self.highest_platform_id = -1
        self.tiles_group.empty()
        self.ground.pos = [0, win_rect.bottom - 100]
        self.ground.rect.topleft = self.ground.pos
        self.platforms_group.empty()
        self.platforms_group.add(self.ground)
        self.scrollable_objects.clear()
        self.scrollable_objects.append(self.ground)
        self.update_tiles()


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
        self.pos = pg.Vector2(500, 675)  # position of player's center represented as a vector
        self.size = [50, 50]
        self.state = 'default'
        self.body_types = {'default': pg.image.load('resources/player/body/default.png').convert_alpha(), 'accumulating': pg.image.load('resources/player/body/accumulating.png').convert_alpha(), 'overcharged': pg.image.load('resources/player/body/overcharged.png').convert_alpha()}
        self.eyeball = pg.image.load('resources/player/eyeball.png').convert_alpha()
        self.energy_level = pg.image.load('resources/player/energy_level.png').convert_alpha()
        self.pupil_types = {'default': pg.image.load('resources/player/pupil/default.png').convert_alpha(), 'accumulating': pg.image.load('resources/player/pupil/accumulating.png').convert_alpha(), 'overcharged': pg.image.load('resources/player/pupil/overcharged.png').convert_alpha()}
        self.image = self.body_types[self.state].copy()
        self.mask = pg.mask.from_surface(self.image, 0)
        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = self.pos
        self.prerect = self.rect.copy()  # represents the rect on the last frame
        self.vel = pg.Vector2(0, 0)
        self.retention = 0.8  # determines how many percent of the initial velocity will be saved after a bounce
        self.friction = 0.1
        self.altitude = 0
        self.bounce_lim = 3  # lowest speed limit, after reaching which the player won't bounce anymore
        self.energy = 10
        self.min_energy = 10
        self.max_energy = 35

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
            self.state = 'default'
            self.energy = min(self.min_energy, self.energy + 0.2)
        elif self.energy > self.max_energy:
            self.turn_accumulation_off()
            self.state = 'overcharged'
            self.release_energy()

    def turn_accumulation_on(self):
        self.state = 'accumulating'
        self.retention = 0.5
        self.friction = 0.3

    def turn_accumulation_off(self):
        self.state = 'default'
        self.retention = 0.8
        self.friction = 0.1

    def handle_player_control(self):
        mouse_pressed = pg.mouse.get_pressed()
        if mouse_pressed[0]:
            if self.state != 'accumulating':
                self.turn_accumulation_on()
        elif self.state == 'accumulating':
            self.turn_accumulation_off()
            self.release_energy()

    def get_mouse_dir(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        if mouse_pos != self.pos:
            mouse_dir = (mouse_pos - self.pos).normalize()
        else:
            mouse_dir = pg.Vector2(0, 1)
        return mouse_dir

    def release_energy(self):
        mouse_dir = self.get_mouse_dir()
        self.produce_energy_wave(mouse_dir)
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
            if self.state == 'accumulating' and self.vel[0] != 0:
                self.energy += self.friction
        else:
            self.vel[1] += GRAVITY

    def check_bounds_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos[0] = self.rect.centerx
            if self.state == 'accumulating':
                self.energy += abs(self.vel[0])
            self.vel[0] = abs(self.vel[0]) * self.retention
        elif self.rect.right > win_rect.right:
            self.rect.right = win_rect.right
            self.pos[0] = self.rect.centerx
            if self.state == 'accumulating':
                self.energy += self.vel[0]
            self.vel[0] = -abs(self.vel[0]) * self.retention

    def check_platform_collision(self):
        hit_platforms = pg.sprite.spritecollide(self, self.game.platforms_group, False)
        for hit_platform in hit_platforms:
            if self.vel[1] > 0 and self.prerect.bottom <= hit_platform.rect.top:
                self.rect.bottom = hit_platform.rect.top
                self.pos[1] = self.rect.centery
                if self.state == 'accumulating':
                    self.energy += self.vel[1]
                if self.vel[1] > self.bounce_lim:
                    self.vel[1] = -abs(self.vel[1]) * self.retention
                else:
                    self.vel[1] = 0
                self.game.lowest_ordinate = hit_platform.rect.top + 100
            elif self.vel[1] < 0 and self.prerect.top >= hit_platform.rect.bottom:
                self.rect.top = hit_platform.rect.bottom
                self.pos[1] = self.rect.centery
                if self.state == 'accumulating':
                    self.energy += abs(self.vel[1])
                self.vel[1] = abs(self.vel[1]) * self.retention
            if self.vel[0] > 0 and self.prerect.right <= hit_platform.rect.left:
                self.rect.right = hit_platform.rect.left
                self.pos[0] = self.rect.centerx
                if self.state == 'accumulating':
                    self.energy += self.vel[0]
                self.vel[0] = -abs(self.vel[0]) * self.retention
            elif self.vel[0] < 0 and self.prerect.left >= hit_platform.rect.right:
                self.rect.left = hit_platform.rect.right
                self.pos[0] = self.rect.centerx
                if self.state == 'accumulating':
                    self.energy += abs(self.vel[0])
                self.vel[0] = abs(self.vel[0]) * self.retention

    def scroll(self, value):
        self.pos[1] += value
        self.rect.centery = round(self.pos[1])

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
        self.game.scrollable_objects.append(wave)

    def update_energy_level(self):
        eyeball = self.eyeball.copy()
        energy_level = self.energy_level.copy()
        eyeball_size = eyeball.get_size()
        relative_fullness = self.energy / self.max_energy
        eyeball.blit(energy_level, (0, eyeball_size[1] - eyeball_size[1] * relative_fullness), (0, eyeball_size[1] - eyeball_size[1] * relative_fullness, eyeball_size[0], eyeball_size[1] * relative_fullness))
        self.image.blit(eyeball, (5, 5))

    def update_pupil(self):
        if self.state != 'overcharged':
            mouse_pos = pg.Vector2(pg.mouse.get_pos())
            if mouse_pos != self.pos:
                vector_to_cursor = mouse_pos - self.pos
                pupil_offset = vector_to_cursor / 20
                pupil_offset.clamp_magnitude_ip(10)
            else:
                pupil_offset = [0, 0]
            self.image.blit(self.pupil_types[self.state], (19 + pupil_offset[0], 19 + pupil_offset[1]))
        else:
            self.image.blit(self.pupil_types['overcharged'], (19, 19))

    def update_visuals(self):
        self.image = self.body_types[self.state].copy()
        self.update_energy_level()
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
        if self.dissipating is False and pg.sprite.spritecollideany(self, self.game.platforms_group):
            if pg.sprite.spritecollide(self, self.game.platforms_group, False, pg.sprite.collide_mask):
                self.dissipating = True
        elif self.dissipating is True and not pg.sprite.spritecollideany(self, self.game.platforms_group):
            if len(pg.sprite.spritecollide(self, self.game.platforms_group, False, pg.sprite.collide_mask)) == 0:
                self.dissipating = False
        if self.dissipating is True:
            self.alpha -= 20
            self.image.set_alpha(self.alpha)

        self.pos += self.vel
        self.rect.centerx, self.rect.centery = round(self.pos[0]), round(self.pos[1])

    def scroll(self, value):
        self.pos[1] += value
        self.rect.y = round(self.pos[1])
        if self.rect.top >= win_rect.bottom:
            self.kill()


class Platform(pg.sprite.Sprite):

    def __init__(self, occupied_tiles, pos, size, type):
        super().__init__()
        self.occupied_tiles = occupied_tiles
        self.pos = pos
        self.size = size
        self.type = type
        if self.type == 'default':
            self.image = pg.image.load('resources/platform.png').convert_alpha()
        else:
            self.image = pg.Surface(self.size).convert()
            self.image.fill('forestgreen')
        self.mask = pg.mask.from_surface(self.image, 0)
        self.rect = pg.Rect(self.pos, self.size)

    def scroll(self, value):
        self.pos[1] += value
        self.rect.y = round(self.pos[1])
        if self.rect.top >= win_rect.bottom and self.type != 'ground':
            self.kill()
            # del self
