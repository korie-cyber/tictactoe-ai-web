# Ultimate Tic-Tac-Toe Challenge

An advanced Tic-Tac-Toe game with multiple difficulty levels including an adaptive AI that learns from gameplay using Q-learning.

## Features

- Multiple difficulty levels: Easy, Medium, Hard, and Adaptive AI
- Play as X or O (X goes first)
- Responsive design for mobile and desktop
- Game statistics tracking
- Animations and visual feedback
- Adaptive AI that learns from your moves

## Deployment Instructions

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:5000`

### Deploying to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Python Version: 3.9 (or newer)
4. Click "Create Web Service"

### Deploying to Vercel

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Deploy:
   ```
   vercel
   ```

3. Or deploy directly from the Vercel dashboard:
   - Import your GitHub repository
   - Vercel will automatically detect it's a Flask application
   - Deploy

## Project Structure

- `app.py`: Main Flask application
- `tictactoe_ai.py`: AI implementation with Q-learning
- `templates/index.html`: Frontend HTML, CSS, and JavaScript
- `game_stats.json`: Game statistics storage
- `q_values.pkl`: Q-learning values storage

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- AI: Custom Q-learning implementation

## License

MIT License