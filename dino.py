import pygame
import random
import sys
import torch

# import AI model
from backend.model import model

# load trained weights
try:
    model.load_state_dict(torch.load("backend/dino_model.pth"))
except:
    print("No trained model found, using random weights")

model.eval()

# ─────────────────────────────
# CONSTANTS
# ─────────────────────────────
W, H = 900, 350
FPS = 60
GROUND_Y = 280
DINO_X = 70

WHITE = (255,255,255)
BLACK = (0,0,0)

# ─────────────────────────────
# DINO
# ─────────────────────────────
class Dino:

    def __init__(self):
        self.width = 40
        self.height = 40
        self.y = GROUND_Y - self.height
        self.vel = 0
        self.jumping = False

    def jump(self):
        if not self.jumping:
            self.vel = -16
            self.jumping = True

    def update(self):
        self.vel += 0.9
        self.y += self.vel

        floor = GROUND_Y - self.height

        if self.y >= floor:
            self.y = floor
            self.vel = 0
            self.jumping = False

    def draw(self,screen):
        pygame.draw.rect(screen,BLACK,(DINO_X,self.y,self.width,self.height))

    def get_rect(self):
        return pygame.Rect(DINO_X,self.y,self.width,self.height)

# ─────────────────────────────
# CACTUS
# ─────────────────────────────
class Cactus:

    def __init__(self,x):
        self.width = random.choice([20,30])
        self.height = random.choice([40,50])
        self.x = x
        self.y = GROUND_Y - self.height

    def update(self,speed):
        self.x -= speed

    def draw(self,screen):
        pygame.draw.rect(screen,BLACK,(self.x,self.y,self.width,self.height))

    def off_screen(self):
        return self.x + self.width < 0

    def get_rect(self):
        return pygame.Rect(self.x,self.y,self.width,self.height)

# ─────────────────────────────
# GAME
# ─────────────────────────────
class Game:

    def __init__(self,screen,font):
        self.screen = screen
        self.font = font
        self.reset()

    def reset(self):
        self.dino = Dino()
        self.obstacles = []
        self.score = 0
        self.speed = 6
        self.spawn_timer = 0

    # ───── AI STATE
    def get_state(self):

        if not self.obstacles:
            return [999,0,self.dino.y,self.speed]

        obstacle = self.obstacles[0]

        distance = obstacle.x - DINO_X
        height = obstacle.height

        return [
            distance,
            height,
            self.dino.y,
            self.speed
        ]

    def update(self):

        self.score += 0.1
        self.speed = min(6 + self.score * 0.01,18)

        self.dino.update()

        # spawn obstacles
        self.spawn_timer += 1

        if self.spawn_timer > random.randint(70,120):
            self.obstacles.append(Cactus(W))
            self.spawn_timer = 0

        for o in self.obstacles:
            o.update(self.speed)

        # collision
        dino_rect = self.dino.get_rect()

        for o in self.obstacles:
            if dino_rect.colliderect(o.get_rect()):
                self.game_over = True

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

    def draw(self):

        self.screen.fill(WHITE)

        pygame.draw.line(self.screen,BLACK,(0,GROUND_Y),(W,GROUND_Y),2)

        for o in self.obstacles:
            o.draw(self.screen)

        self.dino.draw(self.screen)

        score_text = self.font.render(str(int(self.score)),True,BLACK)
        self.screen.blit(score_text,(W-120,20))

        pygame.display.update()

# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():

    pygame.init()

    screen = pygame.display.set_mode((W,H))
    pygame.display.set_caption("Dino AI")

    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial",24)

    game = Game(screen,font)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # get environment state
        state = game.get_state()

        # convert to tensor
        state_tensor = torch.tensor(state).float().unsqueeze(0)

        # AI prediction
        with torch.no_grad():
            output = model(state_tensor)
            action = torch.argmax(output).item()

        # execute action
        if action == 1:
            game.dino.jump()

        game.update()
        game.draw()

        clock.tick(FPS)

if __name__ == "__main__":
    main()