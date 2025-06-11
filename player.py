import pygame as pg
from scaler import Scaler
pg.init()

scaler = Scaler()
base_win_rect = pg.Rect((0, 0), scaler.base_win_size)
DRAG = 0.008
GRAVITY = 0.24
FRICTION = 0.1


class Player(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.init_size = [32, 32]
        self.state = 'default'
        self.body_types = {'default': pg.image.load('resources/player/body/default.png').convert_alpha(), 'absorbing': pg.image.load('resources/player/body/absorbing.png').convert_alpha()}
        self.eyeball = pg.image.load('resources/player/eyeball.png').convert_alpha()
        self.energy_filling = pg.image.load('resources/player/energy_filling.png').convert_alpha()
        self.pupil_types = {'default': pg.image.load('resources/player/pupil/default.png').convert_alpha(), 'absorbing': pg.image.load('resources/player/pupil/absorbing.png').convert_alpha()}
        # self.image = self.body_types[self.state].copy()
        self.image = pg.image.load('resources/player/new_shape32.png').convert_alpha()
        self.image = scaler.scale_surface(self.image)
        self.rect = pg.FRect((344, 208), self.init_size)
        self.prerect = self.rect.copy()  # copy of the rect on the last frame
        self.vel = pg.Vector2(0, 0)
        self.max_speed = 25
        self.retention = 0.8  # determines how many percent of the initial velocity will be saved after a bounce
        self.bounce_lim = 3  # lowest vertical speed limit that prevents the player from bouncing upon reaching
        self.stored_vel = pg.Vector2(0, 0)  # stored velocity during compression which applies after a bounce
        self.max_compress = 16
        self.frames_past_collision = 0
        self.collided_pos = pg.Vector2(0, 0)  # player's position when the last collision happened
        self.jump_power = 0
        self.max_jump_power = 100
        self.is_on_platform = False

    def scroll(self, scroll_value):
        self.prerect.move_ip(0, scroll_value)
        self.rect.move_ip(0, scroll_value)

    def update(self, mouse_pos, platforms_group):
        self.handle_player_input(mouse_pos)
        self.apply_external_forces()
        self.limit_vel()
        self.prerect = self.rect.copy()
        self.rect.move_ip(self.vel)
        self.frames_past_collision += 1
        self.check_bounds_collision()
        self.check_platform_collision(platforms_group)
        self.inflate()

    def handle_player_input(self, mouse_pos):
        mouse_pressed = pg.mouse.get_pressed()
        key_pressed = pg.key.get_pressed()
        if mouse_pressed[0] or key_pressed[pg.K_SPACE]:
            self.state = 'absorbing'
            self.jump_power += 3
        elif self.state == 'absorbing':
            self.state = 'default'
            self.release_jump(mouse_pos)

    def get_mouse_dir(self, mouse_pos):
        center = pg.Vector2(self.rect.center)
        if mouse_pos != center:
            mouse_dir = (mouse_pos - center).normalize()
        else:
            mouse_dir = pg.Vector2(0, 1)
        return mouse_dir

    def release_jump(self, mouse_pos):
        allowed_collision_delay = 12  # after this number of frames since a collision, the player can no longer jump off the collided surface
        allowed_collision_offset = 80  # after getting this far from a collided pos, the player can no longer jump off the collided surface
        if self.frames_past_collision <= allowed_collision_delay and pg.Vector2(self.rect.topleft).distance_to(self.collided_pos) <= allowed_collision_offset:
            mouse_dir = self.get_mouse_dir(mouse_pos)
            if mouse_dir[1] < 0:
                power_to_vel_coefficient = 0.08
                gained_vel = min(self.jump_power, self.max_jump_power) * power_to_vel_coefficient
                self.vel += mouse_dir * gained_vel
        self.jump_power = 0

    def apply_external_forces(self):
        self.vel -= DRAG * self.vel
        if self.is_on_platform is True:
            if self.vel[0] > 0:
                self.vel[0] = max(0, self.vel[0] - FRICTION)
            elif self.vel[0] < 0:
                self.vel[0] = min(self.vel[0] + FRICTION, 0)
        self.vel[1] += GRAVITY

    def limit_vel(self):
        if abs(self.vel[0]) > self.max_speed:
            self.vel[0] = max(min(self.vel[0], self.max_speed), -self.max_speed)
        if abs(self.vel[1]) > self.max_speed:
            self.vel[1] = max(min(self.vel[1], self.max_speed), -self.max_speed)

    def check_bounds_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel[0] = abs(self.vel[0]) * self.retention
        elif self.rect.right > base_win_rect.right:
            self.rect.right = base_win_rect.right
            self.vel[0] = -abs(self.vel[0]) * self.retention

    def check_platform_collision(self, platforms_group):
        self.is_on_platform = False
        hit_platforms = pg.sprite.spritecollide(self, platforms_group, False)
        for hit_platform in hit_platforms:
            collided_side = None
            tolerance = 0.001  # to account for computational errors with floats (e.g., 0.1 + 0.2 = 0.3000004)
            # check platform's top side collision
            if self.vel[1] > 0 and self.prerect.bottom <= hit_platform.rect.top + tolerance:
                collided_side = 'top'
            if hit_platform.solid is True:
                # check platform's bottom side collision
                if self.vel[1] < 0 and self.prerect.top >= hit_platform.rect.bottom - tolerance:
                    collided_side = 'bottom'
                # check platform's left side collision
                if self.vel[0] > 0 and self.prerect.right <= hit_platform.rect.left + tolerance:
                    collided_side = 'left'
                # check platform's right side collision
                elif self.vel[0] < 0 and self.prerect.left >= hit_platform.rect.right - tolerance:
                    collided_side = 'right'
            if collided_side:
                self.bounce_off_platform(hit_platform, collided_side)

    def bounce_off_platform(self, platform, platform_side: str):
        self.frames_past_collision = 0
        self.collided_pos = self.rect.topleft
        match platform_side:
            case 'top':
                if abs(self.vel[1]) > self.bounce_lim:
                    self.compress()
                elif self.stored_vel[1] < 0:
                    self.vel[1] = -self.vel[1]
                else:
                    self.vel[1] = 0
                self.rect.bottom = platform.rect.top
                self.is_on_platform = True
            case 'bottom':
                self.rect.top = platform.rect.bottom
                self.vel[1] = abs(self.vel[1]) * self.retention
            case 'left':
                self.rect.right = platform.rect.left
                self.vel[0] = -abs(self.vel[0]) * self.retention
            case 'right':
                self.rect.left = platform.rect.right
                self.vel[0] = abs(self.vel[0]) * self.retention
        if platform.type == 'bumpy':
            platform.bump_player(platform_side, self.vel)
        elif platform.type == 'ghost':
            if self.is_on_platform is True:
                platform.got_hit()

    def compress(self):
        entry_vel = self.vel[1]
        self.vel[1] *= 0.8  # closer to max compress = stronger vel decrease
        lost_vel = entry_vel - self.vel[1]
        self.stored_vel[1] += -abs(lost_vel) * self.retention
        base_compression = 3  # number of pixels of compression per 1 lost vel unit when the player is completely inflated
        stiffness = (self.init_size[1] - self.rect.height) / self.max_compress  # player's relative compression level
        self.rect.height -= base_compression * (1 - stiffness) * abs(lost_vel)
        self.rect.height = max(self.rect.height, self.init_size[1] - self.max_compress)

    def inflate(self):
        if self.stored_vel[1] < 0 and self.vel[1] < 0:
            height_diff = self.init_size[1] - self.rect.height
            if height_diff > 0:
                current_compression = height_diff / self.max_compress
                height_gain = min(pg.math.lerp(0.5, 2, current_compression), height_diff)
                self.rect.y -= height_gain
                self.rect.height += height_gain
                speed_gain = self.stored_vel[1] * (height_gain / height_diff)
                self.vel[1] += speed_gain
                self.stored_vel[1] -= speed_gain

    def draw(self, canvas, mouse_pos):
        # self.update_visuals(mouse_pos)
        canvas.blit(self.image, scaler.scale_pos(self.rect.topleft))

    def update_visuals(self, mouse_pos):
        self.image = self.body_types[self.state].copy()
        self.update_energy_filling()
        self.update_pupil(mouse_pos)

    def update_energy_filling(self):
        eyeball = self.eyeball.copy()
        energy_filling = self.energy_filling.copy()
        eyeball_size = eyeball.get_size()
        relative_fullness = self.jump_power / self.max_jump_power
        eyeball.blit(energy_filling, (0, eyeball_size[1] - eyeball_size[1] * relative_fullness), (0, eyeball_size[1] - eyeball_size[1] * relative_fullness, eyeball_size[0], eyeball_size[1] * relative_fullness))
        self.image.blit(eyeball, (5, 5))

    def update_pupil(self, mouse_pos):
        center = pg.Vector2(self.rect.center)
        if mouse_pos != center:
            vector_to_cursor = mouse_pos - center
            pupil_offset = vector_to_cursor / 5
            pupil_offset.clamp_magnitude_ip(10)
        else:
            pupil_offset = [0, 0]
        self.image.blit(self.pupil_types[self.state], (19 + pupil_offset[0], 19 + pupil_offset[1]))
