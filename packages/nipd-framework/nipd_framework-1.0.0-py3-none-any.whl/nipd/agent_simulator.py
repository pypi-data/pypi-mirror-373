#!/usr/bin/env python3
"""
Flexible Agent Simulator for NIPD Framework

This script allows you to simulate different combinations of agents:
- Configure agent types and quantities
- Select network topology
- Run simulations and analyze results
- Visualize move patterns and scores

All configuration is hardcoded in the script because I dont like using CLI commands.
"""

import os
import logging
import numpy as np
import matplotlib
import sys
if 'ipykernel' not in sys.modules:
    matplotlib.use('Agg')  # Use non-interactive backend only when not in Jupyter
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import torch
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def flexible_import(module_path: str, class_name: str = None):
    """Helper function to handle flexible imports for both package and direct execution"""
    try:
        # When imported from package
        if class_name:
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        else:
            return __import__(module_path, fromlist=['*'])
    except ImportError:
        # When run directly, add the nipd directory to the path
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        
        if class_name:
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        else:
            return __import__(module_path, fromlist=['*'])

# =============================================================================
# SIMULATION CONFIGURATION - MODIFY THESE SETTINGS AS NEEDED
# =============================================================================

# Agent Configuration - specify how many of each type you want
AGENT_CONFIG = {
    'decentralized_ppo': 1,
    'standard_mappo': 1,
    'cooperative_mappo': 1,
    'lola': 1,
    'q_learner': 1,
    'titfortat': 1,
    'cooperator': 0,
    'defector': 0,
    # Online learning agents (initialized from pretrained models)
    'online_simple_q': 1,
    'online_q_network': 1,
    'online_decentralized_ppo': 1,
    'online_lola': 1,
    'online_mappo': 1,
    'online_simple_q': 1
}

# Network Configuration
NETWORK_CONFIG = {
    'type': 'small_world',        # Options: 'small_world', 'ring', 'full'
    'k_neighbors': 4,             # Number of neighbors per agent, must be < (num_agents - 1)
    'rewire_prob': 0.1            # Rewiring probability for small world
}

# Simulation Parameters
SIMULATION_CONFIG = {
    'episode_length': 250,        # Number of timesteps per episode
    'num_episodes': 1,           # Number of episodes to run
    'reward_matrix': [            # Prisoner's Dilemma reward matrix
        [3.0, 0.0],              # Cooperate vs [Cooperate, Defect]
        [5.0, 1.0]               # Defect vs [Cooperate, Defect]
    ],
    'use_system_rewards': False,      # True: use system-wide rewards, False: use private rewards
    'noise': {
        'enabled': True,              # Enable action noise in simulation
        'probability': 0.05,          # Probability of action flip per agent per timestep (0.0-1.0)
        'description': 'Random chance for agents to execute opposite action than intended'
    }
}

# =============================================================================
# END CONFIGURATION - DO NOT MODIFY BELOW THIS LINE
# =============================================================================

class AgentSimulator:
    """Main simulator class for running agent competitions"""
    
    def __init__(self, agent_config: Dict, network_config: Dict, sim_config: Dict):
        self.agent_config = agent_config
        self.network_config = network_config
        self.sim_config = sim_config
        
        # Calculate total population
        self.total_agents = sum(agent_config.values())
        self.agent_ids = self._assign_agent_ids()
        
        # Initialize network
        self.network = self._create_network()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f"zz_simulation_results_{timestamp}"
        os.makedirs(self.results_dir, exist_ok=True)
        logger.info(f"Results will be saved to: {self.results_dir}")
        
        # Results storage
        self.simulation_results = {
            'episode_scores': [],
            'episode_moves': [],
            'final_scores': {},
            'cooperation_rates': {},
            'move_history': [],
            'noise_data': [],        # Store noise information for visualization
            'leaderboard': []        # Store final rankings of agents
        }
        
        logger.info(f"Simulator initialized with {self.total_agents} agents")
        logger.info(f"Network: {network_config['type']} with {network_config['k_neighbors']} neighbors")
    
    def _assign_agent_ids(self) -> Dict[str, List[int]]:
        """Assign unique IDs to each agent type"""
        agent_ids = {}
        current_id = 0
        
        for agent_type, count in self.agent_config.items():
            agent_ids[agent_type] = list(range(current_id, current_id + count))
            current_id += count
        
        return agent_ids
    
    def _create_network(self) -> np.ndarray:
        """Create network topology based on configuration"""
        # Flexible import system - works both when run directly and when imported
        try:
            # When imported from package
            from .network_tops import make_sw_net, make_ring_net, make_fc_net
        except ImportError:
            # When run directly from the folder
            from network_tops import make_sw_net, make_ring_net, make_fc_net
        
        if self.network_config['type'] == 'small_world':
            network = make_sw_net(
                self.total_agents, 
                self.network_config['k_neighbors'], 
                self.network_config['rewire_prob']
            )
        elif self.network_config['type'] == 'ring':
            network = make_ring_net(self.total_agents, self.network_config['k_neighbors'])
        elif self.network_config['type'] == 'full':
            network = make_fc_net(self.total_agents)
        else:
            raise ValueError(f"Unknown network type: {self.network_config['type']}")
        
        # Verify network structure
        actual_neighbors = [np.sum(network[i]) for i in range(self.total_agents)]
        logger.info(f"Main network: {self.network_config['type']} topology with {self.network_config['k_neighbors']} target neighbors")
        logger.info(f"Actual network: {np.mean(actual_neighbors):.1f} avg neighbors (range: {np.min(actual_neighbors)}-{np.max(actual_neighbors)})")
        
        return network
    
    def _initialize_agents(self) -> Dict[int, 'BaseAgent']:
        """Initialize all agents based on configuration"""
        agents = {}
        
        # Initialize MAPPO, LOLA, and Q agents
        for agent_type in ['decentralized_ppo', 'standard_mappo', 'cooperative_mappo', 'lola', 'q_learner']:
            if agent_type in self.agent_config and self.agent_config[agent_type] > 0:
                agents.update(self._load_trained_agents(agent_type))
        
        # Initialize online learning agents
        for agent_type in ['online_simple_q', 'online_q_network', 'online_decentralized_ppo', 'online_lola', 'online_mappo']:
            if agent_type in self.agent_config and self.agent_config[agent_type] > 0:
                agents.update(self._load_online_agents(agent_type))
        
        # Initialize simple strategy agents
        for agent_type in ['titfortat', 'cooperator', 'defector']:
            if agent_type in self.agent_config and self.agent_config[agent_type] > 0:
                agents.update(self._create_simple_agents(agent_type))
        
        return agents
    
    def _load_trained_agents(self, agent_type: str) -> Dict[int, 'BaseAgent']:
        """Load pretrained agents of specified type"""
        agents = {}
        
        try:
            if agent_type == 'decentralized_ppo':
                # Use flexible import helper
                DecentralizedPPOTrainer = flexible_import('nipd.models.decentralized_ppo.decentralized_ppo_trainer', 'DecentralizedPPOTrainer')
                create_decentralized_training_config = flexible_import('nipd.models.decentralized_ppo.decentralized_ppo_trainer', 'create_decentralized_training_config')
                
                config = create_decentralized_training_config()
                config['num_agents'] = self.agent_config[agent_type]
                config['episode_length'] = self.sim_config['episode_length']
                
                # Handle single agent case - create a minimal network
                if config['num_agents'] == 1:
                    # For single agent, we'll create a dummy network and skip the trainer initialization
                    # since we only need to load the model
                    logger.info("Single decentralized PPO agent detected - creating minimal setup")
                    
                    # Create a dummy network (1x1 matrix with no connections)
                    dummy_network = np.zeros((1, 1), dtype=int)
                    
                    # Create a minimal trainer config for loading
                    minimal_config = config.copy()
                    minimal_config['k_neighbors'] = 0
                    minimal_config['network_type'] = 'full'  # Use full network type to avoid small world issues
                    
                    # Create temporary trainer to access agents
                    temp_trainer = DecentralizedPPOTrainer(minimal_config)
                else:
                    # Ensure k_neighbors is less than num_agents for network creation
                    original_k = config['k_neighbors']
                    if config['k_neighbors'] >= config['num_agents']:
                        config['k_neighbors'] = max(0, config['num_agents'] - 1)  # Allow 0 neighbors for single agent
                        logger.info(f"Adjusted decentralized PPO k_neighbors from {original_k} to {config['k_neighbors']} for {config['num_agents']} agents (temporary network for loading)")
                    
                    # Create temporary trainer to access agents
                    temp_trainer = DecentralizedPPOTrainer(config)
                
                # Load models
                models_dir = "nipd/models/decentralized_ppo/decentralized_ppo_models"
                if not os.path.exists(models_dir):
                    raise FileNotFoundError(f"Decentralized PPO models directory not found: {models_dir}")
                
                for i, agent_id in enumerate(self.agent_ids[agent_type]):
                    # Try final model first, then best model, then base model
                    model_path = os.path.join(models_dir, f"decentralized_ppo_agent_{i}_final.pt")
                    if not os.path.exists(model_path):
                        model_path = os.path.join(models_dir, f"decentralized_ppo_agent_{i}_best.pt")
                    if not os.path.exists(model_path):
                        model_path = os.path.join(models_dir, f"decentralized_ppo_agent_{i}.pt")
                    
                    if not os.path.exists(model_path):
                        raise FileNotFoundError(f"Model not found for {agent_type} agent {agent_id}: {model_path}")
                    
                    temp_trainer.agents[i].load(model_path)
                    # Wrap the agent to ensure consistent interface
                    agents[agent_id] = DecentralizedPPOAgentWrapper(temp_trainer.agents[i], agent_id)
                    logger.info(f"Loaded {agent_type} agent {agent_id} from {os.path.basename(model_path)}")
            
            elif agent_type == 'standard_mappo':

                import torch
                # Use flexible import helper
                StandardMAPPOAgent = flexible_import('nipd.models.standard_mappo.standard_mappo_agent', 'StandardMAPPOAgent')
                
                model_path = "nipd/models/standard_mappo/mappo_models_value_norm/value_norm_mappo_model_final.pt"
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Model not found for {agent_type}: {model_path}")
                
                try:
                    ckpt = torch.load(model_path, map_location='cpu', weights_only=False)
                    # Try to infer dims from checkpoint - handle different architectures
                    if 'actor_state_dict' in ckpt and 'critic_state_dict' in ckpt:
                        # Check for new architecture
                        if 'feature_net.0.weight' in ckpt['actor_state_dict']:
                            local_obs_dim = ckpt['actor_state_dict']['feature_net.0.weight'].shape[1]
                            global_state_dim = ckpt['critic_state_dict']['feature_net.0.weight'].shape[1]
                        elif 'network.0.weight' in ckpt['actor_state_dict']:
                            local_obs_dim = ckpt['actor_state_dict']['network.0.weight'].shape[1]
                            global_state_dim = ckpt['critic_state_dict']['network.0.weight'].shape[1]
                        else:
                            raise ValueError("Cannot infer dimensions from checkpoint")
                        
                        shared_agent = StandardMAPPOAgent(num_agents=self.agent_config[agent_type], local_obs_dim=local_obs_dim, global_state_dim=global_state_dim)
                        shared_agent.load(model_path)
                        logger.info(f"Loaded {agent_type} model with local_obs_dim={local_obs_dim}, global_state_dim={global_state_dim}")
                    else:
                        raise ValueError("Invalid checkpoint format")
                except Exception as e:
                    raise RuntimeError(f"Failed to load {agent_type} model: {e}")
                
                # Create wrappers for each requested agent id (share same underlying model)
                for agent_id in self.agent_ids[agent_type]:
                    agents[agent_id] = StandardMAPPOAgentWrapper(shared_agent, agent_id)
            
            elif agent_type == 'cooperative_mappo':

                import torch
                # Use flexible import helper
                StandardMAPPOAgent = flexible_import('nipd.models.standard_mappo.standard_mappo_agent', 'StandardMAPPOAgent')
                
                model_path = "nipd/models/standard_mappo/cooperative_mappo_models/min_reward_test_b0.625/cooperative_mappo_model_final.pt"
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Model not found for {agent_type}: {model_path}")
                
                try:
                    ckpt = torch.load(model_path, map_location='cpu', weights_only=False)
                    # Try to infer dims from checkpoint - handle different architectures
                    if 'actor_state_dict' in ckpt and 'critic_state_dict' in ckpt:
                        # Check for new architecture
                        if 'feature_net.0.weight' in ckpt['actor_state_dict']:
                            local_obs_dim = ckpt['actor_state_dict']['feature_net.0.weight'].shape[1]
                            global_state_dim = ckpt['critic_state_dict']['feature_net.0.weight'].shape[1]
                        elif 'network.0.weight' in ckpt['actor_state_dict']:
                            local_obs_dim = ckpt['actor_state_dict']['network.0.weight'].shape[1]
                            global_state_dim = ckpt['critic_state_dict']['network.0.weight'].shape[1]
                        else:
                            raise ValueError("Cannot infer dimensions from checkpoint")
                        
                        shared_agent = StandardMAPPOAgent(num_agents=self.agent_config[agent_type], local_obs_dim=local_obs_dim, global_state_dim=global_state_dim)
                        shared_agent.load(model_path)
                        logger.info(f"Loaded {agent_type} model with local_obs_dim={local_obs_dim}, global_state_dim={global_state_dim}")
                    else:
                        raise ValueError("Invalid checkpoint format")
                except Exception as e:
                    raise RuntimeError(f"Failed to load {agent_type} model: {e}")
                
                for agent_id in self.agent_ids[agent_type]:
                    agents[agent_id] = CooperativeMAPPOAgentWrapper(shared_agent, agent_id)
            
            elif agent_type == 'lola':
                # Load LOLA system directly; avoid environment wrapper
                import torch
                # Use flexible import helper
                MultiAgentLOLA = flexible_import('nipd.models.lola.lola_agent', 'MultiAgentLOLA')
                
                agents_dir = "nipd/models/lola/lola_models/final_lola_agents"
                
                if not os.path.exists(agents_dir):
                    raise FileNotFoundError(f"LOLA models directory not found: {agents_dir}")
                
                try:
                    # Infer input_dim from first agent checkpoint
                    first_path = os.path.join(agents_dir, 'lola_agent_0_final.pt')
                    if not os.path.exists(first_path):
                        first_path = os.path.join(agents_dir, 'lola_agent_0_best.pt')
                    if not os.path.exists(first_path):
                        first_path = os.path.join(agents_dir, 'lola_agent_0.pt')
                    
                    ckpt = torch.load(first_path, map_location='cpu', weights_only=False)
                    
                    # Handle different checkpoint architectures
                    if 'policy_net_state_dict' in ckpt:
                        if 'feature_net.0.weight' in ckpt['policy_net_state_dict']:
                            input_dim = ckpt['policy_net_state_dict']['feature_net.0.weight'].shape[1]
                        elif 'network.0.weight' in ckpt['policy_net_state_dict']:
                            input_dim = ckpt['policy_net_state_dict']['network.0.weight'].shape[1]
                        else:
                            raise ValueError("Cannot infer input_dim from LOLA checkpoint")
                    else:
                        raise ValueError("Invalid LOLA checkpoint format")
                    
                    lola_system = MultiAgentLOLA(num_agents=self.agent_config[agent_type], input_dim=input_dim)
                    lola_system.load_all_agents(agents_dir)
                    logger.info(f"Loaded LOLA agents from {agents_dir} with input_dim={input_dim}")
                except Exception as e:
                    raise RuntimeError(f"Failed to load LOLA agents: {e}")
                
                # Wrap each logical agent id mapped to a lola agent index in the system
                for idx, agent_id in enumerate(self.agent_ids[agent_type]):
                    agents[agent_id] = LOLAAgentWrapper(lola_system, agent_index=idx, agent_id=agent_id)
            
            elif agent_type == 'q_learner':
                # Load Simple Q-Learning agents
                # Use flexible import helper
                SimpleQLearningWrapper = flexible_import('nipd.models.simple_q_learning.simple_q_wrapper', 'SimpleQLearningWrapper')
                SimpleQLearningAgent = flexible_import('nipd.models.simple_q_learning.simple_q_agent', 'SimpleQLearningAgent')
                
                # Use final models directory
                models_dir = "nipd/models/simple_q_learning/simple_q_models"
                
                if os.path.exists(models_dir):
                    for i, agent_id in enumerate(self.agent_ids[agent_type]):
                        # Try final model first, then best model, then base model
                        model_path = os.path.join(models_dir, f"simple_q_agent_{i}_final.json")
                        if not os.path.exists(model_path):
                            model_path = os.path.join(models_dir, f"simple_q_agent_{i}_best.json")
                        if not os.path.exists(model_path):
                            model_path = os.path.join(models_dir, f"simple_q_agent_{i}.json")
                        
                        if os.path.exists(model_path):
                            try:
                                # Create Simple Q-Learning agent and load model
                                q_agent = SimpleQLearningAgent(agent_id=i, input_dim=4)
                                q_agent.load(model_path)
                                # Wrap the agent to ensure consistent interface
                                agents[agent_id] = SimpleQLearningWrapper(q_agent, agent_id)
                                logger.info(f"Loaded {agent_type} agent {agent_id} from {os.path.basename(models_dir)}")
                            except Exception as e:
                                raise RuntimeError(f"Failed to load {agent_type} agent {agent_id}: {e}")
                        else:
                            raise FileNotFoundError(f"Model not found for {agent_type} agent {agent_id}")
                else:
                    raise FileNotFoundError(f"Models directory not found for {agent_type}")
            
            return agents
        
        except Exception as e:
            raise RuntimeError(f"Failed to load agents for type {agent_type}: {e}")
    
    def _load_online_agents(self, agent_type: str) -> Dict[int, 'BaseAgent']:
        """Load online learning agents of specified type, initialized from pretrained models"""
        agents = {}
        
        try:
            if agent_type == 'online_simple_q':
                # Use flexible import helper
                OnlineSimpleQLearningAgent = flexible_import('nipd.models.online_simple_q_learning.online_simple_q_agent', 'OnlineSimpleQLearningAgent')
                
                for i, agent_id in enumerate(self.agent_ids[agent_type]):
                    agent = OnlineSimpleQLearningAgent(
                        agent_id=agent_id,
                        input_dim=4,
                        learning_rate=0.5,
                        epsilon=0.3
                    )
                    
                    # Load from pretrained Q-table model
                    pretrained_path = f"nipd/models/simple_q_learning/simple_q_models/simple_q_agent_{i % 10}_final.json"
                    if not os.path.exists(pretrained_path):
                        raise FileNotFoundError(f"Pretrained model not found for online simple Q agent {agent_id}: {pretrained_path}")
                    
                    try:
                        agent.load_model(pretrained_path)
                        logger.info(f"Loaded online simple Q agent {agent_id} from pretrained model: {pretrained_path}")
                    except Exception as e:
                        raise RuntimeError(f"Failed to load pretrained model for online simple Q agent {agent_id}: {e}")
                    
                    agents[agent_id] = OnlineAgentWrapper(agent, agent_id)
            
            elif agent_type == 'online_q_network':
                # Use flexible import helper
                OnlineQNetworkAgent = flexible_import('nipd.models.online_q_network.online_q_network_agent', 'OnlineQNetworkAgent')
                
                for i, agent_id in enumerate(self.agent_ids[agent_type]):
                    agent = OnlineQNetworkAgent(
                        agent_id=agent_id,
                        learning_rate=0.001,  # Increased from 1e-3 to 0.001
                        epsilon=0.3,         # Increased from 0.1 to 0.3
                        device='cpu'
                    )
                    
                    # Load from pretrained Q-network model
                    pretrained_path = f"nipd/models/q_network/q_network_models/q_network_models_final/q_network_agent_{i % 20}_final.pt"
                    if not os.path.exists(pretrained_path):
                        raise FileNotFoundError(f"Pretrained model not found for online Q-network agent {agent_id}: {pretrained_path}")
                    
                    try:
                        self._load_qnetwork_with_flexible_dimensions(agent, pretrained_path, agent_id)
                    except Exception as e:
                        raise RuntimeError(f"Failed to load pretrained model for online Q-network agent {agent_id}: {e}")
                    
                    agents[agent_id] = OnlineAgentWrapper(agent, agent_id)
            
            elif agent_type == 'online_decentralized_ppo':
                # Use flexible import helper
                OnlineDecentralizedPPOAgent = flexible_import('nipd.models.online_decentralized_ppo.online_decentralized_ppo_agent', 'OnlineDecentralizedPPOAgent')
                
                for i, agent_id in enumerate(self.agent_ids[agent_type]):
                    agent = OnlineDecentralizedPPOAgent(
                        agent_id=agent_id,
                        obs_dim=4,
                        lr_actor=0.001,     # Increased from 1e-4 to 0.001
                        lr_critic=0.003,    # Increased from 3e-4 to 0.003
                        clip_epsilon=0.2,   # Standard PPO clipping
                        gamma=0.99,         # Discount factor
                        gae_lambda=0.95,    # GAE parameter
                        device='cpu'
                    )
                    
                    # Load from pretrained decentralized PPO model
                    pretrained_path = f"nipd/models/decentralized_ppo/decentralized_ppo_models/decentralized_ppo_agent_{i % 10}_final.pt"
                    if not os.path.exists(pretrained_path):
                        raise FileNotFoundError(f"Pretrained model not found for online decentralized PPO agent {agent_id}: {pretrained_path}")
                    
                    self._load_ppo_with_flexible_dimensions(agent, pretrained_path, agent_id)
                    
                    agents[agent_id] = OnlineAgentWrapper(agent, agent_id)
            
            elif agent_type == 'online_lola':
                # Use flexible import helper
                OnlineLOLAAgent = flexible_import('nipd.models.online_lola.online_lola_agent', 'OnlineLOLAAgent')
                
                for i, agent_id in enumerate(self.agent_ids[agent_type]):
                    agent = OnlineLOLAAgent(
                        agent_id=agent_id,
                        input_dim=4,
                        lr=0.001,          # Increased from 1e-3 to 0.001
                        lola_lr=0.001,     # Increased LOLA-specific learning rate
                        gamma=0.99,        # Discount factor
                        device='cpu'
                    )
                    
                    # Load from pretrained LOLA model
                    pretrained_path = f"nipd/models/lola/lola_models/final_lola_agents/lola_agent_{i % 10}_final.pt"
                    if not os.path.exists(pretrained_path):
                        raise FileNotFoundError(f"Pretrained model not found for online LOLA agent {agent_id}: {pretrained_path}")
                    
                    self._load_ppo_with_flexible_dimensions(agent, pretrained_path, agent_id)
                    
                    agents[agent_id] = OnlineAgentWrapper(agent, agent_id)
            
            elif agent_type == 'online_mappo':
                # Use flexible import helper
                OnlineCooperativeMAPPOAgent = flexible_import('nipd.models.online_mappo.online_mappo_agent', 'OnlineCooperativeMAPPOAgent')

                for i, agent_id in enumerate(self.agent_ids[agent_type]):
                    # Use pretrained model's global state dimension if model exists, otherwise use current dimension
                    pretrained_path = f"nipd/models/standard_mappo/cooperative_mappo_models/min_reward_test_b0.625/cooperative_mappo_model_final.pt"
                    if os.path.exists(pretrained_path):
                        global_state_dim = 22  # Match pretrained model (20 agents + 2)
                    else:
                        global_state_dim = self.total_agents + 2  # Current configuration
                    
                    agent = OnlineCooperativeMAPPOAgent(
                        num_agents=self.total_agents,
                        local_obs_dim=4,
                        global_state_dim=global_state_dim,
                        lr_actor=0.001,      # Increased from 1e-4 to 0.001
                        lr_critic=0.003,     # Increased from 3e-4 to 0.003
                        gamma=0.99,          # Discount factor
                        clip_epsilon=0.2,    # PPO clipping parameter
                        device='cpu'
                    )
                    
                    # Load from pretrained MAPPO model
                    pretrained_path = f"nipd/models/standard_mappo/cooperative_mappo_models/min_reward_test_b0.625/cooperative_mappo_model_final.pt"
                    if not os.path.exists(pretrained_path):
                        raise FileNotFoundError(f"Pretrained model not found for online MAPPO agent {agent_id}: {pretrained_path}")
                    
                    try:
                        checkpoint = torch.load(pretrained_path, map_location='cpu', weights_only=False)
                        
                        # Load actor state
                        if hasattr(agent.actor, 'load_state_dict') and 'actor_state_dict' in checkpoint:
                            agent.actor.load_state_dict(checkpoint['actor_state_dict'], strict=False)
                            logger.info(f"Loaded online MAPPO agent {agent_id} actor from pretrained model: {pretrained_path}")
                        
                        # Load critic state
                        if hasattr(agent.critic, 'load_state_dict') and 'critic_state_dict' in checkpoint:
                            agent.critic.load_state_dict(checkpoint['critic_state_dict'])
                        logger.info(f"Loaded online MAPPO agent {agent_id} from pretrained model: {pretrained_path}")
                    except Exception as e:
                        raise RuntimeError(f"Failed to load pretrained model for online MAPPO agent {agent_id}: {e}")
                    
                    agents[agent_id] = OnlineAgentWrapper(agent, agent_id)
            
            return agents
        
        except Exception as e:
            raise RuntimeError(f"Failed to load online agents for type {agent_type}: {e}")
    
    def _create_simple_agents(self, agent_type: str) -> Dict[int, 'BaseAgent']:
        """Create simple strategy agents"""
        agents = {}
        
        for agent_id in self.agent_ids[agent_type]:
            if agent_type == 'titfortat':
                agents[agent_id] = TitForTatAgent(agent_id)
            elif agent_type == 'cooperator':
                agents[agent_id] = CooperatorAgent(agent_id)
            elif agent_type == 'defector':
                agents[agent_id] = DefectorAgent(agent_id)
        
        return agents
    
    def run_simulation(self):
        """Run the complete simulation"""
        logger.info("Starting simulation...")
        
        for episode in range(self.sim_config['num_episodes']):
            logger.info(f"Running episode {episode + 1}/{self.sim_config['num_episodes']}")
            
            episode_result = self._run_episode()
            self.simulation_results['episode_scores'].append(episode_result['scores'])
            self.simulation_results['episode_moves'].append(episode_result['moves'])
            self.simulation_results['move_history'].append(episode_result['moves'])
            self.simulation_results['noise_data'].append(episode_result['noise_data'])  # Store noise data
        
        # Calculate final statistics
        self._calculate_final_statistics()
        
        # Create leaderboard
        self._create_leaderboard()
        
        # Calculate decision matrices
        self._calculate_decision_matrices()
        
        # Export results to CSV files
        self._export_results_to_csv()
        
        # Create visualizations
        self.create_visualizations()
        
        logger.info("Simulation completed!")
    
    def _run_episode(self) -> Dict:
        """Run a single episode"""
        # Initialize episode
        episode_moves = np.zeros((self.sim_config['episode_length'], self.total_agents), dtype=np.int64)
        episode_scores = np.zeros((self.sim_config['episode_length'], self.total_agents))
        
        # Reset agent states
        for agent in self.agents.values():
            if hasattr(agent, 'reset'):
                agent.reset()
        
        # Initialize episode noise tracking
        self._episode_noise_data = []
        
        # Run episode steps
        for step in range(self.sim_config['episode_length']):
            # Get actions from all agents
            actions = np.zeros(self.total_agents, dtype=np.int64)
            
            for agent_id in range(self.total_agents):
                if agent_id in self.agents:
                    # Create observation for this agent
                    obs = self._create_observation(agent_id, step, episode_moves)
                    action = self.agents[agent_id].get_action(obs)
                    actions[agent_id] = action
                else:
                    actions[agent_id] = 0  # Default to cooperate
            
            # Store intended actions (before noise)
            episode_moves[step] = actions.copy()
            
            # Apply noise to actions (if enabled)
            actions, _ = self._apply_action_noise(actions)
            
            # Calculate rewards
            rewards = self._calculate_rewards(actions)
            episode_scores[step] = rewards
            
            # Update online learning agents with opponent information
            self._update_online_agents(step, episode_moves, rewards)
        
        return {
            'moves': episode_moves,
            'scores': episode_scores,
            'noise_data': getattr(self, '_episode_noise_data', [])
        }
    
    def _create_observation(self, agent_id: int, step: int, episode_moves: np.ndarray) -> np.ndarray:
        """Create standardized observation for all agents to ensure fairness"""
        # Create standardized 4-dimensional observation for all agents
        # This ensures all agents have access to the same information
        # Online agents only see historical information, not current opponent moves
        obs = np.zeros(4)
        
        # Get neighbor information
        neighbors = np.where(self.network[agent_id] == 1)[0]
        num_neighbors = len(neighbors)
        
        # Feature 0: Own previous action (0 = cooperate, 1 = defect)
        obs[0] = float(episode_moves[step - 1, agent_id]) if step > 0 else 0.0
        
        # Feature 1: Average neighbor action (last round)
        if num_neighbors > 0 and step > 0:
            obs[1] = float(np.mean(episode_moves[step - 1, neighbors]))
        else:
            obs[1] = 0.5
        
        # Feature 2: Neighbor cooperation rate
        if num_neighbors > 0 and step > 0:
            obs[2] = float(np.mean(episode_moves[step - 1, neighbors] == 0))
        else:
            obs[2] = 0.5
        
        # Feature 3: Number of neighbors (normalized)
        obs[3] = float(num_neighbors) / float(max(1, self.total_agents - 1))
        
        return obs

    def _calculate_rewards(self, actions: np.ndarray) -> np.ndarray:
        """Calculate rewards for all agents based on configuration"""
        if self.sim_config['use_system_rewards']:
            # System reward optimization: all agents get equal share of total system reward
            return self._calculate_system_shared_rewards(actions)
        else:
            # Private reward optimization: traditional individual rewards
            return self._calculate_individual_rewards(actions)

    def _calculate_individual_rewards(self, actions: np.ndarray) -> np.ndarray:
        """Calculate traditional individual rewards"""
        rewards = np.zeros(self.total_agents)

        for i in range(self.total_agents):
            neighbors = np.where(self.network[i] == 1)[0]

            if len(neighbors) == 0:
                rewards[i] = 0
                continue

            # Calculate reward based on own action and neighbor actions
            own_action = actions[i]
            neighbor_actions = actions[neighbors]

            total_reward = 0.0
            for neighbor_action in neighbor_actions:
                total_reward += self.sim_config['reward_matrix'][own_action][neighbor_action]

            # Average the reward across neighbors
            rewards[i] = total_reward / len(neighbors)

        return rewards

    def _calculate_system_shared_rewards(self, actions: np.ndarray) -> np.ndarray:
        """Calculate local system rewards where each agent optimizes for itself and its neighbors"""
        rewards = np.zeros(self.total_agents)

        for i in range(self.total_agents):
            neighbors = np.where(self.network[i] == 1)[0]

            if len(neighbors) == 0:
                rewards[i] = 0
                continue

            # Calculate local welfare: agent's own reward + neighbors' rewards from interactions with this agent
            local_welfare = 0.0
            
            # Agent's own reward from all its interactions
            for neighbor in neighbors:
                agent_payoff = self.sim_config['reward_matrix'][actions[i]][actions[neighbor]]
                local_welfare += agent_payoff
            
            # Neighbors' rewards from interactions with this agent
            for neighbor in neighbors:
                neighbor_payoff = self.sim_config['reward_matrix'][actions[neighbor]][actions[i]]
                local_welfare += neighbor_payoff

            # Agent gets the total local welfare (its own rewards + neighbors' rewards from interactions with it)
            # This encourages cooperation within the local neighborhood
            rewards[i] = local_welfare / (len(neighbors) + 1)  # Normalize by total number of agents in local system

        return rewards

    def _apply_action_noise(self, actions: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply noise to agent actions based on configuration"""
        noise_config = self.sim_config.get('noise', {})
        
        if not noise_config.get('enabled', False):
            # No noise applied
            return actions, np.zeros(len(actions), dtype=bool)
        
        noise_prob = noise_config.get('probability', 0.0)
        if noise_prob <= 0.0:
            return actions, np.zeros(len(actions), dtype=bool)
        
        # Generate noise mask - True where noise is applied
        noise_mask = np.random.random(len(actions)) < noise_prob
        
        # Apply noise by flipping actions where mask is True
        noisy_actions = actions.copy()
        noisy_actions[noise_mask] = 1 - noisy_actions[noise_mask]  # Flip 0->1, 1->0
        
        # Store noise data for this step (if episode tracking is active)
        if hasattr(self, '_episode_noise_data'):
            step_noise_data = {
                'intended_actions': actions.copy(),
                'actual_actions': noisy_actions.copy(),
                'noise_mask': noise_mask.copy()
            }
            self._episode_noise_data.append(step_noise_data)
        
        return noisy_actions, noise_mask
    
    def _create_universal_global_state(self, step: int, episode_moves: np.ndarray, target_dim: int) -> np.ndarray:
        """
        Create a universal global state that works with pretrained models regardless of current agent count.
        
        For a 20-agent pretrained model applied to a 10-agent environment:
        - Positions 0-9: Current agents' cooperation rates
        - Positions 10-19: Synthetic agents with averaged behavior (maintains distribution)
        - Position 20: Global cooperation rate
        - Position 21: Normalized round number
        
        This preserves the semantic structure the pretrained model expects.
        """
        # Calculate cooperation rates for actual agents
        actual_agent_rates = []
        for player_id in range(self.total_agents):
            if step > 0:
                player_moves = episode_moves[:step, player_id]
                cooperation_rate = np.mean(player_moves == 0)  # 0 = cooperate
            else:
                cooperation_rate = 0.5  # Neutral prior
            actual_agent_rates.append(cooperation_rate)
        
        # Global cooperation rate (same regardless of agent count)
        if step > 0:
            all_moves = episode_moves[:step, :]
            global_cooperation_rate = np.mean(all_moves == 0)
        else:
            global_cooperation_rate = 0.5
        
        # Round number (normalized by episode length)
        episode_length = episode_moves.shape[0]
        normalized_round = step / max(1, episode_length - 1)
        
        # Create the target-dimensional global state
        global_state = np.zeros(target_dim)
        
        if target_dim == 22:  # Standard 20-agent format
            # Place actual agent rates in first positions
            num_actual = min(self.total_agents, 20)
            global_state[:num_actual] = actual_agent_rates[:num_actual]
            
            # Fill remaining agent positions with copies of real agents
            if self.total_agents < 20:
                # Use actual agent data to fill synthetic positions - this preserves real behavioral patterns
                needed_agents = 20 - self.total_agents
                
                if self.total_agents > 0:
                    # Repeat the real agent cooperation rates to fill the remaining slots
                    # This creates "virtual" copies of real agents rather than fake data
                    repeated_agents = []
                    for i in range(needed_agents):
                        # Cycle through real agents to create copies
                        source_agent_idx = i % self.total_agents
                        repeated_agents.append(actual_agent_rates[source_agent_idx])
                    global_state[self.total_agents:20] = repeated_agents
                else:
                    # Fallback if no real agents (shouldn't happen in practice)
                    global_state[self.total_agents:20] = 0.5
            
            # Add global statistics
            global_state[20] = global_cooperation_rate
            global_state[21] = normalized_round
            
        else:
            # For other target dimensions, use original adaptive approach
            current_state = actual_agent_rates + [global_cooperation_rate, normalized_round]
            current_state = np.array(current_state)
            
            if len(current_state) < target_dim:
                # Pad with average cooperation rate
                avg_rate = np.mean(actual_agent_rates)
                padding = np.full(target_dim - len(current_state), avg_rate)
                global_state = np.concatenate([current_state, padding])
            elif len(current_state) > target_dim:
                # Truncate intelligently
                if target_dim >= 2:
                    agents_to_keep = target_dim - 2
                    global_state = np.concatenate([
                        current_state[:agents_to_keep],
                        current_state[-2:]
                    ])
                else:
                    global_state = current_state[:target_dim]
            else:
                global_state = current_state
        
        return global_state
    
    def _load_critic_with_flexible_dimensions(self, critic_network, critic_state_dict, agent_id):
        """
        Load critic state dict with flexible dimension handling.
        If dimensions don't match, we reinitialize the first layer to match current dimensions.
        """
        try:
            # Try loading normally first
            critic_network.load_state_dict(critic_state_dict, strict=True)
            logger.info(f"Loaded online MAPPO agent {agent_id} critic from pretrained model (exact match)")
        except RuntimeError as e:
            if "size mismatch" in str(e):
                logger.info(f"Dimension mismatch detected for agent {agent_id} critic, adapting...")
                
                # Load what we can
                current_state = critic_network.state_dict()
                loaded_keys = []
                
                for key, param in critic_state_dict.items():
                    if key in current_state:
                        if param.shape == current_state[key].shape:
                            current_state[key] = param
                            loaded_keys.append(key)
                        else:
                            logger.info(f"MISMATCH: {key} - pretrained: {param.shape} vs current: {current_state[key].shape}")

                
                # Load the compatible parameters
                critic_network.load_state_dict(current_state)
                logger.info(f"Loaded {len(loaded_keys)} compatible layers for agent {agent_id} critic")
                
                # Reinitialize first layer if it has dimension mismatch
                if hasattr(critic_network, 'feature_net') and hasattr(critic_network.feature_net, '0'):
                    first_layer = critic_network.feature_net[0]
                    if isinstance(first_layer, torch.nn.Linear):
                        torch.nn.init.orthogonal_(first_layer.weight, gain=1.0)
                        torch.nn.init.constant_(first_layer.bias, 0)
                        logger.info(f"Reinitialized first layer for agent {agent_id} critic")
            else:
                raise e
    
    def _load_qnetwork_with_flexible_dimensions(self, agent, pretrained_path, agent_id):
        """
        Load Q-network model with flexible dimension handling.
        Online agents should only load neural network weights, not training configuration.
        """
        try:
            checkpoint = torch.load(pretrained_path, map_location='cpu', weights_only=False)
            
            # Load compatible parts of the network
            current_state = agent.q_network.state_dict()
            loaded_keys = []
            total_keys = len(current_state)
            
            if 'q_network_state_dict' in checkpoint:
                pretrained_state = checkpoint['q_network_state_dict']
                for key, param in pretrained_state.items():
                    if key in current_state and param.shape == current_state[key].shape:
                        current_state[key] = param
                        loaded_keys.append(key)
                    else:
                        logger.debug(f"Skipping incompatible layer {key}: shape mismatch or missing")
            
            # Verify we loaded most of the network
            if len(loaded_keys) < total_keys * 0.8:  # At least 80% of layers should match
                logger.warning(f"Only loaded {len(loaded_keys)}/{total_keys} layers for Q-network agent {agent_id}")
            
            agent.q_network.load_state_dict(current_state)
            logger.info(f"Loaded {len(loaded_keys)}/{total_keys} compatible layers for Q-network agent {agent_id}")
            
            # Verify the network can do a forward pass
            test_input = torch.randn(1, 4)  # Standard 4D input
            with torch.no_grad():
                _ = agent.q_network(test_input)
            logger.info(f"Q-network agent {agent_id} forward pass test successful")
            
        except Exception as e:
            logger.error(f"Failed to load Q-network weights for agent {agent_id}: {e}")
            raise e
    
    def _load_ppo_with_flexible_dimensions(self, agent, pretrained_path, agent_id):
        """
        Load PPO agent (decentralized or LOLA) with flexible dimension handling.
        Only load neural network weights, not training configuration.
        """
        try:
            # Manually load PyTorch checkpoint
            checkpoint = torch.load(pretrained_path, map_location='cpu', weights_only=False)
            
            # Load LOLA agent components with correct key mapping
            if hasattr(agent, 'policy_network'):
                # This is a LOLA agent
                if 'policy_net_state_dict' in checkpoint:
                    agent.policy_network.load_state_dict(checkpoint['policy_net_state_dict'], strict=False)
                    logger.info(f"Loaded LOLA agent {agent_id} policy network from pretrained model")
                if 'opponent_model_state_dict' in checkpoint and hasattr(agent, 'opponent_model'):
                    agent.opponent_model.load_state_dict(checkpoint['opponent_model_state_dict'], strict=False)
                    logger.info(f"Loaded LOLA agent {agent_id} opponent model from pretrained model")
            else:
                # Load actor/critic for PPO agents
                if hasattr(agent, 'actor') and 'actor_state_dict' in checkpoint:
                    agent.actor.load_state_dict(checkpoint['actor_state_dict'], strict=False)
                    logger.info(f"Loaded agent {agent_id} actor from pretrained model")
                
                # Load critic  
                if hasattr(agent, 'critic') and 'critic_state_dict' in checkpoint:
                    agent.critic.load_state_dict(checkpoint['critic_state_dict'], strict=False)
                    logger.info(f"Loaded agent {agent_id} critic from pretrained model")
                    
        except Exception as e:
            raise RuntimeError(f"Failed to load pretrained model for agent {agent_id}: {e}")
    
    def _update_online_agents(self, step: int, episode_moves: np.ndarray, rewards: np.ndarray):
        """Update online learning agents with standard observation format"""
        for agent_id in range(self.total_agents):
            if agent_id in self.agents and hasattr(self.agents[agent_id], 'update'):
                # Use standard observation format - neighbor_prev already contains historical info
                obs = self._create_observation(agent_id, step, episode_moves)
                next_obs = self._create_observation(agent_id, step + 1, episode_moves) if step + 1 < episode_moves.shape[0] else obs

                # Handle MAPPO agent with special update signature
                if isinstance(self.agents[agent_id], OnlineAgentWrapper):
                    agent_type = type(self.agents[agent_id].online_agent).__name__
                    if agent_type == 'OnlineCooperativeMAPPOAgent':
                        # Create universal global state that works with pretrained models
                        target_global_dim = self.agents[agent_id].online_agent.global_state_dim
                        global_obs = self._create_universal_global_state(step, episode_moves, target_global_dim)
                        next_global_obs = self._create_universal_global_state(step + 1, episode_moves, target_global_dim) if step + 1 < episode_moves.shape[0] else global_obs

                        # Call MAPPO update directly on the wrapped agent
                        self.agents[agent_id].online_agent.update(
                            obs, global_obs, episode_moves[step, agent_id],
                            rewards[agent_id], next_obs, next_global_obs,
                            done=(step == episode_moves.shape[0] - 1)
                        )
                        continue

                # Standard update for other agents
                self.agents[agent_id].update(
                    obs=obs,
                    action=episode_moves[step, agent_id],
                    reward=rewards[agent_id],
                    next_obs=next_obs,
                    done=(step == episode_moves.shape[0] - 1)
                )
    
    def _calculate_final_statistics(self):
        """Calculate final statistics across all episodes"""
        # Calculate average scores per agent
        all_scores = np.array(self.simulation_results['episode_scores'])  # (episodes, steps, agents)
        avg_scores = np.mean(all_scores, axis=(0, 1))  # Average across episodes and steps
        
        # Calculate cooperation rates per agent
        all_moves = np.array(self.simulation_results['episode_moves'])  # (episodes, steps, agents)
        cooperation_rates = np.mean(all_moves == 0, axis=(0, 1))  # Average cooperation across episodes and steps
        
        # Store results by agent type
        for agent_type, agent_ids in self.agent_ids.items():

            if not agent_ids:
                continue

            type_scores = [avg_scores[agent_id] for agent_id in agent_ids]
            type_coop_rates = [cooperation_rates[agent_id] for agent_id in agent_ids]
            
            self.simulation_results['final_scores'][agent_type] = {
                'mean': np.mean(type_scores),
                'std': np.std(type_scores),
                'individual': type_scores
            }
            
            self.simulation_results['cooperation_rates'][agent_type] = {
                'mean': np.mean(type_coop_rates),
                'std': np.std(type_coop_rates),
                'individual': type_coop_rates
            }

    def _create_leaderboard(self):
        """Create leaderboard ranking agents by total score"""
        # Calculate total scores per agent across all episodes
        all_scores = np.array(self.simulation_results['episode_scores'])  # (episodes, steps, agents)
        total_scores = np.sum(all_scores, axis=(0, 1))  # Sum across episodes and steps
        
        # Create leaderboard entries
        leaderboard_entries = []
        for agent_id in range(self.total_agents):
            agent_type = self._get_agent_type(agent_id)
            entry = {
                'rank': 0,  # Will be set after sorting
                'agent_id': agent_id,
                'agent_type': agent_type,
                'total_score': total_scores[agent_id],
                'avg_score_per_round': total_scores[agent_id] / (self.sim_config['num_episodes'] * self.sim_config['episode_length'])
            }
            leaderboard_entries.append(entry)
        
        # Sort by total score (descending)
        leaderboard_entries.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Assign ranks
        for rank, entry in enumerate(leaderboard_entries, 1):
            entry['rank'] = rank
        
        # Store leaderboard
        self.simulation_results['leaderboard'] = leaderboard_entries
        
        # Log leaderboard
        logger.info("FINAL LEADERBOARD")
        logger.info("=" * 60)
        for entry in leaderboard_entries:
            logger.info(f"#{entry['rank']:2d} | Agent {entry['agent_id']:2d} ({entry['agent_type']:15s}) | "
                       f"Total: {entry['total_score']:8.2f} | Avg/Round: {entry['avg_score_per_round']:6.3f}")
        logger.info("=" * 60)
    
    def create_visualizations(self):
        """Create comprehensive visualizations of simulation results"""
        logger.info("Creating visualizations...")
        
        # 1. Move History Visualization
        self._create_move_history_visualization()
        
        # 2. Agent Comparison Plot (Scores and Cooperation Rates)
        self._create_agent_comparison_plot()

        # 4. Score Per Round Visualization
        self._create_score_per_round_visualization()

        # 5. Decision Matrix Visualizations
        if hasattr(self, 'decision_matrices'):
            self._create_decision_matrix_visualizations()

        # 6. Network Structure Visualization
        self._create_network_visualization()
        
        logger.info("Visualizations completed!")
    
    def _create_move_history_visualization(self):
        """Create grid visualization of move history with noise highlighting"""
        # Use the first episode for visualization
        episode_moves = self.simulation_results['episode_moves'][0]  # These are intended actions
        noise_data = self.simulation_results['noise_data'][0] if self.simulation_results['noise_data'] else []
        
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        
        # Transpose to get (agents, timesteps)
        grid = episode_moves.T
        num_agents, num_timesteps = grid.shape
        
        # Create custom RGBA array for coloring
        # Base colors: White = Cooperation (0), Black = Defection (1)
        # Noise colors: Green = Noisy Cooperation, Red = Noisy Defection
        rgba_grid = np.zeros((num_agents, num_timesteps, 4))
        
        for agent_id in range(num_agents):
            for timestep in range(num_timesteps):
                intended_action = grid[agent_id, timestep]  # This is the intended action
                
                # Check if this action was affected by noise
                is_noisy = False
                actual_action = intended_action
                if timestep < len(noise_data):
                    step_noise = noise_data[timestep]
                    if agent_id < len(step_noise['noise_mask']):
                        is_noisy = step_noise['noise_mask'][agent_id]
                        if is_noisy:
                            actual_action = step_noise['actual_actions'][agent_id]
                
                if is_noisy:
                    # Noisy actions get special colors
                    if actual_action == 0:  # Actual cooperation (but intended was different)
                        rgba_grid[agent_id, timestep] = [0.0, 0.8, 0.0, 1.0]  # Green
                    else:  # Actual defection (but intended was different)
                        rgba_grid[agent_id, timestep] = [0.8, 0.0, 0.0, 1.0]  # Red
                else:
                    # Normal actions (intended = actual)
                    if intended_action == 0:  # Normal cooperation
                        rgba_grid[agent_id, timestep] = [1.0, 1.0, 1.0, 1.0]  # White
                    else:  # Normal defection
                        rgba_grid[agent_id, timestep] = [0.0, 0.0, 0.0, 1.0]  # Black
        
        # Display the RGBA grid
        im = ax.imshow(rgba_grid, aspect='auto', interpolation='nearest')
        
        # Set labels
        ax.set_xlabel('Timestep')
        ax.set_ylabel('Agent ID')
        
        # Set x-axis ticks
        ax.set_xticks(range(0, num_timesteps, max(1, num_timesteps // 10)))
        ax.set_xticklabels(range(0, num_timesteps, max(1, num_timesteps // 10)))
        
        # Set y-axis ticks and labels
        ax.set_yticks(range(num_agents))
        
        # Create agent labels showing type and ID
        agent_labels = []
        for agent_id in range(num_agents):
            agent_type = self._get_agent_type(agent_id)
            agent_labels.append(f"{agent_type}_{agent_id}")
        
        ax.set_yticklabels(agent_labels)
        
        # Add custom legend instead of colorbar
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='white', edgecolor='black', label='Intended Cooperation (executed)'),
            Patch(facecolor='black', edgecolor='black', label='Intended Defection (executed)'),
            Patch(facecolor='green', edgecolor='black', label='Actual Cooperation (noise flipped intended defection)'),
            Patch(facecolor='red', edgecolor='black', label='Actual Defection (noise flipped intended cooperation)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.0, 1.0))
        
        # Add grid lines
        ax.grid(True, which='major', color='gray', linewidth=0.5, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Calculate statistics
        cooperation_rate = np.mean(grid == 0)
        noise_rate = 0.0
        if noise_data:
            total_noise_events = sum(np.sum(step['noise_mask']) for step in noise_data)
            total_actions = num_agents * len(noise_data)
            noise_rate = total_noise_events / total_actions if total_actions > 0 else 0.0
        
        # Add title and statistics
        title = f'Move History (Intended vs Actual): {self.network_config["type"]} Network, {self.total_agents} Agents'
        ax.set_title(title)
        
        # Add statistics text
        stats_text = f'Cooperation Rate: {cooperation_rate:.3f}\nNoise Rate: {noise_rate:.3f}'
        ax.text(0.02, 0.98, stats_text, 
               transform=ax.transAxes, fontsize=12, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'simulation_move_history.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_agent_comparison_plot(self):
        """Create comprehensive comparison plot of scores and cooperation rates across agent types"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 12))
        
        # Prepare data
        agent_types = list(self.simulation_results['final_scores'].keys())
        mean_scores = [self.simulation_results['final_scores'][t]['mean'] for t in agent_types]
        std_scores = [self.simulation_results['final_scores'][t]['std'] for t in agent_types]
        mean_coop_rates = [self.simulation_results['cooperation_rates'][t]['mean'] for t in agent_types]
        std_coop_rates = [self.simulation_results['cooperation_rates'][t]['std'] for t in agent_types]
        
        # Plot 1: Mean scores with error bars
        x = np.arange(len(agent_types))
        bars1 = ax1.bar(x, mean_scores, yerr=std_scores, capsize=5, alpha=0.7, color='skyblue')
        ax1.set_xlabel('Agent Type')
        ax1.set_ylabel('Average Score')
        ax1.set_title('Average Scores by Agent Type')
        ax1.set_xticks(x)
        ax1.set_xticklabels(agent_types, rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on score bars
        for bar, score in zip(bars1, mean_scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{score:.2f}', ha='center', va='bottom')
        
        # Plot 2: Mean cooperation rates with error bars
        bars2 = ax2.bar(x, mean_coop_rates, yerr=std_coop_rates, capsize=5, alpha=0.7, color='lightcoral')
        ax2.set_xlabel('Agent Type')
        ax2.set_ylabel('Cooperation Rate')
        ax2.set_title('Cooperation Rates by Agent Type')
        ax2.set_xticks(x)
        ax2.set_xticklabels(agent_types, rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on cooperation bars
        for bar, rate in zip(bars2, mean_coop_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{rate:.3f}', ha='center', va='bottom')
        
        # Plot 3: Score distribution box plot
        ax3.boxplot([self.simulation_results['final_scores'][t]['individual'] for t in agent_types], 
                   tick_labels=agent_types)
        ax3.set_xlabel('Agent Type')
        ax3.set_ylabel('Individual Scores')
        ax3.set_title('Score Distribution by Agent Type')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Cooperation rate distribution box plot
        cooperation_data = [self.simulation_results['cooperation_rates'][t]['individual'] for t in agent_types]
        ax4.boxplot(cooperation_data, tick_labels=agent_types)
        ax4.set_xlabel('Agent Type')
        ax4.set_ylabel('Individual Cooperation Rates')
        ax4.set_title('Cooperation Rate Distribution by Agent Type')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'simulation_agent_comparison.png'), dpi=300, bbox_inches='tight')
        plt.close()

    def _create_score_per_round_visualization(self):
        """Create line plots showing score progression per round for each agent"""
        if not self.simulation_results['episode_scores']:
            logger.warning("No episode score data available for visualization")
            return

        # Use the single episode's scores
        episode_scores = self.simulation_results['episode_scores'][0]  # Shape: (episode_length, num_agents)

        # Get agent type mapping for coloring
        agent_type_colors = {
            'online_simple_q': '#1f77b4',      # Blue
            'online_q_network': '#ff7f0e',     # Orange
            'online_decentralized_ppo': '#2ca02c',  # Green
            'online_lola': '#d62728',         # Red
            'online_mappo': '#9467bd',        # Purple
            'decentralized_ppo': '#8c564b',   # Brown
            'standard_mappo': '#e377c2',      # Pink
            'cooperative_mappo': '#7f7f7f',   # Gray
            'lola': '#bcbd22',                # Olive
            'q_learner': '#17becf',           # Cyan
            'titfortat': '#ff9896',           # Light red
            'cooperator': '#98df8a',          # Light green
            'defector': '#f7b6d2'             # Light pink
        }

        fig, axes = plt.subplots(2, 2, figsize=(20, 12))
        axes = axes.flatten()

        episode_length = episode_scores.shape[0]
        rounds = np.arange(episode_length)

        # Plot 1: All agents scores
        ax = axes[0]
        for agent_id in range(self.total_agents):
            agent_type = self._get_agent_type(agent_id)
            color = agent_type_colors.get(agent_type, '#000000')
            scores = episode_scores[:, agent_id]
            ax.plot(rounds, scores, label=f'Agent {agent_id} ({agent_type})',
                   color=color, alpha=0.8, linewidth=1.5)

        ax.set_xlabel('Round')
        ax.set_ylabel('Score')
        ax.set_title('All Agents - Score per Round')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

        # Plot 2: Online agents only
        ax = axes[1]
        online_agents = []
        for agent_id in range(self.total_agents):
            agent_type = self._get_agent_type(agent_id)
            if agent_type.startswith('online_'):
                online_agents.append(agent_id)

        if online_agents:
            for agent_id in online_agents:
                agent_type = self._get_agent_type(agent_id)
                color = agent_type_colors.get(agent_type, '#000000')
                scores = episode_scores[:, agent_id]
                ax.plot(rounds, scores, label=f'Agent {agent_id} ({agent_type})',
                       color=color, alpha=0.8, linewidth=2)

            ax.set_xlabel('Round')
            ax.set_ylabel('Score')
            ax.set_title('Online Agents - Score per Round')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)

        # Plot 3: Traditional agents only
        ax = axes[2]
        traditional_agents = []
        for agent_id in range(self.total_agents):
            agent_type = self._get_agent_type(agent_id)
            if not agent_type.startswith('online_'):
                traditional_agents.append(agent_id)

        if traditional_agents:
            for agent_id in traditional_agents:
                agent_type = self._get_agent_type(agent_id)
                color = agent_type_colors.get(agent_type, '#000000')
                scores = episode_scores[:, agent_id]
                ax.plot(rounds, scores, label=f'Agent {agent_id} ({agent_type})',
                       color=color, alpha=0.8, linewidth=2)

            ax.set_xlabel('Round')
            ax.set_ylabel('Score')
            ax.set_title('Traditional Agents - Score per Round')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)

        # Plot 4: Average scores by agent type
        ax = axes[3]
        agent_type_scores = {}

        for agent_id in range(self.total_agents):
            agent_type = self._get_agent_type(agent_id)
            if agent_type not in agent_type_scores:
                agent_type_scores[agent_type] = []
            scores = episode_scores[:, agent_id]
            agent_type_scores[agent_type].append(scores)

        for agent_type, scores_list in agent_type_scores.items():
            if scores_list:
                avg_scores = np.mean(scores_list, axis=0)
                color = agent_type_colors.get(agent_type, '#000000')
                ax.plot(rounds, avg_scores, label=f'{agent_type} (avg)',
                       color=color, linewidth=2.5, alpha=0.9)

        ax.set_xlabel('Round')
        ax.set_ylabel('Average Score')
        ax.set_title('Average Score by Agent Type')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.suptitle('Agent Score Progression Per Round', fontsize=16, y=0.95)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'score_per_round_detailed.png'), dpi=300, bbox_inches='tight')
        plt.close()


    


    def _create_decision_matrix_visualizations(self):
        """Create visualizations for decision matrices"""
        import pandas as pd
        
        # 1. Individual Agent Decision Matrices Heatmap
        self._create_individual_decision_matrices_plot()
        
        # 2. Summary Decision Matrix Heatmap
        self._create_summary_decision_matrix_plot()
        
        logger.info("Decision matrix visualizations completed")
    
    def _create_individual_decision_matrices_plot(self):
        """Create 2x2 decision matrix visualization for each individual agent"""
        import pandas as pd
        import seaborn as sns
        
        # Convert decision matrices to DataFrame
        df = pd.DataFrame(self.decision_matrices)
        
        # Get unique agents
        agent_ids = df['agent_id'].unique()
        n_agents = len(agent_ids)
        
        # Calculate grid dimensions
        cols = min(4, n_agents)  # Max 4 columns
        rows = int(np.ceil(n_agents / cols))
        
        fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows))
        
        # Handle single agent case
        if n_agents == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes.reshape(1, -1)
        
        # Flatten axes for easier indexing
        axes_flat = axes.flatten() if n_agents > 1 else axes
        
        for idx, agent_id in enumerate(agent_ids):
            # Filter data for this specific agent
            agent_data = df[df['agent_id'] == agent_id]
            agent_type = agent_data['agent_type'].iloc[0]
            
            # Create 2x2 matrix for this agent
            matrix_2x2 = np.zeros((2, 2))
            
            # Fill the matrix based on previous moves
            for _, row in agent_data.iterrows():
                own_prev = 0 if row['agent_previous_move'] == 'cooperate' else 1
                neigh_prev = 0 if row['neighbors_previous_move'] == 'cooperate' else 1
                matrix_2x2[own_prev, neigh_prev] = row['cooperation_rate']
            
            # Create heatmap for this agent
            ax = axes_flat[idx] if n_agents > 1 else axes_flat[0]
            
            sns.heatmap(
                matrix_2x2,
                annot=True,
                fmt='.3f',
                cmap='RdYlBu_r',
                vmin=0,
                vmax=1,
                cbar=True,
                ax=ax,
                square=True,
                xticklabels=['C', 'D'],
                yticklabels=['C', 'D'],
                annot_kws={'size': 12, 'weight': 'bold'}
            )
            
            ax.set_title(f'Agent {agent_id} ({agent_type.replace("_", " ").title()})\nCooperation Probability', fontsize=12, fontweight='bold')
            ax.set_xlabel('Neighbor\'s Previous Action (C=Cooperate, D=Defect)', fontsize=10)
            ax.set_ylabel('My Previous Action (C=Cooperate, D=Defect)', fontsize=10)
            ax.tick_params(axis='both', which='major', labelsize=9)
        
        # Hide unused subplots
        for idx in range(n_agents, len(axes_flat)):
            axes_flat[idx].set_visible(False)
        
        plt.suptitle('Individual Agent Decision Matrices (2x2 Strategy Matrices)', fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'individual_agent_decision_matrices.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_summary_decision_matrix_plot(self):
        """Create 2x2 summary decision matrix visualization"""
        import pandas as pd
        import seaborn as sns
        
        # Convert summary decision matrix to DataFrame for visualization
        summary_df = pd.DataFrame(self.summary_decision_matrix)
        
        # Filter out rows with zero total cases to avoid visualization issues
        summary_df_filtered = summary_df[summary_df['total_cases'] > 0].copy()
        
        if len(summary_df_filtered) == 0:
            logger.warning("No valid decision matrix data for visualization")
            return
        
        # Create 2x2 matrices
        cooperation_matrix = np.zeros((2, 2))
        cases_matrix = np.zeros((2, 2))
        
        # Fill matrices based on previous moves
        for _, row in summary_df_filtered.iterrows():
            own_prev = 0 if row['agent_previous_move'] == 'cooperate' else 1
            neigh_prev = 0 if row['neighbors_previous_move'] == 'cooperate' else 1
            cooperation_matrix[own_prev, neigh_prev] = row['cooperation_rate']
            cases_matrix[own_prev, neigh_prev] = row['total_cases']
        
        # Create the visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Plot 1: Cooperation Rate Matrix (2x2)
        sns.heatmap(
            cooperation_matrix,
            annot=True,
            fmt='.3f',
            cmap='RdYlBu_r',
            vmin=0,
            vmax=1,
            cbar=True,
            ax=ax1,
            square=True,
            xticklabels=['C', 'D'],
            yticklabels=['C', 'D'],
            annot_kws={'size': 16, 'weight': 'bold'}
        )
        ax1.set_title('Population Decision Matrix\n(Cooperation Rates)', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Neighbors\' Previous Action (C=Cooperate, D=Defect)', fontsize=14)
        ax1.set_ylabel('My Previous Action (C=Cooperate, D=Defect)', fontsize=14)
        ax1.tick_params(axis='both', which='major', labelsize=12)
        
        # Plot 2: Total Cases Matrix (2x2)
        sns.heatmap(
            cases_matrix.astype(int),
            annot=True,
            fmt='d',
            cmap='viridis',
            cbar=True,
            ax=ax2,
            square=True,
            xticklabels=['C', 'D'],
            yticklabels=['C', 'D'],
            annot_kws={'size': 16, 'weight': 'bold'}
        )
        ax2.set_title('Population Decision Matrix\n(Total Cases)', fontsize=16, fontweight='bold')
        ax2.set_xlabel('Neighbors\' Previous Action (C=Cooperate, D=Defect)', fontsize=14)
        ax2.set_ylabel('My Previous Action (C=Cooperate, D=Defect)', fontsize=14)
        ax2.tick_params(axis='both', which='major', labelsize=12)
        
        # Add determinant information
        det_value = self.decision_matrix_summary['value']
        fig.suptitle(f'Population Strategy Analysis\nDeterminant: {det_value:.4f}', fontsize=18, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'summary_decision_matrix.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_network_visualization(self):
        """Create network structure visualization (node-link diagram)"""
        import networkx as nx
            
        # Create NetworkX graph from adjacency matrix
        G = nx.from_numpy_array(self.network)
            
        # Set up the plot
        plt.figure(figsize=(12, 10))
            
        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
            
        # Draw the network
        nx.draw_networkx_nodes(G, pos, 
                              node_color='lightblue', 
                              node_size=500, 
                              alpha=0.8)
            
        nx.draw_networkx_edges(G, pos, 
                              edge_color='gray', 
                              width=1.5, 
                              alpha=0.6)
            
    # Add node labels (agent types and IDs)
        node_labels = {}
        for i in range(self.total_agents):
            agent_type = self._get_agent_type(i)
            node_labels[i] = f"{agent_type}_{i}"
            
            nx.draw_networkx_labels(G, pos, node_labels, font_size=8, font_weight='bold')
            
            # Add edge labels (optional - can be removed if too cluttered)
            # edge_labels = nx.get_edge_attributes(G, 'weight')
            # nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
            
            plt.title(f'Network Structure: {self.network_config["type"].title()} Network\n'
                     f'{self.total_agents} Agents, {G.number_of_edges()} Connections', 
                     fontsize=14, fontweight='bold')
            
            plt.axis('off')
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(os.path.join(self.results_dir, 'network_structure.png'), dpi=300, bbox_inches='tight')
            plt.close()

    
    def _export_results_to_csv(self):
        """Export simulation results to CSV files"""
        import pandas as pd
        
        # Export combined episode data (scores and moves)
        episode_data = []
        for episode_idx, episode_scores in enumerate(self.simulation_results['episode_scores']):
            for step_idx, step_scores in enumerate(episode_scores):
                for agent_idx, score in enumerate(step_scores):
                    intended_move = self.simulation_results['episode_moves'][episode_idx][step_idx][agent_idx]
                    
                    # Get actual move from noise data if available
                    actual_move = intended_move  # Default to intended if no noise data
                    is_noisy = False
                    if (episode_idx < len(self.simulation_results['noise_data']) and 
                        step_idx < len(self.simulation_results['noise_data'][episode_idx])):
                        step_noise = self.simulation_results['noise_data'][episode_idx][step_idx]
                        if agent_idx < len(step_noise['actual_actions']):
                            actual_move = step_noise['actual_actions'][agent_idx]
                            is_noisy = step_noise['noise_mask'][agent_idx]
                    
                    episode_data.append({
                        'episode': episode_idx,
                        'step': step_idx,
                        'agent_id': agent_idx,
                        'agent_type': self._get_agent_type(agent_idx),
                        'score': score,
                        'intended_move': intended_move,
                        'intended_action': 'cooperate' if intended_move == 0 else 'defect',
                        'actual_move': actual_move,
                        'actual_action': 'cooperate' if actual_move == 0 else 'defect',
                        'is_noisy': is_noisy
                    })
        
        episode_df = pd.DataFrame(episode_data)
        episode_df.to_csv(os.path.join(self.results_dir, 'episode_data.csv'), index=False)
        logger.info(f"Episode data exported to '{self.results_dir}/episode_data.csv'")
        
        # Export final statistics and leaderboard
        final_stats = []
        for agent_type, scores in self.simulation_results['final_scores'].items():
            coop_rates = self.simulation_results['cooperation_rates'][agent_type]
            for i, (score, coop_rate) in enumerate(zip(scores['individual'], coop_rates['individual'])):
                final_stats.append({
                    'agent_type': agent_type,
                    'agent_id': self.agent_ids[agent_type][i],
                    'final_score': score,
                    'cooperation_rate': coop_rate,
                    'mean_score': scores['mean'],
                    'std_score': scores['std'],
                    'mean_cooperation': coop_rates['mean'],
                    'std_cooperation': coop_rates['std']
                })
        
        # Add leaderboard data if available
        if self.simulation_results['leaderboard']:
            for i, leaderboard_entry in enumerate(self.simulation_results['leaderboard']):
                if i < len(final_stats):
                    final_stats[i].update(leaderboard_entry)
        
        final_stats_df = pd.DataFrame(final_stats)
        final_stats_df.to_csv(os.path.join(self.results_dir, 'final_statistics.csv'), index=False)
        logger.info(f"Final statistics exported to '{self.results_dir}/final_statistics.csv'")
        
        # Export decision matrices if calculated
        if hasattr(self, 'decision_matrices'):
            # Combine all decision matrix data into one file
            decision_data = {
                'individual_matrices': self.decision_matrices,
                'summary_matrix': self.summary_decision_matrix,
                'determinant_summary': self.decision_matrix_summary
            }
            
            # Save as JSON for better structure preservation
            import json
            decision_json_path = os.path.join(self.results_dir, 'decision_matrices.json')
            with open(decision_json_path, 'w') as f:
                json.dump(decision_data, f, indent=2, default=str)
            logger.info(f"Decision matrices exported to '{self.results_dir}/decision_matrices.json'")
        
        # Export network structure and simulation configuration
        config_data = {
            'network_type': self.network_config['type'],
            'k_neighbors': self.network_config['k_neighbors'],
            'rewire_prob': self.network_config['rewire_prob'],
            'episode_length': self.sim_config['episode_length'],
            'num_episodes': self.sim_config['num_episodes'],
            'total_agents': self.total_agents,
            'network_matrix': self.network.tolist()
        }
        
        # Save as JSON for better structure preservation
        import json
        config_json_path = os.path.join(self.results_dir, 'simulation_config.json')
        with open(config_json_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        logger.info(f"Simulation configuration exported to '{self.results_dir}/simulation_config.json'")
    
    def _calculate_decision_matrices(self):
        """Calculate decision matrices for each agent and overall summary"""
        logger.info("Calculating decision matrices...")
        
        # Combine all episode moves
        all_moves = np.vstack(self.simulation_results['episode_moves'])  # Shape: (total_steps, num_agents)
        
        # Individual agent decision matrices
        self.decision_matrices = []
        
        for agent_id in range(self.total_agents):
            agent_type = self._get_agent_type(agent_id)
            neighbors = np.where(self.network[agent_id] == 1)[0]
            
            # Initialize decision matrix counters
            # [own_prev_action][neighbor_avg_action] -> [cooperate_count, defect_count]
            decision_counts = {
                ('cooperate', 'cooperate'): {'cooperate': 0, 'defect': 0},
                ('cooperate', 'defect'): {'cooperate': 0, 'defect': 0},
                ('defect', 'cooperate'): {'cooperate': 0, 'defect': 0},
                ('defect', 'defect'): {'cooperate': 0, 'defect': 0}
            }
            
            # Analyze moves for this agent (skip first step since no previous action)
            for step in range(1, all_moves.shape[0]):
                own_prev_action = 'cooperate' if all_moves[step-1, agent_id] == 0 else 'defect'
                own_curr_action = 'cooperate' if all_moves[step, agent_id] == 0 else 'defect'
                
                # Calculate average neighbor action (if neighbors exist)
                if len(neighbors) > 0:
                    neighbor_actions = all_moves[step-1, neighbors]
                    avg_neighbor_action = np.mean(neighbor_actions)
                    neighbor_action_label = 'cooperate' if avg_neighbor_action < 0.5 else 'defect'
                else:
                    neighbor_action_label = 'cooperate'  # Default if no neighbors
                
                # Update decision matrix
                key = (own_prev_action, neighbor_action_label)
                decision_counts[key][own_curr_action] += 1
            
            # Calculate rates and determinant for each situation
            for situation in [('cooperate', 'cooperate'), ('cooperate', 'defect'), 
                            ('defect', 'cooperate'), ('defect', 'defect')]:
                own_prev, neighbor_prev = situation
                counts = decision_counts[situation]
                total_cases = counts['cooperate'] + counts['defect']
                
                if total_cases > 0:
                    cooperation_rate = counts['cooperate'] / total_cases
                    defect_rate = counts['defect'] / total_cases
                else:
                    cooperation_rate = 0.0
                    defect_rate = 0.0
                
                # Calculate determinant (for 2x2 matrix, det = ad - bc where matrix is [[a,b],[c,d]])
                # Here we treat it as probability of cooperation vs defection
                determinant = cooperation_rate * defect_rate - (1-cooperation_rate) * (1-defect_rate)
                
                self.decision_matrices.append({
                    'agent_id': agent_id,
                    'agent_type': agent_type,
                    'agent_previous_move': own_prev,
                    'neighbors_previous_move': neighbor_prev,
                    'cooperation_rate': cooperation_rate,
                    'defect_rate': defect_rate,
                    'total_cases': total_cases,
                    'cooperation_count': counts['cooperate'],
                    'defect_count': counts['defect'],
                    'determinant': determinant
                })
        
        # Calculate summary decision matrix across all agents
        self._calculate_summary_decision_matrix()
        logger.info("Decision matrices calculation completed")
    
    def _calculate_summary_decision_matrix(self):
        """Calculate overall summary decision matrix"""
        # Aggregate decision matrix across all agents
        summary_matrix = {
            ('cooperate', 'cooperate'): {'cooperate': 0, 'defect': 0},
            ('cooperate', 'defect'): {'cooperate': 0, 'defect': 0},
            ('defect', 'cooperate'): {'cooperate': 0, 'defect': 0},
            ('defect', 'defect'): {'cooperate': 0, 'defect': 0}
        }
        
        # Sum up across all agents
        for entry in self.decision_matrices:
            situation = (entry['agent_previous_move'], entry['neighbors_previous_move'])
            summary_matrix[situation]['cooperate'] += entry['cooperation_count']
            summary_matrix[situation]['defect'] += entry['defect_count']
        
        # Convert to summary format
        self.summary_decision_matrix = []
        matrix_values = []
        
        for situation in [('cooperate', 'cooperate'), ('cooperate', 'defect'),
                         ('defect', 'cooperate'), ('defect', 'defect')]:
            own_prev, neighbor_prev = situation
            counts = summary_matrix[situation]
            total_cases = counts['cooperate'] + counts['defect']
            
            if total_cases > 0:
                cooperation_rate = counts['cooperate'] / total_cases
            else:
                cooperation_rate = 0.0
            
            matrix_values.append(cooperation_rate)
            
            self.summary_decision_matrix.append({
                'agent_previous_move': own_prev,
                'neighbors_previous_move': neighbor_prev,
                'cooperation_rate': cooperation_rate,
                'total_cases': total_cases,
                'cooperation_count': counts['cooperate'],
                'defect_count': counts['defect']
            })
        
        # Calculate overall determinant (2x2 matrix determinant)
        # Matrix: [[CC, CD], [DC, DD]] where values are cooperation rates
        if len(matrix_values) == 4:
            a, b, c, d = matrix_values
            determinant = a * d - b * c
        else:
            determinant = 0.0
        
        self.decision_matrix_summary = {
            'metric': 'summary_determinant',
            'value': determinant,
            'matrix_values': str(matrix_values),
            'num_agents': self.total_agents
        }
    
    def _get_agent_type(self, agent_id: int) -> str:
        """Get agent type for a given agent ID"""
        for agent_type, agent_ids in self.agent_ids.items():
            if agent_id in agent_ids:
                return agent_type
        return "unknown"
    
    def print_summary(self):
        """Print minimal simulation summary"""
        logger.info("Simulation completed successfully!")
        logger.info(f"Network: {self.network_config['type']} with {self.network_config['k_neighbors']} neighbors")
        logger.info(f"Total Agents: {self.total_agents}")
        logger.info(f"Episodes: {self.sim_config['num_episodes']} x {self.sim_config['episode_length']} steps")
        logger.info(f"Results saved to: {self.results_dir}")
        
        # List files in results directory
        if os.path.exists(self.results_dir):
            files = os.listdir(self.results_dir)
            logger.info(f"Files in results directory: {files}")
    



# =============================================================================
# AGENT WRAPPER CLASSES
# =============================================================================

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.history = []
    
    def get_action(self, obs: np.ndarray) -> int:
        """Get action from observation - to be implemented by subclasses"""
        raise NotImplementedError
    
    def reset(self):
        """Reset agent state"""
        self.history = []

class DecentralizedPPOAgentWrapper(BaseAgent):
    """Wrapper for Decentralized PPO agents"""
    
    def __init__(self, ppo_agent, agent_id: int):
        super().__init__(agent_id)
        self.ppo_agent = ppo_agent
    
    def get_action(self, obs: np.ndarray) -> int:
        try:
            # Convert observation to tensor and get action
            obs_tensor = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            action, _, _ = self.ppo_agent.get_action(obs_tensor, deterministic=True)
            
            # Handle both tensor and integer returns
            if hasattr(action, 'item'):
                action = int(action.item())
            else:
                action = int(action)
                
        except Exception as e:
            raise RuntimeError(f"Failed to get action from PPO agent {self.agent_id}: {e}")
        
        self.history.append(action)
        return action
    
    def reset(self):
        """Reset agent state"""
        super().reset()
        # PPO agents don't have internal state to reset, just clear history

class StandardMAPPOAgentWrapper(BaseAgent):
    """Wrapper for Standard MAPPO agents"""
    
    def __init__(self, mappo_agent, agent_id: int):
        super().__init__(agent_id)
        self.mappo_agent = mappo_agent
    
    def get_action(self, obs: np.ndarray) -> int:
        try:
            # Use underlying actor directly for single-agent inference
            local_obs_tensor = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            action, _, _ = self.mappo_agent.actor.get_action(local_obs_tensor, deterministic=True)
            action = int(action.item())
        except Exception as e:
            raise RuntimeError(f"Failed to get action from Standard MAPPO agent {self.agent_id}: {e}")
        
        self.history.append(action)
        return action

class CooperativeMAPPOAgentWrapper(BaseAgent):
    """Wrapper for Cooperative MAPPO agents"""
    
    def __init__(self, mappo_agent, agent_id: int):
        super().__init__(agent_id)
        self.mappo_agent = mappo_agent
    
    def get_action(self, obs: np.ndarray) -> int:
        try:
            # Use underlying actor directly for single-agent inference
            local_obs_tensor = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            action, _, _ = self.mappo_agent.actor.get_action(local_obs_tensor, deterministic=True)
            action = int(action.item())
        except Exception as e:
            raise RuntimeError(f"Failed to get action from Cooperative MAPPO agent {self.agent_id}: {e}")
        
        self.history.append(action)
        return action

class LOLAAgentWrapper(BaseAgent):
    """Wrapper for LOLA agents"""
    
    def __init__(self, lola_system, agent_index: int, agent_id: int):
        super().__init__(agent_id)
        self.lola_system = lola_system
        self.agent_index = agent_index
    
    def get_action(self, obs: np.ndarray) -> int:
        try:
            # Build a states list matching the number of LOLA agents
            num = len(getattr(self.lola_system, 'agents', [])) or 1
            obs_dim = obs.shape[0]
            
            # Handle dimension mismatch by padding or truncating
            target_dim = self.lola_system.agents[self.agent_index].input_dim
            if obs_dim != target_dim:
                if obs_dim < target_dim:
                    # Pad with zeros
                    padded_obs = np.zeros(target_dim)
                    padded_obs[:obs_dim] = obs
                    obs = padded_obs
                else:
                    # Truncate
                    obs = obs[:target_dim]
            
            observations = [np.zeros(target_dim) for _ in range(num)]
            if 0 <= self.agent_index < num:
                observations[self.agent_index] = obs
            
            actions, _, _ = self.lola_system.get_actions(observations, deterministic=True)
            action = int(actions[self.agent_index]) if len(actions) > self.agent_index else 0
        except Exception as e:
            raise RuntimeError(f"Failed to get action from LOLA agent {self.agent_id}: {e}")
        
        self.history.append(action)
        return action

class TitForTatAgent(BaseAgent):
    """Tit-for-Tat strategy agent - copies the average move of observed neighbors"""
    
    def get_action(self, obs: np.ndarray) -> int:
        if len(self.history) == 0:
            action = 0  # Start with cooperation
        else:
            # Copy average neighbor action from last round
            # obs[1] contains the average neighbor action (0 = cooperate, 1 = defect)
            avg_neighbor_action = obs[1]
            
            # Use threshold of 0.5 to decide: if average >= 0.5, most neighbors defected, so defect
            action = 1 if avg_neighbor_action >= 0.5 else 0
        
        self.history.append(action)
        return action

class CooperatorAgent(BaseAgent):
    """Always cooperate agent"""
    
    def get_action(self, obs: np.ndarray) -> int:
        action = 0  # Always cooperate
        self.history.append(action)
        return action

class DefectorAgent(BaseAgent):
    """Always defect agent"""
    
    def get_action(self, obs: np.ndarray) -> int:
        action = 1  # Always defect
        self.history.append(action)
        return action

class OnlineAgentWrapper(BaseAgent):
    """Wrapper for online learning agents"""
    
    def __init__(self, online_agent, agent_id: int):
        super().__init__(agent_id)
        self.online_agent = online_agent
    
    def get_action(self, obs: np.ndarray) -> int:
        try:
            # Get action from online agent
            result = self.online_agent.get_action(obs, deterministic=False)
            
            # Handle different return formats
            if isinstance(result, tuple):
                # Most online agents return (action, log_prob, hidden_state)
                action = result[0]
            else:
                # Simple Q-Learning agent returns just the action
                action = result
            
            # Handle both tensor and integer returns
            if hasattr(action, 'item'):
                action = int(action.item())
            else:
                action = int(action)
                
        except Exception as e:
            raise RuntimeError(f"Failed to get action from online agent {self.agent_id}: {e}")
        
        self.history.append(action)
        return action
    
    def update(self, obs: np.ndarray, action: int, reward: float, next_obs: np.ndarray, done: bool):
        """Update the online agent with experience"""
        try:
            self.online_agent.update(obs, action, reward, next_obs, done)
        except Exception as e:
            raise RuntimeError(f"Failed to update online agent {self.agent_id}: {e}")
    
    def reset(self):
        """Reset agent state"""
        super().reset()
        if hasattr(self.online_agent, 'reset'):
            self.online_agent.reset()

class RandomAgent(BaseAgent):
    """Random strategy agent (fallback)"""
    
    def get_action(self, obs: np.ndarray) -> int:
        action = np.random.randint(0, 2)  # Random 0 or 1
        self.history.append(action)
        return action


def main():
    """Main simulation function"""
    logger.info("Starting NIPD Agent Simulator")
    
    # Create simulator with current configuration
    simulator = AgentSimulator(AGENT_CONFIG, NETWORK_CONFIG, SIMULATION_CONFIG)
    
    # Run simulation
    simulator.run_simulation()
    
    # Create visualizations
    simulator.create_visualizations()
    
    # Print summary
    simulator.print_summary()


if __name__ == "__main__":
    main()
