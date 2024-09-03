import pygame as pg
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
GRAVITY = pg.Vector2(0, 0.5)
FRICTION = 0.1


class Game:

    def __init__(self):
        # self.bg = pg.transform.scale(pg.image.load(f'resources/cover.jpg'), (1000, 800)).convert()
        ground_platform = Platform([0, win_rect.bottom - 50], [win_rect.width, 50])
        platform1 = Platform([600, 600], [200, 20])
        platform2 = Platform([400, 400], [200, 20])
        platform3 = Platform([200, 200], [200, 20])
        platform4 = Platform([0, 0], [200, 20])
        platform5 = Platform([300, -200], [200, 20])
        platform6 = Platform([800, -400], [200, 20])
        platform7 = Platform([400, -600], [200, 20])
        platform8 = Platform([500, -800], [200, 20])
        self.platforms_group = pg.sprite.Group(ground_platform, platform1, platform2, platform3, platform4, platform5, platform6, platform7, platform8)
        self.player = Player(self)
        self.all_sprites_group = pg.sprite.Group(self.platforms_group, self.player)
        self.lowest_ordinate = win_rect.bottom

    def check_scroll_need(self):
        if self.player.rect.top < win_rect.bottom / 5:
            low_ordinate = win_rect.bottom - (win_rect.bottom / 4 - win_rect.bottom / 5)
            if low_ordinate < self.lowest_ordinate:
                self.lowest_ordinate = low_ordinate

        offset = win_rect.bottom - self.lowest_ordinate
        if offset != 0:
            if offset > 5:
                scroll_step = 5
            else:
                scroll_step = offset
            self.lowest_ordinate += scroll_step
            for sprite in self.all_sprites_group:
                sprite.scroll(scroll_step)


class Player(pg.sprite.Sprite):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.win = pg.display.get_surface()
        self.pos = pg.Vector2(320, 730)  # position of player's center represented as a vector
        self.size = [40, 40]
        self.image = pg.transform.scale(pg.image.load(f'resources/player.png'), self.size).convert_alpha()
        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = self.pos
        self.prerect = self.rect.copy()
        self.vel = pg.Vector2(0, 0)
        self.retention = 0.8  # determines how many percent of the initial velocity will be saved after a bounce
        self.mass = 1
        self.bounce_lim = 3  # lowest speed limit, after reaching which the player won't bounce anymore
        self.is_jumping = False
        self.ray_len = 300
        # self.pull_lim = 300
        # self.push_lim = 150
        self.charges = 2
        self.cooldown = True

    def update(self):
        intersect_point, dist_to_point, ray_dir = self.cast_ray()
        self.check_pull_push(intersect_point, dist_to_point, ray_dir)
        self.apply_external_forces()
        self.pos += self.vel
        self.prerect = self.rect.copy()
        self.rect.centerx, self.rect.centery = round(self.pos[0]), round(self.pos[1])
        self.check_bounds_collision()
        self.check_platform_collision()

    def cast_ray(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        ray_dir = (mouse_pos - self.pos).normalize()
        ray_end = self.pos + ray_dir * self.ray_len
        pg.draw.line(self.win, 'green', self.rect.center, ray_end)
        closest_point = None
        closest_distance = float('inf')
        for platform in self.game.platforms_group:
            intersected_ray = platform.rect.clipline(self.pos, ray_end)
            if intersected_ray:
                entry_pont = pg.Vector2(intersected_ray[0])
                distance = self.pos.distance_to(entry_pont)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_point = entry_pont
        return closest_point, closest_distance, ray_dir

    def check_pull_push(self, intersect_point, dist_to_point, ray_dir):
        mouse_pressed = pg.mouse.get_pressed()
        if intersect_point and self.charges > 0 and self.cooldown is True:
            pg.draw.circle(self.win, 'red', intersect_point, 5)
            if mouse_pressed[0]:
                point_to_rayend_ratio = dist_to_point / self.ray_len
                self.perform_pull_push(point_to_rayend_ratio, ray_dir)
            if mouse_pressed[2]:
                point_to_raystart_ratio = (self.ray_len - dist_to_point) / self.ray_len
                self.perform_pull_push(point_to_raystart_ratio, -ray_dir)
        elif not mouse_pressed[0] and not mouse_pressed[2]:
            self.cooldown = True

    def perform_pull_push(self, coefficient, ray_dir):
        self.cooldown = False
        self.charges -= 1
        delta_vel = max(15 * coefficient, 5) * ray_dir
        self.vel += delta_vel
        if self.is_jumping is False and delta_vel[1] != 0:
            self.is_jumping = True

    def apply_external_forces(self):
        if abs(self.vel[0]) > FRICTION:
            if self.vel[0] > 0:
                self.vel[0] -= FRICTION * self.mass
            elif self.vel[0] < 0:
                self.vel[0] += FRICTION * self.mass
        else:
            self.vel[0] = 0
        if self.is_jumping is True:
            self.vel += GRAVITY * self.mass

    def check_bounds_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos[0] = self.rect.centerx
            self.vel[0] = abs(self.vel[0]) * self.retention
        elif self.rect.right > win_rect.right:
            self.rect.right = win_rect.right
            self.pos[0] = self.rect.centerx
            self.vel[0] = -abs(self.vel[0]) * self.retention

    def check_platform_collision(self):
        hit_platform = pg.sprite.spritecollideany(self, self.game.platforms_group)
        if hit_platform:
            if self.vel[1] > 0 and self.prerect.bottom <= hit_platform.rect.top:
                self.rect.bottom = hit_platform.rect.top
                self.pos[1] = self.rect.centery
                self.charges = 2
                if self.vel[1] > self.bounce_lim:
                    self.vel[1] = -self.vel[1] * self.retention
                else:
                    self.vel[1] = 0
                    self.is_jumping = False
                low_ordinate = hit_platform.rect.top + 100
                if low_ordinate < self.game.lowest_ordinate:
                    self.game.lowest_ordinate = low_ordinate
            elif self.vel[1] < 0 and self.prerect.top >= hit_platform.rect.bottom:
                self.rect.top = hit_platform.rect.bottom
                self.pos[1] = self.rect.centery
                self.vel[1] = -self.vel[1] * self.retention
            if self.vel[0] > 0 and self.prerect.right <= hit_platform.rect.left:
                self.rect.right = hit_platform.rect.left
                self.pos[0] = self.rect.centerx
                self.vel[0] = -self.vel[0] * self.retention
            elif self.vel[0] < 0 and self.prerect.left >= hit_platform.rect.right:
                self.rect.left = hit_platform.rect.right
                self.pos[0] = self.rect.centerx
                self.vel[0] = -self.vel[0] * self.retention

    def scroll(self, value):
        self.pos[1] += value
        self.rect.centery = round(self.pos[1])

    def show(self):
        self.win.blit(self.image, self.rect)


class Platform(pg.sprite.Sprite):

    def __init__(self, pos, size):
        super().__init__()
        self.pos = pos
        self.size = size
        self.image = pg.transform.scale(pg.image.load(f'resources/platform.png'), self.size).convert_alpha()
        self.rect = pg.Rect(self.pos, self.size)

    def scroll(self, value):
        self.pos[1] += value
        self.rect.y = round(self.pos[1])
        if self.rect.top > win_rect.bottom:
            self.kill()
            del self
