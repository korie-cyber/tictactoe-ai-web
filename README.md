# Tic-Tac-Toe Challenge

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A sophisticated Tic-Tac-Toe web application featuring an intelligent adaptive AI that learns from gameplay through reinforcement learning (Q-learning).

## Features

- **Multiple AI Difficulty Levels**:
  - Easy: Random moves for beginners
  - Medium: Strategic but beatable AI
  - Hard: Minimax algorithm with alpha-beta pruning
  - Adaptive: Q-learning AI that improves by playing against you

- **User Experience**:
  - Play as X (first move) or O
  - Responsive design for all devices
  - Animations and visual feedback
  - Win/loss tracking statistics

- **Technical Highlights**:
  - Reinforcement learning implementation
  - Persistent AI model that remembers strategies
  - RESTful API for game state management
  - Clean separation between frontend and backend

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/ultimate-tictactoe.git
cd ultimate-tictactoe

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open browser at http://localhost:5000
```

### Deployment Options

#### Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Python Version: 3.9+

#### Vercel

```bash
npm install -g vercel
vercel
```

## How the AI Works

The adaptive AI implements Q-learning, a model-free reinforcement learning algorithm:

1. Each game state is represented as a unique key
2. The AI maintains Q-values for every possible move in each state
3. During gameplay, the AI uses an epsilon-greedy strategy to balance:
   - **Exploration**: Trying new moves to discover better strategies
   - **Exploitation**: Using moves that have worked well previously
4. After each game, Q-values are updated based on game outcomes:
   - Wins are strongly rewarded (+1)
   - Ties receive moderate rewards (+0.5)
   - Losses are penalized (-1)

This approach allows the AI to continuously improve and adapt to your play style.

## 🛠️ Project Structure

```
ultimate-tictactoe/
│
├── app.py                # Main Flask application
├── tictactoe_ai.py       # AI implementation with Q-learning
├── templates/
│   └── index.html        # Frontend (HTML, CSS, JavaScript)
├── game_stats.json       # Game statistics storage
├── q_values.pkl          # Persistent Q-learning model
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Technologies

- **Backend**:
  - Python with Flask
  - NumPy for numerical operations
  - Pickle for model persistence

- **Frontend**:
  - HTML5 & CSS3
  - Vanilla JavaScript
  - Responsive design with CSS Grid

## 📖 About

This project demonstrates my Python skills and software engineering capabilities, particularly in:
- Creating complete, production-ready applications
- Implementing machine learning algorithms from scratch
- Full-stack development with Python and JavaScript
- Problem-solving and analytical thinking

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
