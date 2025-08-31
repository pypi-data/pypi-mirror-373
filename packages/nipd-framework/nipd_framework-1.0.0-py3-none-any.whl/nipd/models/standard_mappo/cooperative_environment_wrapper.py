import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import deque

class CooperativeRewardShaper:
    """
    Reward shaper that promotes cooperative behavior:
    - Bonus for mutual cooperation
    - Penalty for cooperating with a defector
    """
    
    def __init__(self, base_reward_matrix: np.ndarray, 
                 mutual_cooperation_bonus: float = 0.5,
                 defection_penalty: float = -1.0):
        self.base_reward_matrix = base_reward_matrix
        self.mutual_cooperation_bonus = mutual_cooperation_bonus
        self.defection_penalty = defection_penalty
        
        logging.info(f"CooperativeRewardShaper initialized:")
        logging.info(f"  Mutual cooperation bonus: {mutual_cooperation_bonus}")
        logging.info(f"  Defection penalty: {defection_penalty}")
    
    def shape_reward(self, agent_id: int, agent_action: int, 
                    neighbor_moves: Dict[int, int], base_reward: float,
                    obs_processor) -> float:
        """
        Shape rewards to promote cooperative behavior
        
        Args:
            agent_id: ID of the agent
            agent_action: Action taken by the agent (0=cooperate, 1=defect)
            neighbor_moves: Dictionary of neighbor_id -> neighbor_action
            base_reward: Base reward from the game
            obs_processor: Observation processor for additional context
        
        Returns:
            Shaped reward
        """
        shaped_reward = base_reward
        
        # Only apply shaping if agent cooperated
        if agent_action == 0:  # Cooperate
            for neighbor_id, neighbor_action in neighbor_moves.items():
                if neighbor_action == 0:  # Neighbor also cooperated
                    # Mutual cooperation bonus
                    shaped_reward += self.mutual_cooperation_bonus
                else:  # Neighbor defected
                    # Penalty for cooperating with a defector
                    shaped_reward += self.defection_penalty
        
        return shaped_reward

class CooperativeEnvironmentWrapper:
    """
    Enhanced environment wrapper that promotes cooperative behavior with proper reward shaping
    """
    
    def __init__(self, num_players: int, network: np.ndarray, 
                 player_assignments: Dict[int, str], reward_matrix: np.ndarray,
                 mappo_agent_ids: List[int], history_length: int = 5,
                 use_reward_shaping: bool = True,
                 mutual_cooperation_bonus: float = 0.5,
                 defection_penalty: float = -1.0):
        
        self.num_players = num_players
        self.network = network
        self.player_assignments = player_assignments
        self.reward_matrix = reward_matrix
        self.mappo_agent_ids = mappo_agent_ids
        self.num_mappo_agents = len(mappo_agent_ids)
        self.use_reward_shaping = use_reward_shaping
        
        # Initialize enhanced observation processor (reuse StandardObservationProcessor)
        from standard_observation_processor import StandardObservationProcessor
        self.obs_processor = StandardObservationProcessor(
            num_players, history_length=history_length
        )
        
        # Initialize reward shaper if enabled
        self.reward_shaper = None
        if use_reward_shaping:
            self.reward_shaper = CooperativeRewardShaper(
                base_reward_matrix=reward_matrix,
                mutual_cooperation_bonus=mutual_cooperation_bonus,
                defection_penalty=defection_penalty
            )
        
        # Track previous moves for proper simulate_round calls
        self.previous_moves = None
        
        # State tracking
        self.round_number = 0
        
        logging.info(f"CooperativeEnvironmentWrapper initialized:")
        logging.info(f"  Total players: {num_players}")
        logging.info(f"  MAPPO agents: {mappo_agent_ids}")
        logging.info(f"  Reward shaping: {use_reward_shaping}")
        if use_reward_shaping:
            logging.info(f"  Mutual cooperation bonus: {mutual_cooperation_bonus}")
            logging.info(f"  Defection penalty: {defection_penalty}")
    
    def reset(self) -> Tuple[np.ndarray, np.ndarray]:
        """Reset environment for new episode"""
        self.obs_processor.reset_history()
        self.round_number = 0
        self.previous_moves = None  # Reset previous moves
        
        # Initial observations (empty history)
        local_obs = self.obs_processor.process_all_local_observations(
            self.network, self.mappo_agent_ids
        )
        
        global_state = self.obs_processor.process_global_state(
            self.network, self.player_assignments, self.round_number
        )
        
        return local_obs, global_state
    
    def step(self, mappo_actions: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, bool]:
        """Execute one step with enhanced reward shaping"""
        
        # Since all agents are MAPPO agents, we don't need to simulate non-MAPPO moves
        # Just use the MAPPO actions directly
        all_moves = np.zeros(self.num_players, dtype=int)
        for i, agent_id in enumerate(self.mappo_agent_ids):
            all_moves[agent_id] = mappo_actions[i]
        
        # Calculate rewards based on the MAPPO actions
        mappo_rewards = np.zeros(self.num_mappo_agents)
        shaped_rewards = np.zeros(self.num_mappo_agents)  # For learning signals only
        
        for i, agent_id in enumerate(self.mappo_agent_ids):
            neighbor_moves = self._get_neighbor_moves_dict(agent_id, all_moves)
            base_reward = self._calculate_base_reward(mappo_actions[i], neighbor_moves)
            
            # Store base reward (actual game reward following rules)
            mappo_rewards[i] = base_reward
            
            # Calculate shaped reward for learning signals only
            if self.reward_shaper:
                shaped_reward = self.reward_shaper.shape_reward(
                    agent_id, mappo_actions[i], neighbor_moves, 
                    base_reward, self.obs_processor
                )
                shaped_rewards[i] = shaped_reward
            else:
                shaped_rewards[i] = base_reward
        
        # Store shaped rewards for later access
        self.shaped_rewards = shaped_rewards.copy()
        
        # Update history with the BASE moves (not shaped rewards)
        self.obs_processor.update_history(all_moves, mappo_rewards)
        
        # Store current moves for next step (for neighbor observations)
        self.previous_moves = all_moves.copy()
        
        # Increment round number
        self.round_number += 1
        
        # Check if episode is done (simple termination condition)
        episode_done = self.round_number >= 100  # 100 rounds per episode
        
        # Get next observations
        next_local_obs = self.obs_processor.process_all_local_observations(
            self.network, self.mappo_agent_ids
        )
        
        next_global_state = self.obs_processor.process_global_state(
            self.network, self.player_assignments, self.round_number
        )
        
        # Create done flags for each agent
        dones = np.full(self.num_mappo_agents, episode_done, dtype=bool)
        
        return next_local_obs, next_global_state, mappo_rewards, dones, episode_done
    
    def _get_neighbor_moves_dict(self, agent_id: int, all_moves: np.ndarray) -> Dict[int, int]:
        """Get moves of all neighbors for an agent"""
        neighbors = np.where(self.network[agent_id] == 1)[0]
        neighbor_moves = {}
        for neighbor_id in neighbors:
            neighbor_moves[neighbor_id] = all_moves[neighbor_id]
        return neighbor_moves
    
    def _calculate_base_reward(self, agent_action: int, neighbor_moves: Dict[int, int]) -> float:
        """Calculate base reward based on game rules"""
        if not neighbor_moves:
            return 0.0
        
        total_reward = 0.0
        for neighbor_action in neighbor_moves.values():
            # Use the reward matrix: [agent_action][neighbor_action]
            reward = self.reward_matrix[agent_action][neighbor_action]
            total_reward += reward
        
        # Return average reward across neighbors
        return total_reward / len(neighbor_moves)
    
    def get_cooperation_statistics(self) -> Dict[str, float]:
        """Get cooperation statistics from the environment"""
        if not hasattr(self.obs_processor, 'move_history'):
            return {'cooperation_rate': 0.0, 'mutual_cooperation_rate': 0.0}
        
        # Calculate overall cooperation rate
        total_moves = 0
        total_cooperations = 0
        
        for player_id in range(self.num_players):
            moves = self.obs_processor.move_history[player_id]
            total_moves += len(moves)
            total_cooperations += sum(1 for move in moves if move == 0)
        
        cooperation_rate = total_cooperations / total_moves if total_moves > 0 else 0.0
        
        # Calculate mutual cooperation rate (simplified)
        mutual_cooperation_rate = cooperation_rate ** 2  # Approximation
        
        return {
            'cooperation_rate': cooperation_rate,
            'mutual_cooperation_rate': mutual_cooperation_rate
        }
    
    def get_observation_dims(self) -> Tuple[int, int]:
        """Get observation dimensions"""
        return self.obs_processor.local_obs_dim, self.obs_processor.global_state_dim



