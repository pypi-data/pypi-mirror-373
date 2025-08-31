import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import deque
import os
import json

class OnlineDecentralizedActorNetwork(nn.Module):
    """
    Online Actor network for decentralized PPO - each agent has its own policy
    Uses LSTM for temporal dependencies and online learning
    """
    def __init__(self, obs_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(OnlineDecentralizedActorNetwork, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM layer for sequence processing
        self.lstm = nn.LSTM(hidden_dim, lstm_hidden_dim, batch_first=True)
        
        # Policy head
        self.policy_head = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 2)  # 2 actions: Cooperate (0), Defect (1)
        )
        

        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights for stable learning"""
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
    
    def forward(self, obs: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[Categorical, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Forward pass with LSTM hidden state"""
        # Extract features
        features = self.feature_net(obs)
        
        # Add sequence dimension if needed
        if features.dim() == 2:
            features = features.unsqueeze(1)  # (batch, 1, hidden_dim)
        
        # Process through LSTM
        if hidden_state is not None:
            lstm_out, new_hidden = self.lstm(features, hidden_state)
        else:
            lstm_out, new_hidden = self.lstm(features)
        
        # Get final output for action prediction
        lstm_out = lstm_out.squeeze(1)  # Remove sequence dimension
        
        # Policy head
        logits = self.policy_head(lstm_out)
        
        return Categorical(logits=logits), new_hidden
    
    def get_action(self, obs: torch.Tensor, deterministic: bool = False, 
                   hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Sample action with optional deterministic mode and return hidden state"""
        dist, new_hidden = self.forward(obs, hidden_state)
        
        if deterministic:
            action = torch.argmax(dist.probs, dim=-1)
        else:
            action = dist.sample()
            
        log_prob = dist.log_prob(action)
        return action, log_prob, new_hidden
    
    def evaluate_actions(self, obs: torch.Tensor, actions: torch.Tensor, 
                        hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Evaluate actions for training and return hidden state"""
        dist, new_hidden = self.forward(obs, hidden_state)
        log_probs = dist.log_prob(actions)
        entropy = dist.entropy()
        return log_probs, entropy, new_hidden
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OnlineDecentralizedCriticNetwork(nn.Module):
    """
    Online Critic network for decentralized PPO
    """
    def __init__(self, obs_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(OnlineDecentralizedCriticNetwork, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM layer for sequence processing
        self.lstm = nn.LSTM(hidden_dim, lstm_hidden_dim, batch_first=True)
        
        # Value head
        self.value_head = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights for stable learning"""
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
    
    def forward(self, obs: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Forward pass with LSTM hidden state"""
        # Extract features
        features = self.feature_net(obs)
        
        # Add sequence dimension if needed
        if features.dim() == 2:
            features = features.unsqueeze(1)  # (batch, 1, hidden_dim)
        
        # Process through LSTM
        if hidden_state is not None:
            lstm_out, new_hidden = self.lstm(features, hidden_state)
        else:
            lstm_out, new_hidden = self.lstm(features)
        
        # Get final output for value prediction
        lstm_out = lstm_out.squeeze(1)  # Remove sequence dimension
        
        # Value head
        value = self.value_head(lstm_out)
        
        return value, new_hidden
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OnlineDecentralizedPPOAgent:
    """
    Online Decentralized PPO agent that adapts behavior based on opponent observations
    Implements continuous learning and opponent modeling
    """
    
    def __init__(self, agent_id: int, obs_dim: int = 4, lr_actor: float = 0.001, lr_critic: float = 0.003,
                 gamma: float = 0.99, gae_lambda: float = 0.95, clip_epsilon: float = 0.2,
                 entropy_coef: float = 0.01, value_coef: float = 0.5, max_grad_norm: float = 0.5,
                 opponent_memory_length: int = 10,
                 device: str = 'cpu'):
        self.agent_id = agent_id
        self.obs_dim = obs_dim
        self.lr_actor = lr_actor
        self.lr_critic = lr_critic
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.max_grad_norm = max_grad_norm
        self.opponent_memory_length = opponent_memory_length
        self.device = device
        
        # Initialize networks
        self.actor = OnlineDecentralizedActorNetwork(obs_dim=obs_dim).to(device)
        self.critic = OnlineDecentralizedCriticNetwork(obs_dim=obs_dim).to(device)
        
        # Optimizers
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=lr_actor)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=lr_critic)
        
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
        self.ppo_epochs = 4
        self.clip_ratio = 0.2
        self.value_loss_coef = 0.5
        self.entropy_coef = 0.01
        
        # Experience buffer for online updates
        self.experience_buffer = deque(maxlen=1000)
        self.batch_size = 32

        # Value normalization
        self.value_normalization = True
        self.value_running_mean = 0.0
        self.value_running_var = 1.0
        self.value_count = 1e-8  # Small count to avoid division by zero
        self.value_norm_clip = 10.0  # Clip normalized values to prevent extreme values
        
        # Current episode state
        self.current_actor_hidden = None
        self.current_critic_hidden = None
        self.last_state = None
        self.last_action = None
        self.last_log_prob = None
        self.last_value = None
        
        # Statistics
        self.cooperation_count = 0
        self.total_actions = 0
        self.update_count = 0
    
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
        

    
    def _get_ppo_action(self, obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float, float]:
        """
        Get action using pure PPO policy network
        """
        obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
        
        # Get action from actor network
        with torch.no_grad():
            action, log_prob, new_actor_hidden = self.actor.get_action(obs_tensor, deterministic, self.current_actor_hidden)
            value, new_critic_hidden = self.critic(obs_tensor, self.current_critic_hidden)
            value = value.item()

            # Normalize value for storage
            if self.value_normalization:
                value_tensor = torch.tensor([value], device=self.device)
                normalized_value_tensor = self._normalize_values(value_tensor)
                value = normalized_value_tensor.item()

        # Update hidden states
        self.current_actor_hidden = new_actor_hidden
        self.current_critic_hidden = new_critic_hidden

        return action.item(), log_prob.item(), value
    
    def get_action(self, obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float, Optional[Tuple[np.ndarray, np.ndarray]]]:
        """
        Get action from observation using pure PPO policy
        
        Returns:
            Tuple of (action, log_prob, new_hidden)
        """
        action, log_prob, value = self._get_ppo_action(obs, deterministic)
        
        # Store for learning
        self.last_state = obs.copy()
        self.last_action = action
        self.last_log_prob = log_prob
        self.last_value = value
        
        # Update statistics
        if action == 0:
            self.cooperation_count += 1
        self.total_actions += 1
        
        # Convert hidden state to numpy
        if self.current_actor_hidden is not None:
            h, c = self.current_actor_hidden
            hidden_numpy = (h.squeeze(0).cpu().numpy(), c.squeeze(0).cpu().numpy())
        else:
            hidden_numpy = None
        
        return action, log_prob, hidden_numpy
    
    def update(self, obs: np.ndarray, action: int, reward: float, next_obs: np.ndarray, done: bool):
        """
        Online update of policy and value function based on immediate experience
        """
        if self.last_state is None:
            return
        
        # Store experience
        experience = (self.last_state, action, reward, next_obs, done, self.last_log_prob, self.last_value)
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
        old_values = torch.FloatTensor(np.array([exp[6] for exp in batch])).to(self.device)
        
        # Compute advantages
        with torch.no_grad():
            next_values, _ = self.critic(next_states)
            next_values = next_values.squeeze(-1)

            # Normalize values for advantage computation
            if self.value_normalization:
                normalized_old_values = self._normalize_values(old_values)
                normalized_next_values = self._normalize_values(next_values)
                target_values = rewards + (self.gamma * normalized_next_values * ~dones)
                advantages = target_values - normalized_old_values
            else:
                target_values = rewards + (self.gamma * next_values * ~dones)
                advantages = target_values - old_values
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Actor update
        log_probs, entropy, _ = self.actor.evaluate_actions(states, actions)
        log_probs = log_probs.squeeze(-1)
        
        # Compute policy loss
        ratio = torch.exp(log_probs - old_log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages
        actor_loss = -torch.min(surr1, surr2).mean() - self.entropy_coef * entropy.mean()
        
        # Critic update
        values, _ = self.critic(states)
        values = values.squeeze(-1)

        # Normalize values for critic loss
        if self.value_normalization:
            normalized_values = self._normalize_values(values)
            normalized_target_values = self._normalize_values(target_values)
            critic_loss = F.mse_loss(normalized_values, normalized_target_values)
        else:
            critic_loss = F.mse_loss(values, target_values)
        
        # Update networks
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
        self.actor_optimizer.step()
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
        self.critic_optimizer.step()
    
    def get_cooperation_rate(self) -> float:
        """Get current cooperation rate"""
        if self.total_actions == 0:
            return 0.0
        return self.cooperation_count / self.total_actions
    
    def get_opponent_defection_rate(self) -> float:
        """Get opponent's defection rate"""
        return self.opponent_defection_rate
    
    def _normalize_values(self, values: torch.Tensor) -> torch.Tensor:
        """Normalize values using running statistics"""
        if not self.value_normalization:
            return values

        batch_count = values.numel()

        # Don't update statistics if we only have one sample (avoid variance issues)
        if batch_count > 1:
            # Update running statistics
            batch_mean = values.mean().item()
            batch_var = values.var().item()

            # Update running mean and variance
            delta = batch_mean - self.value_running_mean
            total_count = self.value_count + batch_count

            new_mean = self.value_running_mean + delta * batch_count / total_count
            m_a = self.value_running_var * self.value_count
            m_b = batch_var * batch_count
            m2 = m_a + m_b + delta ** 2 * self.value_count * batch_count / total_count
            new_var = m2 / total_count

            self.value_running_mean = new_mean
            self.value_running_var = new_var
            self.value_count = total_count

        # Normalize values
        if self.value_running_var > 0:
            normalized_values = (values - self.value_running_mean) / torch.sqrt(torch.tensor(self.value_running_var, device=values.device))
        else:
            normalized_values = values - self.value_running_mean

        # Clip to prevent extreme values
        return torch.clamp(normalized_values, -self.value_norm_clip, self.value_norm_clip)

    def get_strategy_mode(self) -> str:
        """Get current learning mode"""
        return "decentralized_ppo_online"
    
    def save_model(self, filepath: str):
        """Save the agent's model and parameters"""
        model_data = {
            'actor_state_dict': self.actor.state_dict(),
            'critic_state_dict': self.critic.state_dict(),
            'actor_optimizer_state_dict': self.actor_optimizer.state_dict(),
            'critic_optimizer_state_dict': self.critic_optimizer.state_dict(),
            'agent_id': self.agent_id,
            'lr_actor': self.lr_actor,
            'lr_critic': self.lr_critic,
            'gamma': self.gamma,
            'gae_lambda': self.gae_lambda,
            'clip_epsilon': self.clip_epsilon,
            'entropy_coef': self.entropy_coef,
            'value_coef': self.value_coef,
            'max_grad_norm': self.max_grad_norm,
            'opponent_memory_length': self.opponent_memory_length,
            'ppo_epochs': self.ppo_epochs,
            'clip_ratio': self.clip_ratio,
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
        
        self.actor.load_state_dict(model_data['actor_state_dict'])
        self.critic.load_state_dict(model_data['critic_state_dict'])
        self.actor_optimizer.load_state_dict(model_data['actor_optimizer_state_dict'])
        self.critic_optimizer.load_state_dict(model_data['critic_optimizer_state_dict'])
        
        self.agent_id = model_data['agent_id']
        self.lr_actor = model_data['lr_actor']
        self.lr_critic = model_data['lr_critic']
        self.gamma = model_data['gamma']
        self.gae_lambda = model_data['gae_lambda']
        self.clip_epsilon = model_data['clip_epsilon']
        self.entropy_coef = model_data['entropy_coef']
        self.value_coef = model_data['value_coef']
        self.max_grad_norm = model_data['max_grad_norm']
        self.opponent_memory_length = model_data['opponent_memory_length']
        self.ppo_epochs = model_data.get('ppo_epochs', 4)
        self.clip_ratio = model_data.get('clip_ratio', 0.2)
        self.opponent_defection_rate = model_data['opponent_defection_rate']
        self.cooperation_count = model_data['cooperation_count']
        self.total_actions = model_data['total_actions']
        self.update_count = model_data['update_count']
    
    def reset(self):
        """Reset agent state for new episode"""
        self.current_actor_hidden = None
        self.current_critic_hidden = None
        self.last_state = None
        self.last_action = None
        self.last_log_prob = None
        self.last_value = None
        # Keep networks intact for online learning
