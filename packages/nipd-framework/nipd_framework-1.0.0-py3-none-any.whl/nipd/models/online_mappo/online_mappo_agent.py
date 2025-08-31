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

class OnlineCooperativeActorNetwork(nn.Module):
    """
    Online Recurrent Actor network for cooperative MAPPO - designed to promote cooperation
    Uses LSTM for temporal dependencies and online learning
    """
    def __init__(self, local_obs_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(OnlineCooperativeActorNetwork, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(local_obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM layer for temporal dependencies
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
                    if 'weight' in name:
                        nn.init.orthogonal_(param, gain=1.0)
                    elif 'bias' in name:
                        nn.init.constant_(param, 0)
    
    def forward(self, local_obs: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[Categorical, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Forward pass with LSTM hidden state"""
        batch_size = local_obs.size(0)
        
        # Extract features
        features = self.feature_net(local_obs)
        
        # Reshape for LSTM if needed
        if len(features.shape) == 2:
            features = features.unsqueeze(1)  # Add sequence dimension
        
        # LSTM forward pass
        lstm_out, hidden_state = self.lstm(features, hidden_state)
        
        # Policy head
        logits = self.policy_head(lstm_out.squeeze(1))
        
        # Add small noise to prevent deterministic behavior during training
        if self.training:
            logits = logits + torch.randn_like(logits) * 0.01
        
        dist = Categorical(logits=logits)
        
        return dist, hidden_state
    
    def get_action(self, local_obs: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None, deterministic: bool = False) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Sample action with optional deterministic mode and return hidden state"""
        dist, new_hidden_state = self.forward(local_obs, hidden_state)
        
        if deterministic:
            action = torch.argmax(dist.probs, dim=-1)
        else:
            action = dist.sample()
            
        log_prob = dist.log_prob(action)
        return action, log_prob, new_hidden_state
    
    def evaluate_actions(self, local_obs: torch.Tensor, actions: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Evaluate actions for training and return hidden state"""
        dist, new_hidden_state = self.forward(local_obs, hidden_state)
        log_probs = dist.log_prob(actions)
        entropy = dist.entropy()
        return log_probs, entropy, new_hidden_state
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OnlineCooperativeCriticNetwork(nn.Module):
    """
    Online Recurrent Critic network for cooperative MAPPO
    """
    def __init__(self, global_state_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(OnlineCooperativeCriticNetwork, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(global_state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM layer for temporal dependencies
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
                    if 'weight' in name:
                        nn.init.orthogonal_(param, gain=1.0)
                    elif 'bias' in name:
                        nn.init.constant_(param, 0)
    
    def forward(self, global_state: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Forward pass with LSTM hidden state"""
        batch_size = global_state.size(0)
        
        # Extract features
        features = self.feature_net(global_state)
        
        # Reshape for LSTM if needed
        if len(features.shape) == 2:
            features = features.unsqueeze(1)  # Add sequence dimension
        
        # LSTM forward pass
        lstm_out, hidden_state = self.lstm(features, hidden_state)
        
        # Value head
        value = self.value_head(lstm_out.squeeze(1))
        
        return value, hidden_state
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OnlineCooperativeMAPPOAgent:
    """
    Online Cooperative MAPPO agent that adapts behavior based on opponent observations
    Implements continuous learning and opponent modeling
    """
    
    def __init__(self, num_agents: int, local_obs_dim: int, global_state_dim: int,
                 lr_actor: float = 0.001, lr_critic: float = 0.003, gamma: float = 0.99,
                 gae_lambda: float = 0.95, clip_epsilon: float = 0.2, entropy_coef: float = 0.01,
                 value_coef: float = 0.5, cooperation_bonus: float = 0.1, max_grad_norm: float = 0.5,
                 opponent_memory_length: int = 10,
                 device: str = 'cpu'):
        self.num_agents = num_agents
        self.local_obs_dim = local_obs_dim
        self.global_state_dim = global_state_dim
        self.lr_actor = lr_actor
        self.lr_critic = lr_critic
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.cooperation_bonus = cooperation_bonus
        self.max_grad_norm = max_grad_norm
        self.opponent_memory_length = opponent_memory_length
        self.device = device
        
        # Initialize networks
        self.actor = OnlineCooperativeActorNetwork(local_obs_dim=local_obs_dim).to(device)
        self.critic = OnlineCooperativeCriticNetwork(global_state_dim=global_state_dim).to(device)
        
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
        self.last_local_obs = None
        self.last_global_state = None
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
        

    
    def _get_ppo_action(self, local_obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float, float]:
        """
        Get action using pure PPO policy network
        """
        local_obs_tensor = torch.FloatTensor(local_obs).unsqueeze(0).to(self.device)

        # Get action from actor network
        with torch.no_grad():
            action, log_prob, new_actor_hidden = self.actor.get_action(local_obs_tensor, self.current_actor_hidden, deterministic)
            # Create universal global state for pretrained model
            if self.global_state_dim == 22:  # Standard 20-agent pretrained model format
                # For action selection, create a simplified global state based on local observation
                # Approximation when episode history isn't available
                local_obs_np = local_obs_tensor.squeeze().cpu().numpy()
                
                # Create synthetic global state for 20-agent format
                global_state_np = np.zeros(22)
                
                # Use neighbor cooperation info to fill agent slots
                neighbor_coop_rate = local_obs_np[2]  # From observation[2]
                global_state_np[:20] = neighbor_coop_rate  # All agents use neighbor cooperation rate
                global_state_np[20] = neighbor_coop_rate   # Global cooperation rate
                global_state_np[21] = 0.5  # Normalized round (unknown during action selection)
                
                global_state_tensor = torch.FloatTensor(global_state_np).unsqueeze(0).to(self.device)
            else:
                # For other dimensions, use simple repeat approach
                global_state_tensor = local_obs_tensor.repeat(1, 6)[:, :self.global_state_dim]
            value, new_critic_hidden = self.critic(global_state_tensor, self.current_critic_hidden)
            value = value.item()

            # Normalize value for storage
            if self.value_normalization:
                value_tensor = torch.tensor([value], device=self.device)
                normalized_value_tensor = self._normalize_values(value_tensor)
                value = normalized_value_tensor.item()

        # Update hidden states (ensure they are proper tuples)
        if isinstance(new_actor_hidden, tuple) and len(new_actor_hidden) == 2:
            self.current_actor_hidden = new_actor_hidden
        else:
            self.current_actor_hidden = None

        if isinstance(new_critic_hidden, tuple) and len(new_critic_hidden) == 2:
            self.current_critic_hidden = new_critic_hidden
        else:
            self.current_critic_hidden = None

        return action.item(), log_prob.item(), value
    
    def get_action(self, local_obs: np.ndarray, deterministic: bool = False) -> Tuple[int, float, Optional[Tuple[np.ndarray, np.ndarray]]]:
        """
        Get action from observation using pure PPO policy

        Returns:
            Tuple of (action, log_prob, new_hidden)
        """
        action, log_prob, value = self._get_ppo_action(local_obs, deterministic)

        # Store for learning
        self.last_local_obs = local_obs.copy()
        self.last_global_state = self.last_local_obs.copy()
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
    
    def get_value(self, global_state: np.ndarray) -> float:
        """Get value estimate for global state"""
        global_state_tensor = torch.FloatTensor(global_state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            value, new_critic_hidden = self.critic(global_state_tensor, self.current_critic_hidden)
        
        # Update hidden state
        self.current_critic_hidden = new_critic_hidden
        
        return value.item()
    
    def update(self, local_obs: np.ndarray, global_state: np.ndarray, action: int, reward: float, 
               next_local_obs: np.ndarray, next_global_state: np.ndarray, done: bool):
        """
        Online update of policy and value function based on immediate experience
        """
        if self.last_local_obs is None:
            return
        
        # Store experience
        experience = (self.last_local_obs, self.last_global_state, action, reward, 
                     next_local_obs, next_global_state, done, self.last_log_prob, self.last_value)
        self.experience_buffer.append(experience)
        
        # Update opponent model if we have opponent action information
        if len(local_obs) > 1:
            opponent_action = int(local_obs[1] > 0.5)  # neighbor_prev action
            self._update_opponent_model(opponent_action, reward)
        
        # Update own history
        self.own_history.append(action)
        self.state_history.append(local_obs)
        
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
        local_obs = torch.FloatTensor(np.array([exp[0] for exp in batch])).to(self.device)
        # Ensure global states have correct dimensions
        global_state_list = []
        for exp in batch:
            global_state = exp[1]
            if len(global_state) < self.global_state_dim:
                # Pad with zeros if too short
                global_state = np.concatenate([global_state, np.zeros(self.global_state_dim - len(global_state))])
            elif len(global_state) > self.global_state_dim:
                # Truncate if too long
                global_state = global_state[:self.global_state_dim]
            global_state_list.append(global_state)

        global_states = torch.FloatTensor(np.array(global_state_list)).to(self.device)
        actions = torch.LongTensor(np.array([exp[2] for exp in batch])).to(self.device)
        rewards = torch.FloatTensor(np.array([exp[3] for exp in batch])).to(self.device)
        next_local_obs = torch.FloatTensor(np.array([exp[4] for exp in batch])).to(self.device)
        # Ensure next global states have correct dimensions
        next_global_state_list = []
        for exp in batch:
            next_global_state = exp[5]
            if len(next_global_state) < self.global_state_dim:
                # Pad with zeros if too short
                next_global_state = np.concatenate([next_global_state, np.zeros(self.global_state_dim - len(next_global_state))])
            elif len(next_global_state) > self.global_state_dim:
                # Truncate if too long
                next_global_state = next_global_state[:self.global_state_dim]
            next_global_state_list.append(next_global_state)

        next_global_states = torch.FloatTensor(np.array(next_global_state_list)).to(self.device)
        dones = torch.BoolTensor(np.array([exp[6] for exp in batch])).to(self.device)
        old_log_probs = torch.FloatTensor(np.array([exp[7] for exp in batch])).to(self.device)
        old_values = torch.FloatTensor(np.array([exp[8] for exp in batch])).to(self.device)
        
        # Compute advantages
        with torch.no_grad():
            next_values, _ = self.critic(next_global_states)
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
        log_probs, entropy, _ = self.actor.evaluate_actions(local_obs, actions)
        log_probs = log_probs.squeeze(-1)
        
        # Compute policy loss
        ratio = torch.exp(log_probs - old_log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages
        actor_loss = -torch.min(surr1, surr2).mean() - self.entropy_coef * entropy.mean()
        
        # Critic update
        values, _ = self.critic(global_states)
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
        return "ppo_online"
    
    def save_model(self, filepath: str):
        """Save the agent's model and parameters"""
        model_data = {
            'actor_state_dict': self.actor.state_dict(),
            'critic_state_dict': self.critic.state_dict(),
            'actor_optimizer_state_dict': self.actor_optimizer.state_dict(),
            'critic_optimizer_state_dict': self.critic_optimizer.state_dict(),
            'num_agents': self.num_agents,
            'local_obs_dim': self.local_obs_dim,
            'global_state_dim': self.global_state_dim,
            'lr_actor': self.lr_actor,
            'lr_critic': self.lr_critic,
            'gamma': self.gamma,
            'gae_lambda': self.gae_lambda,
            'clip_epsilon': self.clip_epsilon,
            'entropy_coef': self.entropy_coef,
            'value_coef': self.value_coef,
            'cooperation_bonus': self.cooperation_bonus,
            'max_grad_norm': self.max_grad_norm,
            'opponent_memory_length': self.opponent_memory_length,
            'strategy_mode': self.strategy_mode,
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
        
        self.num_agents = model_data['num_agents']
        self.local_obs_dim = model_data['local_obs_dim']
        self.global_state_dim = model_data['global_state_dim']
        self.lr_actor = model_data['lr_actor']
        self.lr_critic = model_data['lr_critic']
        self.gamma = model_data['gamma']
        self.gae_lambda = model_data['gae_lambda']
        self.clip_epsilon = model_data['clip_epsilon']
        self.entropy_coef = model_data['entropy_coef']
        self.value_coef = model_data['value_coef']
        self.cooperation_bonus = model_data['cooperation_bonus']
        self.max_grad_norm = model_data['max_grad_norm']
        self.opponent_memory_length = model_data['opponent_memory_length']
        self.strategy_mode = model_data['strategy_mode']
        self.opponent_defection_rate = model_data['opponent_defection_rate']
        self.cooperation_count = model_data['cooperation_count']
        self.total_actions = model_data['total_actions']
        self.update_count = model_data['update_count']
    
    def reset(self):
        """Reset agent state for new episode"""
        self.current_actor_hidden = None
        self.current_critic_hidden = None
        self.last_local_obs = None
        self.last_global_state = None
        self.last_action = None
        self.last_log_prob = None
        self.last_value = None
        # Keep networks intact for online learning
