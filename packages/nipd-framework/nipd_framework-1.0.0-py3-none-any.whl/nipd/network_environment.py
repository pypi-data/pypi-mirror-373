# Flexible import system - works both when run directly and when imported
try:
    # When imported from package
    from .network_tops import make_fc_net, make_ring_net, make_sw_net
    from .round import simulate_round
except ImportError:
    # When run directly
    from network_tops import make_fc_net, make_ring_net, make_sw_net
    from round import simulate_round
import numpy as np
import random

def initialise_network(env_type, num_players, player_types, k_neighbours, p_rewire=0.1):
    """Initialize network topology and player assignments for NIPD games.
    
    Args:
        env_type: Network type ('full', 'ring', 'smallworld')
        num_players: Number of players in the network
        player_types: List of player types for each node
        k_neighbours: Number of neighbors for ring/small-world networks
        p_rewire: Rewiring probability for small-world networks
        
    Returns:
        tuple: (network_matrix, player_assignments_dict)
    """
    network = None
    if env_type == 'full':
        network = make_fc_net(size=num_players)
    elif env_type == 'ring':
        network = make_ring_net(size=num_players, k_neighbours=k_neighbours)
    elif env_type == 'smallworld':
        network = make_sw_net(size=num_players, k_neighbours=k_neighbours, p_rewire=p_rewire)
    else:
        raise ValueError(f"Env type must be one of: 'full', 'ring', 'smallworld'")

    player_assignments = {node_id: player_types[node_id] for node_id in range(num_players)}

    return network, player_assignments

if __name__ == "__main__":
    random.seed(99)
    NUM_PLAYERS = 20
    k_neighbours = 4
    player_types = ['cooperator', 'defector', 'random', 'titfortat']
    players = random.choices(player_types, k=NUM_PLAYERS)
    ENV_TYPE = 'smallworld'
    MAX_ROUNDS = 100
    REWIRE_PROB = 0.3
    PD_REWARD_MATRIX = np.array([
    [3.0, 0.0],  # move = COOPERATE (0)
    [5.0, 1.0]   # move = DEFECT (1)
    ])

    network, player_assignments = initialise_network(ENV_TYPE, NUM_PLAYERS, players, k_neighbours)



    all_players_last_moves = None
    cumulative_scores = np.zeros(NUM_PLAYERS, dtype=float)
    for round_num in range(1, MAX_ROUNDS):
        current_round_moves, current_round_rewards = simulate_round(
                NUM_PLAYERS,
                network,
                player_assignments,
                PD_REWARD_MATRIX,
                all_players_last_moves
            )
        all_players_last_moves = current_round_moves
        cumulative_scores += current_round_rewards



    ranked_players = []
    for player_id in range(NUM_PLAYERS):
        player_score = cumulative_scores[player_id]
        player_label = player_assignments[player_id]
        ranked_players.append({'id': player_id, 'label': player_label, 'score': player_score})

    ranked_players.sort(key=lambda x: x['score'], reverse=True)

