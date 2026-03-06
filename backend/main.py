from fastapi import FastAPI
from pydantic import BaseModel
import torch

from model import model

app = FastAPI()


class GameState(BaseModel):
    distance: float
    obstacle_height: float
    dino_y: float
    speed: float


@app.post("/predict")
def predict_action(state: GameState):

    inputs = torch.tensor([
        state.distance,
        state.obstacle_height,
        state.dino_y,
        state.speed
    ], dtype=torch.float32)

    inputs = inputs.unsqueeze(0)

    with torch.no_grad():
        output = model(inputs)
        action = torch.argmax(output).item()

    if action == 1:
        return {"action": "jump"}
    else:
        return {"action": "none"}