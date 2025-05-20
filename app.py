from flask import Flask, render_template, request, jsonify
import json
from tictactoe_ai import TicTacToeAI

app = Flask(__name__)
ai = TicTacToeAI()

@app.route('/')
def index():
    """Render the game page"""
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    """Process a move and return the AI's response"""
    data = request.get_json()
    board = data['board']
    human_player = data['humanPlayer']
    ai_player = 'O' if human_player == 'X' else 'X'
    
    # Check if game is already over
    if check_win(board, human_player):
        return jsonify({"status": "win", "winner": human_player})
    elif check_win(board, ai_player):
        return jsonify({"status": "win", "winner": ai_player})
    elif check_tie(board):
        return jsonify({"status": "tie"})
    
    # AI's turn
    available_actions = [i for i in range(9) if board[i] == ' ']
    if not available_actions:
        return jsonify({"status": "tie"})
    
    # Get AI move
    ai_move = ai.make_move(board, ai_player)
    board[ai_move] = ai_player
    
    # Check game status after AI move
    if check_win(board, ai_player):
        ai.reward(1.0, board, [])  # AI wins
        ai.save_q_values()
        return jsonify({"status": "win", "winner": ai_player, "move": ai_move, "board": board})
    elif check_tie(board):
        ai.reward(0.2, board, [])  # Tie
        ai.save_q_values()
        return jsonify({"status": "tie", "move": ai_move, "board": board})
    else:
        available_actions = [i for i in range(9) if board[i] == ' ']
        ai.reward(0.0, board, available_actions)  # Game continues
        return jsonify({"status": "ongoing", "move": ai_move, "board": board})

@app.route('/game_over', methods=['POST'])
def game_over():
    """Handle game over scenarios and rewards"""
    data = request.get_json()
    board = data['board']
    result = data['result']
    human_player = data['humanPlayer']
    ai_player = 'O' if human_player == 'X' else 'X'
    
    if result == "human_win":
        ai.reward(-1.0, board, [])  # Negative reward for AI losing
    elif result == "ai_win":
        ai.reward(1.0, board, [])  # Positive reward for AI winning
    elif result == "tie":
        ai.reward(0.2, board, [])  # Small positive reward for tie
    
    ai.save_q_values()
    return jsonify({"status": "success"})

def check_win(board, player):
    """Check if the specified player has won"""
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    
    for combo in winning_combinations:
        if all(board[i] == player for i in combo):
            return True
    return False

def check_tie(board):
    """Check if the game is a tie"""
    return ' ' not in board

if __name__ == '__main__':
    app.run(debug=True)