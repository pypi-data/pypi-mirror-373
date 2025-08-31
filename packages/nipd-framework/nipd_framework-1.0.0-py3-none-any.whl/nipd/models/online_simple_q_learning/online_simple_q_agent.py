import numpy as np
import random
from typing import Dict, List, Tuple, Optional
import json
import os
from collections import deque

class OnlineSimpleQLearningAgent:
    """
    Online Simple Q-Learning agent that adapts behavior based on opponent observations
    Implements pure Q-learning with online updates
    """
    
    def __init__(self, agent_id: int, input_dim: int = 4, learning_rate: float = 0.5,
                 discount_factor: float = 0.95, epsilon: float = 0.3,
                 opponent_memory_length: int = 10):
        self.agent_id = agent_id
        self.input_dim = input_dim
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.opponent_memory_length = opponent_memory_length
        
        # Q-table: state -> action -> Q-value
        self.q_table = {}
        
        # Online learning components
        self.opponent_history = deque(maxlen=opponent_memory_length)
        self.own_history = deque(maxlen=opponent_memory_length)
        self.reward_history = deque(maxlen=opponent_memory_length)
        
        # Opponent modeling
        self.opponent_defection_rate = 0.0
        self.opponent_cooperation_rate = 0.0
        self.recent_opponent_actions = deque(maxlen=5)
        
        # Online learning parameters
        self.epsilon_decay = 0.999  # Faster decay for quicker convergence
        self.min_epsilon = 0.05     # Higher minimum epsilon for continued exploration
        
        # Experience history for online updates
        self.last_state = None
        self.last_action = None
        self.last_reward = None
        
        # Statistics
        self.cooperation_count = 0
        self.total_actions = 0
        
        # Decision matrix tracking
        self.decision_matrix = {
            'cooperate': {'cooperate': 0, 'defect': 0},
            'defect': {'cooperate': 0, 'defect': 0}
        }
    
    def _discretize_state(self, obs: np.ndarray) -> str:
        """
        Discretize continuous observation into discrete state string
        Enhanced to include opponent behavior patterns
        """
        # Standard obs format: [own_prev, neighbor_prev, neighbor_coop_rate, neighbors_norm]
        
        # Discretize own previous action
        own_prev = 'C' if obs[0] < 0.5 else 'D'
        
        # Discretize neighbor previous action (historical opponent info)
        neighbor_prev = 'C' if obs[1] < 0.5 else 'D'
        
        # Discretize cooperation rate into 3 levels
        if obs[2] < 0.33:
            coop_level = 'L'  # Low cooperation
        elif obs[2] < 0.67:
            coop_level = 'M'  # Medium cooperation
        else:
            coop_level = 'H'  # High cooperation
        
        # Discretize number of neighbors into 3 levels
        if obs[3] < 0.33:
            neighbor_level = 'L'  # Few neighbors
        elif obs[3] < 0.67:
            neighbor_level = 'M'  # Medium neighbors
        else:
            neighbor_level = 'H'  # Many neighbors
        
        # Create state string for Q-learning
        state = f"{own_prev}_{neighbor_prev}_{coop_level}_{neighbor_level}"
        return state
    
    def _update_opponent_model(self, opponent_action: int, reward: float):
        """
        Update opponent behavior model for statistics only
        """
        # Update histories for statistics
        self.opponent_history.append(opponent_action)
        self.reward_history.append(reward)
        
        # Update recent opponent actions
        self.recent_opponent_actions.append(opponent_action)
        
        # Calculate opponent defection rate for statistics
        if len(self.opponent_history) > 0:
            self.opponent_defection_rate = sum(1 for action in self.opponent_history if action == 1) / len(self.opponent_history)
            self.opponent_cooperation_rate = 1.0 - self.opponent_defection_rate
    
    def _get_q_action(self, state: str, deterministic: bool = False) -> int:
        """
        Get action using pure Q-learning with epsilon-greedy exploration
        """
        # Initialize Q-values for this state if not seen before
        if state not in self.q_table:
            self.q_table[state] = {'0': 0.0, '1': 0.0}
        
        # Epsilon-greedy action selection
        if deterministic or random.random() > self.epsilon:
            # Choose best action based on Q-values
            q_values = self.q_table[state]
            if q_values['0'] > q_values['1']:
                action = 0  # Cooperate
            elif q_values['1'] > q_values['0']:
                action = 1  # Defect
            else:
                # Tie - choose randomly
                action = random.choice([0, 1])
        else:
            # Random exploration
            action = random.choice([0, 1])
        
        return action
    
    def get_action(self, obs: np.ndarray, deterministic: bool = False) -> int:
        """
        Get action based on current observation
        """
        # Discretize observation into state
        state = self._discretize_state(obs)
        
        # Get action using Q-learning
        action = self._get_q_action(state, deterministic)
        
        # Update tracking variables
        self.last_state = state
        self.last_action = action
        
        # Update statistics
        if action == 0:
            self.cooperation_count += 1
        self.total_actions += 1
        
        # Update decision matrix
        own_prev = 'cooperate' if obs[0] < 0.5 else 'defect'
        neighbor_prev = 'cooperate' if obs[1] < 0.5 else 'defect'
        action_str = 'cooperate' if action == 0 else 'defect'
        
        self.decision_matrix[own_prev][neighbor_prev] += 1
        
        return action
    
    def update(self, obs: np.ndarray, action: int, reward: float, next_obs: np.ndarray, done: bool):
        """
        Online update of Q-values based on immediate experience
        """
        if self.last_state is None:
            return
        
        current_state = self.last_state
        next_state = self._discretize_state(next_obs)
        
        # Initialize Q-values if needed
        if current_state not in self.q_table:
            self.q_table[current_state] = {'0': 0.0, '1': 0.0}
        if next_state not in self.q_table:
            self.q_table[next_state] = {'0': 0.0, '1': 0.0}
        
        # Q-learning update
        current_q = self.q_table[current_state][str(action)]
        next_max_q = max(self.q_table[next_state].values())
        
        # Calculate target Q-value
        if done:
            target_q = reward
        else:
            target_q = reward + self.discount_factor * next_max_q
        
        # Update Q-value
        self.q_table[current_state][str(action)] = current_q + self.learning_rate * (target_q - current_q)
        
        # Decay epsilon for exploration
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        # Update opponent model using neighbor_prev from observation
        # Standard obs format: [own_prev, neighbor_prev, neighbor_coop_rate, neighbors_norm]
        if len(obs) > 1:
            opponent_action = int(obs[1] > 0.5)  # neighbor_prev contains historical opponent action
            self._update_opponent_model(opponent_action, reward)
        
        # Update own history
        self.own_history.append(action)
        self.last_reward = reward
    
    def get_cooperation_rate(self) -> float:
        """Get current cooperation rate"""
        if self.total_actions == 0:
            return 0.0
        return self.cooperation_count / self.total_actions
    
    def get_opponent_defection_rate(self) -> float:
        """Get opponent's defection rate"""
        return self.opponent_defection_rate
    
    def get_strategy_mode(self) -> str:
        """Get current learning mode"""
        return "q_learning"
    
    def save_model(self, filepath: str):
        """Save the agent's Q-table and parameters"""
        model_data = {
            'q_table': self.q_table,
            'agent_id': self.agent_id,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'opponent_memory_length': self.opponent_memory_length,
            'epsilon': self.epsilon,
            'opponent_defection_rate': self.opponent_defection_rate,
            'cooperation_count': self.cooperation_count,
            'total_actions': self.total_actions
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def load_model(self, filepath: str):
        """Load the agent's Q-table and parameters"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            model_data = json.load(f)
        
        self.q_table = model_data['q_table']
        self.agent_id = model_data['agent_id']
        self.learning_rate = model_data.get('learning_rate', 0.5)
        self.discount_factor = model_data.get('discount_factor', 0.95)
        self.epsilon = model_data.get('epsilon', 0.3)
        
        # Handle missing fields that might not exist in older model files
        self.opponent_memory_length = model_data.get('opponent_memory_length', 10)
        self.opponent_defection_rate = model_data.get('opponent_defection_rate', 0.0)
        self.cooperation_count = model_data.get('cooperation_count', 0)
        self.total_actions = model_data.get('total_actions', 0)
    
    def reset(self):
        """Reset agent state for new episode"""
        self.last_state = None
        self.last_action = None
        self.last_reward = None
        # Keep Q-table intact for online learning


# Q-table creation functions for different learning starting points
def create_zero_q_table():
    """Create a Q-table with exactly zero values for unbiased learning"""
    q_table = {}
    
    # Define all possible states
    own_actions = ['C', 'D']
    neighbor_actions = ['C', 'D']
    coop_levels = ['L', 'M', 'H']
    neighbor_levels = ['L', 'M', 'H']
    
    for own_prev in own_actions:
        for neighbor_prev in neighbor_actions:
            for coop_level in coop_levels:
                for neighbor_level in neighbor_levels:
                    state = f"{own_prev}_{neighbor_prev}_{coop_level}_{neighbor_level}"
                    
                    # Zero values - agent will learn purely from experience
                    q_table[state] = {'0': 0.0, '1': 0.0}
    
    return q_table

def create_small_random_q_table():
    """Create a Q-table with small random values to break symmetry"""
    q_table = {}
    
    own_actions = ['C', 'D']
    neighbor_actions = ['C', 'D']
    coop_levels = ['L', 'M', 'H']
    neighbor_levels = ['L', 'M', 'H']
    
    for own_prev in own_actions:
        for neighbor_prev in neighbor_actions:
            for coop_level in coop_levels:
                for neighbor_level in neighbor_levels:
                    state = f"{own_prev}_{neighbor_prev}_{coop_level}_{neighbor_level}"
                    
                    # Small random values to break symmetry (unbiased)
                    q_table[state] = {
                        '0': np.random.uniform(-0.05, 0.05),
                        '1': np.random.uniform(-0.05, 0.05)
                    }
    
    return q_table

def save_q_table(q_table, filepath, agent_id, strategy_name):
    """Save Q-table to JSON file"""
    model_data = {
        'q_table': q_table,
        'agent_id': agent_id,
        'learning_rate': 0.5,
        'discount_factor': 0.95,
        'epsilon': 0.3,
        'opponent_memory_length': 10,
        'epsilon_decay': 0.999,
        'min_epsilon': 0.05,
        'opponent_defection_rate': 0.0,
        'cooperation_count': 0,
        'total_actions': 0,
        'strategy_name': strategy_name
    }
    
    with open(filepath, 'w') as f:
        json.dump(model_data, f, indent=2)

def create_learning_q_tables():
    """Create Q-tables that allow true learning during simulation"""
    os.makedirs("models/simple_q_learning/simple_q_models", exist_ok=True)
    
    # Create unbiased starting points for learning
    strategies = [
        ("zero_learner", create_zero_q_table()),
        ("small_random_learner", create_small_random_q_table())
    ]
    
    # Create 10 agents with unbiased starting points
    for i in range(10):
        strategy_name, q_table = strategies[i % len(strategies)]
        filepath = f"models/simple_q_learning/simple_q_models/simple_q_agent_{i}.json"
        save_q_table(q_table, filepath, i, strategy_name)


if __name__ == "__main__":
    create_learning_q_tables()
