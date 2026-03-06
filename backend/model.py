import torch.nn as nn

class DinoAI(nn.Module):

    def __init__(self):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(4,32),
            nn.ReLU(),
            nn.Linear(32,32),
            nn.ReLU(),
            nn.Linear(32,3)
        )

    def forward(self,x):
        return self.net(x)

model = DinoAI()