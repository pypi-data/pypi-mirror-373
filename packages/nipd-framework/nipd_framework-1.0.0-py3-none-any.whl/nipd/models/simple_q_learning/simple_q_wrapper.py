import numpy as np
from typing import Tuple, Optional
# Flexible import system - works both when run directly and when imported
try:
    # When imported from package
    from .simple_q_agent import SimpleQLearningAgent
except ImportError:
    # When run directly
    from simple_q_agent import SimpleQLearningAgent

class SimpleQLearningWrapper:
    """Wrapper for Simple Q-Learning agents to ensure compatibility with agent simulator"""
    
    def __init__(self, q_agent: SimpleQLearningAgent, agent_id: int):
        self.q_agent = q_agent
        self.agent_id = agent_id
        self.history = []
    
    def get_action(self, obs: np.ndarray) -> int:
        """Get action from observation - compatible with agent simulator interface"""
        try:
            # Agent simulator provides 4-dimensional observations directly
            # Simple Q-Learning uses: [own_prev, neighbor_prev, neighbor_coop_rate, neighbors_norm]
            q_obs = obs
            
            # Get action from Simple Q-Learning (returns action, log_prob, new_hidden)
            action, _, _ = self.q_agent.get_action(q_obs, deterministic=True)
            
        except Exception as e:
            raise RuntimeError(f"Failed to get action from Simple Q-Learning agent {self.agent_id}: {e}")
        
        self.history.append(action)
        return action
    
    def reset(self):
        """Reset agent state for new episode"""
        self.history = []
        self.q_agent.reset()
    
    def set_eval_mode(self):
        """Set agent to evaluation mode"""
        self.q_agent.set_eval_mode()
    
    def set_train_mode(self):
        """Set agent to training mode"""
        self.q_agent.set_train_mode()
    
    def save(self, filepath: str):
        """Save the Simple Q-Learning agent"""
        self.q_agent.save(filepath)
    
    def load(self, filepath: str):
        """Load the Simple Q-Learning agent"""
        self.q_agent.load(filepath)
    
    def get_cooperation_rate(self) -> float:
        """Get cooperation rate from the agent"""
        return self.q_agent.get_cooperation_rate()
    
    def get_decision_matrix(self) -> dict:
        """Get decision matrix from the agent"""
        return self.q_agent.get_decision_matrix()



