# 🦖 Dino AI - Reinforcement Learning Chrome Dino Game

A **Chrome Dino game clone built with Python and Pygame**, integrated with an **AI agent trained using PyTorch**.

The AI learns to automatically **jump over obstacles** using a neural network trained with reinforcement learning.

---

## 👨‍💻 Author

**Sidharth Thakur**

---

## 🚀 Features

- Chrome Dino style game built with **Pygame**
- AI agent powered by **PyTorch**
- Reinforcement learning training script
- Automatic gameplay using trained AI
- Modular project structure

---

## 🧠 How the AI Works

The AI observes the following game state:

```
distance_to_obstacle
obstacle_height
dino_y_position
game_speed
```

The neural network predicts an action:

```
0 → Do nothing
1 → Jump
2 → Duck
```

The training process follows the reinforcement learning pipeline:

```
State → Model → Action → Reward → Training
```

---

## 📂 Project Structure

```
dino-ai/
│
├── dino.py          # Game with AI integration
├── train.py         # Reinforcement learning training script
│
├── backend/
│   └── model.py     # Neural network architecture
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

Clone the repository:

```
git clone https://github.com/sidharth-thakur/AI_Dino_game.git
cd dino-ai
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## 🎮 Run the Game

Run the Dino game with AI:

```
python dino.py
```

The AI will automatically control the dinosaur.

---

## 🤖 Train the AI Model

To train the AI:

```
python train.py
```

Training will run for multiple episodes and save the trained model as:

```
backend/dino_model.pth
```

---

## 📊 Example Training Output

```
Episode 1 Reward -100
Episode 50 Reward 200
Episode 200 Reward 900
Episode 1000 Reward 2500
```

Higher rewards indicate the AI survives longer.

---

## 🛠 Technologies Used

- Python
- Pygame
- PyTorch
- NumPy

---

## 📈 Future Improvements

- Better reward system
- Faster training environment
- Bird obstacle detection
- Performance visualization
- Improved AI model architecture

---

## ⭐ Support

If you like this project, consider giving it a **star ⭐ on GitHub**.