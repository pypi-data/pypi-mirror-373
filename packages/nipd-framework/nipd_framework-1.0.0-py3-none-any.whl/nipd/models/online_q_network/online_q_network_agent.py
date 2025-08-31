import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import deque
import os
import json

class OnlineQNetwork(nn.Module):
    """
    Online Recurrent Q-Network that learns and adapts during gameplay
    Enhanced with opponent modeling and adaptive strategies
    """
    
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64, lstm_hidden_dim: int = 64):
        super(OnlineQNetwork, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM layer for sequence processing
        self.lstm = nn.LSTM(hidden_dim, lstm_hidden_dim, batch_first=True)
        
        # Q-value head
        self.q_head = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 2)  # 2 actions: Cooperate (0), Defect (1)
        )
        

        
        # Initialize weights for stable learning with orthogonal LSTM weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights for stable learning with orthogonal LSTM weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=0.5)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.LSTM):
                for name, param in m.named_parameters():
                    if 'weight_ih' in name:
                        nn.init.orthogonal_(param, gain=1.0)
                    elif 'weight_hh' in name:
                        nn.init.orthogonal_(param, gain=1.0)
                    elif 'bias' in name:
                        nn.init.constant_(param, 0)
    
    def forward(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Forward pass through the recurrent network"""
        # Extract features
        features = self.feature_net(x)
        
        # Add sequence dimension if needed
        if features.dim() == 2:
            features = features.unsqueeze(1)  # (batch, 1, hidden_dim)
        
        # Process through LSTM
        if hidden_state is not None:
            lstm_out, new_hidden = self.lstm(features, hidden_state)
        else:
            lstm_out, new_hidden = self.lstm(features)
        
        # Get final output for Q-values
        lstm_out = lstm_out.squeeze(1)  # Remove sequence dimension
        
        # Q-value head
        q_values = self.q_head(lstm_out)
        
        return q_values, new_hidden
    
    def get_q_values(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Get Q-values for all actions"""
        q_values, new_hidden = self.forward(x, hidden_state)
        return q_values, new_hidden
    
    def get_action(self, x: torch.Tensor, epsilon: float = 0.1, 
                   hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[int, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Get action using epsilon-greedy policy with hidden state"""
        q_values, new_hidden = self.get_q_values(x, hidden_state)
        
        # Store Q-values for entropy computation
        self.last_q_values = q_values
        
        if np.random.random() < epsilon:
            action = torch.randint(0, 2, (1,))
        else:
            action = torch.argmax(q_values, dim=-1)
        
        return action.item(), q_values, new_hidden
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OnlineQNetworkAgent:
    """
    Online Q-Network agent that adapts behavior based on opponent observations
    Implements continuous learning and opponent modeling
    """
    
    def __init__(self, agent_id: int, input_dim: int = 4, learning_rate: float = 0.001,
                 discount_factor: float = 0.95, epsilon: float = 0.3,
                 opponent_memory_length: int = 10,
                 device: str = 'cpu'):
        self.agent_id = agent_id
        self.input_dim = input_dim
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.opponent_memory_length = opponent_memory_length
        self.device = device
        
        # Initialize Q-network
        self.q_network = OnlineQNetwork(input_dim=input_dim).to(device)
        self.target_network = OnlineQNetwork(input_dim=input_dim).to(device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer
        self.optimizer = torch.optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Online learning components
        self.opponent_history = deque(maxlen=opponent_memory_length)
        self.own_history = deque(maxlen=opponent_memory_length)
        self.reward_history = deque(maxlen=opponent_memory_length)
        self.state_history = deque(maxlen=opponent_memory_length)
        
        # Opponent modeling
        self.opponent_defection_rate = 0.0
        self.opponent_cooperation_rate = 0.0
        self.recent_opponent_actions = deque(maxlen=5)
        
        # Online learning parameters
        self.epsilon_decay = 0.999  # Faster decay for quicker convergence
        self.min_epsilon = 0.05     # Higher minimum epsilon for continued exploration
        self.target_update_freq = 100  # Update target network every N steps
        
        # Experience replay for online updates
        self.experience_buffer = deque(maxlen=1000)
        self.batch_size = 32
        
        # Current episode state
        self.current_hidden_state = None
        self.last_state = None
        self.last_action = None
        self.last_q_values = None
        
        # Statistics
        self.cooperation_count = 0
        self.total_actions = 0
        self.update_count = 0
        
        # Target network update frequency
        self.target_update_freq = 100
    
    def _update_opponent_model(self, opponent_action: int, reward: float):
        """
        Update opponent behavior model based on recent observations
        """
        # Update histories
        self.opponent_history.append(opponent_action)
        self.reward_history.append(reward)
        
        # Update recent opponent actions
        self.recent_opponent_actions.append(opponent_action)
        
        # Calculate opponent defection rate
        if len(self.opponent_history) > 0:
            self.opponent_defection_rate = sum(1 for action in self.opponent_history if action == 1) / len(self.opponent_history)
            self.opponent_cooperation_rate = 1.0 - self.opponent_defection_rate
        

    
    def _get_q_action(self, obs: np.ndarray, deterministic: bool = False) -> int:
        """
        Get action using pure Q-network with epsilon-greedy exploration
        """
        obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
        
        # Get Q-values
        with torch.no_grad():
            q_values, new_hidden = self.q_network.get_q_values(obs_tensor, self.current_hidden_state)
            q_values = q_values.squeeze(0)
        
        # Pure Q-learning with epsilon-greedy action selection
        if not deterministic and np.random.random() < self.epsilon:
            action = np.random.choice([0, 1])
        else:
            action = torch.argmax(q_values).item()
        
        # Update hidden state
        self.current_hidden_state = new_hidden
        
        return action
    
    def get_action(self, obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float, Optional[Tuple[np.ndarray, np.ndarray]]]:
        """
        Get action from observation using pure Q-network learning
        
        Returns:
            Tuple of (action, log_prob, new_hidden)
        """
        action = self._get_q_action(obs, deterministic)
        
        # Store for learning
        self.last_state = obs.copy()
        self.last_action = action
        
        # Update statistics
        if action == 0:
            self.cooperation_count += 1
        self.total_actions += 1
        
        # Convert hidden state to numpy
        if self.current_hidden_state is not None:
            h, c = self.current_hidden_state
            hidden_numpy = (h.squeeze(0).cpu().numpy(), c.squeeze(0).cpu().numpy())
        else:
            hidden_numpy = None
        
        return action, 0.0, hidden_numpy
    
    def update(self, obs: np.ndarray, action: int, reward: float, next_obs: np.ndarray, done: bool):
        """
        Online update of Q-values based on immediate experience
        """
        if self.last_state is None:
            return
        
        # Store experience
        experience = (self.last_state, action, reward, next_obs, done)
        self.experience_buffer.append(experience)
        
        # Update opponent model if we have opponent action information
        if len(obs) > 1:
            opponent_action = int(obs[1] > 0.5)  # neighbor_prev action
            self._update_opponent_model(opponent_action, reward)
        
        # Update own history
        self.own_history.append(action)
        self.state_history.append(obs)
        
        # Perform online learning update
        self._online_update()
        
        # Update target network periodically
        if self.update_count % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay epsilon for exploration
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        self.update_count += 1
    
    def _online_update(self):
        """
        Perform online learning update using experience replay
        """
        if len(self.experience_buffer) < self.batch_size:
            return
        
        # Sample batch from experience buffer
        batch_indices = np.random.choice(len(self.experience_buffer), self.batch_size, replace=False)
        batch = [self.experience_buffer[i] for i in batch_indices]
        
        # Prepare batch data - optimized tensor creation
        states = torch.FloatTensor(np.array([exp[0] for exp in batch])).to(self.device)
        actions = torch.LongTensor(np.array([exp[1] for exp in batch])).to(self.device)
        rewards = torch.FloatTensor(np.array([exp[2] for exp in batch])).to(self.device)
        next_states = torch.FloatTensor(np.array([exp[3] for exp in batch])).to(self.device)
        dones = torch.BoolTensor(np.array([exp[4] for exp in batch])).to(self.device)
        
        # Compute current Q-values
        current_q_values, _ = self.q_network.get_q_values(states)
        current_q = current_q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Compute target Q-values
        with torch.no_grad():
            next_q_values, _ = self.target_network.get_q_values(next_states)
            next_max_q = next_q_values.max(1)[0]
            target_q = rewards + (self.discount_factor * next_max_q * ~dones)
        
        # Compute loss
        loss = F.mse_loss(current_q, target_q)
        
        # Update network
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
    
    def get_cooperation_rate(self) -> float:
        """Get current cooperation rate"""
        if self.total_actions == 0:
            return 0.0
        return self.cooperation_count / self.total_actions
    
    def get_opponent_defection_rate(self) -> float:
        """Get opponent's defection rate"""
        return self.opponent_defection_rate
    
    def get_strategy_mode(self) -> str:
        """Get current learning mode"""
        return "q_network_online"
    
    def save_model(self, filepath: str):
        """Save the agent's model and parameters"""
        model_data = {
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'agent_id': self.agent_id,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'opponent_memory_length': self.opponent_memory_length,
            'epsilon_decay': self.epsilon_decay,
            'min_epsilon': self.min_epsilon,
            'opponent_defection_rate': self.opponent_defection_rate,
            'cooperation_count': self.cooperation_count,
            'total_actions': self.total_actions,
            'update_count': self.update_count
        }
        
        torch.save(model_data, filepath)
    
    def load_model(self, filepath: str):
        """Load the agent's model and parameters"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = torch.load(filepath, map_location=self.device, weights_only=False)
        
        self.q_network.load_state_dict(model_data['q_network_state_dict'])
        self.target_network.load_state_dict(model_data['target_network_state_dict'])
        self.optimizer.load_state_dict(model_data['optimizer_state_dict'])
        
        self.agent_id = model_data['agent_id']
        self.learning_rate = model_data['learning_rate']
        self.discount_factor = model_data['discount_factor']
        self.epsilon = model_data['epsilon']
        self.opponent_memory_length = model_data['opponent_memory_length']
        self.epsilon_decay = model_data.get('epsilon_decay', 0.995)
        self.min_epsilon = model_data.get('min_epsilon', 0.01)
        self.opponent_defection_rate = model_data['opponent_defection_rate']
        self.cooperation_count = model_data['cooperation_count']
        self.total_actions = model_data['total_actions']
        self.update_count = model_data['update_count']
    
    def reset(self):
        """Reset agent state for new episode"""
        self.current_hidden_state = None
        self.last_state = None
        self.last_action = None
        self.last_q_values = None
        # Keep Q-network intact for online learning
