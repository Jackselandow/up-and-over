import pygame as pg
from debug import output
pg.init()

win_size = 1000, 800
win = pg.display.set_mode(win_size)
pg.display.set_caption('SkyJump')
# pg.display.set_icon(pg.image.load('resources/heart.jpg'))
clock = pg.time.Clock()
FPS = 60
GRAVITY = pg.Vector2(0, 0.5)
FRICTION = 0.1


class Player(pg.sprite.Sprite):

    def __init__(self, platforms_group):
        super().__init__()
        self.platforms_group = platforms_group
        self.pos = pg.Vector2(320, 750)  # position of player's center represented as a vector
        self.size = [40, 40]
        self.image = pg.transform.scale(pg.image.load(f'resources/player.png'), self.size).convert_alpha()
        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = self.pos
        self.prerect = self.rect.copy()
        self.vel = pg.Vector2(0, 0)
        self.retention = 0.8  # determines how many percent of the initial velocity will be saved after a bounce
        self.mass = 1
        self.bounce_lim = 3  # lowest speed limit, after reaching which the player won't bounce anymore
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
        pg.draw.line(win, 'green', self.rect.center, ray_end)
        closest_point = None
        closest_distance = float('inf')
        for platform in self.platforms_group:
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
            pg.draw.circle(win, 'red', intersect_point, 5)
            if mouse_pressed[0]:
                self.cooldown = False
                self.charges -= 1
                point_to_rayend_ratio = dist_to_point / self.ray_len
                delta_vel = max(15 * point_to_rayend_ratio, 5) * ray_dir
                self.vel += delta_vel
            if mouse_pressed[2]:
                self.cooldown = False
                self.charges -= 1
                point_to_raystart_ratio = (self.ray_len - dist_to_point) / self.ray_len
                delta_vel = max(15 * point_to_raystart_ratio, 5) * -ray_dir
                self.vel += delta_vel
        elif not mouse_pressed[0] and not mouse_pressed[2]:
            self.cooldown = True

    def apply_external_forces(self):
        if abs(self.vel[0]) > FRICTION:
            if self.vel[0] > 0:
                self.vel[0] -= FRICTION * self.mass
            elif self.vel[0] < 0:
                self.vel[0] += FRICTION * self.mass
        else:
            self.vel[0] = 0
        self.vel += GRAVITY * self.mass

    def check_bounds_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos[0] = self.rect.centerx
            self.vel[0] = abs(self.vel[0]) * self.retention
        elif self.rect.right > win_size[0]:
            self.rect.right = win_size[0]
            self.pos[0] = self.rect.centerx
            self.vel[0] = -abs(self.vel[0]) * self.retention

    def check_platform_collision(self):
        hit_platform = pg.sprite.spritecollideany(self, self.platforms_group)
        if hit_platform:
            if self.vel[1] > 0 and self.prerect.bottom <= hit_platform.rect.top:
                self.rect.bottom = hit_platform.rect.top
                self.pos[1] = self.rect.centery
                self.charges = 2
                if self.vel[1] > self.bounce_lim:
                    self.vel[1] = -self.vel[1] * self.retention
                else:
                    self.vel[1] = 0
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


def run():
    # bg = pg.transform.scale(pg.image.load(f'resources/cover.jpg'), (1000, 800)).convert()
    ground_platform = Platform([0, win_size[1] - 30], [win_size[0], 50])
    platform1 = Platform([600, 600], [200, 20])
    platform2 = Platform([400, 400], [200, 20])
    platform3 = Platform([200, 200], [200, 20])
    platform4 = Platform([0, 0], [200, 20])
    platform5 = Platform([300, -200], [200, 20])
    platform6 = Platform([800, -400], [200, 20])
    platform7 = Platform([400, -600], [200, 20])
    platform8 = Platform([500, -800], [200, 20])
    platforms_group = pg.sprite.Group(ground_platform, platform1, platform2, platform3, platform4, platform5, platform6, platform7, platform8)
    player = Player(platforms_group)
    player_group = pg.sprite.GroupSingle(player)
    all_sprites_group = pg.sprite.Group(platforms_group, player_group)
    while True:
        clock.tick(FPS)
        events = pg.event.get()
        # globs = globals()
        # locs = locals()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_r]:
            run()
        if key_pressed[pg.K_UP]:
            offset = 5
        elif key_pressed[pg.K_DOWN]:
            offset = -5
        else:
            offset = 0
        if offset != 0:
            for sprite in all_sprites_group:
                sprite.scroll(offset)
        win.fill('white')
        platforms_group.draw(win)
        player_group.update()
        player_group.draw(win)
        output(f'player.vel: {player.vel}', 1)
        output(f'charges: {player.charges}', 2)
        pg.display.update()


if __name__ == "__main__":
    run()
