import numpy as np
import torch
import logging
import time
import os
import sys
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict
from tqdm import tqdm

# Flexible import system - works both when run directly and when imported
try:
    # When imported from comparison script
    from .standard_mappo_agent import StandardMAPPOAgent
    from .standard_observation_processor import StandardEnvironmentWrapper
    from .cooperative_environment_wrapper import CooperativeEnvironmentWrapper
    from ...network_environment import initialise_network
except ImportError:
    # When run directly from the folder
    from standard_mappo_agent import StandardMAPPOAgent
    from standard_observation_processor import StandardEnvironmentWrapper
    from cooperative_environment_wrapper import CooperativeEnvironmentWrapper
    # Add parent directory to path for network_environment
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from network_environment import initialise_network

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ValueNormalizedMAPPOTrainer:
    """
    Enhanced MAPPO trainer for standard MAPPO training with value normalization (no reward shaping)
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
        self.num_mappo_agents = config.get('num_mappo_agents', 20)
        self.total_timesteps = config.get('total_timesteps', 2000)
        self.rollout_length = config.get('rollout_length', 100)
        self.num_epochs = config.get('num_epochs', 10)
        self.batch_size = config.get('batch_size', 64)
        self.save_interval = config.get('save_interval', 1000)
        self.eval_interval = config.get('eval_interval', 500)
        
        # Learning rate annealing
        self.lr_annealing = config.get('lr_annealing', False)
        self.initial_lr_actor = config.get('initial_lr_actor', 1e-3)
        self.initial_lr_critic = config.get('initial_lr_critic', 5e-3)
        self.final_lr_actor = config.get('final_lr_actor', 1e-4)
        self.final_lr_critic = config.get('final_lr_critic', 5e-4)
        
        # Additional parameters
        self.use_reward_shaping = config.get('use_reward_shaping', False)  # Disabled for standard MAPPO
        self.history_length = config.get('history_length', 5)
        
        # Value normalization parameters
        self.use_value_norm = True  # Enable value normalization
        self.value_norm_decay = 0.99
        self.value_norm_eps = 1e-8
        
        # Value normalization statistics
        self.value_norm_mean = 0.0
        self.value_norm_var = 1.0
        self.value_norm_count = 0
        
        # Initialize metrics tracking
        self.training_metrics = defaultdict(list)
        self.detailed_metrics = defaultdict(list)
        self.cooperation_history = []
        
        # Initialize start time for training
        self.start_time = time.time()
        
        # Create save directory
        self.save_dir = config.get('save_dir', 'standard_mappo_models')
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Initialize environment
        self._setup_environment()
        
        # Initialize agent
        local_obs_dim, global_state_dim = self.env.get_observation_dims()
        self.agent = StandardMAPPOAgent(
            num_agents=self.num_mappo_agents,
            local_obs_dim=local_obs_dim,
            global_state_dim=global_state_dim,
            lr_actor=config.get('lr_actor', 1e-4),
            lr_critic=config.get('lr_critic', 3e-4),
            gamma=config.get('gamma', 0.99),
            gae_lambda=config.get('gae_lambda', 0.95),
            clip_epsilon=config.get('clip_epsilon', 0.2),
            entropy_coef=config.get('entropy_coef', 0.05),  # Higher entropy
            value_coef=config.get('value_coef', 0.5),
            cooperation_bonus=config.get('cooperation_bonus', 0.0)  # Use config setting
        )
        
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
            'progress': [],
            'value_norm_stats': []  # Value normalization statistics
        }
        
        logging.info("Value-Normalized MAPPO Trainer initialized successfully")
        logging.info(f"Environment: {self.num_players} players, {self.num_mappo_agents} MAPPO agents")
        logging.info(f"Observation dims: local={local_obs_dim}, global={global_state_dim}")
        logging.info(f"Reward shaping: {self.use_reward_shaping}")
        logging.info(f"Value normalization: {self.use_value_norm}")
        
        # Log initial hyperparameters
        logging.info(f"Learning rates - Actor: {config.get('lr_actor', 1e-4):.2e}, Critic: {config.get('lr_critic', 3e-4):.2e}")
        logging.info(f"Training parameters - Total steps: {self.total_timesteps}, Rollout: {self.rollout_length}, Epochs: {self.num_epochs}")
        logging.info(f"PPO parameters - Clip epsilon: {config.get('clip_epsilon', 0.2)}, Entropy coef: {config.get('entropy_coef', 0.05)}")
        logging.info(f"Value normalization - Decay: {self.value_norm_decay}, Epsilon: {self.value_norm_eps}")
    
    def _setup_environment(self):
        """Setup the cooperative training environment"""
        # Create player assignments (all MAPPO agents for training)
        player_types = ['mappo'] * self.num_players
        player_assignments = {i: player_types[i] for i in range(self.num_players)}
        
        # Initialize network
        network, _ = initialise_network(
            self.env_type, 
            self.num_players, 
            player_types, 
            self.k_neighbours, 
            self.rewire_prob
        )
        
        # All players are MAPPO agents during training
        mappo_agent_ids = list(range(self.num_mappo_agents))
        
        # Create environment wrapper based on reward shaping setting
        if self.use_reward_shaping:
            # Use cooperative environment wrapper for reward shaping
            self.env = CooperativeEnvironmentWrapper(
                num_players=self.num_players,
                network=network,
                player_assignments=player_assignments,
                reward_matrix=self.reward_matrix,
                mappo_agent_ids=mappo_agent_ids,
                history_length=self.history_length,
                use_reward_shaping=True,  # Enabled for cooperative MAPPO
                mutual_cooperation_bonus=self.config.get('cooperation_bonus', 4.0),
                defection_penalty=self.config.get('defection_penalty', 0.0)
            )
        else:
            # Use standard environment wrapper for no reward shaping
            self.env = StandardEnvironmentWrapper(
                num_players=self.num_players,
                network=network,
                player_assignments=player_assignments,
                reward_matrix=self.reward_matrix,
                mappo_agent_ids=mappo_agent_ids,
                history_length=self.history_length,
                use_reward_shaping=False
            )
        
        logging.info(f"Standard training environment setup complete")
        logging.info(f"Network type: {self.env_type}, Rewire prob: {self.rewire_prob}")
    
    def _get_annealed_learning_rates(self, timestep: int) -> Dict[str, float]:
        """Get annealed learning rates based on training progress"""
        if not self.lr_annealing:
            return {}
        
        # Calculate progress (0 to 1)
        progress = timestep / self.total_timesteps
        
        # Anneal learning rates linearly
        current_lr_actor = self.initial_lr_actor + (self.final_lr_actor - self.initial_lr_actor) * progress
        current_lr_critic = self.initial_lr_critic + (self.final_lr_critic - self.initial_lr_critic) * progress
        
        return {
            'lr_actor': current_lr_actor,
            'lr_critic': current_lr_critic,
            'progress': progress
        }
    
    def collect_rollout(self, timestep: int) -> Tuple[float, int, Dict[str, float]]:
        """
        Collect a rollout of experiences with curriculum learning
        """
        local_obs, global_state = self.env.reset()
        
        episode_rewards = []
        episode_length = 0
        cooperation_rates = []
        
        # Get learning rate parameters
        lr_params = self._get_annealed_learning_rates(timestep)
        
        # Initialize hidden states for recurrent networks
        actor_hidden_states, critic_hidden_state = self.agent.get_initial_hidden_states()
        
        # Progress bar for rollout collection
        with tqdm(total=self.rollout_length, desc=f"Rollout", 
                 leave=False, ncols=80) as pbar:
            for step in range(self.rollout_length):
                # Get actions from MAPPO agents with hidden states
                actions, log_probs, new_actor_hidden_states = self.agent.get_action(
                    local_obs, deterministic=False, hidden_states=actor_hidden_states
                )
                
                # Get value estimates with hidden state
                values, new_critic_hidden = self.agent.get_value(global_state, hidden_state=critic_hidden_state)
                
                # Apply value normalization if enabled
                if self.use_value_norm:
                    # Update value normalization statistics
                    self._update_value_norm_stats(values)
                    # Normalize values for storage
                    normalized_values = self._normalize_values(values)
                else:
                    normalized_values = values
                
                # Take environment step
                next_local_obs, next_global_state, rewards, dones, episode_done = self.env.step(actions)
                
                # Get shaped rewards for learning (with cooperation bonuses/penalties)
                shaped_rewards = self.env.shaped_rewards if hasattr(self.env, 'shaped_rewards') else rewards
                
                # Calculate cooperation rates
                step_cooperation_rate = np.mean(actions == 0)  # 0 = Cooperate
                cooperation_rates.append(step_cooperation_rate)
                
                # Store experience in buffer with hidden states
                self.agent.store_experience(
                    local_obs=local_obs,
                    global_state=global_state,
                    actions=actions,
                    rewards=shaped_rewards,  # Use shaped rewards for learning
                    values=normalized_values,  # Store normalized values
                    log_probs=log_probs,
                    dones=dones,
                    actor_hidden_states=actor_hidden_states,
                    critic_hidden_states=critic_hidden_state
                )
                
                # Update observations and hidden states
                local_obs = next_local_obs
                global_state = next_global_state
                actor_hidden_states = new_actor_hidden_states
                critic_hidden_state = new_critic_hidden
                
                episode_rewards.append(np.mean(rewards))
                episode_length += 1
                
                # Update progress bar
                pbar.set_postfix({
                    'Reward': f'{np.mean(rewards):.2f}',
                    'Coop': f'{step_cooperation_rate:.2f}'
                })
                pbar.update(1)
                
        
                if step % 25 == 0:  # Log every 25 steps instead of 10 to reduce spam
                    logging.debug(f"Step {step}: Rewards={rewards}, Mean={np.mean(rewards):.4f}, Std={np.std(rewards):.4f}")
                
                if episode_done:
                    break
        
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0.0
        avg_cooperation_rate = np.mean(cooperation_rates) if cooperation_rates else 0.0
        
        # Get environment cooperation statistics
        env_coop_stats = self.env.get_cooperation_statistics()
        
        rollout_stats = {
            'avg_reward': avg_reward,
            'avg_cooperation_rate': avg_cooperation_rate,
            'final_cooperation_rate': cooperation_rates[-1] if cooperation_rates else 0.0,
            **env_coop_stats,
            **lr_params
        }
        
        return avg_reward, episode_length, rollout_stats
    
    def _log_detailed_metrics(self, timestep: int, metrics: Dict, rollout_stats: Dict):
        """Log detailed training metrics for comprehensive analysis"""
        # Extract metrics from agent update
        self.detailed_metrics['actor_losses'].append(metrics['actor_loss'])
        self.detailed_metrics['critic_losses'].append(metrics['critic_loss'])
        self.detailed_metrics['entropy_values'].append(metrics['entropy'])
        
        # Log learning rates
        current_lr_actor = self.agent.actor_optimizer.param_groups[0]['lr']
        current_lr_critic = self.agent.critic_optimizer.param_groups[0]['lr']
        self.detailed_metrics['learning_rates_actor'].append(current_lr_actor)
        self.detailed_metrics['learning_rates_critic'].append(current_lr_critic)
        
        # Log curriculum parameters
        self.detailed_metrics['learning_rates_actor'].append(rollout_stats['lr_actor'])
        self.detailed_metrics['learning_rates_critic'].append(rollout_stats['lr_critic'])
        
        # Log gradient norms
        grad_norms = self.agent.get_gradient_norms()
        self.detailed_metrics['gradient_norms_actor'].append(grad_norms['actor'])
        self.detailed_metrics['gradient_norms_critic'].append(grad_norms['critic'])
        
        # Log cooperation rates and rewards
        self.detailed_metrics['cooperation_rates'].append(rollout_stats['avg_cooperation_rate'])
        self.detailed_metrics['rewards'].append(rollout_stats['avg_reward'])
        
        # Log progress
        progress = timestep / self.total_timesteps
        self.detailed_metrics['progress'].append(progress)
        
        # Log value normalization statistics
        self.detailed_metrics['value_norm_stats'].append({
            'mean': self.value_norm_mean,
            'var': self.value_norm_var,
            'count': self.value_norm_count
        })
    
    def _update_value_norm_stats(self, values: np.ndarray):
        """Update value normalization statistics using Welford's online algorithm"""
        if not self.use_value_norm:
            return
        
        # Flatten values for statistics calculation
        flat_values = values.flatten()
        batch_size = flat_values.size
        
        if batch_size == 0:
            return
        
        batch_mean = np.mean(flat_values)
        
        # Update running statistics
        if self.value_norm_count == 0:
            self.value_norm_mean = batch_mean
            self.value_norm_var = np.var(flat_values) if batch_size > 1 else 1.0
        else:
            # Welford's online algorithm for variance
            delta = batch_mean - self.value_norm_mean
            self.value_norm_mean += delta * batch_size / (self.value_norm_count + batch_size)
            
            # Update variance using Welford's method
            for value in flat_values:
                delta2 = value - self.value_norm_mean
                self.value_norm_var = (self.value_norm_var * self.value_norm_count + 
                                     delta * delta2) / (self.value_norm_count + 1)
                self.value_norm_count += 1
                return  # Exit after first iteration to avoid double counting
        
        self.value_norm_count += batch_size
        
        # Ensure variance is never zero
        if self.value_norm_var < self.value_norm_eps:
            self.value_norm_var = self.value_norm_eps
    
    def _normalize_values(self, values: np.ndarray) -> np.ndarray:
        """Normalize values using running statistics"""
        if self.use_value_norm:
            normalized = (values - self.value_norm_mean) / (np.sqrt(self.value_norm_var) + self.value_norm_eps)
            return normalized
        return values
    
    def _denormalize_values(self, normalized_values: np.ndarray) -> np.ndarray:
        """Denormalize values back to original scale"""
        if self.use_value_norm:
            denormalized = normalized_values * (np.sqrt(self.value_norm_var) + self.value_norm_eps) + self.value_norm_mean
            return denormalized
        return normalized_values
    
    def train_step(self, timestep: int) -> Dict[str, float]:
        """Perform one training step with curriculum learning"""
        # Collect rollout
        avg_reward, episode_length, rollout_stats = self.collect_rollout(timestep)
        
        # Update curriculum parameters if needed
        lr_params = self._get_annealed_learning_rates(timestep)
        if 'lr_actor' in lr_params:
            self.agent.actor_optimizer.param_groups[0]['lr'] = lr_params['lr_actor']
        if 'lr_critic' in lr_params:
            self.agent.critic_optimizer.param_groups[0]['lr'] = lr_params['lr_critic']
        
        # Log learning rate changes periodically
        if timestep % (self.eval_interval * 2) == 0:
            current_lr_actor = self.agent.actor_optimizer.param_groups[0]['lr'] if hasattr(self.agent, 'actor_optimizer') else 0
            current_lr_critic = self.agent.critic_optimizer.param_groups[0]['lr'] if hasattr(self.agent, 'critic_optimizer') else 0
            logging.info(f"Learning rates annealed - Actor: {current_lr_actor:.2e}, Critic: {current_lr_critic:.2e}")
            
            # Log value normalization statistics
            if self.use_value_norm:
                logging.info(f"Value normalization - Mean: {self.value_norm_mean:.4f}, Var: {self.value_norm_var:.4f}, Count: {self.value_norm_count}")
        

        if self.agent.buffer.size >= self.rollout_length:
            # Update agent
            metrics = self.agent.update(self.num_epochs, self.batch_size)
            
            # Clear buffer only after successful update
            self.agent.buffer.clear()
        else:
            # Not enough experiences yet, return empty metrics
            metrics = {}
        
        # Combine metrics
        metrics.update({
            'avg_reward': avg_reward,
            'episode_length': episode_length,
            **rollout_stats
        })
        
        # Log detailed metrics
        self._log_detailed_metrics(timestep, metrics, rollout_stats)
        
        return metrics
    
    def evaluate(self, num_episodes: int = 10) -> Dict[str, float]:
        """Evaluate the current policy"""
        self.agent.set_eval_mode()
        
        eval_rewards = []
        eval_cooperation_rates = []
        eval_mutual_cooperation_rates = []
        move_history = []  # Store moves for visualization
        
        # Progress bar for evaluation
        with tqdm(total=num_episodes, desc="Evaluation", ncols=80) as eval_pbar:
            for episode in range(num_episodes):
                local_obs, global_state = self.env.reset()
                episode_rewards = []  # Store rewards for each step
                episode_moves = []  # Store moves for each step
                episode_cooperations = 0
                episode_mutual_cooperations = 0
                episode_length = 0
                
                # Initialize hidden states for recurrent networks
                actor_hidden_states, critic_hidden_state = self.agent.get_initial_hidden_states()
            
            for step in range(self.rollout_length):
                # Get deterministic actions with hidden states
                actions, _, new_actor_hidden_states = self.agent.get_action(
                    local_obs, deterministic=True, hidden_states=actor_hidden_states
                )
                
                # Store moves for this step
                episode_moves.append(actions.copy())
                
                # Count cooperations and mutual cooperations
                cooperations = np.sum(actions == 0)
                episode_cooperations += cooperations
                
                # Count mutual cooperations (all agents cooperate)
                if cooperations == self.num_mappo_agents:
                    episode_mutual_cooperations += 1
                
                # Take step
                next_local_obs, next_global_state, rewards, dones, episode_done = self.env.step(actions)
                
                # Get shaped rewards for learning (if available)
                shaped_rewards = None
                if hasattr(self.env, 'get_shaped_rewards'):
                    shaped_rewards = self.env.get_shaped_rewards()
                
        
                if episode == 0 and step < 2:  # Reduced from 3 to 2 steps
                    logging.debug(f"Episode {episode}, Step {step}: Actions={actions}, Base Rewards={rewards}, Shaped Rewards={shaped_rewards}")
                
                # Store the rewards for this step (use base rewards for logging)
                episode_rewards.append(rewards)
                episode_length += 1
                
                local_obs = next_local_obs
                global_state = next_global_state
                actor_hidden_states = new_actor_hidden_states
                
                if episode_done:
                    break
            
            # Calculate the average reward per agent for this episode
            if episode_rewards:
                # episode_rewards is a list of arrays, each array contains rewards for all agents for that step
                # We want the average reward per agent across all steps
                episode_reward = np.mean([np.mean(step_rewards) for step_rewards in episode_rewards])
            else:
                episode_reward = 0.0
            
    
            if episode % 5 == 0:  # Only log every 5th episode
                logging.debug(f"Episode {episode}: Length={episode_length}, Reward={episode_reward:.4f}, Cooperation Rate={episode_cooperations/(episode_length * self.num_mappo_agents):.4f}")
            
            eval_rewards.append(episode_reward)
            eval_cooperation_rates.append(episode_cooperations / (episode_length * self.num_mappo_agents))
            eval_mutual_cooperation_rates.append(episode_mutual_cooperations / episode_length)
            
            # Store episode moves for visualization
            if episode_moves:
                # Convert to numpy array: (timesteps, agents)
                episode_moves_array = np.array(episode_moves)
                move_history.append(episode_moves_array)
            
            # Update evaluation progress bar
            eval_pbar.set_postfix({
                'Reward': f'{episode_reward:.2f}',
                'Coop': f'{episode_cooperations/(episode_length * self.num_mappo_agents):.2f}'
            })
            eval_pbar.update(1)
        
        self.agent.set_train_mode()
        
        return {
            'eval_reward_mean': np.mean(eval_rewards),
            'eval_reward_std': np.std(eval_rewards),
            'eval_cooperation_rate': np.mean(eval_cooperation_rates),
            'eval_mutual_cooperation_rate': np.mean(eval_mutual_cooperation_rates),
            'cooperation_bias': self.agent.get_cooperation_rate(),
            'move_history': move_history  # Add move history for visualization
        }
    
    def train(self):
        """Main training loop with curriculum learning"""
        logging.info("Starting Value-Normalized MAPPO training...")
        logging.info(f"Total timesteps: {self.total_timesteps}")
        logging.info(f"Rollout length: {self.rollout_length}")
        
        # Training progress tracking
        timestep = 0
        best_cooperation_rate = 0.0
        
        # Progress bar for overall training
        with tqdm(total=self.total_timesteps, desc="Training Progress", ncols=100) as pbar:
            while timestep < self.total_timesteps:
                # Perform training step
                metrics = self.train_step(timestep)
                
                # Update progress bar
                current_reward = metrics.get('avg_reward', 0.0)
                current_coop = metrics.get('avg_cooperation_rate', 0.0)
                pbar.set_postfix({
                    'Timestep': f'{timestep}/{self.total_timesteps}',
                    'Reward': f'{current_reward:.2f}',
                    'Coop': f'{current_coop:.2f}'
                })
                pbar.update(self.rollout_length)
                
                # Update timestep
                timestep += self.rollout_length
                
                # Save model periodically
                if timestep % self.save_interval == 0:
                    model_path = os.path.join(self.save_dir, f'value_norm_mappo_model_{timestep}.pt')
                    self.agent.save(model_path)
                    logging.info(f"Value-Normalized MAPPO Agent saved to {model_path}")
                    logging.info(f"Model saved at timestep {timestep}")
                
                # Evaluate periodically
                if timestep % self.eval_interval == 0:
                    eval_metrics = self.evaluate()
                    logging.info(f"Evaluation at timestep {timestep}:")
                    for key, value in eval_metrics.items():
                        if isinstance(value, (int, float)):
                            logging.info(f"  {key}: {value:.4f}")
                        elif isinstance(value, list):
                            logging.info(f"  {key}: {value}")
                        else:
                            logging.info(f"  {key}: {value}")
                    
                    # Save best model based on cooperation rate
                    if eval_metrics['eval_cooperation_rate'] > best_cooperation_rate:
                        best_cooperation_rate = eval_metrics['eval_cooperation_rate']
                        best_model_path = os.path.join(self.save_dir, 'value_norm_mappo_model_best.pt')
                        self.agent.save(best_model_path)
                        logging.info(f"New best model saved with cooperation rate: {best_cooperation_rate:.4f}")
        
        # Save final model
        final_model_path = os.path.join(self.save_dir, 'value_norm_mappo_model_final.pt')
        self.agent.save(final_model_path)
        logging.info(f"Training completed in {time.time() - self.start_time:.2f} seconds")
        logging.info(f"Best cooperation rate achieved: {best_cooperation_rate:.4f}")
        
        # Save training metrics
        self._save_training_metrics()
        
        # Plot training curves
        self.plot_training_curves()
    
    def _save_training_metrics(self):
        """Save training metrics to file"""
        metrics_path = os.path.join(self.save_dir, 'value_norm_mappo_training_metrics.npz')
        detailed_metrics_path = os.path.join(self.save_dir, 'value_norm_mappo_detailed_metrics.npz')
        detailed_json_path = os.path.join(self.save_dir, 'value_norm_mappo_detailed_metrics.json')
        
        # Save basic training metrics
        np.savez(metrics_path, **self.training_metrics)
        logging.info(f"Training metrics saved to {metrics_path}")
        
        # Save detailed metrics
        np.savez(detailed_metrics_path, **self.detailed_metrics)
        logging.info(f"Detailed training metrics saved to {detailed_metrics_path}")
        
        # Save detailed metrics as JSON for easy inspection
        import json
        json_metrics = {}
        

        logging.info(f"Attempting to serialize {len(self.detailed_metrics)} metric keys")
        
        for key, values in self.detailed_metrics.items():
            try:
                if isinstance(values, list) and len(values) > 0:
                    # Convert numpy arrays and types to Python native types for JSON serialization
                    converted_values = []
                    for v in values:
                        if hasattr(v, 'tolist'):  # NumPy array
                            converted_values.append(v.tolist())
                        elif hasattr(v, 'item'):  # NumPy scalar
                            converted_values.append(v.item())
                        elif isinstance(v, np.integer):  # NumPy integer types
                            converted_values.append(int(v))
                        elif isinstance(v, np.floating):  # NumPy float types
                            converted_values.append(float(v))
                        elif isinstance(v, np.bool_):  # NumPy boolean
                            converted_values.append(bool(v))
                        else:
                            converted_values.append(v)
                    json_metrics[key] = converted_values
                else:
                    # Handle single values
                    if hasattr(values, 'item'):  # NumPy scalar
                        json_metrics[key] = values.item()
                    elif isinstance(values, np.integer):
                        json_metrics[key] = int(values)
                    elif isinstance(values, np.floating):
                        json_metrics[key] = float(values)
                    elif isinstance(values, np.bool_):
                        json_metrics[key] = bool(values)
                    else:
                        json_metrics[key] = values
                        
            except Exception as e:
                logging.warning(f"Failed to serialize metric {key}: {e}")
                # Skip problematic metrics
                continue
        

        logging.info(f"Successfully converted {len(json_metrics)} metrics for JSON serialization")
        
        try:
            with open(detailed_json_path, 'w') as f:
                json.dump(json_metrics, f, indent=2)
            logging.info(f"Detailed metrics JSON saved to {detailed_json_path}")
        except Exception as e:
            logging.error(f"Failed to save JSON metrics: {e}")
            # Save a simplified version instead
            simple_metrics = {k: str(v) for k, v in json_metrics.items()}
            with open(detailed_json_path, 'w') as f:
                json.dump(simple_metrics, f, indent=2)
            logging.info(f"Simplified metrics JSON saved to {detailed_json_path}")
    
    def plot_training_curves(self, save_path: Optional[str] = None):
        """Plot comprehensive training curves with value normalization statistics"""
        if save_path is None:
            save_path = os.path.join(self.save_dir, 'value_norm_mappo_comprehensive_training_curves.png')
        
        # Create figure with 2x4 subplots
        fig, axes = plt.subplots(2, 4, figsize=(20, 12))
        fig.suptitle('Value-Normalized MAPPO Training Curves', fontsize=16, fontweight='bold')
        
        # Training rewards
        ax1 = plt.subplot(2, 4, 1)
        ax1.plot(self.detailed_metrics['rewards'], label='Training Reward', color='blue')
        ax1.set_title('Training Rewards')
        ax1.set_xlabel('Training Step')
        ax1.set_ylabel('Average Reward')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Cooperation rates
        ax2 = plt.subplot(2, 4, 2)
        ax2.plot(self.detailed_metrics['cooperation_rates'], label='Cooperation Rate', color='green')
        ax2.set_title('Cooperation Rates')
        ax2.set_xlabel('Training Step')
        ax2.set_ylabel('Cooperation Rate')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Actor losses
        ax3 = plt.subplot(2, 4, 3)
        ax3.plot(self.detailed_metrics['actor_losses'], label='Actor Loss', color='red')
        ax3.set_title('Actor Losses')
        ax3.set_xlabel('Training Step')
        ax3.set_ylabel('Loss')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Critic losses
        ax4 = plt.subplot(2, 4, 4)
        ax4.plot(self.detailed_metrics['critic_losses'], label='Critic Loss', color='orange')
        ax4.set_title('Critic Losses')
        ax4.set_xlabel('Training Step')
        ax4.set_ylabel('Loss')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Learning rates
        ax5 = plt.subplot(2, 4, 5)
        ax5.plot(self.detailed_metrics['learning_rates_actor'], label='Actor LR')
        ax5.plot(self.detailed_metrics['learning_rates_critic'], label='Critic LR')
        ax5.set_title('Learning Rates')
        ax5.set_xlabel('Training Step')
        ax5.set_ylabel('Learning Rate')
        ax5.set_yscale('log')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # Gradient norms
        ax6 = plt.subplot(2, 4, 6)
        ax6.plot(self.detailed_metrics['gradient_norms_actor'], label='Actor Grad')
        ax6.plot(self.detailed_metrics['gradient_norms_critic'], label='Critic Grad')
        ax6.set_title('Gradient Norms')
        ax6.set_xlabel('Training Step')
        ax6.set_ylabel('Gradient Norm')
        ax6.set_yscale('log')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # Value normalization statistics
        ax7 = plt.subplot(2, 4, 7)
        means = [stats['mean'] for stats in self.detailed_metrics['value_norm_stats']]
        vars = [stats['var'] for stats in self.detailed_metrics['value_norm_stats']]
        ax7.plot(means, label='Mean', color='purple')
        ax7.plot(vars, label='Variance', color='brown')
        ax7.set_title('Value Normalization Stats')
        ax7.set_xlabel('Training Step')
        ax7.set_ylabel('Value')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # Empty subplot for future use
        ax8 = plt.subplot(2, 4, 8)
        ax8.set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logging.info(f"Value-Normalized MAPPO training curves saved to {save_path}")
        else:
            plt.show()


def create_standard_training_config() -> Dict:
    """Create standard MAPPO training configuration (no reward shaping)"""
    return {
        # Environment parameters
        'num_players': 20,
        'num_mappo_agents': 20,
        'env_type': 'smallworld',
        'k_neighbours': 4,
        'rewire_prob': 0.1,
        'reward_matrix': [
            [3.0, 0.0],  # Cooperate vs [Cooperate, Defect]
            [5.0, 1.0]   # Defect vs [Cooperate, Defect]
        ],
        
        # Training parameters
        'total_timesteps': 2000,  # Increased for proper learning
        'rollout_length': 100,      # Reasonable rollout length
        'num_epochs': 4,           # Reduced to prevent overfitting
        'batch_size': 32,          # Smaller batch size for stability
        'save_interval': 2000,
        'eval_interval': 1000,
        
        # Additional training parameters
        'use_reward_shaping': True,  # Change according to needs
        'history_length': 5,
        'cooperation_bonus': 4.0,  # Reward shaping bonus for mutual cooperation
        'defection_penalty': 0.0,  # Penalty for cooperating with a defector
        
        # Agent parameters
        'lr_actor': 1e-3,
        'lr_critic': 5e-3,
        'gamma': 0.99,
        'gae_lambda': 0.95,
        'clip_epsilon': 0.2,
        'entropy_coef': 0.01,
        'value_coef': 0.5,
        'max_grad_norm': 0.5,
        
        # Learning rate annealing parameters
        'lr_annealing': True,
        'initial_lr_actor': 1e-3,
        'initial_lr_critic': 5e-3,
        'final_lr_actor': 1e-4,
        'final_lr_critic': 5e-4,
        
        # Save directory
        'save_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mappo_models_value_norm')
    }


if __name__ == "__main__":
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Create standard training configuration
    config = create_standard_training_config()
    
    # Initialize trainer
    trainer = ValueNormalizedMAPPOTrainer(config)
    
    # Start training
    trainer.train()
    
    logging.info("Value-Normalized MAPPO training completed successfully!")