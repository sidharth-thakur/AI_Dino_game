"""
Chrome Dino Game — Python + Pygame
====================================
Install:  pip install pygame
Run:      python dino_game.py

Controls:
  Space / Up Arrow  →  Jump
  Down Arrow        →  Duck
  R                 →  Restart after Game Over
"""

import pygame
import random
import sys
import math

# ─── Constants ────────────────────────────────────────────────────────────────
W, H        = 900, 350
FPS         = 60
GROUND_Y    = 265          # y-coordinate of the ground line
DINO_X      = 70           # fixed x position of the dino
PS          = 3            # 1 art-pixel = PS × PS screen pixels

# Chrome colour palette
C_BG        = (255, 255, 255)
C_DARK      = (83,  83,  83)
C_GREY      = (180, 180, 180)
C_CLOUD     = (200, 200, 200)
C_WHITE     = (255, 255, 255)
C_HUD_DIM   = (170, 170, 170)


# ─── Pixel-art helper ─────────────────────────────────────────────────────────
def draw_pixels(surface, pixels, ox, oy, color, ps=PS):
    """Blit a list of (col, row) art-pixels at screen offset (ox, oy)."""
    for (c, r) in pixels:
        pygame.draw.rect(surface, color,
                         (ox + c * ps, oy + r * ps, ps, ps))


# ═════════════════════════════════════════════════════════════════════════════
#  T-REX  SPRITE  DATA
# ═════════════════════════════════════════════════════════════════════════════
_HEAD = [
    (6,0),(7,0),(8,0),(9,0),(10,0),(11,0),
    (5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),
    (5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),
    (4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),
    (4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),
    (4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),
    (5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),
    (6,7),(7,7),(8,7),(9,7),(10,7),
]
_JAW_OPEN  = [(7,7),(8,7),(9,7)]
_JAW_CLOSE = [(6,7),(7,7),(8,7),(9,7),(10,7)]
_NECK = [
    (9,8),(10,8),(11,8),
    (9,9),(10,9),(11,9),
]
_BODY = [
    (3,10),(4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(10,10),
    (2,11),(3,11),(4,11),(5,11),(6,11),(7,11),(8,11),(9,11),(10,11),(11,11),
    (1,12),(2,12),(3,12),(4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),
    (1,13),(2,13),(3,13),(4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),
    (1,14),(2,14),(3,14),(4,14),(5,14),(6,14),(7,14),(8,14),(9,14),
    (2,15),(3,15),(4,15),(5,15),(6,15),(7,15),(8,15),
    (3,16),(4,16),(5,16),(6,16),(7,16),
]
_TAIL = [
    (11,11),(12,11),(13,11),
    (12,12),(13,12),(14,12),
    (13,13),(14,13),(15,13),
    (14,14),(15,14),
]
_ARM = [(8,11),(9,11),(10,11),(10,12)]

_LEG_A = [
    (5,17),(6,17),(4,18),(5,18),(3,19),(4,19),(5,19),
    (8,17),(9,17),(9,18),(10,18),(9,19),(10,19),(11,19),
]
_LEG_B = [
    (4,17),(5,17),(4,18),(5,18),(4,19),(5,19),(6,19),
    (9,17),(10,17),(9,18),(10,18),(10,19),(11,19),
]
_LEG_C = [
    (5,17),(6,17),(5,18),(6,18),(5,19),(6,19),
    (8,17),(9,17),(8,18),(9,18),(8,19),(9,19),
]

# Duck pose
_DUCK_BODY = [
    (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),
    (0,5),(1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),
    (1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),
    (2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),
    (10,5),(11,5),(12,5),(13,5),(12,6),(13,6),(14,6),
]
_DUCK_NECK = [
    (9,2),(10,2),(11,2),(12,2),
    (9,3),(10,3),(11,3),(12,3),
]
_DUCK_HEAD = [
    (10,0),(11,0),(12,0),(13,0),(14,0),(15,0),(16,0),
    (10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(16,1),(17,1),
    (10,2),(11,2),(12,2),(13,2),(14,2),(15,2),(16,2),
]
_DUCK_JAW = [(12,2),(13,2),(14,2),(15,2)]
_DUCK_LEG_A = [
    (3,8),(4,8),(3,9),(4,9),(2,9),
    (7,8),(8,8),(8,9),(9,9),(9,10),
]
_DUCK_LEG_B = [
    (2,8),(3,8),(2,9),(3,9),(2,10),
    (7,8),(8,8),(7,9),(8,9),(8,10),
]

# X-eye pixels (death)
_EYE_X = [(6,2),(8,2),(7,3),(6,4),(8,4)]


class TRex:
    STAND_H = 60   # standing pixel height
    DUCK_H  = 30   # ducking pixel height
    WIDTH   = 48

    def __init__(self):
        self.reset()

    def reset(self):
        self.y       = GROUND_Y - self.STAND_H
        self.vy      = 0
        self.jumping = False
        self.ducking = False
        self.dead    = False
        self.frame   = 0
        self.blink   = 0     # blink counter for death animation

    def jump(self):
        if not self.jumping and not self.ducking:
            self.vy      = -18
            self.jumping = True

    def duck(self, on):
        self.ducking = on
        if on and self.jumping:
            self.vy = 2   # cut jump short

    def update(self, frame_count):
        if self.dead:
            self.blink += 1
            return

        self.frame = frame_count

        if self.ducking:
            self.y  = GROUND_Y - self.DUCK_H
            self.vy = 0
        else:
            self.vy += 0.85
            self.y  += self.vy
            floor = GROUND_Y - self.STAND_H
            if self.y >= floor:
                self.y       = floor
                self.vy      = 0
                self.jumping = False

    def get_rect(self):
        """Collision rectangle."""
        pad = 8
        if self.ducking:
            return pygame.Rect(DINO_X + pad, GROUND_Y - self.DUCK_H + pad,
                               self.WIDTH - pad * 2, self.DUCK_H - pad)
        else:
            return pygame.Rect(DINO_X + pad, self.y + pad,
                               self.WIDTH - pad * 2 - 8, self.STAND_H - pad * 2)

    def draw(self, surface):
        if self.dead and (self.blink // 5) % 2 == 1:
            return   # blink: skip every other frame

        ox, oy = DINO_X, int(self.y)
        f      = self.frame

        if self.ducking:
            draw_pixels(surface, _DUCK_BODY, ox, oy, C_DARK)
            draw_pixels(surface, _DUCK_NECK, ox, oy, C_DARK)
            draw_pixels(surface, _DUCK_HEAD, ox, oy, C_DARK)
            draw_pixels(surface, _DUCK_JAW,  ox, oy, C_DARK)
            # Eye
            draw_pixels(surface, [(15, 1)], ox, oy, C_WHITE)
            # Legs
            legs = _DUCK_LEG_A if (f // 4) % 2 == 0 else _DUCK_LEG_B
            draw_pixels(surface, legs, ox, oy, C_DARK)
        else:
            draw_pixels(surface, _HEAD, ox, oy, C_DARK)
            draw_pixels(surface, _NECK, ox, oy, C_DARK)
            draw_pixels(surface, _BODY, ox, oy, C_DARK)
            draw_pixels(surface, _TAIL, ox, oy, C_DARK)
            draw_pixels(surface, _ARM,  ox, oy, C_DARK)

            # Eye (white dot)
            draw_pixels(surface, [(7, 3)], ox, oy, C_WHITE)

            if self.dead:
                # X over eye
                draw_pixels(surface, _EYE_X, ox, oy, C_DARK)
                draw_pixels(surface, [(6,2),(8,2),(6,4),(8,4)], ox, oy, C_WHITE)
            else:
                # Animated jaw
                jaw = _JAW_OPEN if (f // 6) % 2 == 0 else _JAW_CLOSE
                draw_pixels(surface, jaw, ox, oy, C_DARK)

            # Legs
            stride = (f // 4) % 3
            if stride == 0:   legs = _LEG_A
            elif stride == 1: legs = _LEG_C
            else:             legs = _LEG_B
            draw_pixels(surface, legs, ox, oy, C_DARK)


# ═════════════════════════════════════════════════════════════════════════════
#  CACTUS
# ═════════════════════════════════════════════════════════════════════════════
_CACTUS = [
    # variant 0 – single tall
    [(1,c) for c in range(14)] +
    [(0,5),(2,5),(0,4),(2,4),(0,6),(2,6)],

    # variant 1 – double
    [(1,c) for c in range(2,14)] + [(0,6),(2,6),(0,5),(2,5)] +
    [(5,c) for c in range(14)]   + [(4,5),(6,5),(4,4),(6,4),(3,7),(4,7),(6,7),(7,7)],

    # variant 2 – triple cluster
    [(1,c) for c in range(3,14)] + [(0,7),(2,7),(0,6),(2,6)] +
    [(4,c) for c in range(14)]   + [(3,5),(5,5),(3,4),(5,4),(3,6),(5,6)] +
    [(8,c) for c in range(2,14)] + [(7,6),(9,6),(7,5),(9,5)],
]

_CACTUS_WIDTHS = [9, 22, 33]   # art-columns wide


class Cactus:
    HEIGHT_ROWS = 14

    def __init__(self, x):
        self.variant = random.randint(0, 2)
        self.w = _CACTUS_WIDTHS[self.variant] * PS
        self.h = self.HEIGHT_ROWS * PS
        self.x = x
        self.y = GROUND_Y - self.h

    def update(self, speed):
        self.x -= speed

    def get_rect(self):
        pad = 6
        return pygame.Rect(self.x + pad, self.y + pad,
                           self.w - pad * 2, self.h - pad)

    def draw(self, surface):
        draw_pixels(surface, _CACTUS[self.variant], int(self.x), self.y, C_DARK)

    def off_screen(self):
        return self.x + self.w < -20


# ═════════════════════════════════════════════════════════════════════════════
#  PTERODACTYL
# ═════════════════════════════════════════════════════════════════════════════
_PTERO_BODY = [
    (4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),
    (3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),
    (3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),
    (4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),
    (10,2),(11,2),(12,2),
    (9,3),(10,3),(11,3),(12,3),(13,3),
    (9,4),(10,4),(11,4),(12,4),(13,4),
    (13,5),(14,5),(15,5),(16,5),
    (13,6),(14,6),
]
_PTERO_WING_UP = [
    (0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),
    (1,1),(2,1),(3,1),(4,1),(5,1),
    (2,2),(3,2),(4,2),
    (8,0),(9,0),(10,0),(11,0),(12,0),(13,0),(14,0),
    (9,1),(10,1),(11,1),(12,1),(13,1),
    (10,2),(11,2),(12,2),
]
_PTERO_WING_DOWN = [
    (2,7),(3,7),(4,7),
    (1,8),(2,8),(3,8),(4,8),(5,8),
    (0,9),(1,9),(2,9),(3,9),(4,9),(5,9),(6,9),
    (9,7),(10,7),(11,7),
    (9,8),(10,8),(11,8),(12,8),(13,8),
    (10,9),(11,9),(12,9),(13,9),(14,9),
]

# Three flight heights: low (must jump over), mid, high (duck under)
PTERO_HEIGHTS = [
    GROUND_Y - TRex.STAND_H - 15,   # low  – jump required
    GROUND_Y - TRex.STAND_H - 45,   # mid
    GROUND_Y - TRex.STAND_H - 72,   # high – duck required
]


class Pterodactyl:
    WIDTH  = 52
    HEIGHT = 32

    def __init__(self, x):
        self.x    = x
        self.y    = random.choice(PTERO_HEIGHTS)
        self.w    = self.WIDTH
        self.h    = self.HEIGHT

    def update(self, speed):
        self.x -= speed

    def get_rect(self):
        pad = 7
        return pygame.Rect(self.x + pad, self.y + pad,
                           self.w - pad * 2, self.h - pad * 2)

    def draw(self, surface, frame):
        draw_pixels(surface, _PTERO_BODY, int(self.x), self.y, C_DARK)
        # Eye
        draw_pixels(surface, [(11, 3)], int(self.x), self.y, C_WHITE)
        wings = _PTERO_WING_UP if (frame // 7) % 2 == 0 else _PTERO_WING_DOWN
        draw_pixels(surface, wings, int(self.x), self.y, C_DARK)

    def off_screen(self):
        return self.x + self.w < -20


# ═════════════════════════════════════════════════════════════════════════════
#  CLOUD
# ═════════════════════════════════════════════════════════════════════════════
_CLOUD_PIX = [
    (3,0),(4,0),(5,0),(6,0),
    (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),
    (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),
    (0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),
    (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),
]


class Cloud:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = y

    def update(self):
        self.x -= 0.8

    def draw(self, surface):
        draw_pixels(surface, _CLOUD_PIX, int(self.x), self.y, C_CLOUD, ps=2)

    def off_screen(self):
        return self.x < -130


# ═════════════════════════════════════════════════════════════════════════════
#  GROUND SCROLLER
# ═════════════════════════════════════════════════════════════════════════════
_PEBBLE_OFFSETS = [4, 14, 22, 35, 44, 53, 7, 28, 40, 60]


class Ground:
    def __init__(self):
        self.scroll = 0.0

    def update(self, speed):
        self.scroll = (self.scroll + speed) % 700

    def draw(self, surface):
        pygame.draw.line(surface, C_DARK, (0, GROUND_Y), (W, GROUND_Y), 2)
        sx = int(self.scroll)
        for seg in range(-1, W // 70 + 2):
            bx = seg * 70 - (sx % 70)
            for i, o in enumerate(_PEBBLE_OFFSETS):
                px2 = bx + o
                row_off = i % 3
                if -4 < px2 < W + 4:
                    pygame.draw.rect(surface, C_DARK,
                                     (px2, GROUND_Y + 3 + row_off * 2,
                                      2 + (i % 2), 1))


# ═════════════════════════════════════════════════════════════════════════════
#  GAME
# ═════════════════════════════════════════════════════════════════════════════
class Game:
    def __init__(self, screen, font_big, font_med, font_sm):
        self.screen   = screen
        self.font_big = font_big
        self.font_med = font_med
        self.font_sm  = font_sm
        self.hi_score = 0
        self.reset()

    def reset(self):
        self.dino          = TRex()
        self.obstacles     = []
        self.clouds        = [Cloud(random.randint(100, 700),
                                    random.randint(30, 90)) for _ in range(4)]
        self.ground        = Ground()
        self.score         = 0.0
        self.speed         = 6.0
        self.frame_count   = 0
        self.spawn_timer   = 0
        self.spawn_interval = 90
        self.state         = "idle"   # idle | playing | dead

    def _spawn(self):
        r = random.random()
        if self.score > 300 and r < 0.28:
            self.obstacles.append(Pterodactyl(W + 10))
        else:
            self.obstacles.append(Cactus(W + 10))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if self.state == "idle":
                    self.state = "playing"
                elif self.state == "dead":
                    self.hi_score = max(self.hi_score, int(self.score))
                    self.reset()
                    self.state = "playing"
                else:
                    self.dino.jump()

            elif event.key == pygame.K_DOWN:
                if self.state == "playing":
                    self.dino.duck(True)

            elif event.key == pygame.K_r and self.state == "dead":
                self.hi_score = max(self.hi_score, int(self.score))
                self.reset()
                self.state = "playing"

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.dino.duck(False)

    def update(self):
        if self.state != "playing":
            return

        self.frame_count += 1
        self.score  += 0.1
        self.speed   = min(6.0 + self.score * 0.005, 18.0)

        # Animate faster at higher speeds
        anim_rate = max(3, 8 - int(self.speed // 3))
        anim_frame = self.frame_count // anim_rate * anim_rate  # step

        self.dino.update(self.frame_count)
        self.ground.update(self.speed)

        # Clouds
        for c in self.clouds:
            c.update()
        self.clouds = [c for c in self.clouds if not c.off_screen()]
        if len(self.clouds) < 5 and random.random() < 0.01:
            self.clouds.append(Cloud(W + 60, random.randint(25, 90)))

        # Obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self._spawn()
            self.spawn_timer = 0
            self.spawn_interval = max(40,
                int(80 - self.score * 0.02) + random.randint(0, 30))

        for o in self.obstacles:
            o.update(self.speed)

        # Collision
        dino_rect = self.dino.get_rect()
        for o in self.obstacles:
            if dino_rect.colliderect(o.get_rect()):
                self.dino.dead = True
                self.state     = "dead"
                self.hi_score  = max(self.hi_score, int(self.score))
                break

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

    def draw(self):
        self.screen.fill(C_BG)

        # Clouds
        for c in self.clouds:
            c.draw(self.screen)

        # Ground
        self.ground.draw(self.screen)

        # Obstacles
        for o in self.obstacles:
            if isinstance(o, Pterodactyl):
                o.draw(self.screen, self.frame_count)
            else:
                o.draw(self.screen)

        # Dino
        self.dino.draw(self.screen)

        # ── HUD ──────────────────────────────────────────────────────────────
        score_str = str(int(self.score)).zfill(5)
        score_surf = self.font_med.render(score_str, True, C_DARK)
        self.screen.blit(score_surf, (W - score_surf.get_width() - 16, 18))

        if self.hi_score > 0:
            hi_str  = f"HI  {str(self.hi_score).zfill(5)}"
            hi_surf = self.font_med.render(hi_str, True, C_HUD_DIM)
            self.screen.blit(hi_surf, (W - hi_surf.get_width() - 100, 18))

        # ── Overlays ─────────────────────────────────────────────────────────
        if self.state == "idle":
            msg = self.font_med.render("PRESS  SPACE  TO  START", True, C_DARK)
            self.screen.blit(msg, (W // 2 - msg.get_width() // 2, GROUND_Y - 50))

        elif self.state == "dead":
            over  = self.font_big.render("G A M E   O V E R", True, C_DARK)
            retry = self.font_sm.render("PRESS  SPACE  OR  R  TO  RESTART",
                                        True, C_HUD_DIM)
            self.screen.blit(over,  (W // 2 - over.get_width()  // 2, GROUND_Y - 75))
            self.screen.blit(retry, (W // 2 - retry.get_width() // 2, GROUND_Y - 32))

            # Replay arrow  ▶
            arrow_cx = W // 2
            arrow_cy = GROUND_Y + 15
            pygame.draw.polygon(self.screen, C_DARK, [
                (arrow_cx - 14, arrow_cy - 12),
                (arrow_cx - 14, arrow_cy + 12),
                (arrow_cx + 14, arrow_cy),
            ])

        pygame.display.flip()


# ═════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Chrome Dino")
    clock  = pygame.time.Clock()

    # Fonts – use the built-in monospace fallback
    try:
        font_big = pygame.font.SysFont("couriernew", 28, bold=True)
        font_med = pygame.font.SysFont("couriernew", 20, bold=True)
        font_sm  = pygame.font.SysFont("couriernew", 14)
    except Exception:
        font_big = pygame.font.Font(None, 34)
        font_med = pygame.font.Font(None, 24)
        font_sm  = pygame.font.Font(None, 18)

    game = Game(screen, font_big, font_med, font_sm)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update()
        game.draw()
        clock.tick(FPS)


if __name__ == "__main__":
    main()