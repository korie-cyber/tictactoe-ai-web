import os
import pickle
import random
import numpy as np
from datetime import datetime

class TicTacToeAI:
    """An adaptive AI for Tic-Tac-Toe using Q-learning"""
    
    def __init__(self, q_file='q_values.pkl', exploration_rate=0.1, learning_rate=0.5, discount_factor=0.9, 
                 decay_rate=0.995, min_exploration_rate=0.01, backup_interval=100):
        self.q = {}  # Q-values dictionary: state -> [q-values for each action]
        self.q_file = q_file
        self.exploration_rate = exploration_rate  # Initial exploration rate (epsilon)
        self.learning_rate = learning_rate  # Alpha
        self.discount_factor = discount_factor  # Gamma
        self.decay_rate = decay_rate  # Rate at which exploration decreases
        self.min_exploration_rate = min_exploration_rate  # Minimum exploration rate
        self.backup_interval = backup_interval  # How often to back up q-values
        self.moves_since_backup = 0
        self.game_history = []  # Record of states and actions for current game
        self.load_q_values()
    
    def board_to_state(self, board):
        """Convert board to a string representation"""
        return ''.join(cell if cell != ' ' else '-' for cell in board)
    
    def load_q_values(self):
        """Load Q-values from file if it exists"""
        if os.path.exists(self.q_file):
            try:
                with open(self.q_file, 'rb') as f:
                    self.q = pickle.load(f)
                print(f"Loaded {len(self.q)} states from {self.q_file}")
            except Exception as e:
                print(f"Error loading Q-values: {e}")
                self.q = {}
        else:
            print(f"No existing Q-values file found at {self.q_file}")
            self.q = {}
    
    def save_q_values(self, force=False):
        """Save Q-values to file"""
        self.moves_since_backup += 1
        
        # Only save periodically or when forced to avoid excessive disk I/O
        if force or self.moves_since_backup >= self.backup_interval:
            try:
                # Create backup with timestamp
                if os.path.exists(self.q_file):
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    backup_file = f"{self.q_file}.{timestamp}.bak"
                    
                    # Keep only the 5 most recent backups
                    backups = [f for f in os.listdir('.') if f.startswith(f"{self.q_file}.") and f.endswith('.bak')]
                    if len(backups) >= 5:
                        backups.sort()  # Sort by timestamp
                        for old_backup in backups[:-4]:  # Keep the 4 newest, delete the rest
                            try:
                                os.remove(old_backup)
                            except:
                                pass
                    
                    # Create a new backup
                    with open(self.q_file, 'rb') as src, open(backup_file, 'wb') as dst:
                        dst.write(src.read())
                
                # Save current Q-values
                with open(self.q_file, 'wb') as f:
                    pickle.dump(self.q, f)
                print(f"Saved {len(self.q)} states to {self.q_file}")
                self.moves_since_backup = 0
            except Exception as e:
                print(f"Error saving Q-values: {e}")
    
    def get_state_key(self, board, player):
        """Generate a unique key for the current board state and player"""
        # Use board representation and player marker
        return self.board_to_state(board) + player
    
    def get_available_moves(self, board):
        """Get list of available moves"""
        return [i for i, cell in enumerate(board) if cell == ' ']
    
    def make_move(self, board, player):
        """
        Choose a move using epsilon-greedy strategy
        Returns the chosen move index
        """
        state_key = self.get_state_key(board, player)
        available_moves = self.get_available_moves(board)
        
        if not available_moves:
            return None  # No valid moves
        
        # Initialize q-values for this state if we haven't seen it before
        if state_key not in self.q:
            self.q[state_key] = [0.0] * 9  # Initialize with zeros for all 9 positions
        
        # Exploration vs exploitation (epsilon-greedy)
        if random.random() < self.exploration_rate:
            # Exploration: choose a random move
            move = random.choice(available_moves)
        else:
            # Exploitation: choose the best move according to Q-values
            # but only from available moves
            q_values = self.q[state_key]
            
            # Get q-values only for available moves
            available_q_values = [(i, q_values[i]) for i in available_moves]
            
            # Find best move(s) among available ones
            max_q = max(available_q_values, key=lambda x: x[1])[1]
            best_moves = [i for i, q in available_q_values if q == max_q]
            
            # Choose randomly among best moves to break ties
            move = random.choice(best_moves)
        
        # Record this state and action for potential later updates
        self.game_history.append((state_key, move))
        
        # Decrease exploration rate over time
        self.exploration_rate = max(
            self.min_exploration_rate, 
            self.exploration_rate * self.decay_rate
        )
        
        return move
    
    def reward(self, reward_value, board, move, player='O'):
        """
        Update Q-value for the given state-action pair
        reward_value: 1 for win, 0.5 for tie, 0 for ongoing, -1 for loss
        """
        state_key = self.get_state_key(board, player)
        
        if state_key not in self.q:
            self.q[state_key] = [0.0] * 9
        
        # Update Q-value using the learning rate
        old_value = self.q[state_key][move]
        new_value = old_value + self.learning_rate * (reward_value - old_value)
        self.q[state_key][move] = new_value
        
        # Save Q-values periodically
        self.save_q_values()
    
    def update_q_value(self, board, move, reward, next_board, player='O'):
        """
        Update Q-value using Q-learning formula with consideration of future rewards
        Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
        """
        state_key = self.get_state_key(board, player)
        next_state_key = self.get_state_key(next_board, player)
        
        if state_key not in self.q:
            self.q[state_key] = [0.0] * 9
        if next_state_key not in self.q:
            self.q[next_state_key] = [0.0] * 9
        
        # Get the best next action's value
        best_next_q = max(self.q[next_state_key])
        
        # Q-learning update formula
        self.q[state_key][move] += self.learning_rate * (
            reward + self.discount_factor * best_next_q - self.q[state_key][move]
        )
        
        # Save Q-values periodically
        self.save_q_values()
    
    def reset_game_history(self):
        """Clear the history of the current game"""
        self.game_history = []
    
    def perform_batch_update(self, final_reward):
        """
        Update all state-action pairs in the current game with discounted rewards
        This implements a form of eligibility traces
        """
        if not self.game_history:
            return
        
        # Calculate discounted rewards backward from the end
        current_reward = final_reward
        for state_key, action in reversed(self.game_history):
            if state_key not in self.q:
                self.q[state_key] = [0.0] * 9
            
            # Update Q-value
            self.q[state_key][action] += self.learning_rate * (
                current_reward - self.q[state_key][action]
            )
            
            # Discount the reward for earlier states
            current_reward *= self.discount_factor
        
        # Clear history after updates
        self.reset_game_history()
        
        # Force save after batch update
        self.save_q_values(force=True)
    
    def get_board_evaluation(self, board, player):
        """
        Evaluate the current board state from the perspective of the given player
        Returns a value between -1 and 1
        """
        state_key = self.get_state_key(board, player)
        
        if state_key not in self.q:
            return 0.0  # Neutral evaluation for unknown states
        
        available_moves = self.get_available_moves(board)
        if not available_moves:
            return 0.0  # No moves available
        
        # Get max Q-value among available moves
        q_values = [self.q[state_key][move] for move in available_moves]
        return max(q_values) if q_values else 0.0 