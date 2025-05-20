import random
import pickle
import os.path

class TicTacToeAI:
    def __init__(self, learning_rate=0.1, exploration_rate=0.3):
        # Initialize Q-learning parameters
        self.learning_rate = learning_rate  # How quickly the AI adapts to new information
        self.exploration_rate = exploration_rate  # Probability of making a random exploratory move
        self.q_values = {}  # Dictionary to store state-action values
        self.last_state = None
        self.last_action = None
        
        # Try to load existing Q-values if available
        self.load_q_values()
    
    def get_q_value(self, state, action):
        # Get the Q-value for a state-action pair, default to 0.0 if not found
        if (state, action) not in self.q_values:
            self.q_values[(state, action)] = 0.0
        return self.q_values[(state, action)]
    
    def choose_action(self, state, available_actions):
        # Choose an action based on the current state
        if random.random() < self.exploration_rate:
            # Exploration: choose a random action
            return random.choice(available_actions)
        else:
            # Exploitation: choose the best action based on Q-values
            q_values = [self.get_q_value(state, action) for action in available_actions]
            max_q = max(q_values)
            # If multiple actions have the same max Q-value, choose randomly among them
            best_actions = [action for i, action in enumerate(available_actions) if q_values[i] == max_q]
            return random.choice(best_actions)
    
    def learn(self, state, action, reward, next_state, next_available_actions):
        # Q-learning update rule
        # If game is over (no next actions), only consider immediate reward
        if not next_available_actions:
            max_next_q = 0
        else:
            # Otherwise, consider the maximum future value
            max_next_q = max([self.get_q_value(next_state, next_action) 
                             for next_action in next_available_actions], default=0)
        
        # Update Q-value for the current state-action pair
        current_q = self.get_q_value(state, action)
        self.q_values[(state, action)] = current_q + self.learning_rate * (reward + max_next_q - current_q)
    
    def make_move(self, board, player):
        # Convert board to tuple for state representation
        state = tuple(board)
        
        # Get available actions (empty cells)
        available_actions = [i for i in range(9) if board[i] == ' ']
        
        if not available_actions:
            return None
        
        # Choose an action
        action = self.choose_action(state, available_actions)
        
        # Store state and action for learning
        self.last_state = state
        self.last_action = action
        
        return action
    
    def reward(self, value, board, available_actions):
        # Provide reward to the AI and allow it to learn
        if self.last_state is not None and self.last_action is not None:
            self.learn(self.last_state, self.last_action, value, tuple(board), available_actions)
    
    def save_q_values(self):
        # Save Q-values to a file
        with open('tictactoe_q_values.pkl', 'wb') as f:
            pickle.dump(self.q_values, f)
    
    def load_q_values(self):
        # Load Q-values from a file if it exists
        if os.path.isfile('tictactoe_q_values.pkl'):
            try:
                with open('tictactoe_q_values.pkl', 'rb') as f:
                    self.q_values = pickle.load(f)
            except:
                # If there's an error loading, start with empty Q-values
                self.q_values = {}