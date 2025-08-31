import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

class DecentralizedActorNetwork(nn.Module):
    """
    Actor network for decentralized PPO - each agent has its own policy
    """
    def __init__(self, obs_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(DecentralizedActorNetwork, self).__init__()
        
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
    
    def forward(self, obs: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[Categorical, Tuple[torch.Tensor, torch.Tensor]]:
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


class DecentralizedCriticNetwork(nn.Module):
    """
    Critic network for decentralized PPO - each agent has its own value function
    """
    def __init__(self, obs_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(DecentralizedCriticNetwork, self).__init__()
        
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
        """Initialize weights for stable value learning"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=1.0)
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


class DecentralizedRolloutBuffer:
    """
    Rollout buffer for decentralized PPO - each agent has its own buffer
    """
    def __init__(self, max_size: int, obs_dim: int):
        self.max_size = max_size
        self.obs_dim = obs_dim
        
        # Initialize buffers
        self.observations = np.zeros((max_size, obs_dim), dtype=np.float32)
        self.actions = np.zeros(max_size, dtype=np.int64)
        self.rewards = np.zeros(max_size, dtype=np.float32)
        self.values = np.zeros(max_size, dtype=np.float32)
        self.log_probs = np.zeros(max_size, dtype=np.float32)
        self.dones = np.zeros(max_size, dtype=np.bool_)
        self.advantages = np.zeros(max_size, dtype=np.float32)
        self.returns = np.zeros(max_size, dtype=np.float32)
        
        # Hidden states for recurrent networks
        self.actor_hidden_states = []  # List of (h, c) tuples
        self.critic_hidden_states = []  # List of (h, c) tuples
        
        self.ptr = 0
        self.size = 0
    
    def store(self, obs: np.ndarray, action: int, reward: float, 
              value: float, log_prob: float, done: bool,
              actor_hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None,
              critic_hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None):
        """Store a step of experience with optional hidden states"""
        assert self.ptr < self.max_size
        
        self.observations[self.ptr] = obs
        self.actions[self.ptr] = action
        self.rewards[self.ptr] = reward
        self.values[self.ptr] = value
        self.log_probs[self.ptr] = log_prob
        self.dones[self.ptr] = done
        
        # Store hidden states if provided
        if actor_hidden_state is not None:
            self.actor_hidden_states.append(actor_hidden_state)
        if critic_hidden_state is not None:
            self.critic_hidden_states.append(critic_hidden_state)
        
        self.ptr += 1
        self.size = min(self.size + 1, self.max_size)
    
    def compute_advantages(self, gamma: float = 0.99, gae_lambda: float = 0.95, 
                          last_value: float = 0.0):
        """Compute advantages using GAE"""
        advantages = np.zeros(self.ptr)
        last_gae_lam = 0
        
        for step in reversed(range(self.ptr)):
            if step == self.ptr - 1:
                next_non_terminal = 1.0 - self.dones[step]
                next_value = last_value
            else:
                next_non_terminal = 1.0 - self.dones[step + 1]
                next_value = self.values[step + 1]
            
            # TD error
            delta = (self.rewards[step] + 
                    gamma * next_value * next_non_terminal - 
                    self.values[step])
            
            advantages[step] = last_gae_lam = (
                delta + gamma * gae_lambda * next_non_terminal * last_gae_lam
            )
        
        self.advantages[:self.ptr] = advantages
        self.returns[:self.ptr] = advantages + self.values[:self.ptr]
    
    def get_batch(self, batch_size: int) -> Dict[str, torch.Tensor]:
        """Get a random batch of experiences"""
        indices = np.random.choice(self.ptr, batch_size, replace=False)
        
        batch = {
            'observations': torch.FloatTensor(self.observations[indices]),
            'actions': torch.LongTensor(self.actions[indices]),
            'old_log_probs': torch.FloatTensor(self.log_probs[indices]),
            'advantages': torch.FloatTensor(self.advantages[indices]),
            'returns': torch.FloatTensor(self.returns[indices]),
            'values': torch.FloatTensor(self.values[indices])
        }
        
        # Add hidden states if available
        if self.actor_hidden_states and self.critic_hidden_states:
            # Convert hidden states to tensors
            actor_hidden_batch = []
            critic_hidden_batch = []
            
            for idx in indices:
                if idx < len(self.actor_hidden_states):
                    actor_hidden = self.actor_hidden_states[idx]
                    critic_hidden = self.critic_hidden_states[idx]
                    
                    # Convert numpy arrays to tensors with correct shape for LSTM
                    # LSTM expects (num_layers, batch_size, hidden_dim)
                    actor_h = (torch.FloatTensor(actor_hidden[0]).unsqueeze(1), torch.FloatTensor(actor_hidden[1]).unsqueeze(1))
                    critic_h = (torch.FloatTensor(critic_hidden[0]).unsqueeze(1), torch.FloatTensor(critic_hidden[1]).unsqueeze(1))
                    
                    actor_hidden_batch.append(actor_h)
                    critic_hidden_batch.append(critic_h)
                else:
                    # Create zero hidden states for missing indices
                    zero_hidden = (torch.zeros(1, 1, 64), torch.zeros(1, 1, 64))  # (num_layers, batch_size, hidden_dim)
                    actor_hidden_batch.append(zero_hidden)
                    critic_hidden_batch.append(zero_hidden)
            
            batch['actor_hidden_states'] = actor_hidden_batch
            batch['critic_hidden_states'] = critic_hidden_batch
        else:
            # Create default hidden states if none available
            batch_size = len(indices)
            zero_hidden = (torch.zeros(1, 1, 64), torch.zeros(1, 1, 64))  # (num_layers, batch_size, hidden_dim)
            batch['actor_hidden_states'] = [zero_hidden] * batch_size
            batch['critic_hidden_states'] = [zero_hidden] * batch_size
        
        return batch
    
    def clear(self):
        """Clear the buffer"""
        self.ptr = 0
        self.size = 0
        self.actor_hidden_states.clear()
        self.critic_hidden_states.clear()


class DecentralizedPPOAgent:
    """
    Decentralized PPO Agent - each agent trains independently
    """
    def __init__(self, agent_id: int, obs_dim: int, lr_actor: float = 3e-4, 
                 lr_critic: float = 1e-3, gamma: float = 0.99, gae_lambda: float = 0.95,
                 clip_epsilon: float = 0.2, entropy_coef: float = 0.01,
                 value_coef: float = 0.5, max_grad_norm: float = 0.5):
        
        self.agent_id = agent_id
        self.obs_dim = obs_dim
        
        # Hyperparameters
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.max_grad_norm = max_grad_norm
        
        # Networks - each agent has its own actor and critic
        self.actor = DecentralizedActorNetwork(obs_dim, lstm_hidden_dim=64)
        self.critic = DecentralizedCriticNetwork(obs_dim, lstm_hidden_dim=64)
        
        # Optimizers
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=lr_actor)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=lr_critic)
        
        # Rollout buffer - each agent has its own buffer
        self.buffer = DecentralizedRolloutBuffer(max_size=10000, obs_dim=obs_dim)
        
        # Training mode flag
        self.training_mode = True
        self.update_count = 0
        
        logging.info(f"Initialized Decentralized PPO Agent {agent_id} with obs_dim: {obs_dim}")
    
    def get_action(self, obs: np.ndarray, deterministic: bool = False, 
                   hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> Tuple[int, Optional[float], Tuple[np.ndarray, np.ndarray]]:
        """Get action for this agent with optional hidden state"""
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
            
            if hidden_state is not None:
                h_tensor = torch.FloatTensor(hidden_state[0]).unsqueeze(0)
                c_tensor = torch.FloatTensor(hidden_state[1]).unsqueeze(0)
                hidden_tensor = (h_tensor, c_tensor)
                action, log_prob, new_hidden = self.actor.get_action(obs_tensor, deterministic, hidden_tensor)
                new_hidden_np = (new_hidden[0].squeeze(0).cpu().numpy(), 
                                new_hidden[1].squeeze(0).cpu().numpy())
            else:
                action, log_prob, new_hidden = self.actor.get_action(obs_tensor, deterministic)
                new_hidden_np = (np.zeros(64), np.zeros(64))  # Default size
            
        return action[0].item(), log_prob[0].item(), new_hidden_np
    
    def get_value(self, obs: np.ndarray, hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> Tuple[float, Tuple[np.ndarray, np.ndarray]]:
        """Get value estimate for this agent with optional hidden state"""
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
            
            if hidden_state is not None:
                h_tensor = torch.FloatTensor(hidden_state[0]).unsqueeze(0)
                c_tensor = torch.FloatTensor(hidden_state[1]).unsqueeze(0)
                hidden_tensor = (h_tensor, c_tensor)
                value, new_hidden = self.critic(obs_tensor, hidden_tensor)
                new_hidden_np = (new_hidden[0].squeeze(0).cpu().numpy(), 
                                new_hidden[1].squeeze(0).cpu().numpy())
            else:
                value, new_hidden = self.critic(obs_tensor)
                new_hidden_np = (np.zeros(64), np.zeros(64))  # Default size
            
        return value.item(), new_hidden_np
    
    def store_experience(self, obs: np.ndarray, action: int, reward: float, 
                        value: float, log_prob: float, done: bool,
                        actor_hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                        critic_hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None):
        """Store experience in this agent's buffer with optional hidden states"""
        self.buffer.store(obs, action, reward, value, log_prob, done, 
                         actor_hidden_state, critic_hidden_state)
    
    def update(self, num_epochs: int = 10, batch_size: int = 64) -> Dict[str, float]:
        """Update networks using this agent's buffer"""
        if self.buffer.size == 0:
            return {}
        
        # Compute advantages
        self.buffer.compute_advantages(self.gamma, self.gae_lambda)
        
        # Training metrics
        total_actor_loss = 0
        total_critic_loss = 0
        total_entropy = 0
        num_updates = 0
        
        for epoch in range(num_epochs):
            # Number of batches per epoch
            num_batches = max(1, self.buffer.size // batch_size)
            
            for _ in range(num_batches):
                batch = self.buffer.get_batch(batch_size)
                
                # Actor update
                actor_loss, entropy = self._update_actor(batch)
                total_actor_loss += actor_loss
                total_entropy += entropy
                
                # Critic update
                critic_loss = self._update_critic(batch)
                total_critic_loss += critic_loss
                
                num_updates += 1
        
        self.update_count += 1
        
        # Average metrics
        metrics = {
            'actor_loss': total_actor_loss / num_updates,
            'critic_loss': total_critic_loss / num_updates,
            'entropy': total_entropy / num_updates,
            'buffer_size': self.buffer.size
        }
        
        return metrics
    
    def _update_actor(self, batch: Dict[str, torch.Tensor]) -> Tuple[float, float]:
        """Update actor network"""
        observations = batch['observations']
        actions = batch['actions']
        old_log_probs = batch['old_log_probs']
        advantages = batch['advantages']
        actor_hidden_states = batch['actor_hidden_states']
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Get current policy with hidden states
        # Handle batch of hidden states - each element is a tuple (h, c)
        batch_size = observations.size(0)
        new_log_probs_list = []
        entropy_list = []
        
        for i in range(batch_size):
            obs_i = observations[i:i+1]  # Keep batch dimension
            action_i = actions[i:i+1]
            hidden_i = actor_hidden_states[i]  # This is a tuple (h, c)
            
            log_probs_i, entropy_i, _ = self.actor.evaluate_actions(obs_i, action_i, hidden_i)
            new_log_probs_list.append(log_probs_i)
            entropy_list.append(entropy_i)
        
        new_log_probs = torch.cat(new_log_probs_list, dim=0)
        entropy = torch.cat(entropy_list, dim=0)
        
        # Compute ratio
        ratio = torch.exp(new_log_probs - old_log_probs)
        
        # Compute surrogate losses
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages
        
        # PPO loss
        actor_loss = -torch.min(surr1, surr2).mean()
        
        # Entropy loss
        entropy_loss = -self.entropy_coef * entropy.mean()
        
        # Total loss
        total_loss = actor_loss + entropy_loss
        
        # Update actor
        self.actor_optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
        self.actor_optimizer.step()
        
        return actor_loss.item(), entropy.mean().item()
    
    def _update_critic(self, batch: Dict[str, torch.Tensor]) -> float:
        """Update critic network"""
        observations = batch['observations']
        returns = batch['returns']
        critic_hidden_states = batch['critic_hidden_states']
        
        # Get current values with hidden states
        # Handle batch of hidden states - each element is a tuple (h, c)
        batch_size = observations.size(0)
        values_list = []
        
        for i in range(batch_size):
            obs_i = observations[i:i+1]  # Keep batch dimension
            hidden_i = critic_hidden_states[i]  # This is a tuple (h, c)
            
            value_i, _ = self.critic(obs_i, hidden_i)
            values_list.append(value_i)
        
        values = torch.cat(values_list, dim=0).squeeze()
        
        # Critic loss (MSE)
        critic_loss = F.mse_loss(values, returns)
        
        # Update critic
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
        self.critic_optimizer.step()
        
        return critic_loss.item()
    
    def save(self, filepath: str):
        """Save model parameters"""
        torch.save({
            'actor_state_dict': self.actor.state_dict(),
            'critic_state_dict': self.critic.state_dict(),
            'actor_optimizer_state_dict': self.actor_optimizer.state_dict(),
            'critic_optimizer_state_dict': self.critic_optimizer.state_dict(),
            'update_count': self.update_count,
        }, filepath)
        logging.info(f"Decentralized PPO Agent {self.agent_id} saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model parameters"""
        checkpoint = torch.load(filepath)
        self.actor.load_state_dict(checkpoint['actor_state_dict'])
        self.critic.load_state_dict(checkpoint['critic_state_dict'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer_state_dict'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer_state_dict'])
        
        if 'update_count' in checkpoint:
            self.update_count = checkpoint['update_count']
        
        logging.info(f"Decentralized PPO Agent {self.agent_id} loaded from {filepath}")
    
    def set_eval_mode(self):
        """Set networks to evaluation mode"""
        self.actor.eval()
        self.critic.eval()
        self.training_mode = False
    
    def set_train_mode(self):
        """Set networks to training mode"""
        self.actor.train()
        self.critic.train()
        self.training_mode = True
    
    def reset(self):
        """Reset agent state for new episodes"""
        # Clear the buffer for new episode
        self.buffer.clear()
    
    def get_cooperation_rate(self) -> float:
        """Get cooperation rate from recent actions in buffer"""
        if self.buffer.size == 0:
            return 0.5  # Neutral prior
        
        recent_actions = self.buffer.actions[:self.buffer.size]
        cooperation_rate = np.mean(recent_actions == 0)  # Action 0 is cooperate
        return cooperation_rate
    
    def get_gradient_norms(self) -> Dict[str, float]:
        """Get gradient norms for actor and critic networks"""
        actor_norm = 0.0
        critic_norm = 0.0
        
        if self.actor is not None:
            actor_norm = torch.nn.utils.clip_grad_norm_(self.actor.parameters(), float('inf'))
        
        if self.critic is not None:
            critic_norm = torch.nn.utils.clip_grad_norm_(self.critic.parameters(), float('inf'))
        
        return {
            'actor_grad_norm': actor_norm,
            'critic_grad_norm': critic_norm
        }
    
    def get_lstm_hidden_dim(self) -> int:
        """Get LSTM hidden dimension"""
        return 64
    
    def get_initial_hidden_states(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get initial hidden states for LSTM networks"""
        batch_size = 1
        device = next(self.actor.parameters()).device
        
        actor_hidden = self.actor.get_initial_hidden_state(batch_size, device)
        critic_hidden = self.critic.get_initial_hidden_state(batch_size, device)
        
        # Convert to numpy arrays for storage
        actor_hidden_np = (actor_hidden[0].cpu().numpy(), actor_hidden[1].cpu().numpy())
        critic_hidden_np = (critic_hidden[0].cpu().numpy(), critic_hidden[1].cpu().numpy())
        
        return actor_hidden_np, critic_hidden_np
