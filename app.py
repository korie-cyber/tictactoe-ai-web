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
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'games': 0, 'human_wins': 0, 'ai_wins': 0, 'ties': 0}
    return {'games': 0, 'human_wins': 0, 'ai_wins': 0, 'ties': 0}

def save_stats(stats):
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
    human_player = 'X' if ai_player == 'O' else 'X'
    
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
        _, best_move = minimax(board, 0, True, ai_player=ai_player)
        return best_move
    
    else:  # "adaptive" or any other value defaults to adaptive
        # Adaptive difficulty: use Q-learning
        return ai.make_move(board, ai_player)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    """Process a move and respond with the AI's move"""
    data = request.get_json()
    board = data['board']
    human_player = data['humanPlayer']
    difficulty = data.get('difficulty', 'adaptive')  # Default to adaptive if not provided
    ai_player = 'O' if human_player == 'X' else 'X'

    # Check if human won or board is full
    winner, win_pattern = check_winner(board)
    if winner:
        return jsonify({
            'status': 'win', 
            'winner': winner,
            'line': WIN_PATTERNS.index(win_pattern) if win_pattern else -1
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

@app.route('/game_over', methods=['POST'])
def game_over():
    """Record the game outcome and update AI's learning"""
    data = request.get_json()
    board = data['board']
    result = data['result']
    human_player = data['humanPlayer']
    difficulty = data.get('difficulty', 'adaptive')
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

    return jsonify({'status': 'ok'})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Return the current game statistics"""
    stats = load_stats()
    return jsonify(stats)

# Create templates folder if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Write index.html to templates folder if it doesn't exist
if not os.path.exists('templates/index.html'):
    with open('templates/index.html', 'w') as f:
        with open('index.html', 'r') as source:
            f.write(source.read())

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)