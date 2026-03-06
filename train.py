import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np

from backend.model import model
from dino import Game

# Hyperparameters
GAMMA = 0.9
LR = 0.001
EPISODES = 1000
EPSILON = 1.0
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.01

optimizer = optim.Adam(model.parameters(), lr=LR)
criterion = nn.MSELoss()

def choose_action(state, epsilon):

    if random.random() < epsilon:
        return random.randint(0,2)

    state = torch.tensor(state).float().unsqueeze(0)

    with torch.no_grad():
        q_values = model(state)

    return torch.argmax(q_values).item()

def train_step(state, action, reward, next_state, done):

    state = torch.tensor(state).float()
    next_state = torch.tensor(next_state).float()

    q_values = model(state)
    next_q_values = model(next_state)

    target = q_values.clone()

    if done:
        target[action] = reward
    else:
        target[action] = reward + GAMMA * torch.max(next_q_values)

    loss = criterion(q_values, target)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


def train():

    global EPSILON

    game = Game(None, None)  # headless training

    for episode in range(EPISODES):

        game.reset()

        total_reward = 0

        while True:

            state = game.get_state()

            action = choose_action(state, EPSILON)

            if action == 1:
                game.dino.jump()

            game.update()

            next_state = game.get_state()

            reward = 1

            done = False

            # collision check
            dino_rect = game.dino.get_rect()

            for o in game.obstacles:
                if dino_rect.colliderect(o.get_rect()):
                    reward = -100
                    done = True

            train_step(state, action, reward, next_state, done)

            total_reward += reward

            if done:
                break

        EPSILON = max(EPSILON * EPSILON_DECAY, EPSILON_MIN)

        print(f"Episode {episode} Reward {total_reward}")

        if episode % 100 == 0:
            torch.save(model.state_dict(), "backend/dino_model.pth")


if __name__ == "__main__":
    train()