import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from collections import deque
import copy
import os
import json

class OnlineLOLANetwork(nn.Module):
    """
    Online Recurrent neural network for LOLA agent with opponent modeling capabilities
    Enhanced for continuous learning and adaptation
    """
    def __init__(self, input_dim: int, hidden_dim: int = 64, output_dim: int = 2, lstm_hidden_dim: int = 64):
        super(OnlineLOLANetwork, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh()
        )
        
        # LSTM layer for sequence processing
        self.lstm = nn.LSTM(hidden_dim, lstm_hidden_dim, batch_first=True)
        
        # Policy head
        self.policy_head = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, output_dim)
        )
        
        # Opponent modeling head
        self.opponent_head = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, output_dim)
        )
        
        # Initialize weights for stable learning
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights with Xavier initialization and orthogonal LSTM weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0.0)
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
        
        # Get final output for policy
        lstm_out = lstm_out.squeeze(1)  # Remove sequence dimension
        
        # Policy head
        logits = self.policy_head(lstm_out)
        
        # Opponent prediction head
        opponent_logits = self.opponent_head(lstm_out)
        
        return logits, opponent_logits, new_hidden
    
    def get_action_probs(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Get action probabilities using softmax"""
        logits, opponent_logits, new_hidden = self.forward(x, hidden_state)
        probs = F.softmax(logits, dim=-1)
        opponent_probs = F.softmax(opponent_logits, dim=-1)
        return probs, opponent_probs, new_hidden
    
    def get_action_logits(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Get raw action logits"""
        return self.forward(x, hidden_state)
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OnlineOpponentModel(nn.Module):
    """
    Online Recurrent model to predict opponent's policy and learning updates
    Enhanced for continuous adaptation
    """
    def __init__(self, input_dim: int, hidden_dim: int = 64, lstm_hidden_dim: int = 64):
        super(OnlineOpponentModel, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh()
        )
        
        # LSTM layer for sequence processing
        self.lstm = nn.LSTM(hidden_dim, lstm_hidden_dim, batch_first=True)
        
        # Opponent policy head
        self.opponent_policy_head = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 2)  # 2 actions: Cooperate (0), Defect (1)
        )
        
        # Learning rate prediction head
        self.lr_head = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()  # Learning rate between 0 and 1
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights for stable learning"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0.0)
            elif isinstance(m, nn.LSTM):
                for name, param in m.named_parameters():
                    if 'weight_ih' in name:
                        nn.init.orthogonal_(param, gain=1.0)
                    elif 'weight_hh' in name:
                        nn.init.orthogonal_(param, gain=1.0)
                    elif 'bias' in name:
                        nn.init.constant_(param, 0)
    
    def forward(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Forward pass through the opponent model"""
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
        
        # Get final output
        lstm_out = lstm_out.squeeze(1)  # Remove sequence dimension
        
        # Opponent policy head
        opponent_logits = self.opponent_policy_head(lstm_out)
        
        # Learning rate head
        lr_pred = self.lr_head(lstm_out)
        
        return opponent_logits, lr_pred, new_hidden
    
    def get_opponent_probs(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Get opponent action probabilities"""
        opponent_logits, lr_pred, new_hidden = self.forward(x, hidden_state)
        opponent_probs = F.softmax(opponent_logits, dim=-1)
        return opponent_probs, lr_pred, new_hidden

    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OnlineLOLAAgent:
    """
    Online LOLA agent that adapts behavior based on opponent observations
    Implements continuous learning and opponent modeling with LOLA principles
    """
    
    def __init__(self, agent_id: int, input_dim: int = 4, hidden_dim: int = 64, lstm_hidden_dim: int = 64,
                 lr: float = 0.001, lola_lr: float = 0.001, gamma: float = 0.99,
                 opponent_memory_length: int = 10,
                 device: str = 'cpu'):
        self.agent_id = agent_id
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        self.lr = lr
        self.lola_lr = lola_lr
        self.gamma = gamma
        self.opponent_memory_length = opponent_memory_length
        self.device = device
        
        # Initialize networks
        self.policy_network = OnlineLOLANetwork(input_dim=input_dim, hidden_dim=hidden_dim, 
                                               output_dim=2, lstm_hidden_dim=lstm_hidden_dim).to(device)
        self.opponent_model = OnlineOpponentModel(input_dim=input_dim, hidden_dim=hidden_dim, 
                                                 lstm_hidden_dim=lstm_hidden_dim).to(device)
        
        # Optimizers
        self.policy_optimizer = torch.optim.Adam(self.policy_network.parameters(), lr=lr)
        self.opponent_optimizer = torch.optim.Adam(self.opponent_model.parameters(), lr=lr)
        
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
        self.lola_alpha = 0.1  # LOLA learning rate for opponent gradient
        self.lola_lambda = 0.5  # Weight for opponent-aware updates
        self.lookahead_steps = 1  # Number of lookahead steps
        
        # Experience buffer for online updates
        self.experience_buffer = deque(maxlen=1000)
        self.batch_size = 32
        
        # Current episode state
        self.current_policy_hidden = None
        self.current_opponent_hidden = None
        self.last_state = None
        self.last_action = None
        self.last_log_prob = None
        
        # Statistics
        self.cooperation_count = 0
        self.total_actions = 0
        self.update_count = 0
        
        # LOLA specific parameters
        self.lola_enabled = True
        self.opponent_lr_estimate = 0.1
    
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
        

    
    def _get_lola_action(self, obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float]:
        """
        Get action using pure LOLA with opponent-aware learning
        """
        obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
        batch_size = obs_tensor.size(0)

        # Initialize hidden states if None or wrong batch size
        if self.current_policy_hidden is None:
            self.current_policy_hidden = self.policy_network.get_initial_hidden_state(batch_size, self.device)
        elif self.current_policy_hidden[0].size(1) != batch_size:
            self.current_policy_hidden = self.policy_network.get_initial_hidden_state(batch_size, self.device)

        if self.current_opponent_hidden is None:
            self.current_opponent_hidden = self.opponent_model.get_initial_hidden_state(batch_size, self.device)
        elif self.current_opponent_hidden[0].size(1) != batch_size:
            self.current_opponent_hidden = self.opponent_model.get_initial_hidden_state(batch_size, self.device)

        # Get action from policy network
        with torch.no_grad():
            logits, opponent_logits, new_policy_hidden = self.policy_network.get_action_logits(obs_tensor, self.current_policy_hidden)
            opponent_probs, lr_pred, new_opponent_hidden = self.opponent_model.get_opponent_probs(obs_tensor, self.current_opponent_hidden)
        
        # Pure LOLA action selection with opponent modeling
        probs = F.softmax(logits, dim=-1)
        
        if deterministic:
            action = torch.argmax(probs, dim=-1).item()
        else:
            # Sample action with opponent-aware probabilities
            # Adjust probabilities based on opponent model
            opponent_action_probs = opponent_probs.squeeze(0)
            adjusted_probs = probs.squeeze(0) * (1 + self.lola_lambda * opponent_action_probs)
            adjusted_probs = adjusted_probs / adjusted_probs.sum()  # Renormalize
            
            action_dist = Categorical(adjusted_probs)
            action = action_dist.sample().item()
        
        log_prob = torch.log(probs.squeeze(0)[action] + 1e-8).item()

        # Update hidden states
        self.current_policy_hidden = new_policy_hidden
        self.current_opponent_hidden = new_opponent_hidden
        
        return action, log_prob
    
    def get_action(self, obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float, Optional[Tuple[np.ndarray, np.ndarray]]]:
        """
        Get action from observation using pure LOLA learning
        
        Returns:
            Tuple of (action, log_prob, new_hidden)
        """
        action, log_prob = self._get_lola_action(obs, deterministic)
        
        # Store for learning
        self.last_state = obs.copy()
        self.last_action = action
        self.last_log_prob = log_prob
        
        # Update statistics
        if action == 0:
            self.cooperation_count += 1
        self.total_actions += 1
        
        # Convert hidden state to numpy
        if self.current_policy_hidden is not None:
            h, c = self.current_policy_hidden
            hidden_numpy = (h.squeeze(0).cpu().numpy(), c.squeeze(0).cpu().numpy())
        else:
            hidden_numpy = None
        
        return action, log_prob, hidden_numpy
    
    def update(self, obs: np.ndarray, action: int, reward: float, next_obs: np.ndarray, done: bool):
        """
        Online update of policy and opponent model based on immediate experience
        """
        if self.last_state is None:
            return
        
        # Store experience
        experience = (self.last_state, action, reward, next_obs, done, self.last_log_prob)
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
        old_log_probs = torch.FloatTensor(np.array([exp[5] for exp in batch])).to(self.device)

        # Initialize hidden states for batch processing
        batch_size = states.size(0)
        policy_hidden = self.policy_network.get_initial_hidden_state(batch_size, self.device)
        opponent_hidden = self.opponent_model.get_initial_hidden_state(batch_size, self.device)

        # Policy update
        logits, opponent_logits, _ = self.policy_network.get_action_logits(states, policy_hidden)
        probs = F.softmax(logits, dim=-1)
        
        # Compute policy loss with LOLA correction
        action_probs = probs.gather(1, actions.unsqueeze(1)).squeeze(1)
        log_probs = torch.log(action_probs + 1e-8)
        
        # LOLA correction: consider opponent's learning
        if self.lola_enabled:
            opponent_probs, lr_pred, _ = self.opponent_model.get_opponent_probs(states, opponent_hidden)
            opponent_lr = lr_pred.squeeze(-1)
            
            # LOLA correction term
            lola_correction = 0.1 * opponent_lr * torch.sum(opponent_probs * log_probs.unsqueeze(1), dim=-1)
            policy_loss = -(log_probs + lola_correction).mean()
        else:
            policy_loss = -log_probs.mean()
        
        # Opponent model update
        opponent_logits_pred, lr_pred, _ = self.opponent_model(states, opponent_hidden)
        opponent_probs_pred = F.softmax(opponent_logits_pred, dim=-1)
        
        # Create target for opponent actions (assuming we can observe them)
        opponent_targets = torch.zeros_like(opponent_probs_pred)
        # Simplified version - in practice you'd need actual opponent action data
        opponent_targets[:, 0] = 0.5  # Assume uniform distribution initially
        opponent_targets[:, 1] = 0.5
        
        opponent_loss = F.mse_loss(opponent_probs_pred, opponent_targets)
        
        # Update networks
        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_network.parameters(), 1.0)
        self.policy_optimizer.step()
        
        self.opponent_optimizer.zero_grad()
        opponent_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.opponent_model.parameters(), 1.0)
        self.opponent_optimizer.step()
    
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
        return "lola_online"
    
    def save_model(self, filepath: str):
        """Save the agent's model and parameters"""
        model_data = {
            'policy_network_state_dict': self.policy_network.state_dict(),
            'opponent_model_state_dict': self.opponent_model.state_dict(),
            'policy_optimizer_state_dict': self.policy_optimizer.state_dict(),
            'opponent_optimizer_state_dict': self.opponent_optimizer.state_dict(),
            'agent_id': self.agent_id,
            'lr': self.lr,
            'lola_lr': self.lola_lr,
            'gamma': self.gamma,
            'opponent_memory_length': self.opponent_memory_length,
            'lola_alpha': self.lola_alpha,
            'lola_lambda': self.lola_lambda,
            'opponent_defection_rate': self.opponent_defection_rate,
            'cooperation_count': self.cooperation_count,
            'total_actions': self.total_actions,
            'update_count': self.update_count,
            'lola_enabled': self.lola_enabled
        }
        
        torch.save(model_data, filepath)
    
    def load_model(self, filepath: str):
        """Load the agent's model and parameters"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = torch.load(filepath, map_location=self.device, weights_only=False)
        
        # Handle different key naming conventions
        # Original LOLA models use 'policy_net_state_dict', online LOLA expects 'policy_network_state_dict'
        if 'policy_network_state_dict' in model_data:
            # New format
            self.policy_network.load_state_dict(model_data['policy_network_state_dict'])
            self.opponent_model.load_state_dict(model_data['opponent_model_state_dict'])
            self.policy_optimizer.load_state_dict(model_data['policy_optimizer_state_dict'])
            self.opponent_optimizer.load_state_dict(model_data['opponent_optimizer_state_dict'])
            
            self.agent_id = model_data['agent_id']
            self.lr = model_data['lr']
            self.lola_lr = model_data['lola_lr']
            self.gamma = model_data['gamma']
            self.opponent_memory_length = model_data['opponent_memory_length']
            
            # Load parameters
            self.lola_alpha = model_data.get('lola_alpha', 0.1)
            self.lola_lambda = model_data.get('lola_lambda', 0.5)
            self.opponent_defection_rate = model_data['opponent_defection_rate']
            self.cooperation_count = model_data['cooperation_count']
            self.total_actions = model_data['total_actions']
            self.update_count = model_data['update_count']
            self.lola_enabled = model_data['lola_enabled']
        elif 'policy_net_state_dict' in model_data:
            # Original format
            self.policy_network.load_state_dict(model_data['policy_net_state_dict'], strict=False)
            self.opponent_model.load_state_dict(model_data['opponent_model_state_dict'], strict=False)
            self.agent_id = model_data.get('agent_id', self.agent_id)

            self.lola_alpha = model_data.get('lola_alpha', self.lola_alpha)
            self.lola_lambda = model_data.get('lola_lambda', self.lola_lambda)
            self.opponent_defection_rate = model_data.get('opponent_defection_rate', self.opponent_defection_rate)
            self.cooperation_count = model_data.get('cooperation_count', self.cooperation_count)
            self.total_actions = model_data.get('total_actions', self.total_actions)
            self.update_count = model_data.get('update_count', self.update_count)
            self.lola_enabled = model_data.get('lola_enabled', self.lola_enabled)
        else:
            raise KeyError("No compatible policy network state dict found in checkpoint")
    
    def reset(self):
        """Reset agent state for new episode"""
        self.current_policy_hidden = None
        self.current_opponent_hidden = None
        self.last_state = None
        self.last_action = None
        self.last_log_prob = None
        # Keep networks intact for online learning
