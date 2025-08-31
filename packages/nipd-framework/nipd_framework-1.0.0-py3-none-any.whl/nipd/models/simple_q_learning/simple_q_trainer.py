#!/usr/bin/env python3
"""
Simple Q-Learning Trainer

Trains simple Q-learning agents for the NIPD environment.
"""

import os
import sys
import numpy as np
import torch
import logging
import json
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
from collections import defaultdict
from tqdm import tqdm

# Flexible import system - works both when run directly and when imported
try:
    # When imported from comparison script
    from .simple_q_agent import SimpleQLearningAgent
    from .simple_q_wrapper import SimpleQLearningWrapper
except ImportError:
    # When run directly from the folder
    from simple_q_agent import SimpleQLearningAgent
    from simple_q_wrapper import SimpleQLearningWrapper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleQLearningTrainer:
    """Trainer for Simple Q-Learning agents"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.num_agents = config.get('num_agents', 10)
        self.episode_length = config.get('episode_length', 100)
        self.num_episodes = config.get('num_episodes', 1000)
        self.save_dir = config.get('save_dir', 'simple_q_models')
        
        # Create agents
        self.agents = []
        for i in range(self.num_agents):
            agent = SimpleQLearningAgent(
                agent_id=i,
                input_dim=4,  # Standard 4-dimensional observations
                learning_rate=config.get('learning_rate', 0.1),
                discount_factor=config.get('gamma', 0.99),
                epsilon=config.get('epsilon', 0.1)
            )
            self.agents.append(agent)
        
        # Training metrics
        self.episode_rewards = []
        self.episode_cooperation_rates = []
        
        # Detailed training metrics for comprehensive logging
        self.detailed_metrics = {
            'q_table_updates': [],
            'epsilon_values': [],
            'learning_rates': [],
            'cooperation_rates': [],
            'rewards': [],
            'episode_numbers': [],
            'agent_ids': [],
            'exploration_rates': [],
            'q_table_entropy': []
        }
        
        # Create save directory
        os.makedirs(self.save_dir, exist_ok=True)
        
        logger.info(f"Simple Q-Learning Trainer initialized with {self.num_agents} agents")
        logger.info(f"Training episodes: {self.num_episodes}, Episode length: {self.episode_length}")
        logger.info(f"Learning rate: {config.get('learning_rate', 0.1)}, Gamma: {config.get('gamma', 0.99)}")
    
    def _create_observation(self, agent_id: int, step: int, episode_actions: np.ndarray) -> np.ndarray:
        """Create observation for an agent"""
        if step == 0:
            # First step: no history
            return np.array([0.0, 0.0, 0.5, 0.5])  # Default values
        
        # Previous actions
        own_prev = episode_actions[step-1, agent_id]
        neighbor_prev = np.mean([episode_actions[step-1, j] for j in range(self.num_agents) if j != agent_id])
        
        # Cooperation rate (last 10 steps)
        recent_steps = max(0, step-10)
        if recent_steps < step:
            recent_actions = episode_actions[recent_steps:step, :]
            neighbor_coop_rate = 1.0 - np.mean(recent_actions)
        else:
            neighbor_coop_rate = 0.5
        
        # Normalized number of neighbors (assuming small world network)
        neighbors_norm = 0.5  # Default value
        
        return np.array([own_prev, neighbor_prev, neighbor_coop_rate, neighbors_norm])
    
    def _calculate_rewards(self, actions: np.ndarray) -> np.ndarray:
        """Calculate rewards for all agents"""
        rewards = np.zeros(self.num_agents)
        
        for i in range(self.num_agents):
            # Calculate average action of neighbors (all other agents)
            neighbor_actions = np.mean([actions[j] for j in range(self.num_agents) if j != i])
            
            # Prisoner's Dilemma reward matrix
            if actions[i] == 0:  # Cooperate
                if neighbor_actions < 0.5:  # Most neighbors cooperate
                    rewards[i] = 3.0
                else:  # Most neighbors defect
                    rewards[i] = 0.0
            else:  # Defect
                if neighbor_actions < 0.5:  # Most neighbors cooperate
                    rewards[i] = 5.0
                else:  # Most neighbors defect
                    rewards[i] = 1.0
        
        return rewards
    
    def train_episode(self) -> Dict[str, float]:
        """Train for one episode"""
        episode_actions = np.zeros((self.episode_length, self.num_agents), dtype=np.int64)
        episode_rewards = np.zeros((self.episode_length, self.num_agents))
        
        total_cooperation = 0
        total_actions = 0
        
        for step in range(self.episode_length):
            # Get actions from all agents
            actions = np.zeros(self.num_agents, dtype=np.int64)
            
            for agent_id in range(self.num_agents):
                obs = self._create_observation(agent_id, step, episode_actions)
                action, _, _ = self.agents[agent_id].get_action(obs)
                actions[agent_id] = action
            
            # Calculate rewards
            rewards = self._calculate_rewards(actions)
            
            # Store actions and rewards
            episode_actions[step] = actions
            episode_rewards[step] = rewards
            
            # Update agents
            for agent_id in range(self.num_agents):
                obs = self._create_observation(agent_id, step, episode_actions)
                next_obs = self._create_observation(agent_id, step + 1, episode_actions) if step < self.episode_length - 1 else obs
                
                self.agents[agent_id].update(rewards[agent_id], next_obs)
            
            # Count cooperations
            total_cooperation += np.sum(actions == 0)
            total_actions += self.num_agents
        
        # Calculate episode metrics
        episode_reward = np.mean(episode_rewards)
        cooperation_rate = total_cooperation / total_actions
        
        return {
            'episode_reward': episode_reward,
            'episode_cooperation_rate': cooperation_rate
        }
    
    def train(self) -> Dict[str, List[float]]:
        """Train all agents"""
        logger.info(f"Starting Simple Q-Learning training for {self.num_episodes} episodes...")
        
        # Progress bar
        with tqdm(total=self.num_episodes, desc="Simple Q-Learning Training Progress") as pbar:
            for episode in range(self.num_episodes):
                metrics = self.train_episode()
                
                self.episode_rewards.append(metrics['episode_reward'])
                self.episode_cooperation_rates.append(metrics['episode_cooperation_rate'])
                
                # Store detailed metrics
                self.detailed_metrics['rewards'].append(metrics['episode_reward'])
                self.detailed_metrics['cooperation_rates'].append(metrics['episode_cooperation_rate'])
                self.detailed_metrics['episode_numbers'].append(episode)
                
                # Log epsilon values and learning rates
                for agent in self.agents:
                    self.detailed_metrics['epsilon_values'].append(agent.epsilon)
                    self.detailed_metrics['learning_rates'].append(agent.learning_rate)
                    self.detailed_metrics['agent_ids'].append(agent.agent_id)
                
                # Update progress bar
                pbar.set_postfix({
                    'Episode': f'{episode+1}/{self.num_episodes}',
                    'Reward': f'{metrics["episode_reward"]:.3f}',
                    'Cooperation': f'{metrics["episode_cooperation_rate"]:.3f}'
                })
                pbar.update(1)
                
                if episode % 100 == 0:
                    logger.info(f"Episode {episode}: Reward={metrics['episode_reward']:.3f}, "
                              f"Cooperation={metrics['episode_cooperation_rate']:.3f}")
        
        # Save final models and metrics
        self.save_models()
        self.save_training_metrics()
        self.plot_training_curves()
        
        logger.info("Simple Q-Learning training completed!")
        
        return {
            'episode_rewards': self.episode_rewards,
            'episode_cooperation_rates': self.episode_cooperation_rates
        }
    
    def save_models(self):
        """Save all agent models"""
        for i, agent in enumerate(self.agents):
            model_path = os.path.join(self.save_dir, f'simple_q_agent_{i}_final.json')
            agent.save(model_path)
        
        logger.info(f"Simple Q-Learning models saved to {self.save_dir}")
    
    def save_training_metrics(self):
        """Save training metrics to files"""
        metrics_dir = os.path.join(self.save_dir, 'training_metrics')
        os.makedirs(metrics_dir, exist_ok=True)
        
        # Save detailed metrics as numpy arrays
        np.savez(
            os.path.join(metrics_dir, 'simple_q_detailed_metrics.npz'),
            episode_rewards=np.array(self.episode_rewards),
            episode_cooperation_rates=np.array(self.episode_cooperation_rates),
            epsilon_values=np.array(self.detailed_metrics['epsilon_values']),
            learning_rates=np.array(self.detailed_metrics['learning_rates']),
            agent_ids=np.array(self.detailed_metrics['agent_ids'])
        )
        
        # Save as JSON for easy reading
        metrics_dict = {
            'episode_rewards': self.episode_rewards,
            'episode_cooperation_rates': self.episode_cooperation_rates,
            'epsilon_values': self.detailed_metrics['epsilon_values'],
            'learning_rates': self.detailed_metrics['learning_rates'],
            'agent_ids': self.detailed_metrics['agent_ids']
        }
        
        with open(os.path.join(metrics_dir, 'simple_q_detailed_metrics.json'), 'w') as f:
            json.dump(metrics_dict, f, indent=2)
        
        logger.info(f"Training metrics saved to {metrics_dir}")
    
    def plot_training_curves(self, save_path: Optional[str] = None):
        """Plot comprehensive training curves with detailed metrics"""
        # Create a comprehensive visualization with multiple subplots
        fig = plt.figure(figsize=(20, 10))
        
        # Training progress metrics
        ax1 = plt.subplot(2, 3, 1)
        if self.episode_rewards:
            ax1.plot(self.episode_rewards)
            ax1.set_title('Episode Rewards')
            ax1.set_xlabel('Training Episode')
            ax1.set_ylabel('Reward')
            ax1.grid(True, alpha=0.3)
        
        ax2 = plt.subplot(2, 3, 2)
        if self.episode_cooperation_rates:
            ax2.plot(self.episode_cooperation_rates)
            ax2.set_title('Cooperation Rates')
            ax2.set_xlabel('Training Episode')
            ax2.set_ylabel('Cooperation Rate')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
        
        # Learning dynamics
        ax3 = plt.subplot(2, 3, 3)
        if self.detailed_metrics['epsilon_values']:
            # Plot epsilon values for first agent only to avoid clutter
            first_agent_epsilons = [self.detailed_metrics['epsilon_values'][i] 
                                   for i in range(0, len(self.detailed_metrics['epsilon_values']), self.num_agents)]
            ax3.plot(first_agent_epsilons)
            ax3.set_title('Epsilon Values (First Agent)')
            ax3.set_xlabel('Training Episode')
            ax3.set_ylabel('Epsilon')
            ax3.grid(True, alpha=0.3)
        
        # Learning rates
        ax4 = plt.subplot(2, 3, 4)
        if self.detailed_metrics['learning_rates']:
            # Plot learning rates for first agent only
            first_agent_lrs = [self.detailed_metrics['learning_rates'][i] 
                              for i in range(0, len(self.detailed_metrics['learning_rates']), self.num_agents)]
            ax4.plot(first_agent_lrs)
            ax4.set_title('Learning Rates (First Agent)')
            ax4.set_xlabel('Training Episode')
            ax4.set_ylabel('Learning Rate')
            ax4.grid(True, alpha=0.3)
        
        # Cooperation rate distribution
        ax5 = plt.subplot(2, 3, 5)
        if self.episode_cooperation_rates:
            ax5.hist(self.episode_cooperation_rates, bins=20, alpha=0.7)
            ax5.set_title('Cooperation Rate Distribution')
            ax5.set_xlabel('Cooperation Rate')
            ax5.set_ylabel('Frequency')
            ax5.grid(True, alpha=0.3)
        
        # Reward distribution
        ax6 = plt.subplot(2, 3, 6)
        if self.episode_rewards:
            ax6.hist(self.episode_rewards, bins=20, alpha=0.7)
            ax6.set_title('Reward Distribution')
            ax6.set_xlabel('Reward')
            ax6.set_ylabel('Frequency')
            ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training curves saved to {save_path}")
        else:
            plot_path = os.path.join(self.save_dir, 'simple_q_training_curves.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training curves saved to {plot_path}")
        
        plt.close()
    
    def evaluate(self, num_episodes: int = 10) -> Dict[str, float]:
        """Evaluate the trained agents"""
        logger.info(f"Evaluating Simple Q-Learning agents for {num_episodes} episodes...")
        
        eval_rewards = []
        eval_cooperation_rates = []
        
        for episode in range(num_episodes):
            metrics = self.train_episode()
            eval_rewards.append(metrics['episode_reward'])
            eval_cooperation_rates.append(metrics['episode_cooperation_rate'])
        
        avg_reward = np.mean(eval_rewards)
        avg_cooperation = np.mean(eval_cooperation_rates)
        
        logger.info(f"Evaluation results: Avg Reward={avg_reward:.3f}, Avg Cooperation={avg_cooperation:.3f}")
        
        return {
            'avg_reward': avg_reward,
            'avg_cooperation_rate': avg_cooperation
        }

def create_simple_q_config() -> Dict:
    """Create configuration for Simple Q-Learning training"""
    return {
        'num_agents': 10,
        'episode_length': 100,
        'num_episodes': 20,  # 2000 total timesteps (20 episodes × 100 steps)
        'learning_rate': 0.1,
        'epsilon': 0.1,
        'gamma': 0.99,
        'save_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simple_q_models')
    }

if __name__ == "__main__":
    # Set random seeds
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Create configuration
    config = create_simple_q_config()
    
    # Initialize trainer
    trainer = SimpleQLearningTrainer(config)
    
    # Train agents
    training_results = trainer.train()
    
    # Evaluate trained agents
    evaluation_results = trainer.evaluate()
    
    logger.info("Simple Q-Learning training and evaluation completed!")
