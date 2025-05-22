import random
import json
import os
from collections import defaultdict

class TicTacToeAI:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.3):
        """
        Initialize the Q-learning AI for Tic-Tac-Toe
        
        Args:
            learning_rate: How much the AI learns from each experience (0-1)
            discount_factor: How much the AI values future rewards (0-1)
            exploration_rate: How often the AI explores vs exploits (0-1)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.load_q_table()
        
    def get_board_state(self, board):
        """Convert board to a string representation for Q-table indexing"""
        return ''.join(board)
    
    def get_available_moves(self, board):
        """Get all available moves on the board"""
        return [i for i, cell in enumerate(board) if cell == ' ']
    
    def make_move(self, board, player):
        """
        Make a move using Q-learning strategy
        
        Args:
            board: Current board state
            player: The AI player ('X' or 'O')
            
        Returns:
            The chosen move index
        """
        state = self.get_board_state(board)
        available_moves = self.get_available_moves(board)
        
        if not available_moves:
            return None
        
        # Exploration vs Exploitation
        if random.random() < self.exploration_rate:
            # Explore: choose a random move
            return random.choice(available_moves)
        else:
            # Exploit: choose the best known move
            best_move = None
            best_value = float('-inf')
            
            for move in available_moves:
                q_value = self.q_table[state][move]
                if q_value > best_value:
                    best_value = q_value
                    best_move = move
            
            # If all Q-values are the same (or 0), choose randomly
            if best_move is None or best_value == 0:
                return random.choice(available_moves)
            
            return best_move
    
    def reward(self, reward_value, prev_board, move, player):
        """
        Update Q-values based on the reward received
        
        Args:
            reward_value: The reward for the move (-1 for loss, 0 for ongoing, 0.5 for tie, 1 for win)
            prev_board: The board state before the move
            move: The move that was made
            player: The player who made the move
        """
        if move is None:
            return
            
        prev_state = self.get_board_state(prev_board)
        
        # Create new board state after the move
        new_board = prev_board[:]
        new_board[move] = player
        new_state = self.get_board_state(new_board)
        
        # Get the maximum Q-value for the new state
        available_moves = self.get_available_moves(new_board)
        max_future_q = 0
        if available_moves:
            max_future_q = max([self.q_table[new_state][m] for m in available_moves])
        
        # Q-learning update formula
        current_q = self.q_table[prev_state][move]
        new_q = current_q + self.learning_rate * (
            reward_value + self.discount_factor * max_future_q - current_q
        )
        self.q_table[prev_state][move] = new_q
        
        # Save the updated Q-table
        self.save_q_table()
    
    def load_q_table(self):
        """Load Q-table from file if it exists"""
        try:
            if os.path.exists('q_table.json'):
                with open('q_table.json', 'r') as f:
                    data = json.load(f)
                    # Convert back to defaultdict structure
                    for state, actions in data.items():
                        for action, value in actions.items():
                            self.q_table[state][int(action)] = value
        except Exception as e:
            print(f"Error loading Q-table: {e}")
            self.q_table = defaultdict(lambda: defaultdict(float))
    
    def save_q_table(self):
        """Save Q-table to file"""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            data = {}
            for state, actions in self.q_table.items():
                data[state] = dict(actions)
            
            with open('q_table.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving Q-table: {e}")
            # In production environments, we might not have write access
            pass
    
    def get_stats(self):
        """Get statistics about the AI's learning"""
        total_states = len(self.q_table)
        total_q_values = sum(len(actions) for actions in self.q_table.values())
        
        return {
            'total_states': total_states,
            'total_q_values': total_q_values,
            'exploration_rate': self.exploration_rate,
            'learning_rate': self.learning_rate
        }
    
    def adjust_difficulty(self, win_rate):
        """
        Adjust the AI's difficulty based on the player's win rate
        
        Args:
            win_rate: Player's win rate (0-1)
        """
        # If player is winning too much, decrease exploration (make AI stronger)
        if win_rate > 0.6:
            self.exploration_rate = max(0.1, self.exploration_rate - 0.05)
        # If player is losing too much, increase exploration (make AI weaker)
        elif win_rate < 0.3:
            self.exploration_rate = min(0.5, self.exploration_rate + 0.05)
        
        # Save the adjusted parameters
        self.save_q_table()