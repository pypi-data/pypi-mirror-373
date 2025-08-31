import os
import logging
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
import torch
import sys
import time
from tqdm import tqdm
# Flexible import system - works both when run directly and when imported
try:
    # When imported from comparison script
    from ...network_tops import make_ring_net, make_sw_net, make_fc_net
    from .decentralized_ppo_agent import DecentralizedPPOAgent
except ImportError:
    # When run directly from the folder
    # Add parent directory to path for network_tops
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from network_tops import make_ring_net, make_sw_net, make_fc_net
    from decentralized_ppo_agent import DecentralizedPPOAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecentralizedPPOTrainer:
    """
    Trainer for decentralized PPO agents - each agent trains independently
    """
    def __init__(self, config: Dict):
        self.config = config
        self.num_agents = config.get('num_agents', 10)
        self.obs_dim = config.get('obs_dim', 4)  # Standardized 4-dimensional observations
        self.episode_length = config.get('episode_length', 100)  # Rollout length = 100
        self.total_timesteps = config.get('total_timesteps', 5000)  # Total timesteps = 5,000
        self.total_episodes = self.total_timesteps // self.episode_length  # Calculate episodes needed
        self.update_frequency = config.get('update_frequency', 10)
        self.batch_size = config.get('batch_size', 64)
        self.num_epochs = config.get('num_epochs', 10)
        self.report_interval = config.get('report_interval', 2500)  # Report metrics at step 2500
        
        # Learning rate annealing parameters
        self.lr_actor_start = config.get('lr_actor', 3e-4)
        self.lr_critic_start = config.get('lr_critic', 1e-3)
        self.lr_decay_rate = config.get('lr_decay_rate', 0.9999)
        
        # Network configuration
        self.network_type = config.get('network_type', 'small_world')
        self.k_neighbors = config.get('k_neighbors', 2)
        
        # Create save directory
        self.save_dir = config.get('save_dir', 'decentralized_ppo_models')
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Create network
        self.network = self._create_network()
        
        # Create agents
        self.agents = self._create_agents()
        
        # Training metrics - Enhanced logging
        self.episode_rewards = []
        self.episode_cooperation_rates = []
        self.training_metrics = []
        
        # Detailed training metrics for comprehensive logging
        self.detailed_metrics = {
            'actor_losses': [],
            'critic_losses': [],
            'entropy_values': [],
            'learning_rates_actor': [],
            'learning_rates_critic': [],
            'gradient_norms_actor': [],
            'gradient_norms_critic': [],
            'cooperation_rates': [],
            'rewards': [],
            'episode_numbers': [],
            'agent_ids': []
        }
        
        logger.info(f"Initialized Decentralized PPO Trainer with {self.num_agents} agents")
        logger.info(f"Network: {self.network_type}, k_neighbors: {self.k_neighbors}")
        logger.info(f"Observation dimension: {self.obs_dim} (standardized 4D)")
        
        # Log initial hyperparameters
        logger.info(f"Learning rates - Actor: {self.lr_actor_start:.2e}, Critic: {self.lr_critic_start:.2e}, Decay: {self.lr_decay_rate}")
        logger.info(f"Training parameters - Total timesteps: {self.total_timesteps}, Episodes: {self.total_episodes}, Episode length: {self.episode_length}")
        logger.info(f"PPO parameters - Clip epsilon: {self.config.get('clip_epsilon', 0.2)}, Entropy coef: {self.config.get('entropy_coef', 0.01)}")
        
    def _anneal_learning_rates(self, episode: int):
        """Anneal learning rates over time"""
        for agent in self.agents:
            if hasattr(agent, 'actor_optimizer'):
                new_lr_actor = self.lr_actor_start * (self.lr_decay_rate ** (episode / 100))
                for param_group in agent.actor_optimizer.param_groups:
                    param_group['lr'] = new_lr_actor
            
            if hasattr(agent, 'critic_optimizer'):
                new_lr_critic = self.lr_critic_start * (self.lr_decay_rate ** (episode / 100))
                for param_group in agent.critic_optimizer.param_groups:
                    param_group['lr'] = new_lr_critic
    
    def _create_network(self) -> np.ndarray:
        """Create network topology"""
        if self.network_type == 'ring':
            network = make_ring_net(self.num_agents, self.k_neighbors)
        elif self.network_type == 'small_world':
            network = make_sw_net(self.num_agents, self.k_neighbors, 0.1)
        elif self.network_type == 'full':
            network = make_fc_net(self.num_agents)
        else:
            raise ValueError(f"Unknown network type: {self.network_type}")
        
        return network
    
    def _create_agents(self) -> List[DecentralizedPPOAgent]:
        """Create decentralized PPO agents"""
        agents = []
        for i in range(self.num_agents):
            agent = DecentralizedPPOAgent(
                agent_id=i,
                obs_dim=self.obs_dim,
                lr_actor=self.config.get('lr_actor', 3e-4),
                lr_critic=self.config.get('lr_critic', 1e-3),
                gamma=self.config.get('gamma', 0.99),
                gae_lambda=self.config.get('gae_lambda', 0.95),
                clip_epsilon=self.config.get('clip_epsilon', 0.2),
                entropy_coef=self.config.get('entropy_coef', 0.01),
                value_coef=self.config.get('value_coef', 0.5),
                max_grad_norm=self.config.get('max_grad_norm', 0.5)
            )
            agents.append(agent)
        
        return agents
    
    def _create_observation(self, agent_id: int, round_num: int, 
                          all_actions: np.ndarray) -> np.ndarray:
        """Create standardized 4-dimensional observation for a specific agent"""
        # Get neighbors
        neighbors = np.where(self.network[agent_id] == 1)[0]
        num_neighbors = len(neighbors)
        
        # Create standardized 4-dimensional observation
        obs = np.zeros(4, dtype=np.float32)
        
        # Feature 0: Own previous action (0 = cooperate, 1 = defect)
        obs[0] = float(all_actions[round_num - 1, agent_id]) if round_num > 0 else 0.0
        
        # Feature 1: Average neighbor action (last round)
        if num_neighbors > 0 and round_num > 0:
            neighbor_actions = all_actions[round_num - 1, neighbors]
            obs[1] = float(np.mean(neighbor_actions))
        else:
            obs[1] = 0.5
        
        # Feature 2: Neighbor cooperation rate (across whole episode history)
        if num_neighbors > 0 and round_num > 0:
            # Calculate cooperation rate across all previous rounds in this episode
            neighbor_coop_rates = []
            for neighbor in neighbors:
                if round_num > 0:
                    # Get all previous actions for this neighbor in this episode
                    neighbor_actions = all_actions[:round_num, neighbor]
                    if len(neighbor_actions) > 0:
                        coop_rate = float(np.mean(neighbor_actions == 0))  # 0 = cooperate
                        neighbor_coop_rates.append(coop_rate)
            
            if neighbor_coop_rates:
                obs[2] = float(np.mean(neighbor_coop_rates))
            else:
                obs[2] = 0.5
        else:
            obs[2] = 0.5
        
        # Feature 3: Number of neighbors (normalized)
        obs[3] = float(num_neighbors) / float(max(1, self.num_agents - 1))
        
        return obs
    
    def _log_detailed_metrics(self, episode: int, agent_id: int, metrics: Dict):
        """Log detailed training metrics for comprehensive analysis"""
        # Extract metrics from agent update
        if 'actor_loss' in metrics:
            self.detailed_metrics['actor_losses'].append(metrics['actor_loss'])
        if 'critic_loss' in metrics:
            self.detailed_metrics['critic_losses'].append(metrics['critic_loss'])
        if 'entropy' in metrics:
            self.detailed_metrics['entropy_values'].append(metrics['entropy'])

        
        # Log learning rates
        agent = self.agents[agent_id]
        if hasattr(agent, 'actor_optimizer'):
            current_lr_actor = agent.actor_optimizer.param_groups[0]['lr']
            self.detailed_metrics['learning_rates_actor'].append(current_lr_actor)
        if hasattr(agent, 'critic_optimizer'):
            current_lr_critic = agent.critic_optimizer.param_groups[0]['lr']
            self.detailed_metrics['learning_rates_critic'].append(current_lr_critic)
        
        # Log training progress
        self.detailed_metrics['episode_numbers'].append(episode)
        self.detailed_metrics['agent_ids'].append(agent_id)
        
        # Log gradient norms if available
        if hasattr(agent, 'get_gradient_norms'):
            grad_norms = agent.get_gradient_norms()
            if 'actor_grad_norm' in grad_norms:
                self.detailed_metrics['gradient_norms_actor'].append(grad_norms['actor_grad_norm'])
            if 'critic_grad_norm' in grad_norms:
                self.detailed_metrics['gradient_norms_critic'].append(grad_norms['critic_grad_norm'])
    
    def _calculate_rewards(self, actions: np.ndarray) -> np.ndarray:
        """Calculate rewards for all agents based on Prisoner's Dilemma"""
        rewards = np.zeros(self.num_agents)
        
        for i in range(self.num_agents):
            # Get neighbors
            neighbors = np.where(self.network[i] == 1)[0]
            
            if len(neighbors) == 0:
                rewards[i] = 0
                continue
            
            # Calculate reward based on own action and neighbor actions
            own_action = actions[i]
            neighbor_actions = actions[neighbors]
            
            # Prisoner's Dilemma reward matrix - average across neighbors
            total_reward = 0.0
            for neighbor_action in neighbor_actions:
                if own_action == 0:  # Cooperate
                    if neighbor_action == 0:  # Neighbor cooperates
                        total_reward += 3.0  # Mutual cooperation
                    else:  # Neighbor defects
                        total_reward += 0.0  # Sucker's payoff
                else:  # Defect
                    if neighbor_action == 0:  # Neighbor cooperates
                        total_reward += 5.0  # Temptation to defect
                    else:  # Neighbor defects
                        total_reward += 1.0  # Mutual defection
            
            # Average the reward across neighbors
            rewards[i] = total_reward / len(neighbors)
        
        return rewards
    
    def train(self) -> Dict[str, List[float]]:
        """Train all agents independently"""
        logger.info("Starting decentralized PPO training...")
        logger.info(f"Total timesteps: {self.total_timesteps}")
        logger.info(f"Episode length: {self.episode_length}")
        
        start_time = time.time()
        
        # Main training progress bar
        with tqdm(total=self.total_episodes, desc="Decentralized PPO Training Progress", ncols=100) as main_pbar:
            for episode in range(self.total_episodes):
                # Reset episode
                episode_rewards = np.zeros(self.num_agents)
                episode_actions = np.zeros((self.episode_length, self.num_agents), dtype=np.int64)
                episode_observations = np.zeros((self.episode_length, self.num_agents, self.obs_dim))
                episode_rewards_per_step = np.zeros((self.episode_length, self.num_agents))
                
                # Initialize hidden states for all agents
                initial_states = [agent.get_initial_hidden_states() for agent in self.agents]
                device = next(self.agents[0].actor.parameters()).device
                actor_hidden_states = [(torch.from_numpy(states[0][0]).squeeze(1).to(device), torch.from_numpy(states[0][1]).squeeze(1).to(device)) for states in initial_states]
                critic_hidden_states = [(torch.from_numpy(states[1][0]).squeeze(1).to(device), torch.from_numpy(states[1][1]).squeeze(1).to(device)) for states in initial_states]
                
                # Episode loop
                for step in range(self.episode_length):
                    # Get actions from all agents
                    actions = np.zeros(self.num_agents, dtype=np.int64)
                    values = np.zeros(self.num_agents)
                    log_probs = np.zeros(self.num_agents)
                    
                    for agent_id in range(self.num_agents):
                        # Create observation
                        obs = self._create_observation(agent_id, step, episode_actions)
                        episode_observations[step, agent_id] = obs
                        
                        # Get action from agent with hidden states
                        action, log_prob, new_actor_hidden = self.agents[agent_id].get_action(obs, hidden_state=actor_hidden_states[agent_id])
                        value, new_critic_hidden = self.agents[agent_id].get_value(obs, critic_hidden_states[agent_id])
                        
                        # Update hidden states
                        actor_hidden_states[agent_id] = new_actor_hidden
                        critic_hidden_states[agent_id] = new_critic_hidden
                        
                        actions[agent_id] = action
                        values[agent_id] = value
                        log_probs[agent_id] = log_prob
                    
                    # Store actions for next step observation
                    episode_actions[step] = actions
                    
                    # Calculate rewards
                    rewards = self._calculate_rewards(actions)
                    episode_rewards_per_step[step] = rewards
                    episode_rewards += rewards
                    
                    # Store experience in each agent's buffer
                    for agent_id in range(self.num_agents):
                        obs = episode_observations[step, agent_id]
                        action = actions[agent_id]
                        reward = rewards[agent_id]
                        value = values[agent_id]
                        log_prob = log_probs[agent_id]
                        done = (step == self.episode_length - 1)
                        actor_hidden = actor_hidden_states[agent_id]
                        critic_hidden = critic_hidden_states[agent_id]
                        
                        self.agents[agent_id].store_experience(
                            obs, action, reward, value, log_prob, done, actor_hidden, critic_hidden
                        )
                
                # Record metrics
                avg_reward = np.mean(episode_rewards)
                cooperation_rate = np.mean(episode_actions == 0)
                current_timestep = (episode + 1) * self.episode_length
            
                self.episode_rewards.append(avg_reward)
                self.episode_cooperation_rates.append(cooperation_rate)
                
                # Also track in detailed metrics
                self.detailed_metrics['rewards'].append(avg_reward)
                self.detailed_metrics['cooperation_rates'].append(cooperation_rate)
                
                # Update progress bar - similar to cooperative MAPPO
                main_pbar.set_postfix({
                    'Timestep': f'{current_timestep}/{self.total_timesteps}',
                    'Reward': f'{avg_reward:.2f}',
                    'Coop': f'{cooperation_rate:.2f}',
                    'LR Actor': f'{self.agents[0].actor_optimizer.param_groups[0]["lr"]:.2e}' if self.agents and hasattr(self.agents[0], 'actor_optimizer') else '0.00e+00'
                })
                main_pbar.update(1)
                
                # Apply learning rate annealing
                self._anneal_learning_rates(episode)
                
                # Report detailed metrics at specified interval
                if current_timestep >= self.report_interval and current_timestep % self.report_interval == 0:
                    self._report_agent_metrics(episode, current_timestep)
                
                # Periodic logging - similar to cooperative MAPPO for consistency
                if current_timestep % (self.report_interval * 2) == 0:  # Log every 2x report interval
                    # Get current learning rates for first agent (representative)
                    if self.agents and hasattr(self.agents[0], 'actor_optimizer'):
                        current_lr_actor = self.agents[0].actor_optimizer.param_groups[0]['lr']
                        current_lr_critic = self.agents[0].critic_optimizer.param_groups[0]['lr']
                    else:
                        current_lr_actor = 0
                        current_lr_critic = 0
                    
                    logger.info(f"Timestep {current_timestep}/{self.total_timesteps}")
                    logger.info(f"Avg Reward: {avg_reward:.4f}")
                    logger.info(f"Cooperation Rate: {cooperation_rate:.4f}")
                    logger.info(f"Learning Rate (Actor): {current_lr_actor:.2e}")
                    logger.info(f"Learning Rate (Critic): {current_lr_critic:.2e}")
                    logger.info("-" * 50)
            
                # Update agents if it's time (after recording metrics)
                if (episode + 1) % self.update_frequency == 0:
                    self._update_agents()
                    # Clear agent buffers after updating to prevent overflow
                    for agent in self.agents:
                        agent.buffer.clear()
        
        # Final logging summary - similar to cooperative MAPPO
        total_time = time.time() - start_time if 'start_time' in locals() else 0
        best_cooperation_rate = max(self.episode_cooperation_rates) if self.episode_cooperation_rates else 0.0
        final_avg_reward = np.mean(self.episode_rewards[-10:]) if self.episode_rewards else 0.0  # Last 10 episodes
        
        logger.info(f"Training completed in {total_time:.2f} seconds")
        logger.info(f"Best cooperation rate achieved: {best_cooperation_rate:.4f}")
        logger.info(f"Final average reward (last 10 episodes): {final_avg_reward:.4f}")
        
        # Save models and training metrics
        self.save_models()
        
        return {
            'episode_rewards': self.episode_rewards,
            'episode_cooperation_rates': self.episode_cooperation_rates,
            'training_metrics': self.training_metrics
        }
    
    def _update_agents(self):
        """Update all agents independently"""
        for agent_id, agent in enumerate(self.agents):
            if agent.buffer.size > 0:
                metrics = agent.update(
                    num_epochs=self.num_epochs,
                    batch_size=self.batch_size
                )
                
                if metrics:
                    metrics['agent_id'] = agent_id
                    self.training_metrics.append(metrics)
                    
                    # Log detailed metrics
                    self._log_detailed_metrics(0, agent_id, metrics)  # episode not available in this context
    
    def _report_agent_metrics(self, episode: int, timestep: int):
        """Report detailed metrics for each agent at specified intervals"""
        # Get cooperation rates for all agents
        cooperation_rates = [agent.get_cooperation_rate() for agent in self.agents]
        avg_cooperation = np.mean(cooperation_rates)
        
        # Get learning rates
        current_lr_actor = self.agents[0].actor_optimizer.param_groups[0]['lr']
        current_lr_critic = self.agents[0].critic_optimizer.param_groups[0]['lr']
        
        # Log detailed metrics
        logger.info(f"Episode {episode}, Timestep {timestep}/{self.total_timesteps}")
        logger.info(f"Avg Cooperation Rate: {avg_cooperation:.4f}")
        logger.info(f"Learning Rate (Actor): {current_lr_actor:.2e}")
        logger.info(f"Learning Rate (Critic): {current_lr_critic:.2e}")
        
        # Store in detailed metrics
        self.detailed_metrics['learning_rates_actor'].append(current_lr_actor)
        self.detailed_metrics['learning_rates_critic'].append(current_lr_critic)
        
        logger.info("-" * 50)
    
    def save_training_metrics(self):
        """Save training metrics to files"""
        metrics_dir = os.path.join(self.save_dir, 'training_metrics')
        os.makedirs(metrics_dir, exist_ok=True)
        
        # Save detailed metrics as numpy arrays
        np.savez(
            os.path.join(metrics_dir, 'decentralized_ppo_detailed_metrics.npz'),
            episode_rewards=np.array(self.episode_rewards),
            episode_cooperation_rates=np.array(self.episode_cooperation_rates),
            actor_losses=np.array(self.detailed_metrics['actor_losses']),
            critic_losses=np.array(self.detailed_metrics['critic_losses']),
            entropy_values=np.array(self.detailed_metrics['entropy_values']),
            learning_rates_actor=np.array(self.detailed_metrics['learning_rates_actor']),
            learning_rates_critic=np.array(self.detailed_metrics['learning_rates_critic']),
            gradient_norms_actor=np.array(self.detailed_metrics['gradient_norms_actor']),
            gradient_norms_critic=np.array(self.detailed_metrics['gradient_norms_critic'])
        )
        
        # Save as JSON for easy reading
        metrics_dict = {
            'episode_rewards': self.episode_rewards,
            'episode_cooperation_rates': self.episode_cooperation_rates,
            'actor_losses': self.detailed_metrics['actor_losses'],
            'critic_losses': self.detailed_metrics['critic_losses'],
            'entropy_values': self.detailed_metrics['entropy_values'],
            'learning_rates_actor': self.detailed_metrics['learning_rates_actor'],
            'learning_rates_critic': self.detailed_metrics['learning_rates_critic'],
            'gradient_norms_actor': self.detailed_metrics['gradient_norms_actor'],
            'gradient_norms_critic': self.detailed_metrics['gradient_norms_critic']
        }
        
        with open(os.path.join(metrics_dir, 'decentralized_ppo_detailed_metrics.json'), 'w') as f:
            json.dump(metrics_dict, f, indent=2)
        
        logger.info(f"Training metrics saved to {metrics_dir}")
    
    def save_models(self, save_dir: str = None):
        """Save only final agent models"""
        if save_dir is None:
            save_dir = self.save_dir
        
        os.makedirs(save_dir, exist_ok=True)
        
        for agent_id, agent in enumerate(self.agents):
            model_path = os.path.join(save_dir, f"decentralized_ppo_agent_{agent_id}_final.pt")
            agent.save(model_path)
        
        # Save training metrics
        metrics_path = os.path.join(save_dir, "training_metrics.npz")
        np.savez(metrics_path,
                 episode_rewards=np.array(self.episode_rewards),
                 episode_cooperation_rates=np.array(self.episode_cooperation_rates))
        
        logger.info(f"All models saved to {save_dir}")
        
        # Plot comprehensive training curves
        plot_path = os.path.join(save_dir, "decentralized_ppo_comprehensive_training_curves.png")
        self.plot_training_curves(save_path=plot_path)
        
        # Save detailed metrics separately
        detailed_metrics_path = os.path.join(save_dir, "decentralized_ppo_detailed_metrics.npz")
        np.savez(detailed_metrics_path, **self.detailed_metrics)
        logger.info(f"Detailed training metrics saved to {detailed_metrics_path}")
        
        # Save metrics as JSON for easy inspection
        json_metrics = {}
        for key, value in self.detailed_metrics.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], (int, float)):
                    json_metrics[key] = value
                else:
                    json_metrics[key] = [str(v) for v in value]
            else:
                json_metrics[key] = value
        
        json_path = os.path.join(save_dir, "decentralized_ppo_detailed_metrics.json")
        with open(json_path, 'w') as f:
            json.dump(json_metrics, f, indent=2)
        logger.info(f"Detailed metrics JSON saved to {json_path}")
    
    def plot_training_curves(self, save_path: Optional[str] = None):
        """Plot comprehensive training curves with detailed metrics - matching cooperative MAPPO implementation"""
        import matplotlib.pyplot as plt
        
        # Create a comprehensive visualization with multiple subplots - 2x4 layout like cooperative MAPPO
        fig = plt.figure(figsize=(20, 10))
        
        # Training progress metrics
        ax1 = plt.subplot(2, 4, 1)
        if self.episode_rewards:
            ax1.plot(self.episode_rewards)
            ax1.set_title('Episode Rewards')
            ax1.set_xlabel('Training Step')
            ax1.set_ylabel('Reward')
            ax1.grid(True, alpha=0.3)
        
        ax2 = plt.subplot(2, 4, 2)
        if self.episode_cooperation_rates:
            ax2.plot(self.episode_cooperation_rates)
            ax2.set_title('Cooperation Rates')
            ax2.set_xlabel('Training Step')
            ax2.set_ylabel('Cooperation Rate')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
        
        # Loss metrics
        ax3 = plt.subplot(2, 4, 3)
        if self.detailed_metrics['actor_losses']:
            ax3.plot(self.detailed_metrics['actor_losses'], label='Actor Loss')
        if self.detailed_metrics['critic_losses']:
            ax3.plot(self.detailed_metrics['critic_losses'], label='Critic Loss')
        ax3.set_title('Training Losses')
        ax3.set_xlabel('Training Step')
        ax3.set_ylabel('Loss')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        ax4 = plt.subplot(2, 4, 4)
        if self.detailed_metrics['entropy_values']:
            ax4.plot(self.detailed_metrics['entropy_values'])
        ax4.set_title('Policy Entropy')
        ax4.set_xlabel('Training Step')
        ax4.set_ylabel('Entropy')
        ax4.grid(True, alpha=0.3)
        
        # Learning dynamics
        ax5 = plt.subplot(2, 4, 5)
        if self.detailed_metrics['learning_rates_actor']:
            ax5.plot(self.detailed_metrics['learning_rates_actor'], label='Actor LR')
        if self.detailed_metrics['learning_rates_critic']:
            ax5.plot(self.detailed_metrics['learning_rates_critic'], label='Critic LR')
        ax5.set_title('Learning Rates')
        ax5.set_xlabel('Training Step')
        ax5.set_ylabel('Learning Rate')
        ax5.set_yscale('log')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        ax6 = plt.subplot(2, 4, 6)
        if self.detailed_metrics['gradient_norms_actor']:
            ax6.plot(self.detailed_metrics['gradient_norms_actor'], label='Actor Grad')
        if self.detailed_metrics['gradient_norms_critic']:
            ax6.plot(self.detailed_metrics['gradient_norms_critic'], label='Critic Grad')
        ax6.set_title('Gradient Norms')
        ax6.set_xlabel('Training Step')
        ax6.set_ylabel('Gradient Norm')
        ax6.set_yscale('log')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Comprehensive training curves saved to {save_path}")
        else:
            plt.show()
    
    def evaluate(self, num_episodes: int = 100) -> Dict[str, float]:
        """Evaluate trained agents"""
        logger.info(f"Evaluating agents over {num_episodes} episodes...")
        
        # Set agents to evaluation mode
        for agent in self.agents:
            agent.set_eval_mode()
        
        episode_rewards = []  # Store average reward per episode
        total_cooperation_actions = np.zeros(self.num_agents)
        total_actions = 0
        move_history = []  # Store moves for visualization
        
        for episode in range(num_episodes):
            episode_actions = np.zeros((self.episode_length, self.num_agents), dtype=np.int64)
            episode_rewards_per_step = []  # Store rewards for each step
            
            # Initialize hidden states for evaluation
            initial_states = [agent.get_initial_hidden_states() for agent in self.agents]
            device = next(self.agents[0].actor.parameters()).device
            actor_hidden_states = [(torch.from_numpy(states[0][0]).squeeze(1).to(device), torch.from_numpy(states[0][1]).squeeze(1).to(device)) for states in initial_states]
            
            for step in range(self.episode_length):
                actions = np.zeros(self.num_agents, dtype=np.int64)
                
                for agent_id in range(self.num_agents):
                    obs = self._create_observation(agent_id, step, episode_actions)
                    action, _, new_hidden = self.agents[agent_id].get_action(obs, deterministic=True, hidden_state=actor_hidden_states[agent_id])
                    actions[agent_id] = action
                    actor_hidden_states[agent_id] = new_hidden
                
                episode_actions[step] = actions
                rewards = self._calculate_rewards(actions)
                episode_rewards_per_step.append(rewards)
                total_cooperation_actions += (actions == 0)
                total_actions += self.num_agents
            
            # Calculate average reward per agent for this episode
            if episode_rewards_per_step:
                # episode_rewards_per_step is a list of arrays, each array contains rewards for all agents for that step
                # We want the average reward per agent across all steps
                episode_reward = np.mean([np.mean(step_rewards) for step_rewards in episode_rewards_per_step])
                episode_rewards.append(episode_reward)
            else:
                episode_rewards.append(0.0)
            
            # Store episode moves for visualization
            move_history.append(episode_actions.copy())
        
        # Calculate metrics
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.0
        cooperation_rate_per_agent = total_cooperation_actions / (num_episodes * self.episode_length)
        overall_cooperation_rate = np.sum(total_cooperation_actions) / total_actions
        
        # Set agents back to training mode
        for agent in self.agents:
            agent.set_train_mode()
        
        evaluation_results = {
            'avg_reward_per_agent': cooperation_rate_per_agent.tolist(),
            'cooperation_rate_per_agent': cooperation_rate_per_agent.tolist(),
            'overall_cooperation_rate': overall_cooperation_rate,
            'avg_reward': avg_reward,
            'std_reward': np.std(episode_rewards) if episode_rewards else 0.0,
            'move_history': move_history  # Add move history for visualization
        }
        
        logger.info(f"Evaluation completed - Overall Cooperation Rate: {overall_cooperation_rate:.3f}")
        return evaluation_results


def create_decentralized_training_config() -> Dict:
    """Create default training configuration for decentralized PPO"""
    return {
        'num_agents': 10,
        'obs_dim': 4,  # Standardized 4-dimensional observations
        'episode_length': 100,  # Rollout length = 100
        'total_timesteps': 2000,  # Total timesteps = 2,000
        'report_interval': 1000,  # Report agent metrics at step 1000
        'update_frequency': 2,
        'batch_size': 64,
        'num_epochs': 10,
        'lr_decay_rate': 0.999,  # Learning rate decay rate
        'network_type': 'small_world',
        'k_neighbors': 2,
        'lr_actor': 3e-4,
        'lr_critic': 1e-3,
        'gamma': 0.99,
        'gae_lambda': 0.95,
        'clip_epsilon': 0.2,
        'entropy_coef': 0.01,
        'value_coef': 0.5,
        'max_grad_norm': 0.5,
        
        # Save directory - always save in the decentralized_ppo folder
        'save_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decentralized_ppo_models')
    }


if __name__ == "__main__":

    config = create_decentralized_training_config()
    trainer = DecentralizedPPOTrainer(config)
    
    # Train agents
    training_results = trainer.train()
    
    # Evaluate trained agents
    evaluation_results = trainer.evaluate()
    logger.info(f"Training completed. Final cooperation rate: {evaluation_results['overall_cooperation_rate']:.3f}")

