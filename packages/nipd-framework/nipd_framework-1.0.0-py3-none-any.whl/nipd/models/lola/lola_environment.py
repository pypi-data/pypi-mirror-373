import numpy as np
import torch
import logging
import sys
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Flexible import system for both direct execution and package imports
try:
    from lola.lola_agent import MultiAgentLOLA
except ImportError:
    # Add current directory to path for direct execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from lola.lola_agent import MultiAgentLOLA
    except ImportError:
        # Try relative import
        from .lola_agent import MultiAgentLOLA

# Flexible import system for network_environment and round
try:
    from ...network_environment import initialise_network
    from ...round import simulate_round
except ImportError:
    # When run directly, add parent directories to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from network_environment import initialise_network
    from round import simulate_round

class LOLAEnvironmentWrapper:
    """
    Environment wrapper for LOLA agents in Network Iterated Prisoner's Dilemma
    """
    
    def __init__(self, num_players: int, network: np.ndarray,
                 player_assignments: Dict[int, str], reward_matrix: np.ndarray,
                 lola_agent_ids: List[int], history_length: int = 5):
        
        self.num_players = num_players
        self.network = network
        self.player_assignments = player_assignments
        self.reward_matrix = reward_matrix
        self.lola_agent_ids = lola_agent_ids
        self.num_lola_agents = len(lola_agent_ids)
        self.history_length = history_length
        
        # State tracking
        self.move_history = {i: [] for i in range(num_players)}
        self.reward_history = {i: [] for i in range(num_players)}
        self.round_number = 0
        
        # Calculate observation dimension
        self.obs_dim = self._calculate_obs_dim()
        
        logging.info(f"LOLA Environment initialized:")
        logging.info(f"  Total players: {num_players}")
        logging.info(f"  LOLA agents: {lola_agent_ids}")
        logging.info(f"  Observation dimension: {self.obs_dim}")
    
    def _calculate_obs_dim(self) -> int:
        """
        Calculate observation dimension for LOLA agents
        
        Observation includes:
        - Own previous action (1)
        - Average neighbor action (1)
        - Neighbor cooperation rate (1)
        - Number of neighbors (1)
        """
        return 4
    
    def reset(self) -> List[np.ndarray]:
        """
        Reset environment for new episode
        
        Returns:
            List of initial observations for LOLA agents
        """
        # Clear history
        self.move_history = {i: [] for i in range(self.num_players)}
        self.reward_history = {i: [] for i in range(self.num_players)}
        self.round_number = 0
        
        # Generate initial observations
        observations = []
        for agent_id in self.lola_agent_ids:
            obs = self._get_observation(agent_id)
            observations.append(obs)
        
        return observations
    
    def _get_observation(self, agent_id: int) -> np.ndarray:
        """
        Get standardized 4-dimensional observation for a specific LOLA agent
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Standardized 4-dimensional observation vector
        """
        # Get neighbors
        neighbors = np.where(self.network[agent_id] == 1)[0]
        num_neighbors = len(neighbors)
        
        # Create standardized 4-dimensional observation
        obs = np.zeros(4, dtype=np.float32)
        
        # Feature 0: Own previous action (0 = cooperate, 1 = defect)
        if self.move_history[agent_id]:
            obs[0] = float(self.move_history[agent_id][-1])
        else:
            obs[0] = 0.0  # Default to cooperate for first step
        
        # Feature 1: Average neighbor action (last round)
        if num_neighbors > 0 and self.move_history[agent_id]:
            neighbor_actions = []
            for neighbor in neighbors:
                if self.move_history[neighbor]:
                    neighbor_actions.append(float(self.move_history[neighbor][-1]))
            if neighbor_actions:
                obs[1] = float(np.mean(neighbor_actions))
            else:
                obs[1] = 0.5
        else:
            obs[1] = 0.5
        
        # Feature 2: Neighbor cooperation rate (across whole game history)
        if num_neighbors > 0:
            neighbor_coop_rates = []
            for neighbor_id in neighbors:
                if self.move_history[neighbor_id]:
                    # Calculate cooperation rate across entire game history
                    coop_rate = sum(1 for move in self.move_history[neighbor_id] if move == 0) / len(self.move_history[neighbor_id])
                else:
                    coop_rate = 0.5  # Neutral prior
                neighbor_coop_rates.append(coop_rate)
            obs[2] = float(np.mean(neighbor_coop_rates))
        else:
            obs[2] = 0.5
        
        # Feature 3: Number of neighbors (normalized)
        obs[3] = float(num_neighbors) / float(max(1, self.num_players - 1))
        
        return obs
    
    def step(self, lola_actions: List[int]) -> Tuple[List[np.ndarray], List[float], bool]:
        """
        Execute one step in the environment
        
        Args:
            lola_actions: Actions from LOLA agents
            
        Returns:
            Tuple of (next_observations, rewards, done)
        """
        # Initialize moves array
        all_moves = np.zeros(self.num_players, dtype=int)
        all_rewards = np.zeros(self.num_players, dtype=float)
        
        # Set LOLA agent moves first
        for i, agent_id in enumerate(self.lola_agent_ids):
            all_moves[agent_id] = lola_actions[i]
        
        # Get moves for fixed strategy players only
        fixed_player_assignments = {}
        for player_id in range(self.num_players):
            if player_id not in self.lola_agent_ids:
                fixed_player_assignments[player_id] = self.player_assignments[player_id]
        
        # Simulate moves for fixed strategy players
        if fixed_player_assignments:
            last_moves = None if self.round_number == 0 else self._get_last_moves()
            
            for player_id, player_type in fixed_player_assignments.items():
                # Get observations for this fixed strategy player
                if last_moves is not None:
                    observations = self._get_neighbor_moves(player_id, last_moves)
                    own_last_move = last_moves[player_id]
                else:
                    observations = {}
                    own_last_move = self._get_initial_move(player_type)
                
                # Calculate move for fixed strategy player
                move = self._calculate_player_move(player_type, observations, own_last_move)
                all_moves[player_id] = move
        
        # Calculate rewards for all players
        for player_id in range(self.num_players):
            neighbor_moves = self._get_neighbor_moves(player_id, all_moves)
            reward = self._calculate_reward(all_moves[player_id], neighbor_moves)
            all_rewards[player_id] = reward
        
        # Extract LOLA agent rewards
        lola_rewards = [all_rewards[agent_id] for agent_id in self.lola_agent_ids]
        
        # Update history
        for player_id in range(self.num_players):
            self.move_history[player_id].append(all_moves[player_id])
            self.reward_history[player_id].append(all_rewards[player_id])
        
        self.round_number += 1
        
        # Get next observations
        next_observations = []
        for agent_id in self.lola_agent_ids:
            obs = self._get_observation(agent_id)
            next_observations.append(obs)
        
        # Episode termination (can be customized)
        done = False  # Continuous episodes
        
        return next_observations, lola_rewards, done
    
    def _get_last_moves(self) -> np.ndarray:
        """Get last moves from all players"""
        last_moves = np.zeros(self.num_players, dtype=int)
        for player_id in range(self.num_players):
            if self.move_history[player_id]:
                last_moves[player_id] = self.move_history[player_id][-1]
        return last_moves
    
    def _get_neighbor_moves(self, player_id: int, all_moves: np.ndarray) -> Dict[int, int]:
        """Get neighbor moves as dictionary"""
        neighbors = np.where(self.network[player_id] == 1)[0]
        return {neighbor_id: all_moves[neighbor_id] for neighbor_id in neighbors}
    
    def _calculate_reward(self, own_move: int, neighbor_moves: Dict[int, int]) -> float:
        """Calculate reward for a single agent"""
        if not neighbor_moves:
            return 0.0
        
        total_reward = 0.0
        for neighbor_move in neighbor_moves.values():
            total_reward += self.reward_matrix[own_move][neighbor_move]
        
        return total_reward / len(neighbor_moves)
    
    def _get_initial_move(self, player_type: str) -> int:
        """Get initial move for a player type"""
        nice_strats = ['cooperator', 'titfortat']
        
        if player_type in nice_strats:
            return 0  # COOPERATE
        elif player_type == 'random':
            import random
            return random.choice([0, 1])
        else:
            return 1  # DEFECT
    
    def _calculate_player_move(self, player_type: str, observations: Dict[int, int], own_last_move: int) -> int:
        """Calculate move for a fixed strategy player"""
        if player_type == 'cooperator':
            return 0  # COOPERATE
        elif player_type == 'defector':
            return 1  # DEFECT
        elif player_type == 'titfortat':
            if observations:
                observed_moves_values = list(observations.values())
                mean_observed_move = np.mean(observed_moves_values)
                return round(mean_observed_move)
            else:
                return 0  # COOPERATE by default
        elif player_type == 'random':
            import random
            return random.choice([0, 1])
        else:
            return 0  # Default to cooperation

    def get_cooperation_statistics(self) -> Dict[str, float]:
        """Get cooperation statistics"""
        stats = {}
        
        for agent_id in self.lola_agent_ids:
            moves = self.move_history[agent_id]
            if moves:
                coop_rate = sum(1 for move in moves if move == 0) / len(moves)
                stats[f'agent_{agent_id}_cooperation_rate'] = coop_rate
        
        if stats:
            stats['lola_cooperation_rate'] = np.mean(list(stats.values()))
        
        return stats


class LOLANetworkGame:
    """
    Complete LOLA system for Network Iterated Prisoner's Dilemma
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Environment parameters
        self.num_players = config['num_players']
        self.env_type = config['env_type']
        self.k_neighbours = config['k_neighbours']
        self.rewire_prob = config.get('rewire_prob', 0.1)
        self.reward_matrix = np.array(config['reward_matrix'])
        
        # LOLA parameters
        self.num_lola_agents = config['num_lola_agents']
        self.lola_correction = config.get('lola_correction', True)
        self.history_length = config.get('history_length', 5)
        
        # Setup environment
        self._setup_environment()
        
        # Initialize LOLA agents
        self.lola_system = MultiAgentLOLA(
            num_agents=self.num_lola_agents,
            input_dim=self.env.obs_dim,
            lr_policy=config.get('lr_policy', 0.005),
            lr_opponent=config.get('lr_opponent', 0.01),
            gamma=config.get('gamma', 0.96),
            lola_correction=self.lola_correction
        )
        
        logging.info("LOLA Network Game initialized")
        logging.info(f"Environment: {self.num_players} players, {self.num_lola_agents} LOLA agents")
        logging.info(f"LOLA correction enabled: {self.lola_correction}")
    
    def _setup_environment(self):
        """Setup the LOLA environment"""
        # Create player assignments
        player_types = []
        lola_agent_ids = []
        
        # First num_lola_agents are LOLA agents
        for i in range(self.num_lola_agents):
            player_types.append('lola')
            lola_agent_ids.append(i)
        
        # Remaining players are fixed strategies
        remaining_players = self.num_players - self.num_lola_agents
        fixed_strategies = self.config.get('fixed_strategies', ['cooperator', 'defector', 'titfortat'])
        
        for i in range(remaining_players):
            strategy = fixed_strategies[i % len(fixed_strategies)]
            player_types.append(strategy)
        
        player_assignments = {i: player_types[i] for i in range(self.num_players)}
        
        # Initialize network
        network, _ = initialise_network(
            self.env_type,
            self.num_players,
            player_types,
            self.k_neighbours,
            self.rewire_prob
        )
        
        # Create environment wrapper
        self.env = LOLAEnvironmentWrapper(
            num_players=self.num_players,
            network=network,
            player_assignments=player_assignments,
            reward_matrix=self.reward_matrix,
            lola_agent_ids=lola_agent_ids,
            history_length=self.history_length
        )
        
        logging.info(f"LOLA environment setup complete")
        logging.info(f"Network type: {self.env_type}")
        logging.info(f"LOLA agents: {lola_agent_ids}")
        logging.info(f"Fixed strategies: {[player_assignments[i] for i in range(self.num_lola_agents, self.num_players)]}")
    
    def train_episode(self, episode_length: int = 100) -> Dict[str, float]:
        """
        Train LOLA agents for one episode
        
        Args:
            episode_length: Length of the episode
            
        Returns:
            Training metrics
        """
        # Reset environment
        observations = self.env.reset()
        
        # Initialize hidden states for all LOLA agents
        hidden_states = [agent.get_initial_hidden_states() for agent in self.lola_system.agents]
        
        # Storage for batch updates
        batch_states = [[] for _ in range(self.num_lola_agents)]
        batch_actions = [[] for _ in range(self.num_lola_agents)]
        batch_rewards = [[] for _ in range(self.num_lola_agents)]
        
        episode_rewards = []
        episode_cooperation_rates = []
        
        for step in range(episode_length):
            # Get actions from LOLA agents with hidden states
            actions, log_probs, new_hidden_states = self.lola_system.get_actions(observations, False, hidden_states)
            
            # Update hidden states
            hidden_states = new_hidden_states
            
            # Store states and actions
            for i in range(self.num_lola_agents):
                batch_states[i].append(observations[i])
                batch_actions[i].append(actions[i])
            
            # Take environment step
            next_observations, rewards, done = self.env.step(actions)
            
            # Store rewards
            for i in range(self.num_lola_agents):
                batch_rewards[i].append(rewards[i])
            
            # Track metrics
            step_reward = np.mean(rewards)
            step_cooperation = np.mean([1 - a for a in actions])  # 0 = cooperate
            episode_rewards.append(step_reward)
            episode_cooperation_rates.append(step_cooperation)
            
            # Update observations
            observations = next_observations
            
            if done:
                break
        
        # Create network neighbors mapping for LOLA agents
        network_neighbors = {}
        for i, lola_agent_id in enumerate(self.env.lola_agent_ids):
            # Get neighbors of this LOLA agent from the network
            neighbors = np.where(self.env.network[lola_agent_id] == 1)[0]
            # Map to LOLA agent indices (only include other LOLA agents)
            lola_neighbors = []
            for neighbor_id in neighbors:
                if neighbor_id in self.env.lola_agent_ids:
                    neighbor_lola_idx = self.env.lola_agent_ids.index(neighbor_id)
                    lola_neighbors.append(neighbor_lola_idx)
            network_neighbors[i] = lola_neighbors
        
        # Update LOLA agents with network-aware opponent modeling
        training_metrics = self.lola_system.update_all_agents(
            batch_states, batch_actions, batch_rewards, network_neighbors
        )
        
        # Add episode metrics
        training_metrics.update({
            'episode_reward': np.mean(episode_rewards),
            'episode_cooperation_rate': np.mean(episode_cooperation_rates),
            'final_cooperation_rate': episode_cooperation_rates[-1] if episode_cooperation_rates else 0.0
        })
        
        # Add environment cooperation statistics
        env_stats = self.env.get_cooperation_statistics()
        training_metrics.update(env_stats)
        
        return training_metrics
    
    def evaluate(self, num_episodes: int = 10, episode_length: int = 100) -> Dict[str, float]:
        """
        Evaluate LOLA agents
        
        Args:
            num_episodes: Number of evaluation episodes
            episode_length: Length of each episode
            
        Returns:
            Evaluation metrics
        """
        eval_rewards = []
        eval_cooperation_rates = []
        eval_mutual_cooperation_rates = []
        move_history = []  # Store moves for visualization
        
        for episode in range(num_episodes):
            observations = self.env.reset()
            episode_rewards = []  # Store rewards for each step
            episode_moves = []  # Store moves for each step
            episode_cooperations = 0
            episode_mutual_cooperations = 0
            
            for step in range(episode_length):
                # Get deterministic actions
                actions, _ = self.lola_system.get_actions(observations, deterministic=True)
                
                # Store moves for this step
                episode_moves.append(actions.copy())
                
                # Count cooperations
                cooperations = sum(1 - a for a in actions)  # 0 = cooperate
                episode_cooperations += cooperations
                
                # Count mutual cooperations
                if cooperations == self.num_lola_agents:
                    episode_mutual_cooperations += 1
                
                # Take step
                next_observations, rewards, done = self.env.step(actions)
                
                # Store the rewards for this step (rewards is already per-agent)
                episode_rewards.append(rewards)
                observations = next_observations
                
                if done:
                    break
            
            # Calculate the average reward per agent for this episode
            if episode_rewards:
                # episode_rewards is a list of arrays, each array contains rewards for all agents for that step
                # We want the average reward per agent across all steps
                episode_reward = np.mean([np.mean(step_rewards) for step_rewards in episode_rewards])
            else:
                episode_reward = 0.0
            
            eval_rewards.append(episode_reward)
            eval_cooperation_rates.append(episode_cooperations / (episode_length * self.num_lola_agents))
            eval_mutual_cooperation_rates.append(episode_mutual_cooperations / episode_length)
            
            # Store episode moves for visualization
            if episode_moves:
                # Convert to numpy array: (timesteps, agents)
                episode_moves_array = np.array(episode_moves)
                move_history.append(episode_moves_array)
        
        return {
            'eval_reward_mean': np.mean(eval_rewards),
            'eval_reward_std': np.std(eval_rewards),
            'eval_cooperation_rate': np.mean(eval_cooperation_rates),
            'eval_mutual_cooperation_rate': np.mean(eval_mutual_cooperation_rates),
            'move_history': move_history  # Add move history for visualization
        }
    
    def save_agents(self, directory: str):
        """Save LOLA agents"""
        self.lola_system.save_all_agents(directory)
    
    def load_agents(self, directory: str):
        """Load LOLA agents"""
        self.lola_system.load_all_agents(directory)


def create_lola_config() -> Dict:
    """Create default LOLA configuration"""
    return {
        # Environment parameters
        'num_players': 20,
        'num_lola_agents': 10,  # Half are LOLA agents
        'env_type': 'smallworld',
        'k_neighbours': 4,
        'rewire_prob': 0.1,
        'reward_matrix': [
            [3.0, 0.0],  # Cooperate vs [Cooperate, Defect]
            [5.0, 1.0]   # Defect vs [Cooperate, Defect]
        ],
        'fixed_strategies': ['titfortat'], #['cooperator', 'defector', 'titfortat', 'random'], #Compare learning vs different combinations of opponents
        
        # LOLA parameters - reduced learning rates for more stable learning
        'lola_correction': True,
        'history_length': 5,
        'lr_policy': 0.002,  # Reduced from 0.005 for more stable learning
        'lr_opponent': 0.006,  # Reduced from 0.01 for better opponent modeling
        'gamma': 0.96,
        
        # Training parameters
        'num_episodes': 500,  # Standardized to match cooperative MAPPO
        'episode_length': 100,  # Standardized to match cooperative MAPPO
        'eval_interval': 50,
        'save_interval': 100,
        'lr_decay_rate': 0.9999,  # Learning rate decay rate
        
        # Save directory - always save in the lola folder
        'save_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lola_models')
    }