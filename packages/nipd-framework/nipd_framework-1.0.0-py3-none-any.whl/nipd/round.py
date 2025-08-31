import numpy as np
import random

COOPERATE = 0
DEFECT = 1

PD_REWARD_MATRIX = np.array([
    [3.0, 0.0],  # move = COOPERATE (0)
    [5.0, 1.0]   # move = DEFECT (1)
])

def _get_initial_move(player_type: str) -> int:
    """
    Determines a player's initial move for a round if no previous move exists.

    Args:
        player_type (str): The type/strategy of the player.

    Returns:
        int: The initial move (COOPERATE or DEFECT).
    """
    nice_strats = ['cooperate', 'titfortat']

    if player_type in nice_strats:
        return COOPERATE
    elif player_type == 'random':
        return random.choice([COOPERATE, DEFECT])
    else:
        return DEFECT

def _gather_observations(player_id: int, network: np.ndarray, all_players_last_moves: np.ndarray) -> dict:
    """
    Gathers observations (moves) for a given player from their connected neighbors.
    This is where you'd implement specific observation rules (e.g., observe all neighbors,
    observe only a subset, observe with noise, etc.).

    Args:
        player_id (int): The ID of the player for whom to gather observations.
        network (np.ndarray): The adjacency matrix representing connections.
        all_players_last_moves (np.ndarray): An array where all_players_last_moves[i] is the move
                                            made by player i in the previous round.

    Returns:
        dict: A dictionary of observations, e.g., {neighbor_id: neighbor_move}.
    """
    observations = {}
    num_players = network.shape[0]

    for neighbor_id in range(num_players):
        # Check if there's a connection between player_id and neighbor_id
        if network[player_id, neighbor_id] == 1:
            # If connected, observe the neighbor's move from the previous round
            observations[neighbor_id] = all_players_last_moves[neighbor_id]
            
    return observations

def _calculate_player_move(player_type: str, observations: dict, own_last_move: int) -> int:
    """
    Calculates the next move for a player based on their type/strategy and observations.

    Args:
        player_type (str): The type of the player (e.g., 'cooperator', 'defector', 'tit-for-tat').
        observations (dict): Observations gathered from neighbors {neighbor_id: neighbor_move}.
        own_last_move (int): The player's own move in the previous round.

    Returns:
        int: The calculated move (COOPERATE or DEFECT).
    """

    if player_type == 'cooperator':
        return COOPERATE
    elif player_type == 'defector':
        return DEFECT
    elif player_type == 'titfortat':
        if observations: 
            observed_moves_values = list(observations.values())
            mean_observed_move = np.mean(observed_moves_values)
            return round(mean_observed_move)
        else: return COOPERATE
    elif player_type == 'random':
        return random.choice([COOPERATE, DEFECT])
    elif player_type == 'mappo':
        # For MAPPO agents, use a default cooperative strategy initially
        # The actual moves will be overridden by the environment wrapper
        return COOPERATE

def _calculate_reward(own_move: int, neighbor_moves: dict, reward_matrix: np.ndarray) -> float:
    """
    Calculates the total reward for a player in the current round.

    Args:
        player_id (int): The ID of the player.
        own_move (int): The move made by the player in this round.
        neighbor_moves (dict): Moves made by neighbors in this round {neighbor_id: neighbor_move}.
        reward_matrix (np.ndarray): The reward matrix for the dilemma.
                                    Expected format: reward_matrix[my_move][opponent_move]

    Returns:
        float: The total reward for the player in this round.
    """
    total_reward = 0.0
    number_of_interactions = len(neighbor_moves)
    if not neighbor_moves:
        return 0.0

    for neighbor_move in neighbor_moves.values():
        reward_from_interaction = reward_matrix[own_move][neighbor_move]
        total_reward += reward_from_interaction
    
    average_reward = total_reward / number_of_interactions
    
    return average_reward

def simulate_round(num_players: int, network: np.ndarray, player_assignments: list[str],
                   reward_matrix: np.ndarray, all_players_last_moves: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
    """
    Simulates one round of the dilemma, including observation, move calculation, and reward.

    Args:
        num_players (int): Total number of players/nodes.
        network (np.ndarray): Adjacency matrix of the network.
        player_assignments (list[str]): List where player_assignments[i] is the type of player at node i.
        reward_matrix (np.ndarray): Reward matrix for the dilemma (e.g., standard PD matrix).
        all_players_last_moves (np.ndarray | None): Array of moves from the previous round (None if first round).
                                                     all_players_last_moves[i] is player i's last move.

    Returns:
        tuple: (current_moves, current_rewards)
            - current_moves (np.ndarray): Moves made by all players in this round.
            - current_rewards (np.ndarray): Rewards received by all players in this round.
    """

    current_moves = np.zeros(num_players, dtype=int)
    current_rewards = np.zeros(num_players, dtype=float)

    # Initialize all_players_last_moves if None (first round)
    if all_players_last_moves is None:
        all_players_last_moves = np.array([
            _get_initial_move(player_assignments[player_id])
            for player_id in range(num_players)
        ])

    # Phase 1: Players determine their move for the CURRENT round
    for player_id in range(num_players):
        player_type = player_assignments[player_id]

        # 1. Gather observations from connected neighbors (based on previous round's moves)
        observations = _gather_observations(player_id, network, all_players_last_moves)
        
        # 2. Calculate the player's move for the current round
        # Pass the player's own move from the previous round for strategy logic
        own_move = _calculate_player_move(player_type, observations, all_players_last_moves[player_id])
        current_moves[player_id] = own_move

    # Phase 2: Calculate rewards for all players based on CURRENT moves
    for player_id in range(num_players):
        own_move = current_moves[player_id]

        # Gather actual neighbors' moves for reward calculation (from current_moves)
        neighbor_moves_for_reward = _gather_observations(player_id, network, current_moves)

        # 3. Calculate the player's reward for the current round
        current_rewards[player_id] = _calculate_reward(own_move, neighbor_moves_for_reward, reward_matrix)
            
    return current_moves, current_rewards