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
    from .lola_environment import LOLANetworkGame, create_lola_config
except ImportError:
    # When run directly from the folder
    from lola_environment import LOLANetworkGame, create_lola_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LOLATrainer:
    """
    Trainer for LOLA agents in Network Iterated Prisoner's Dilemma
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Training parameters
        self.num_episodes = min(config['num_episodes'], 500)  # Standardized to match cooperative MAPPO
        self.episode_length = config['episode_length']
        self.eval_interval = config.get('eval_interval', 50)
        self.save_interval = config.get('save_interval', 100)
        
        # Learning rate annealing parameters
        self.lr_actor_start = config.get('lr_actor', 3e-4)
        self.lr_critic_start = config.get('lr_critic', 3e-4)
        self.lr_decay_rate = config.get('lr_decay_rate', 0.9999)
        
        # Initialize LOLA game
        self.game = LOLANetworkGame(config)
        
        # Training metrics - Enhanced logging
        self.training_metrics = defaultdict(list)
        
        # Detailed training metrics for comprehensive logging
        self.detailed_metrics = {
            'policy_losses': [],  # For LOLA policy losses
            'opponent_losses': [],
            'lola_correction_magnitudes': [],
            'cooperation_rates': [],
            'rewards': [],
            'episode_numbers': [],
            'shaped_rewards': [],
            'base_rewards': []
        }
        
        # Create save directory
        self.save_dir = config.get('save_dir', 'lola_models')
        os.makedirs(self.save_dir, exist_ok=True)
        
        logging.info("LOLA Trainer initialized successfully")
        logging.info(f"Training episodes: {self.num_episodes}")
        logging.info(f"Episode length: {self.episode_length}")
        logging.info(f"LOLA correction: {config.get('lola_correction', True)}")
        
        # Log initial hyperparameters
        logging.info(f"Learning rates - Actor: {self.lr_actor_start:.2e}, Critic: {self.lr_critic_start:.2e}")
        logging.info(f"Training parameters - Total episodes: {self.num_episodes}, Episode length: {self.episode_length}")
        logging.info(f"LOLA parameters - Correction strength: {config.get('lola_correction_strength', 1.0)}, Opponent modeling: {config.get('opponent_modeling', True)}")
        
    def _anneal_learning_rates(self, episode: int):
        """Anneal learning rates over time"""
        if hasattr(self.game, 'actor_optimizer'):
            new_lr_actor = self.lr_actor_start * (self.lr_decay_rate ** (episode / 100))
            for param_group in self.game.actor_optimizer.param_groups:
                param_group['lr'] = new_lr_actor
        
        if hasattr(self.game, 'critic_optimizer'):
            new_lr_critic = self.lr_critic_start * (self.lr_decay_rate ** (episode / 100))
            for param_group in self.game.critic_optimizer.param_groups:
                param_group['lr'] = new_lr_critic
    
    def _log_detailed_metrics(self, episode: int, metrics: Dict):
        """Log detailed training metrics for comprehensive analysis"""
        # Extract metrics from training episode
        if 'avg_policy_loss' in metrics:
            self.detailed_metrics['policy_losses'].append(metrics['avg_policy_loss'])
        if 'avg_opponent_loss' in metrics:
            self.detailed_metrics['opponent_losses'].append(metrics['avg_opponent_loss'])
        if 'avg_lola_correction_magnitude' in metrics:
            self.detailed_metrics['lola_correction_magnitudes'].append(metrics['avg_lola_correction_magnitude'])
        if 'episode_cooperation_rate' in metrics:
            self.detailed_metrics['cooperation_rates'].append(metrics['episode_cooperation_rate'])
        if 'episode_reward' in metrics:
            self.detailed_metrics['rewards'].append(metrics['episode_reward'])
        if 'avg_shaped_reward' in metrics:
            self.detailed_metrics['shaped_rewards'].append(metrics['avg_shaped_reward'])
        if 'avg_base_reward' in metrics:
            self.detailed_metrics['base_rewards'].append(metrics['avg_base_reward'])
        
        # Log training progress
        self.detailed_metrics['episode_numbers'].append(episode)
    
    def train(self):
        """Main training loop for LOLA agents"""
        logging.info("Starting LOLA training...")
        
        start_time = time.time()
        best_cooperation_rate = 0.0
        
        # Main training progress bar
        with tqdm(total=self.num_episodes, desc="LOLA Training Progress", ncols=100) as main_pbar:
            for episode in range(self.num_episodes):
                # Training episode
                metrics = self.game.train_episode(self.episode_length)
                
                # Anneal learning rates
                self._anneal_learning_rates(episode)
                
                # Update main progress bar
                main_pbar.set_postfix({
                    'Episode': f'{episode+1}/{self.num_episodes}',
                    'Coop': f'{metrics.get("episode_cooperation_rate", 0.0):.3f}',
                    'Reward': f'{metrics.get("episode_reward", 0.0):.3f}',
                    'Policy Loss': f'{metrics.get("avg_policy_loss", 0.0):.4f}'
                })
                main_pbar.update(1)
                
                # Store metrics
                for key, value in metrics.items():
                    self.training_metrics[key].append(value)
                
                # Log detailed metrics
                self._log_detailed_metrics(episode, metrics)
                
                # Periodic logging - Enhanced with detailed metrics
                if episode % 5 == 0:  # More frequent logging for shorter training
                    coop_rate = metrics.get('episode_cooperation_rate', 0.0)
                    reward = metrics.get('episode_reward', 0.0)
                    policy_loss = metrics.get('avg_policy_loss', 0.0)
                    opponent_loss = metrics.get('avg_opponent_loss', 0.0)
                    lola_correction = metrics.get('avg_lola_correction_magnitude', 0.0)
                
                logging.info(f"Episode {episode:4d}: "
                           f"Coop={coop_rate:.3f}, "
                           f"Reward={reward:.3f}, "
                           f"PolicyLoss={policy_loss:.4f}, "
                           f"OpponentLoss={opponent_loss:.4f}, "
                           f"LOLACorrection={lola_correction:.4f}")
                
                # Log additional detailed metrics
                if 'avg_value_loss' in metrics:
                    logging.info(f"  Value Loss: {metrics['avg_value_loss']:.4f}")
                if 'avg_entropy' in metrics:
                    logging.info(f"  Entropy: {metrics['avg_entropy']:.4f}")
                if 'avg_clip_fraction' in metrics:
                    logging.info(f"  Clip Fraction: {metrics['avg_clip_fraction']:.4f}")
                if 'avg_kl_divergence' in metrics:
                    logging.info(f"  KL Divergence: {metrics['avg_kl_divergence']:.4f}")
                
                # Log learning rates if available
                if hasattr(self.game, 'agents'):
                    for agent in self.game.agents:
                        if hasattr(agent, 'actor_optimizer'):
                            lr_actor = agent.actor_optimizer.param_groups[0]['lr']
                            logging.info(f"  Learning Rate (Actor): {lr_actor:.2e}")
                        if hasattr(agent, 'critic_optimizer'):
                            lr_critic = agent.critic_optimizer.param_groups[0]['lr']
                            logging.info(f"  Learning Rate (Critic): {lr_critic:.2e}")
                        break  # Just log from first agent for simplicity
            
            # Evaluation
            if episode % self.eval_interval == 0 and episode > 0:
                eval_metrics = self.game.evaluate(num_episodes=5)
                logging.info(f"Evaluation at episode {episode}:")
                for key, value in eval_metrics.items():
                    # Skip move_history to avoid cluttering terminal output
                    if key == 'move_history':
                        continue
                    if isinstance(value, (int, float)):
                        logging.info(f"  {key}: {value:.4f}")
                    else:
                        logging.info(f"  {key}: {value}")
                    # Only store numeric metrics in training_metrics
                    if isinstance(value, (int, float)):
                        self.training_metrics[key].append(value)
                
                # Save best model based on cooperation rate
                current_coop_rate = eval_metrics.get('eval_cooperation_rate', 0.0)
                if current_coop_rate > best_cooperation_rate:
                    best_cooperation_rate = current_coop_rate
                    best_model_dir = os.path.join(self.save_dir, 'best_lola_agents')
                    self.game.save_agents(best_model_dir)
                    logging.info(f"New best cooperation rate: {best_cooperation_rate:.4f}")
            
            # Save models
            if episode % self.save_interval == 0 and episode > 0:
                save_dir = os.path.join(self.save_dir, f'lola_agents_episode_{episode}')
                self.game.save_agents(save_dir)
                logging.info(f"Models saved at episode {episode}")
        
        # Final save
        final_save_dir = os.path.join(self.save_dir, 'final_lola_agents')
        self.game.save_agents(final_save_dir)
        
        total_time = time.time() - start_time
        logging.info(f"LOLA training completed in {total_time:.2f} seconds")
        logging.info(f"Best cooperation rate achieved: {best_cooperation_rate:.4f}")
        
        # Save training metrics
        self.save_training_metrics()
        
        # Plot comprehensive training curves
        plot_path = os.path.join(self.save_dir, 'lola_comprehensive_training_curves.png')
        self.plot_training_curves(save_path=plot_path)
    
    def save_training_metrics(self):
        """Save training metrics to file"""
        metrics_path = os.path.join(self.save_dir, 'lola_training_metrics.npz')
        np.savez(metrics_path, **self.training_metrics)
        logging.info(f"Training metrics saved to {metrics_path}")
        
        # Save detailed metrics separately
        detailed_metrics_path = os.path.join(self.save_dir, 'lola_detailed_metrics.npz')
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
        
        json_path = os.path.join(self.save_dir, 'lola_detailed_metrics.json')
        with open(json_path, 'w') as f:
            json.dump(json_metrics, f, indent=2)
        logging.info(f"Detailed metrics JSON saved to {json_path}")
    
    def plot_training_curves(self, save_path: Optional[str] = None):
        """Plot comprehensive training curves with detailed metrics"""
        # Create visualization with multiple subplots - 2x4 layout
        fig = plt.figure(figsize=(20, 10))
        
        # Training progress metrics
        ax1 = plt.subplot(2, 4, 1)
        if self.detailed_metrics['rewards']:
            ax1.plot(self.detailed_metrics['rewards'])
            ax1.set_title('Episode Rewards')
            ax1.set_xlabel('Training Step')
            ax1.set_ylabel('Reward')
            ax1.grid(True, alpha=0.3)
        
        ax2 = plt.subplot(2, 4, 2)
        if self.detailed_metrics['cooperation_rates']:
            ax2.plot(self.detailed_metrics['cooperation_rates'])
            ax2.set_title('Cooperation Rates')
            ax2.set_xlabel('Training Step')
            ax2.set_ylabel('Cooperation Rate')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
        
        # LOLA-specific loss metrics
        ax3 = plt.subplot(2, 4, 3)
        if self.detailed_metrics['policy_losses']:
            ax3.plot(self.detailed_metrics['policy_losses'], label='Policy Loss')
        if self.detailed_metrics['opponent_losses']:
            ax3.plot(self.detailed_metrics['opponent_losses'], label='Opponent Loss')
        ax3.set_title('LOLA Training Losses')
        ax3.set_xlabel('Training Step')
        ax3.set_ylabel('Loss')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # LOLA correction magnitudes
        ax4 = plt.subplot(2, 4, 4)
        if self.detailed_metrics['lola_correction_magnitudes']:
            ax4.plot(self.detailed_metrics['lola_correction_magnitudes'])
            ax4.set_title('LOLA Correction Magnitudes')
            ax4.set_xlabel('Training Step')
            ax4.set_ylabel('Correction Magnitude')
            ax4.grid(True, alpha=0.3)
        
        # Reward comparison (base vs shaped)
        ax5 = plt.subplot(2, 4, 5)
        if self.detailed_metrics['base_rewards'] and self.detailed_metrics['shaped_rewards']:
            ax5.plot(self.detailed_metrics['base_rewards'], label='Base Rewards', alpha=0.7)
            ax5.plot(self.detailed_metrics['shaped_rewards'], label='Shaped Rewards', alpha=0.7)
            ax5.set_title('Base vs Shaped Rewards')
            ax5.set_xlabel('Training Step')
            ax5.set_ylabel('Reward')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        
        # Cooperation rate distribution
        ax6 = plt.subplot(2, 4, 6)
        if self.detailed_metrics['cooperation_rates']:
            ax6.hist(self.detailed_metrics['cooperation_rates'], bins=20, alpha=0.7)
            ax6.set_title('Cooperation Rate Distribution')
            ax6.set_xlabel('Cooperation Rate')
            ax6.set_ylabel('Frequency')
            ax6.grid(True, alpha=0.3)
        
        # Reward distribution
        ax7 = plt.subplot(2, 4, 7)
        if self.detailed_metrics['rewards']:
            ax7.hist(self.detailed_metrics['rewards'], bins=20, alpha=0.7)
            ax7.set_title('Reward Distribution')
            ax7.set_xlabel('Reward')
            ax7.set_ylabel('Frequency')
            ax7.grid(True, alpha=0.3)
        
        # Empty subplot for consistency
        ax8 = plt.subplot(2, 4, 8)
        ax8.set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logging.info(f"LOLA comprehensive training curves saved to {save_path}")
        else:
            plt.show()
    
    def compare_with_without_lola(self):
        """
        Compare LOLA with and without opponent learning awareness
        """
        logging.info("Comparing LOLA with and without opponent learning awareness...")
        
        # Train without LOLA correction
        config_no_lola = self.config.copy()
        config_no_lola['lola_correction'] = False
        config_no_lola['num_episodes'] = min(200, self.num_episodes)  # Shorter for comparison
        
        game_no_lola = LOLANetworkGame(config_no_lola)
        
        no_lola_rewards = []
        no_lola_cooperation = []
        
        for episode in range(config_no_lola['num_episodes']):
            metrics = game_no_lola.train_episode(self.episode_length)
            no_lola_rewards.append(metrics.get('episode_reward', 0.0))
            no_lola_cooperation.append(metrics.get('episode_cooperation_rate', 0.0))
        
        # Train with LOLA correction
        config_with_lola = self.config.copy()
        config_with_lola['lola_correction'] = True
        config_with_lola['num_episodes'] = min(200, self.num_episodes)
        
        game_with_lola = LOLANetworkGame(config_with_lola)
        
        with_lola_rewards = []
        with_lola_cooperation = []
        
        for episode in range(config_with_lola['num_episodes']):
            metrics = game_with_lola.train_episode(self.episode_length)
            with_lola_rewards.append(metrics.get('episode_reward', 0.0))
            with_lola_cooperation.append(metrics.get('episode_cooperation_rate', 0.0))
        
        # Plot comparison
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        episodes = range(len(no_lola_rewards))
        
        # Rewards comparison
        ax1.plot(episodes, no_lola_rewards, label='Without LOLA', alpha=0.7)
        ax1.plot(episodes, with_lola_rewards, label='With LOLA', alpha=0.7)
        ax1.set_title('Reward Comparison')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Reward')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Cooperation comparison
        ax2.plot(episodes, no_lola_cooperation, label='Without LOLA', alpha=0.7)
        ax2.plot(episodes, with_lola_cooperation, label='With LOLA', alpha=0.7)
        ax2.set_title('Cooperation Rate Comparison')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Cooperation Rate')
        ax2.set_ylim(0, 1)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        comparison_path = os.path.join(self.save_dir, 'lola_comparison.png')
        plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
        logging.info(f"LOLA comparison plot saved to {comparison_path}")
        
        # Print summary statistics
        logging.info("\nComparison Results:")
        logging.info(f"Without LOLA - Final reward: {np.mean(no_lola_rewards[-10:]):.3f}, "
                    f"Final cooperation: {np.mean(no_lola_cooperation[-10:]):.3f}")
        logging.info(f"With LOLA - Final reward: {np.mean(with_lola_rewards[-10:]):.3f}, "
                    f"Final cooperation: {np.mean(with_lola_cooperation[-10:]):.3f}")
        
        return {
            'no_lola_final_reward': np.mean(no_lola_rewards[-10:]),
            'no_lola_final_cooperation': np.mean(no_lola_cooperation[-10:]),
            'with_lola_final_reward': np.mean(with_lola_rewards[-10:]),
            'with_lola_final_cooperation': np.mean(with_lola_cooperation[-10:])
        }


def main():
    """Main training function"""
    # Set random seeds
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Create LOLA configuration
    config = create_lola_config()
    
    # You can modify the config here for different experiments
    # config['num_episodes'] = 500  # Shorter training for testing
    # config['lola_correction'] = False  # Disable LOLA correction
    # config['num_lola_agents'] = 5  # Fewer LOLA agents
    
    # Initialize trainer
    trainer = LOLATrainer(config)
    
    # Start training
    trainer.train()
    
    # Plot training curves
    plot_path = os.path.join(config.get('save_dir', 'lola_models'), 'lola_training_curves.png')
    trainer.plot_training_curves(save_path=plot_path)
    
    # Compare with and without LOLA (optional)
    if config.get('run_comparison', False):
        trainer.compare_with_without_lola()
    
    logging.info("LOLA training completed successfully!")

if __name__ == "__main__":
    main()