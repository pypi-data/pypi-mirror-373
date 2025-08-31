import numpy as np
from typing import Tuple, Optional
from unified_agent_interface import BaseAgent
from decentralized_ppo_agent import DecentralizedPPOAgent

class DecentralizedPPOWrapper(BaseAgent):
    """
    Wrapper for Decentralized PPO Agent to integrate with unified interface
    """
    def __init__(self, agent_id: int, agent: DecentralizedPPOAgent):
        super().__init__(agent_id, "decentralized_ppo")
        self.agent = agent
    
    def get_action(self, observation: np.ndarray, deterministic: bool = False) -> Tuple[int, Optional[float]]:
        """Get action from the decentralized PPO agent"""
        return self.agent.get_action(observation, deterministic)
    
    def reset(self):
        """Reset the agent for new episodes"""
        self.agent.reset()
    
    def set_eval_mode(self):
        """Set agent to evaluation mode"""
        self.agent.set_eval_mode()
    
    def set_train_mode(self):
        """Set agent to training mode"""
        self.agent.set_train_mode()
    
    def save(self, filepath: str):
        """Save the agent model"""
        self.agent.save(filepath)
    
    def load(self, filepath: str):
        """Load the agent model"""
        self.agent.load(filepath)
    
    def get_cooperation_rate(self) -> float:
        """Get cooperation rate from the agent"""
        return self.agent.get_cooperation_rate()

