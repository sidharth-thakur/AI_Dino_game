import torch
import torch.nn as nn

class DinoAI(nn.Module):

    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(4,16),
            nn.ReLU(),
            nn.Linear(16,16),
            nn.ReLU(),
            nn.Linear(16,2)
        )

    def forward(self,x):
        return self.network(x)


model = DinoAI()

# load trained model if available
try:
    model.load_state_dict(torch.load("dino_model.pth"))
except:
    pass

model.eval()