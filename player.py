import pygame as pg
pg.init()

win_rect = pg.Rect((0, 0), (1000, 800))
DRAG = 0.014
GRAVITY = 0.4
FRICTION = 0.2


class Player(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.pos = pg.Vector2(500, 575)  # position of player's center represented as a vector
        self.size = [50, 50]
        self.state = 'default'
        self.body_types = {'default': pg.image.load('resources/player/body/default.png').convert_alpha(), 'absorbing': pg.image.load('resources/player/body/absorbing.png').convert_alpha()}
        self.eyeball = pg.image.load('resources/player/eyeball.png').convert_alpha()
        self.energy_filling = pg.image.load('resources/player/energy_filling.png').convert_alpha()
        self.pupil_types = {'default': pg.image.load('resources/player/pupil/default.png').convert_alpha(), 'absorbing': pg.image.load('resources/player/pupil/absorbing.png').convert_alpha()}
        self.image = self.body_types[self.state].copy()
        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = self.pos
        self.prerect = self.rect.copy()  # copy of the rect on the last frame
        self.vel = pg.Vector2(0, 0)
        self.retention = 0.9  # determines how many percent of the initial velocity will be saved after a bounce
        self.bounce_lim = 3  # lowest vertical speed limit that prevents the player from bouncing upon reaching
        self.frames_past_collision = 0
        self.collided_pos = pg.Vector2(0, 0)  # player's position when the last collision happened
        self.jump_power = 0
        self.max_jump_power = 100
        self.is_on_platform = True

    def update(self, platforms_group):
        self.handle_player_input()
        self.apply_external_forces()
        self.pos += self.vel
        self.prerect = self.rect.copy()
        self.rect.centerx, self.rect.centery = round(self.pos[0]), round(self.pos[1])
        self.frames_past_collision += 1
        self.check_bounds_collision()
        self.check_platform_collision(platforms_group)

    def handle_player_input(self):
        mouse_pressed = pg.mouse.get_pressed()
        if mouse_pressed[0]:
            self.state = 'absorbing'
            self.jump_power += 1.6
        elif self.state == 'absorbing':
            self.state = 'default'
            self.release_jump()

    def get_mouse_dir(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        if mouse_pos != self.pos:
            mouse_dir = (mouse_pos - self.pos).normalize()
        else:
            mouse_dir = pg.Vector2(0, 1)
        return mouse_dir

    def release_jump(self):
        allowed_collision_delay = 12  # after this number of frames since collision, the player can no longer jump off the collided surface
        allowed_collision_offset = 80  # after getting this far from a collided pos, the player can no longer jump off the collided surface
        if self.frames_past_collision <= allowed_collision_delay and self.pos.distance_to(self.collided_pos) <= allowed_collision_offset:
            mouse_dir = self.get_mouse_dir()
            power_to_vel_coefficient = 0.18
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

    def check_bounds_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos[0] = self.rect.centerx
            self.vel[0] = abs(self.vel[0]) * self.retention
        elif self.rect.right > win_rect.right:
            self.rect.right = win_rect.right
            self.pos[0] = self.rect.centerx
            self.vel[0] = -abs(self.vel[0]) * self.retention

    def check_platform_collision(self, platforms_group):
        self.is_on_platform = False
        hit_platforms = pg.sprite.spritecollide(self, platforms_group, False)
        for hit_platform in hit_platforms:
            # check bottom side collision
            if self.vel[1] > 0 and self.prerect.bottom <= hit_platform.rect.top:
                self.frames_past_collision = 0
                self.collided_pos = self.pos.copy()
                self.rect.bottom = hit_platform.rect.top
                self.pos[1] = self.rect.centery
                if self.vel[1] > self.bounce_lim:
                    self.vel[1] = -abs(self.vel[1]) * self.retention
                else:
                    self.vel[1] = 0
                self.is_on_platform = True
            if hit_platform.solid is True:
                # check top side collision
                if self.vel[1] < 0 and self.prerect.top >= hit_platform.rect.bottom:
                    self.frames_past_collision = 0
                    self.collided_pos = self.pos.copy()
                    self.rect.top = hit_platform.rect.bottom
                    self.pos[1] = self.rect.centery
                    self.vel[1] = abs(self.vel[1]) * self.retention
                # check right side collision
                if self.vel[0] > 0 and self.prerect.right <= hit_platform.rect.left:
                    self.frames_past_collision = 0
                    self.collided_pos = self.pos.copy()
                    self.rect.right = hit_platform.rect.left
                    self.pos[0] = self.rect.centerx
                    self.vel[0] = -abs(self.vel[0]) * self.retention
                # check left side collision
                elif self.vel[0] < 0 and self.prerect.left >= hit_platform.rect.right:
                    self.frames_past_collision = 0
                    self.collided_pos = self.pos.copy()
                    self.rect.left = hit_platform.rect.right
                    self.pos[0] = self.rect.centerx
                    self.vel[0] = abs(self.vel[0]) * self.retention

    def draw(self, surface):
        self.update_visuals()
        surface.blit(self.image, self.rect)

    def update_visuals(self):
        self.image = self.body_types[self.state].copy()
        self.update_energy_filling()
        self.update_pupil()

    def update_energy_filling(self):
        eyeball = self.eyeball.copy()
        energy_filling = self.energy_filling.copy()
        eyeball_size = eyeball.get_size()
        relative_fullness = self.jump_power / self.max_jump_power
        eyeball.blit(energy_filling, (0, eyeball_size[1] - eyeball_size[1] * relative_fullness), (0, eyeball_size[1] - eyeball_size[1] * relative_fullness, eyeball_size[0], eyeball_size[1] * relative_fullness))
        self.image.blit(eyeball, (5, 5))

    def update_pupil(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        if mouse_pos != self.pos:
            vector_to_cursor = mouse_pos - self.pos
            pupil_offset = vector_to_cursor / 5
            pupil_offset.clamp_magnitude_ip(10)
        else:
            pupil_offset = [0, 0]
        self.image.blit(self.pupil_types[self.state], (19 + pupil_offset[0], 19 + pupil_offset[1]))
