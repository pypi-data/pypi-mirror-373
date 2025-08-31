import numpy as np
import torch
import logging
import time
import os
import sys
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from collections import defaultdict
from tqdm import tqdm

# Flexible import system - works both when run directly and when imported
try:
    # When imported from comparison script
    from .q_network_agent import QNetworkAgent
    from ...network_environment import initialise_network
except ImportError:
    # When run directly from the folder
    from q_network_agent import QNetworkAgent
    # Add parent directory to path for network_environment
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from network_environment import initialise_network

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QNetworkTrainer:
    """
    Trainer for Q-Network agents that learn decision matrices
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Environment parameters
        self.num_players = config['num_players']
        self.env_type = config['env_type']
        self.k_neighbours = config['k_neighbours']
        self.rewire_prob = config.get('rewire_prob', 0.1)
        self.reward_matrix = np.array(config['reward_matrix'])
        
        # Training parameters
        self.num_q_agents = config['num_q_agents']
        self.total_timesteps = config['total_timesteps']
        self.episode_length = config['episode_length']
        self.update_frequency = config.get('update_frequency', 4)
        self.target_update_frequency = config.get('target_update_frequency', 1000)
        
        # Learning rate annealing parameters
        self.lr_start = config.get('lr', 1e-3)
        self.lr_decay_rate = config.get('lr_decay_rate', 0.9999)
        
        # Q-learning parameters
        self.epsilon_start = config.get('epsilon_start', 1.0)
        self.epsilon_end = config.get('epsilon_end', 0.01)
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        
        # Initialize environment
        self._setup_environment()
        
        # Initialize Q-Network agents
        self.agents = self._initialize_agents()
        
        # Training metrics - Enhanced logging
        self.training_metrics = defaultdict(list)
        self.cooperation_history = []
        
        # Detailed training metrics for comprehensive logging
        self.detailed_metrics = {
            'q_losses': [],
            'entropy_values': [],
            'learning_rates': [],
            'gradient_norms': [],
            'epsilon_values': [],
            'cooperation_rates': [],
            'rewards': [],
            'episode_numbers': [],
            'agent_ids': [],
            'target_update_counts': [],
            'exploration_rates': []
        }
        
        # Create save directory
        self.save_dir = config.get('save_dir', 'q_network_models')
        os.makedirs(self.save_dir, exist_ok=True)
        
        logging.info("Q-Network Trainer initialized successfully")
        logging.info(f"Environment: {self.num_players} players, {self.num_q_agents} Q-Network agents")
        logging.info(f"Total timesteps: {self.total_timesteps}, Episode length: {self.episode_length}")
        
        # Log initial hyperparameters
        logging.info(f"Learning rate: {self.lr_start:.2e}")
        logging.info(f"Q-learning parameters - Gamma: {self.config.get('gamma', 0.99)}, Epsilon start: {self.epsilon_start}")
        logging.info(f"Training parameters - Update freq: {self.update_frequency}, Target update freq: {self.target_update_frequency}")
        
    def _anneal_learning_rates(self, timestep: int):
        """Anneal learning rates over time"""
        for agent in self.agents:
            if hasattr(agent, 'optimizer'):
                new_lr = self.lr_start * (self.lr_decay_rate ** (timestep / 1000))
                for param_group in agent.optimizer.param_groups:
                    param_group['lr'] = new_lr
    
    def _setup_environment(self):
        """Setup the training environment"""
        # Create player assignments (all Q-Network agents for training)
        player_types = ['q_network'] * self.num_players
        player_assignments = {i: player_types[i] for i in range(self.num_players)}
        
        # Initialize network
        network, _ = initialise_network(
            self.env_type, 
            self.num_players, 
            player_types, 
            self.k_neighbours, 
            self.rewire_prob
        )
        
        self.network = network
        logging.info(f"Training environment setup complete")
        logging.info(f"Network type: {self.env_type}, Rewire prob: {self.rewire_prob}")
    
    def _initialize_agents(self) -> List[QNetworkAgent]:
        """Initialize Q-Network agents"""
        agents = []
        
        for i in range(self.num_q_agents):
            agent = QNetworkAgent(
                agent_id=i,
                input_dim=4,  # [own_prev, neighbor_prev, step_norm, neighbors_norm]
                hidden_dim=64,
                lr=self.config.get('lr', 1e-3),
                gamma=self.config.get('gamma', 0.99),
                epsilon=self.epsilon_start
            )
            agents.append(agent)
        
        logging.info(f"Initialized {len(agents)} Q-Network agents")
        return agents
    
    def _log_detailed_metrics(self, timestep: int, episode: int, metrics: Dict, agent_id: Optional[int] = None):
        """Log detailed training metrics for comprehensive analysis"""
        # Extract metrics from training
        if 'q_loss' in metrics:
            self.detailed_metrics['q_losses'].append(metrics['q_loss'])
        
        # Get entropy from agents if available
        if agent_id is not None and agent_id < len(self.agents):
            agent = self.agents[agent_id]
            if hasattr(agent, 'get_policy_entropy'):
                entropy = agent.get_policy_entropy()
                self.detailed_metrics['entropy_values'].append(entropy)
        
        if 'exploration_rate' in metrics:
            self.detailed_metrics['exploration_rates'].append(metrics['exploration_rate'])
        
        # Log learning rates
        if agent_id is not None and agent_id < len(self.agents):
            agent = self.agents[agent_id]
            if hasattr(agent, 'optimizer'):
                current_lr = agent.optimizer.param_groups[0]['lr']
                self.detailed_metrics['learning_rates'].append(current_lr)
        
        # Log training progress
        self.detailed_metrics['episode_numbers'].append(episode)
        if 'avg_reward' in metrics:
            self.detailed_metrics['rewards'].append(metrics['avg_reward'])

        if 'cooperation_rate' in metrics:
            self.detailed_metrics['cooperation_rates'].append(metrics['cooperation_rate'])
        
        # Log epsilon values
        if hasattr(self, 'epsilon'):
            self.detailed_metrics['epsilon_values'].append(self.epsilon)
        else:
            # Get epsilon from the first agent
            if self.agents:
                self.detailed_metrics['epsilon_values'].append(self.agents[0].epsilon)
        
        # Log agent IDs if available
        if agent_id is not None:
            self.detailed_metrics['agent_ids'].append(agent_id)
        
        # Log target update counts
        if hasattr(self, 'target_update_count'):
            self.detailed_metrics['target_update_counts'].append(self.target_update_count)
        else:
            # Calculate target update count based on episode
            target_update_count = episode // self.target_update_frequency if episode > 0 else 0
            self.detailed_metrics['target_update_counts'].append(target_update_count)
        
        # Log gradient norms if available
        if agent_id is not None and agent_id < len(self.agents):
            agent = self.agents[agent_id]
            if hasattr(agent, 'get_gradient_norms'):
                grad_norms = agent.get_gradient_norms()
                if 'q_grad_norm' in grad_norms:
                    self.detailed_metrics['gradient_norms'].append(grad_norms['q_grad_norm'])
    
    def _create_observation(self, agent_id: int, step: int, episode_actions: np.ndarray) -> np.ndarray:
        """Create 4-dimensional observation for Q-Network agents"""
        # Get neighbors
        neighbors = np.where(self.network[agent_id] == 1)[0]
        num_neighbors = len(neighbors)
        
        # Create 4-dimensional observation
        obs = np.zeros(4, dtype=np.float32)
        
        # Feature 0: Own previous action (0 = cooperate, 1 = defect)
        obs[0] = float(episode_actions[step - 1, agent_id]) if step > 0 else 0.0
        
        # Feature 1: Average neighbor action (last round)
        if num_neighbors > 0 and step > 0:
            neighbor_actions = episode_actions[step - 1, neighbors]
            obs[1] = float(np.mean(neighbor_actions))
        else:
            obs[1] = 0.5
        
        # Feature 2: Neighbor cooperation rate
        if num_neighbors > 0 and step > 0:
            obs[2] = float(np.mean(episode_actions[step - 1, neighbors] == 0))
        else:
            obs[2] = 0.5
        
        # Feature 3: Number of neighbors (normalized)
        obs[3] = float(num_neighbors) / float(max(1, self.num_players - 1))
        
        return obs
    
    def _calculate_rewards(self, actions: np.ndarray) -> np.ndarray:
        """Calculate rewards for all agents based on Prisoner's Dilemma"""
        rewards = np.zeros(self.num_players)
        
        for i in range(self.num_players):
            neighbors = np.where(self.network[i] == 1)[0]
            
            if len(neighbors) == 0:
                rewards[i] = 0
                continue
            
            # Calculate reward based on own action and neighbor actions
            own_action = actions[i]
            neighbor_actions = actions[neighbors]
            
            total_reward = 0.0
            for neighbor_action in neighbor_actions:
                total_reward += self.reward_matrix[own_action][neighbor_action]
            
            # Sum rewards across neighbors for this timestep
            # This will be averaged later to get per-neighbor interaction reward
            rewards[i] = total_reward
        
        return rewards
    
    def _update_epsilon(self, timestep: int):
        """Update exploration epsilon"""
        for agent in self.agents:
            agent.epsilon = max(self.epsilon_end, agent.epsilon * self.epsilon_decay)
    
    def train_episode(self) -> Dict[str, float]:
        """Train for one episode"""
        episode_rewards = np.zeros(self.num_players)
        episode_actions = np.zeros((self.episode_length, self.num_players), dtype=np.int64)
        episode_observations = np.zeros((self.episode_length, self.num_players, 4))
        episode_rewards_per_step = np.zeros((self.episode_length, self.num_players))
        
        # Initialize hidden states for all agents
        hidden_states = [agent.get_initial_hidden_states() for agent in self.agents]
        
        # Reset episode
        for step in range(self.episode_length):
            actions = np.zeros(self.num_players, dtype=np.int64)
            
            # Get actions from all agents
            for agent_id in range(self.num_players):
                if agent_id < len(self.agents):
                    obs = self._create_observation(agent_id, step, episode_actions)
                    episode_observations[step, agent_id] = obs
                    
                    action, _, new_hidden = self.agents[agent_id].get_action(obs, deterministic=False, hidden_state=hidden_states[agent_id])
                    hidden_states[agent_id] = new_hidden
                    actions[agent_id] = action
                else:
                    actions[agent_id] = 0  # Default to cooperate
            
            # Store actions
            episode_actions[step] = actions
            
            # Calculate rewards
            rewards = self._calculate_rewards(actions)
            episode_rewards_per_step[step] = rewards
            episode_rewards += rewards
            
            # Store experiences for training (skip first step)
            if step > 0:
                for agent_id in range(min(self.num_q_agents, self.num_players)):
                    current_obs = episode_observations[step - 1, agent_id]
                    next_obs = episode_observations[step, agent_id]
                    action = episode_actions[step - 1, agent_id]
                    reward = episode_rewards_per_step[step - 1, agent_id]
                    done = (step == self.episode_length - 1)
                    
                    self.agents[agent_id].store_experience(
                        current_obs, action, reward, next_obs, done
                    )
        
        # Calculate episode metrics
        # episode_rewards contains total rewards per agent across all timesteps and neighbors
        # We want average reward per timestep per agent per neighbor interaction
        # First calculate total neighbor interactions across all agents
        total_neighbor_interactions = 0
        for i in range(self.num_players):
            neighbors = np.where(self.network[i] == 1)[0]
            total_neighbor_interactions += len(neighbors) * self.episode_length
        
        # Calculate average reward per neighbor interaction
        if total_neighbor_interactions > 0:
            avg_reward_per_neighbor = np.sum(episode_rewards) / total_neighbor_interactions
        else:
            avg_reward_per_neighbor = 0.0
            
        cooperation_rate = np.mean(episode_actions == 0)
        
        return {
            'episode_reward': avg_reward_per_neighbor,
            'episode_cooperation_rate': cooperation_rate,
            'episode_actions': episode_actions,
            'episode_observations': episode_observations
        }
    
    def train(self) -> Dict[str, List[float]]:
        """Main training loop"""
        logging.info("Starting Q-Network training...")
        logging.info(f"Total timesteps: {self.total_timesteps}")
        logging.info(f"Episode length: {self.episode_length}")
        
        start_time = time.time()
        timestep = 0
        episode = 0
        best_cooperation_rate = 0.0
        
        # Main training progress bar
        total_episodes = self.total_timesteps // self.episode_length
        with tqdm(total=total_episodes, desc="Q-Network Training Progress", ncols=100) as main_pbar:
            while timestep < self.total_timesteps:
                # Train one episode
                episode_metrics = self.train_episode()
                episode += 1
                timestep += self.episode_length
                
                # Train agents on stored experiences
                episode_losses = []
                for agent in self.agents:
                    # Train multiple steps per episode
                    for _ in range(self.update_frequency):
                        loss = agent.train_step()
                        if loss is not None:
                            episode_losses.append(loss)
                    
                    # Update target network periodically
                    if episode % self.target_update_frequency == 0:
                        agent.update_target_network()
                
                # Update epsilon
                self._update_epsilon(timestep)
                
                # Anneal learning rates
                self._anneal_learning_rates(timestep)
                
                # Update main progress bar
                main_pbar.set_postfix({
                    'Episode': f'{episode}/{total_episodes}',
                    'Timestep': f'{timestep}/{self.total_timesteps}',
                    'Reward': f'{episode_metrics.get("episode_reward", 0.0):.2f}',
                    'Coop': f'{episode_metrics.get("episode_cooperation_rate", 0.0):.2f}',
                    'Epsilon': f'{self.agents[0].epsilon:.3f}'
                })
                main_pbar.update(1)
                
                # Store metrics
                self.training_metrics['episode_reward'].append(episode_metrics['episode_reward'])
                self.training_metrics['episode_cooperation_rate'].append(episode_metrics['episode_cooperation_rate'])
                if episode_losses:
                    self.training_metrics['episode_loss'].append(np.mean(episode_losses))
                
                # Track cooperation history
                self.cooperation_history.append(episode_metrics['episode_cooperation_rate'])
                
                # Log detailed metrics
                episode_metrics_with_loss = episode_metrics.copy()
                episode_metrics_with_loss['episode_loss'] = np.mean(episode_losses) if episode_losses else 0.0
                episode_metrics_with_loss['episode_length'] = self.episode_length
                episode_metrics_with_loss['cooperation_rate'] = episode_metrics['episode_cooperation_rate']
                episode_metrics_with_loss['avg_reward'] = episode_metrics['episode_reward']
                
                self._log_detailed_metrics(timestep, episode, episode_metrics_with_loss)
                
                                # Periodic logging
                if episode % 5 == 0:
                    elapsed_time = time.time() - start_time
                    coop_rate = episode_metrics['episode_cooperation_rate']
                    reward = episode_metrics['episode_reward']
                    loss = np.mean(episode_losses) if episode_losses else 0.0
                    
                    logging.info(f"Episode {episode}, Timestep {timestep}/{self.total_timesteps}")
                    logging.info(f"Avg Reward: {reward:.4f}")
                    logging.info(f"Cooperation Rate: {coop_rate:.4f}")
                    logging.info(f"Avg Loss: {loss:.4f}")
                    logging.info(f"Epsilon: {self.agents[0].epsilon:.4f}")
                    
                    # Log additional detailed metrics

                    lr = self.agents[0].optimizer.param_groups[0]['lr']
                    logging.info(f"Learning Rate: {lr:.2e}")
                    
                    # Log gradient norms if available
                    grad_norms = self.agents[0].get_gradient_norms()
                    logging.info(f"Gradient Norm: {grad_norms['q_grad_norm']:.4f}")
                    
                    # Log exploration rate
                    exploration_rate = 1.0 - self.agents[0].epsilon
                    logging.info(f"Exploration Rate: {exploration_rate:.4f}")
                    
                    # Store exploration rate in detailed metrics
                    self.detailed_metrics['exploration_rates'].append(exploration_rate)
                    
                    logging.info(f"Time elapsed: {elapsed_time:.2f}s")
                    logging.info("-" * 50)
            
            # Save best model based on cooperation rate
            current_coop_rate = episode_metrics['episode_cooperation_rate']
            if current_coop_rate > best_cooperation_rate:
                best_cooperation_rate = current_coop_rate
                best_model_path = os.path.join(self.save_dir, 'best_q_network_model.pt')
                self.save_models(best_model_path)
                logging.info(f"New best cooperation rate: {best_cooperation_rate:.4f}")
            
            # Save models periodically
            if episode % 100 == 0:
                save_path = os.path.join(self.save_dir, f'q_network_model_episode_{episode}.pt')
                self.save_models(save_path)
                logging.info(f"Models saved at episode {episode}")
        
        # Final save
        final_save_path = os.path.join(self.save_dir, 'q_network_model_final.pt')
        self.save_models(final_save_path)
        
        total_time = time.time() - start_time
        logging.info(f"Training completed in {total_time:.2f} seconds")
        logging.info(f"Best cooperation rate achieved: {best_cooperation_rate:.4f}")
        
        # Save training metrics
        self.save_training_metrics()
        
        # Plot comprehensive training curves
        plot_path = os.path.join(self.save_dir, 'q_network_comprehensive_training_curves.png')
        self.plot_training_curves(save_path=plot_path)
        
        return {
            'episode_rewards': self.training_metrics.get('episode_reward', []),
            'episode_cooperation_rates': self.training_metrics.get('episode_cooperation_rate', []),
            'final_cooperation_rate': self.cooperation_history[-1] if self.cooperation_history else 0.0,
            'final_avg_reward': self.training_metrics.get('episode_reward', [0.0])[-1] if self.training_metrics.get('episode_reward') else 0.0
        }
    
    def evaluate(self, num_episodes: int = 10) -> Dict[str, float]:
        """Evaluate the current policy"""
        for agent in self.agents:
            agent.set_eval_mode()
        
        eval_rewards = []
        eval_cooperation_rates = []
        eval_mutual_cooperation_rates = []
        move_history = []
        
        for episode in range(num_episodes):
            episode_rewards = np.zeros(self.num_players)
            episode_actions = np.zeros((self.episode_length, self.num_players), dtype=np.int64)
            episode_cooperations = 0
            episode_mutual_cooperations = 0
            
            # Initialize hidden states for evaluation
            hidden_states = [agent.get_initial_hidden_states() for agent in self.agents]
            
            for step in range(self.episode_length):
                actions = np.zeros(self.num_players, dtype=np.int64)
                
                # Get deterministic actions
                for agent_id in range(min(self.num_q_agents, self.num_players)):
                    obs = self._create_observation(agent_id, step, episode_actions)
                    action, _, new_hidden = self.agents[agent_id].get_action(obs, deterministic=True, hidden_state=hidden_states[agent_id])
                    hidden_states[agent_id] = new_hidden
                    actions[agent_id] = action
                
                episode_actions[step] = actions
                
                # Count cooperations
                cooperations = np.sum(actions == 0)
                episode_cooperations += cooperations
                
                # Count mutual cooperations
                if cooperations == self.num_q_agents:
                    episode_mutual_cooperations += 1
                
                # Calculate rewards
                rewards = self._calculate_rewards(actions)
                episode_rewards += rewards
            
            # Calculate episode metrics
            episode_reward = np.mean(episode_rewards)
            episode_coop_rate = episode_cooperations / (self.episode_length * self.num_q_agents)
            episode_mutual_coop_rate = episode_mutual_cooperations / self.episode_length
            
            eval_rewards.append(episode_reward)
            eval_cooperation_rates.append(episode_coop_rate)
            eval_mutual_cooperation_rates.append(episode_mutual_coop_rate)
            move_history.append(episode_actions.copy())
        
        # Set agents back to training mode
        for agent in self.agents:
            agent.set_train_mode()
        
        return {
            'eval_reward_mean': np.mean(eval_rewards),
            'eval_reward_std': np.std(eval_rewards),
            'eval_cooperation_rate': np.mean(eval_cooperation_rates),
            'eval_mutual_cooperation_rate': np.mean(eval_mutual_cooperation_rates),
            'move_history': move_history
        }
    
    def save_models(self, directory: str):
        """Save all Q-Network agents"""
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        for i, agent in enumerate(self.agents):
            agent_path = os.path.join(directory, f'q_network_agent_{i}.pt')
            agent.save(agent_path)
        
        logging.info(f"Q-Network agents saved to {directory}")
    
    def load_models(self, directory: str):
        """Load all Q-Network agents"""
        if not os.path.exists(directory):
            logging.warning(f"Directory {directory} does not exist")
            return
        
        for i, agent in enumerate(self.agents):
            # Try final model first, then best model, then base model
            agent_path = os.path.join(directory, f'q_network_agent_{i}_final.pt')
            if not os.path.exists(agent_path):
                agent_path = os.path.join(directory, f'q_network_agent_{i}_best.pt')
            if not os.path.exists(agent_path):
                agent_path = os.path.join(directory, f'q_network_agent_{i}.pt')
            
            if os.path.exists(agent_path):
                agent.load(agent_path)
                logging.info(f"Loaded Q-Network agent {i} from {agent_path}")
            else:
                logging.warning(f"Model file not found for agent {i} in {directory}")
    
    def save_training_metrics(self):
        """Save training metrics to file"""
        metrics_path = os.path.join(self.save_dir, 'q_network_training_metrics.npz')
        np.savez(metrics_path, **self.training_metrics)
        logging.info(f"Training metrics saved to {metrics_path}")
        
        # Save detailed metrics separately
        detailed_metrics_path = os.path.join(self.save_dir, 'q_network_detailed_metrics.npz')
        np.savez(detailed_metrics_path, **self.detailed_metrics)
        logging.info(f"Detailed training metrics saved to {detailed_metrics_path}")
        
        # Save metrics as JSON for easy inspection
        import json
        json_metrics = {}
        for key, value in self.detailed_metrics.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], (int, float)):
                    json_metrics[key] = value
                else:
                    json_metrics[key] = [str(v) for v in value]
            else:
                json_metrics[key] = value
        
        json_path = os.path.join(self.save_dir, 'q_network_detailed_metrics.json')
        with open(json_path, 'w') as f:
            json.dump(json_metrics, f, indent=2)
        logging.info(f"Detailed metrics JSON saved to {json_path}")
    
    def plot_training_curves(self, save_path: Optional[str] = None):
        """Plot comprehensive training curves with detailed metrics - matching cooperative MAPPO implementation"""
        # Create a comprehensive visualization with multiple subplots - 2x4 layout like cooperative MAPPO
        fig = plt.figure(figsize=(20, 10))
        
        # Training progress metrics
        ax1 = plt.subplot(2, 4, 1)
        ax1.plot(self.detailed_metrics['rewards'])
        ax1.set_title('Episode Rewards')
        ax1.set_xlabel('Training Step')
        ax1.set_ylabel('Reward')
        ax1.grid(True, alpha=0.3)
        
        ax2 = plt.subplot(2, 4, 2)
        ax2.plot(self.detailed_metrics['cooperation_rates'])
        ax2.set_title('Cooperation Rates')
        ax2.set_xlabel('Training Step')
        ax2.set_ylabel('Cooperation Rate')
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        
        # Q-Losses (if available)
        ax3 = plt.subplot(2, 4, 3)
        if self.detailed_metrics['q_losses']:
            ax3.plot(self.detailed_metrics['q_losses'])
            ax3.set_title('Q-Losses')
            ax3.set_xlabel('Training Step')
            ax3.set_ylabel('Loss')
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No Q-Losses Available', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Q-Losses')
        
        # Empty subplot for future use
        ax4 = plt.subplot(2, 4, 4)
        ax4.set_visible(False)
        
        # Empty subplot for future use
        ax5 = plt.subplot(2, 4, 5)
        ax5.set_visible(False)
        
        # Empty subplot for future use
        ax6 = plt.subplot(2, 4, 6)
        ax6.set_visible(False)
        
        # Empty subplot for future use
        ax7 = plt.subplot(2, 4, 7)
        ax7.set_visible(False)
        
        # Empty subplot for future use
        ax8 = plt.subplot(2, 4, 8)
        ax8.set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logging.info(f"Comprehensive training curves saved to {save_path}")
        else:
            plt.show()


def create_q_network_training_config() -> Dict:
    """Create Q-Network training configuration"""
    return {
        # Environment parameters
        'num_players': 20,
        'num_q_agents': 20,  # All players are Q-Network agents during training
        'env_type': 'smallworld',
        'k_neighbours': 4,
        'rewire_prob': 0.1,
        'reward_matrix': [
            [3.0, 0.0],  # Cooperate vs [Cooperate, Defect] - per interaction
            [5.0, 1.0]   # Defect vs [Cooperate, Defect] - per interaction
        ],
        
        # Training parameters
        'total_timesteps': 10000,
        'episode_length': 100,
        'update_frequency': 4,
        'target_update_frequency': 250,
        'lr_decay_rate': 0.9999,  # Learning rate decay rate
        
        # Q-learning parameters
        'epsilon_start': 1.0,      # Start with full exploration
        'epsilon_end': 0.01,       # End with minimal exploration
        'epsilon_decay': 0.995,    # Decay rate
        
        # Agent parameters
        'lr': 1e-3,
        'gamma': 0.99,
        
        # Save directory
        'save_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'q_network_models')
    }


if __name__ == "__main__":
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Create training configuration
    config = create_q_network_training_config()
    
    # Initialize trainer
    trainer = QNetworkTrainer(config)
    
    # Start training
    trainer.train()
    
    # Plot training curves
    plot_path = os.path.join(config['save_dir'], 'q_network_training_curves.png')
    trainer.plot_training_curves(save_path=plot_path)
    
    logging.info("Q-Network training completed successfully!")

