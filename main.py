import pygame as pg
from debug import output
pg.init()

win_size = 1000, 800
win = pg.display.set_mode(win_size)
pg.display.set_caption('SkyJump')
# pg.display.set_icon(pg.image.load('resources/heart.jpg'))
clock = pg.time.Clock()
FPS = 60
GRAVITY = 0.5


class Player(pg.sprite.Sprite):

    def __init__(self, platforms_group):
        super().__init__()
        self.platforms_group = platforms_group
        self.pos = [300, 755]
        self.size = [40, 40]
        self.image = pg.transform.scale(pg.image.load(f'resources/player.png'), self.size).convert_alpha()
        self.rect = pg.Rect(self.pos, self.size)
        self.prerect = self.rect.copy()
        self.idle = True
        self.xvel, self.yvel = 0, 0
        self.start_vel = -15
        self.retention = 0.8  # determines how many percent of the initial velocity will be saved after a bounce
        self.mass = 1
        self.bounce_lim = 3  # lowest speed limit, after reaching which the player won't bounce anymore

    def update(self):
        key_pressed = pg.key.get_pressed()
        if self.idle is True:
            if key_pressed[pg.K_SPACE]:
                self.idle = False
                self.yvel = self.start_vel
        else:

            # horizontal movement
            if key_pressed[pg.K_a]:
                self.xvel = -5
            elif key_pressed[pg.K_d]:
                self.xvel = 5
            else:
                self.xvel = 0

            # vertical movement
            if key_pressed[pg.K_s]:
                self.mass = 2.5
            else:
                self.mass = 1
            self.yvel += GRAVITY * self.mass

            # print(win_size[1] - self.rect.top - 5)
            self.prerect = self.rect.copy()
            self.pos[0] += self.xvel
            self.pos[1] += self.yvel
            self.rect.x, self.rect.y = round(self.pos[0]), round(self.pos[1])

            # check collision with platforms
            hit_platform = pg.sprite.spritecollideany(self, self.platforms_group)
            if self.yvel > 0 and hit_platform and self.prerect.bottom <= hit_platform.rect.top:
                self.rect.bottom = hit_platform.rect.top
                self.pos[1] = self.rect.y
                if self.yvel > self.bounce_lim:
                    self.yvel = -self.yvel * self.retention
                else:
                    self.idle = True
                    self.yvel = 0


class Platform(pg.sprite.Sprite):

    def __init__(self, pos, size):
        super().__init__()
        self.size = size
        self.image = pg.transform.scale(pg.image.load(f'resources/platform.png'), self.size).convert_alpha()
        self.rect = pg.Rect(pos[0], pos[1], self.size[0], self.size[1])


def run():
    # bg = pg.transform.scale(pg.image.load(f'resources/cover.jpg'), (1000, 800)).convert()
    ground_platform = Platform((0, win_size[1] - 5), (win_size[0], 50))
    platform1 = Platform((600, 600), (200, 20))
    platform2 = Platform((400, 400), (200, 20))
    platforms_group = pg.sprite.Group(ground_platform, platform1, platform2)
    player = Player(platforms_group)
    player_group = pg.sprite.GroupSingle(player)
    while True:
        clock.tick(FPS)
        events = pg.event.get()
        # globs = globals()
        # locs = locals()
        for event in events:
            if event.type == pg.QUIT:
                exit()

        win.fill('white')
        platforms_group.draw(win)
        player_group.update()
        player_group.draw(win)
        output(f'self.yvel: {player.yvel}')
        pg.display.update()


if __name__ == "__main__":
    run()
