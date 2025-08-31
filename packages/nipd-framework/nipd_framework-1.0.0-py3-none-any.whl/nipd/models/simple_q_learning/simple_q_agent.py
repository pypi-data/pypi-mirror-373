import numpy as np
import random
from typing import Dict, List, Tuple, Optional
import json
import os

class SimpleQLearningAgent:
    """
    Simple Q-Learning agent using Q-table instead of neural networks
    """
    
    def __init__(self, agent_id: int, input_dim: int = 4, learning_rate: float = 0.1, 
                 discount_factor: float = 0.95, epsilon: float = 0.1):
        self.agent_id = agent_id
        self.input_dim = input_dim
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-table: state -> action -> Q-value
        # State is discretized observation, action is 0 (cooperate) or 1 (defect)
        self.q_table = {}
        
        # Experience history
        self.history = []
        self.last_state = None
        self.last_action = None
        
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
        """
        # obs format: [own_prev, neighbor_prev, neighbor_coop_rate, neighbors_norm]
        
        # Discretize own previous action
        own_prev = 'C' if obs[0] < 0.5 else 'D'
        
        # Discretize neighbor previous action
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
        
        # Create state string
        state = f"{own_prev}_{neighbor_prev}_{coop_level}_{neighbor_level}"
        return state
    
    def get_action(self, obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float, None]:
        """
        Get action from observation using epsilon-greedy policy
        
        Returns:
            Tuple of (action, log_prob, new_hidden) - last two are None
        """
        state = self._discretize_state(obs)
        
        # Initialize Q-values for this state if not exists
        if state not in self.q_table:
            self.q_table[state] = {'0': 0.0, '1': 0.0}  # 0=cooperate, 1=defect
        
        # Epsilon-greedy action selection
        if not deterministic and random.random() < self.epsilon:
            action = random.choice([0, 1])
        else:
            # Choose action with highest Q-value
            q_values = self.q_table[state]
            if q_values['0'] > q_values['1']:
                action = 0
            elif q_values['1'] > q_values['0']:
                action = 1
            else:
                # If equal, prefer cooperation
                action = 0
        
        # Store for learning
        self.last_state = state
        self.last_action = action
        
        # Update statistics
        if action == 0:
            self.cooperation_count += 1
        self.total_actions += 1
        
        # Update decision matrix (simplified - just track own action)
        if obs[0] < 0.5:  # I cooperated last time
            if action == 0:
                self.decision_matrix['cooperate']['cooperate'] += 1
            else:
                self.decision_matrix['cooperate']['defect'] += 1
        else:  # I defected last time
            if action == 0:
                self.decision_matrix['defect']['cooperate'] += 1
            else:
                self.decision_matrix['defect']['defect'] += 1
        
        # Return action, None, None
        return action, None, None
    
    def update(self, reward: float, next_obs: np.ndarray):
        """
        Update Q-values using Q-learning update rule
        """
        if self.last_state is None or self.last_action is None:
            return
        
        next_state = self._discretize_state(next_obs)
        
        # Initialize Q-values for next state if not exists
        if next_state not in self.q_table:
            self.q_table[next_state] = {'0': 0.0, '1': 0.0}
        
        # Q-learning update rule
        current_q = self.q_table[self.last_state][str(self.last_action)]
        max_next_q = max(self.q_table[next_state].values())
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[self.last_state][str(self.last_action)] = new_q
    
    def get_cooperation_rate(self) -> float:
        """Get cooperation rate from history"""
        if self.total_actions == 0:
            return 0.0
        return self.cooperation_count / self.total_actions
    
    def get_decision_matrix(self) -> Dict:
        """Get decision matrix for this agent"""
        return self.decision_matrix.copy()
    
    def save(self, filepath: str):
        """Save Q-table and agent parameters"""
        data = {
            'agent_id': self.agent_id,
            'input_dim': self.input_dim,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'q_table': self.q_table,
            'decision_matrix': self.decision_matrix
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Load Q-table and agent parameters"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.agent_id = data['agent_id']
        self.input_dim = data['input_dim']
        self.learning_rate = data['learning_rate']
        self.discount_factor = data['discount_factor']
        self.epsilon = data['epsilon']
        self.q_table = data['q_table']
        self.decision_matrix = data['decision_matrix']
    
    def set_eval_mode(self):
        """Set agent to evaluation mode (no exploration)"""
        self.epsilon = 0.0
    
    def set_train_mode(self):
        """Set agent to training mode (with exploration)"""
        self.epsilon = 0.1
    
    def reset(self):
        """Reset agent state for new episode"""
        self.history = []
        self.last_state = None
        self.last_action = None



