import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import deque

class StandardObservationProcessor:
    """
    Enhanced observation processor for standard MAPPO training (no reward shaping)
    by including temporal information and better state representation
    """
    
    def __init__(self, num_players: int, max_neighbors: int = None, history_length: int = 5):
        self.num_players = num_players
        self.max_neighbors = max_neighbors or num_players - 1
        self.history_length = history_length
        
        # Store full game history for cooperation rate calculation
        self.move_history = {i: deque(maxlen=1000) for i in range(num_players)}  # Large enough for full game
        self.reward_history = {i: deque(maxlen=1) for i in range(num_players)}  # Only previous round for rewards
        
        # Observation dimensions
        self.local_obs_dim = self._calculate_local_obs_dim()
        self.global_state_dim = self._calculate_global_state_dim()
        
        logging.info(f"StandardObservationProcessor initialized:")
        logging.info(f"  Local obs dim: {self.local_obs_dim}")
        logging.info(f"  Global state dim: {self.global_state_dim}")
        logging.info(f"  History length: Full game for cooperation rates, previous round for rewards")
    
    def _calculate_local_obs_dim(self) -> int:
        """
        Standardized 4-dimensional observation space for all agents:
        - Own previous action (1)
        - Average neighbor action (1)
        - Neighbor cooperation rate (1)
        - Number of neighbors (1)
        """
        return 4
    
    def _calculate_global_state_dim(self) -> int:
        """
        Enhanced global state space including:
        - All player cooperation rates (num_players)
        - Global cooperation rate (1)
        - Round number (normalized) (1)
        """
        return self.num_players + 2
    
    def update_history(self, all_moves: np.ndarray, all_rewards: np.ndarray):
        """Update move and reward history for all players"""
        for player_id in range(self.num_players):
            self.move_history[player_id].append(all_moves[player_id])
            self.reward_history[player_id].append(all_rewards[player_id])
    
    def reset_history(self):
        """Reset all history (for new episodes)"""
        for player_id in range(self.num_players):
            self.move_history[player_id].clear()
            self.reward_history[player_id].clear()
    
    def _get_cooperation_rate(self, moves: deque) -> float:
        """Calculate cooperation rate from move history"""
        if not moves:
            return 0.5  # Neutral prior
        return sum(1 for move in moves if move == 0) / len(moves)
    
    def process_local_observations(self, player_id: int, network: np.ndarray, 
                                 mappo_agent_ids: List[int]) -> np.ndarray:
        """
        Process standardized 4-dimensional local observations for a single agent
        """
        local_obs = []
        
        # Get neighbors
        neighbors = np.where(network[player_id] == 1)[0]
        
        # 1. Own previous action (from last round only)
        if len(self.move_history[player_id]) > 0:
            own_prev_action = self.move_history[player_id][-1]  # Last action only
        else:
            own_prev_action = 0.5  # Neutral prior if no history
        local_obs.append(own_prev_action)
        
        # 2. Average neighbor action (from last round only)
        if len(neighbors) > 0:
            neighbor_actions = []
            for neighbor_id in neighbors:
                if len(self.move_history[neighbor_id]) > 0:
                    neighbor_actions.append(self.move_history[neighbor_id][-1])  # Last action only
            
            if neighbor_actions:
                avg_neighbor_action = np.mean(neighbor_actions)
                local_obs.append(avg_neighbor_action)
            else:
                local_obs.append(0.5)  # Neutral prior if no valid neighbors
        else:
            local_obs.append(0.5)  # Neutral prior if no neighbors
        
        # 3. Neighbor cooperation rate (across whole game history)
        if len(neighbors) > 0:
            neighbor_coop_rates = []
            for neighbor_id in neighbors:
                if len(self.move_history[neighbor_id]) > 0:
                    # Calculate cooperation rate across entire game history
                    coop_rate = sum(1 for move in self.move_history[neighbor_id] if move == 0) / len(self.move_history[neighbor_id])
                    neighbor_coop_rates.append(coop_rate)
            
            if neighbor_coop_rates:
                avg_neighbor_coop_rate = np.mean(neighbor_coop_rates)
                local_obs.append(avg_neighbor_coop_rate)
            else:
                local_obs.append(0.5)  # Neutral prior if no valid neighbors
        else:
            local_obs.append(0.5)  # Neutral prior if no neighbors
        
        # 4. Number of neighbors (normalized)
        local_obs.append(len(neighbors) / self.max_neighbors)
        
        return np.array(local_obs, dtype=np.float32)
    
    def process_all_local_observations(self, network: np.ndarray, 
                                     mappo_agent_ids: List[int]) -> np.ndarray:
        """Process local observations for all MAPPO agents"""
        local_obs_batch = []
        
        for agent_id in mappo_agent_ids:
            local_obs = self.process_local_observations(agent_id, network, mappo_agent_ids)
            local_obs_batch.append(local_obs)
        
        return np.array(local_obs_batch)
    
    def process_global_state(self, network: np.ndarray, 
                           player_assignments: Dict[int, str],
                           round_number: int = 0) -> np.ndarray:
        """Process enhanced global state for centralized training"""
        global_state = []
        
        # 1. All player cooperation rates
        for player_id in range(self.num_players):
            coop_rate = self._get_cooperation_rate(self.move_history[player_id])
            global_state.append(coop_rate)
        
        # 2. Global cooperation rate
        all_coop_rates = [self._get_cooperation_rate(self.move_history[i]) 
                         for i in range(self.num_players)]
        global_coop_rate = np.mean(all_coop_rates)
        global_state.append(global_coop_rate)
        
        # 3. Round number (normalized)
        normalized_round = min(round_number / 1000.0, 1.0)  # Normalize to [0, 1]
        global_state.append(normalized_round)
        
        return np.array(global_state, dtype=np.float32)

    def update_reward_shaping(self, cooperation_bonus: float = 0.0, 
                             mutual_cooperation_bonus: float = 3.0,
                             reciprocity_bonus: float = 1.0):
        """Update reward shaping parameters dynamically"""
        if self.reward_shaper:
            self.reward_shaper.cooperation_bonus = cooperation_bonus
            self.reward_shaper.mutual_cooperation_bonus = mutual_cooperation_bonus
            self.reward_shaper.reciprocity_bonus = reciprocity_bonus


class StandardRewardShaper:
    """
    Reward shaping for standard MAPPO (all bonuses set to 0)
    """
    
    def __init__(self, base_reward_matrix: np.ndarray, 
                 cooperation_bonus: float = 0.5,
                 mutual_cooperation_bonus: float = 1.0,
                 reciprocity_bonus: float = 0.3):
        
        self.base_reward_matrix = base_reward_matrix
        self.cooperation_bonus = cooperation_bonus
        self.mutual_cooperation_bonus = mutual_cooperation_bonus
        self.reciprocity_bonus = reciprocity_bonus
        
        logging.info(f"StandardRewardShaper initialized (all bonuses set to 0):")
        logging.info(f"  Cooperation bonus: {cooperation_bonus}")
        logging.info(f"  Mutual cooperation bonus: {mutual_cooperation_bonus}")
        logging.info(f"  Reciprocity bonus: {reciprocity_bonus}")
    
    def shape_reward(self, player_id: int, own_move: int, neighbor_moves: Dict[int, int],
                    base_reward: float, obs_processor: StandardObservationProcessor) -> float:
        """
        Apply reward shaping to encourage mutual cooperation
        
        Args:
            player_id: ID of the player
            own_move: Player's move (0=cooperate, 1=defect)
            neighbor_moves: Dictionary of neighbor moves
            base_reward: Original reward from the game
            obs_processor: Observation processor for history access
            
        Returns:
            Shaped reward
        """
        shaped_reward = base_reward
        
        if not neighbor_moves:
            return shaped_reward
        
        # 1. Mutual cooperation bonus - extra reward when both cooperate
        # This encourages strategic cooperation, not blind cooperation
        mutual_cooperations = sum(1 for neighbor_move in neighbor_moves.values() 
                                if own_move == 0 and neighbor_move == 0)
        if mutual_cooperations > 0:
            # Strong bonus for mutual cooperation
            shaped_reward += self.mutual_cooperation_bonus * mutual_cooperations / len(neighbor_moves)
        
        # 2. Reciprocity bonus - reward for matching neighbor's historical behavior
        # This encourages tit-for-tat like strategies
        if len(obs_processor.move_history[player_id]) > 0:
            reciprocity_score = 0
            for neighbor_id in neighbor_moves.keys():
                if len(obs_processor.move_history[neighbor_id]) > 0:
                    # Check if player's current move matches neighbor's previous move
                    neighbor_last_move = obs_processor.move_history[neighbor_id][-1]
                    if own_move == neighbor_last_move:
                        reciprocity_score += 1
            
            if reciprocity_score > 0:
                shaped_reward += self.reciprocity_bonus * reciprocity_score / len(neighbor_moves)
        
        return shaped_reward
    
    def get_long_term_reward_estimate(self, cooperation_rate: float) -> float:
        """
        Estimate long-term reward based on cooperation rate
        This can be used for additional reward shaping
        """
        # Mutual cooperation gives 3.0, mutual defection gives 1.0
        # Linear interpolation based on cooperation rate
        return 1.0 + 2.0 * cooperation_rate


class StandardEnvironmentWrapper:
    """
    Enhanced environment wrapper for standard MAPPO training (no reward shaping)
    """
    
    def __init__(self, num_players: int, network: np.ndarray, 
                 player_assignments: Dict[int, str], reward_matrix: np.ndarray,
                 mappo_agent_ids: List[int], history_length: int = 5,
                 use_reward_shaping: bool = False):
        
        self.num_players = num_players
        self.network = network
        self.player_assignments = player_assignments
        self.reward_matrix = reward_matrix
        self.mappo_agent_ids = mappo_agent_ids
        self.num_mappo_agents = len(mappo_agent_ids)
        self.use_reward_shaping = use_reward_shaping

        
        # Initialize enhanced observation processor
        self.obs_processor = StandardObservationProcessor(
            num_players, history_length=history_length
        )
        
        # Initialize reward shaper if enabled (but with 0 bonus)
        self.reward_shaper = None
        if use_reward_shaping:
            # Even if enabled, set all bonuses to 0 for standard MAPPO
            self.reward_shaper = StandardRewardShaper(
                base_reward_matrix=reward_matrix,
                cooperation_bonus=0.0,        # No blind cooperation bonus
                mutual_cooperation_bonus=0.0, # No mutual cooperation bonus
                reciprocity_bonus=0.0         # No reciprocity bonus
            )
        

        
        # Track previous moves for proper simulate_round calls
        self.previous_moves = None
        
        # State tracking
        self.round_number = 0
        
        logging.info(f"StandardEnvironmentWrapper initialized:")
        logging.info(f"  Total players: {num_players}")
        logging.info(f"  MAPPO agents: {mappo_agent_ids}")
        logging.info(f"  Reward shaping: {use_reward_shaping} (all bonuses set to 0)")

    
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
        
        self.round_number += 1
        
        # Get next observations
        next_local_obs = self.obs_processor.process_all_local_observations(
            self.network, self.mappo_agent_ids
        )
        
        next_global_state = self.obs_processor.process_global_state(
            self.network, self.player_assignments, self.round_number
        )
        
        # Episode termination
        dones = np.zeros(self.num_mappo_agents, dtype=bool)
        episode_done = False
        
        # Return shaped rewards if available, otherwise base rewards
        if self.reward_shaper:
            return next_local_obs, next_global_state, shaped_rewards, dones, episode_done
        else:
            return next_local_obs, next_global_state, mappo_rewards, dones, episode_done
    
    def get_shaped_rewards(self) -> np.ndarray:
        """Get shaped rewards for learning (not for logging)"""
        return self.shaped_rewards if hasattr(self, 'shaped_rewards') else None
    
    def _get_neighbor_moves_dict(self, player_id: int, all_moves: np.ndarray) -> Dict[int, int]:
        """Get neighbor moves as dictionary"""
        neighbors = np.where(self.network[player_id] == 1)[0]
        return {neighbor_id: all_moves[neighbor_id] for neighbor_id in neighbors}
    
    def _calculate_base_reward(self, own_move: int, neighbor_moves: Dict[int, int]) -> float:
        """Calculate base reward without shaping"""
        if not neighbor_moves:
            return 0.0
        
        total_reward = 0.0
        for neighbor_move in neighbor_moves.values():
            total_reward += self.reward_matrix[own_move][neighbor_move]
        
        return total_reward / len(neighbor_moves)
    
    def get_observation_dims(self) -> Tuple[int, int]:
        """Get observation dimensions"""
        return self.obs_processor.local_obs_dim, self.obs_processor.global_state_dim
    
    def get_cooperation_statistics(self) -> Dict[str, float]:
        """Get current cooperation statistics"""
        stats = {}
        
        for agent_id in self.mappo_agent_ids:
            coop_rate = self.obs_processor._get_cooperation_rate(
                self.obs_processor.move_history[agent_id]
            )
            stats[f'agent_{agent_id}_cooperation_rate'] = coop_rate
        
        # Overall MAPPO cooperation rate
        mappo_coop_rates = [stats[f'agent_{agent_id}_cooperation_rate'] 
                           for agent_id in self.mappo_agent_ids]
        stats['mappo_cooperation_rate'] = np.mean(mappo_coop_rates)
        
        return stats