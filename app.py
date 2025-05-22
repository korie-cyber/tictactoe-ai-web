from flask import Flask, render_template, request, jsonify
from tictactoe_ai import TicTacToeAI
import random
import json
import os 

app = Flask(__name__)
ai = TicTacToeAI()

# Win patterns for checking victory
WIN_PATTERNS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
    [0, 4, 8], [2, 4, 6]              # diagonals
]

# Global stats tracking
STATS_FILE = 'game_stats.json'

def load_stats():
    """Load game statistics from file"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'games': 0, 'human_wins': 0, 'ai_wins': 0, 'ties': 0}
    return {'games': 0, 'human_wins': 0, 'ai_wins': 0, 'ties': 0}

def save_stats(stats):
    """Save game statistics to file"""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f)
    except Exception as e:
        print(f"Error saving stats: {e}")
        # In production environments, we might not have write access
        pass

def check_winner(board):
    """Check if there is a winner"""
    for pattern in WIN_PATTERNS:
        a, b, c = pattern
        if board[a] == board[b] == board[c] != ' ':
            return board[a], pattern  # Return winner and winning pattern
    return None, None

def is_full(board):
    """Check if the board is full"""
    return ' ' not in board

def get_available_moves(board):
    """Get all available moves"""
    return [i for i, cell in enumerate(board) if cell == ' ']

def minimax(board, depth, is_maximizing, alpha=-float('inf'), beta=float('inf'), ai_player='O'):
    """Minimax algorithm with alpha-beta pruning for hard difficulty"""
    human_player = 'X' if ai_player == 'O' else 'O'
    
    # Check for terminal states
    winner, _ = check_winner(board)
    if winner == ai_player:
        return 10 - depth, None
    elif winner == human_player:
        return depth - 10, None
    elif is_full(board):
        return 0, None
    
    if is_maximizing:
        best_score = -float('inf')
        best_move = None
        
        for move in get_available_moves(board):
            board[move] = ai_player
            score, _ = minimax(board, depth + 1, False, alpha, beta, ai_player)
            board[move] = ' '  # Undo move
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        
        return best_score, best_move
    else:
        best_score = float('inf')
        best_move = None
        
        for move in get_available_moves(board):
            board[move] = human_player
            score, _ = minimax(board, depth + 1, True, alpha, beta, ai_player)
            board[move] = ' '  # Undo move
            
            if score < best_score:
                best_score = score
                best_move = move
            
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        
        return best_score, best_move

def make_move_by_difficulty(board, difficulty, ai_player):
    """Make AI move based on difficulty level"""
    available_moves = get_available_moves(board)
    
    if not available_moves:
        return None
    
    if difficulty == "hard":
        # Hard difficulty: minimax algorithm
        _, best_move = minimax(board.copy(), 0, True, ai_player=ai_player)
        return best_move
    else:  # "adaptive" or any other value defaults to adaptive
        # Adaptive difficulty: use Q-learning
        return ai.make_move(board, ai_player)

@app.route('/')
def index():
    """Render the main page"""
    # Check if we need to create templates directory and copy the HTML
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create the template file from the updated HTML
    template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TIC-TAC-TOE Challenge</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
    <!-- CSS and JavaScript content would go here -->
</head>
<body>
    <!-- The full HTML content from the artifact would be here -->
</body>
</html>"""
    
    # For now, serve a simple template - in production you'd use the full HTML
    return render_template_string(template_content)

# Alternative route to serve the HTML directly
@app.route('/game')
def game():
    """Serve the game HTML directly"""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Game file not found. Please ensure index.html is in the same directory as app.py"

@app.route('/make_move', methods=['POST'])
def make_move():
    """Process a move and respond with the AI's move"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'})
        
        board = data.get('board')
        human_player = data.get('humanPlayer')
        difficulty = data.get('difficulty', 'adaptive')
        
        if not board or not human_player:
            return jsonify({'status': 'error', 'message': 'Missing required data'})
        
        ai_player = 'O' if human_player == 'X' else 'X'

        # Check if human won or board is full after human move
        winner, win_pattern = check_winner(board)
        if winner:
            line_index = WIN_PATTERNS.index(win_pattern) if win_pattern else -1
            return jsonify({
                'status': 'win', 
                'winner': winner,
                'line': line_index
            })
        if is_full(board):
            return jsonify({'status': 'tie'})

        # AI makes a move
        move = make_move_by_difficulty(board, difficulty, ai_player)
        
        if move is None:
            return jsonify({'status': 'error', 'message': 'No valid moves available'})
        
        # Update board with AI's move
        new_board = board[:]
        new_board[move] = ai_player

        # Check outcome after AI move
        winner, win_pattern = check_winner(new_board)
        
        response = {'move': move}
        
        if winner:
            line_index = WIN_PATTERNS.index(win_pattern) if win_pattern else -1
            # If using adaptive AI, update the Q-values
            if difficulty == "adaptive":
                ai.reward(1, board, move, ai_player)
            response.update({'status': 'win', 'winner': winner, 'line': line_index})
        elif is_full(new_board):
            # If using adaptive AI, update the Q-values
            if difficulty == "adaptive":
                ai.reward(0.5, board, move, ai_player)
            response.update({'status': 'tie'})
        else:
            # If using adaptive AI, provide initial feedback
            if difficulty == "adaptive":
                ai.reward(0, board, move, ai_player)
            response.update({'status': 'continue'})

        return jsonify(response)
        
    except Exception as e:
        print(f"Error in make_move: {e}")
        return jsonify({'status': 'error', 'message': 'Server error occurred'})

@app.route('/game_over', methods=['POST'])
def game_over():
    """Record the game outcome and update AI's learning"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'})
        
        board = data.get('board')
        result = data.get('result')
        human_player = data.get('humanPlayer')
        difficulty = data.get('difficulty', 'adaptive')
        
        if not all([board, result, human_player]):
            return jsonify({'status': 'error', 'message': 'Missing required data'})
        
        ai_player = 'O' if human_player == 'X' else 'X'

        # Only update Q-values if using adaptive AI
        if difficulty == "adaptive":
            if result == 'human_win':
                # Penalize AI for losing
                for i, cell in enumerate(board):
                    if cell == ai_player:
                        ai.reward(-1, board, i, ai_player)
            elif result == 'tie':
                # Neutral reward for a tie
                for i, cell in enumerate(board):
                    if cell == ai_player:
                        ai.reward(0.5, board, i, ai_player)

        # Update global stats
        stats = load_stats()
        stats['games'] += 1
        
        if result == 'human_win':
            stats['human_wins'] += 1
        elif result == 'ai_win':
            stats['ai_wins'] += 1
        else:  # tie
            stats['ties'] += 1
        
        save_stats(stats)

        # Adjust AI difficulty based on win rate
        if difficulty == "adaptive" and stats['games'] > 0:
            human_win_rate = stats['human_wins'] / stats['games']
            ai.adjust_difficulty(human_win_rate)

        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Error in game_over: {e}")
        return jsonify({'status': 'error', 'message': 'Server error occurred'})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Return the current game statistics"""
    try:
        stats = load_stats()
        ai_stats = ai.get_stats()
        return jsonify({
            **stats,
            'ai_learning_stats': ai_stats
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'games': 0, 'human_wins': 0, 'ai_wins': 0, 'ties': 0})

@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    """Reset all game statistics"""
    try:
        stats = {'games': 0, 'human_wins': 0, 'ai_wins': 0, 'ties': 0}
        save_stats(stats)
        return jsonify({'status': 'ok', 'message': 'Stats reset successfully'})
    except Exception as e:
        print(f"Error resetting stats: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to reset stats'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# Template string function for simple rendering
def render_template_string(template_string, **context):
    """Simple template rendering function"""
    return template_string

# Create templates folder and files if they don't exist
def setup_templates():
    """Setup templates directory and files"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create a simple index.html template that redirects to /game
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TIC-TAC-TOE Challenge</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #242424, #121212);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .btn {
            padding: 12px 28px;
            background: linear-gradient(135deg, #000000, #333333);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>TIC-TAC-TOE Challenge</h1>
        <p>Welcome to the Adaptive AI Tic-Tac-Toe Game!</p>
        <a href="/game" class="btn">Start Playing</a>
    </div>
</body>
</html>'''
    
    with open('templates/index.html', 'w') as f:
        f.write(template_content)

if __name__ == '__main__':
    # Setup templates
    setup_templates()
    
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    print("Starting Tic-Tac-Toe AI Server...")
    print(f"Game available at: http://localhost:{port}/game")
    print(f"API endpoints: /make_move, /game_over, /stats")
    
    app.run(host='0.0.0.0', port=port, debug=True) 