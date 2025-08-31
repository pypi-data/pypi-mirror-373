import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from tqdm import tqdm

class StandardActorNetwork(nn.Module):
    """
    Recurrent Actor network for standard MAPPO - no reward shaping
    """
    def __init__(self, local_obs_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(StandardActorNetwork, self).__init__()
        
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
    
    def forward(self, local_obs: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[Categorical, Tuple[torch.Tensor, torch.Tensor]]:
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


class StandardCriticNetwork(nn.Module):
    """
    Recurrent Critic network for standard MAPPO - uses global state information
    """
    def __init__(self, global_state_dim: int, hidden_dim: int = 128, lstm_hidden_dim: int = 64):
        super(StandardCriticNetwork, self).__init__()
        
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
        """Initialize weights for stable value learning"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=1.0)
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


class StandardRolloutBuffer:
    """
    Rollout buffer for standard MAPPO - stores shared experience
    """
    def __init__(self, max_size: int, num_agents: int, local_obs_dim: int, global_state_dim: int):
        """Initialize the rollout buffer"""
        self.max_size = max_size
        self.num_agents = num_agents
        self.local_obs_dim = local_obs_dim
        self.global_state_dim = global_state_dim
        
        # Experience data arrays
        self.local_observations = np.zeros((max_size, num_agents, local_obs_dim), dtype=np.float32)
        self.global_states = np.zeros((max_size, global_state_dim), dtype=np.float32)
        self.actions = np.zeros((max_size, num_agents), dtype=np.int64)
        self.rewards = np.zeros((max_size, num_agents), dtype=np.float32)
        self.values = np.zeros((max_size, num_agents), dtype=np.float32)
        self.log_probs = np.zeros((max_size, num_agents), dtype=np.float32)
        self.dones = np.zeros((max_size, num_agents), dtype=np.bool_)
        self.advantages = np.zeros((max_size, num_agents), dtype=np.float32)
        self.returns = np.zeros((max_size, num_agents), dtype=np.float32)
        
        # Hidden states for recurrent networks
        self.actor_hidden_states = np.zeros((max_size, num_agents, 2, 64), dtype=np.float32)  # (h, c) for each agent
        self.critic_hidden_states = np.zeros((max_size, 2, 64), dtype=np.float32)  # (h, c) for critic
        
        self.ptr = 0
        self.size = 0
    
    def store(self, local_obs: np.ndarray, global_state: np.ndarray, actions: np.ndarray, 
              rewards: np.ndarray, values: np.ndarray, log_probs: np.ndarray, dones: np.ndarray,
              actor_hidden_states: Optional[List[Tuple[np.ndarray, np.ndarray]]] = None,
              critic_hidden_states: Optional[List[Tuple[np.ndarray, np.ndarray]]] = None):
        """Store a step of experience with optional hidden states"""
        assert self.ptr < self.max_size
        
        self.local_observations[self.ptr] = local_obs
        self.global_states[self.ptr] = global_state
        self.actions[self.ptr] = actions
        self.rewards[self.ptr] = rewards
        self.values[self.ptr] = values
        self.log_probs[self.ptr] = log_probs
        self.dones[self.ptr] = dones
        

        if actor_hidden_states is not None:
            for i, (h, c) in enumerate(actor_hidden_states):
                if i < self.num_agents:  # Safety check
                    self.actor_hidden_states[self.ptr, i, 0] = h.flatten()[:64]  # Ensure correct size
                    self.actor_hidden_states[self.ptr, i, 1] = c.flatten()[:64]
        
        if critic_hidden_states is not None:
            h, c = critic_hidden_states
            self.critic_hidden_states[self.ptr, 0] = h.flatten()[:64]  # Ensure correct size
            self.critic_hidden_states[self.ptr, 1] = c.flatten()[:64]
        
        self.ptr += 1
        self.size = min(self.size + 1, self.max_size)
    
    def compute_advantages(self, gamma: float = 0.99, gae_lambda: float = 0.95, 
                          last_values: np.ndarray = None):
        """Compute advantages using GAE"""
        if last_values is None:
            last_values = np.zeros(self.num_agents)
        

        advantages = np.zeros((self.ptr, self.num_agents))
        returns = np.zeros((self.ptr, self.num_agents))
        
        for agent_id in range(self.num_agents):
            last_gae_lam = 0
            
            for step in reversed(range(self.ptr)):
                if step == self.ptr - 1:
                    next_non_terminal = 1.0 - self.dones[step, agent_id]
                    next_values = last_values[agent_id]
                else:
                    next_non_terminal = 1.0 - self.dones[step + 1, agent_id]
                    next_values = self.values[step + 1, agent_id]
                
                # TD error
                delta = (self.rewards[step, agent_id] + 
                        gamma * next_values * next_non_terminal - 
                        self.values[step, agent_id])
                
                advantages[step, agent_id] = last_gae_lam = (
                    delta + gamma * gae_lambda * next_non_terminal * last_gae_lam
                )
                
                # Compute returns (discounted cumulative rewards)
                if step == self.ptr - 1:
                    returns[step, agent_id] = (self.rewards[step, agent_id] + 
                                             gamma * last_values[agent_id] * next_non_terminal)
                else:
                    returns[step, agent_id] = (self.rewards[step, agent_id] + 
                                             gamma * returns[step + 1, agent_id] * next_non_terminal)
        
        self.advantages[:self.ptr] = advantages
        self.returns[:self.ptr] = returns
        

        if self.ptr > 0:
            adv_mean = np.mean(advantages[:self.ptr])
            adv_std = np.std(advantages[:self.ptr])
            adv_min = np.min(advantages[:self.ptr])
            adv_max = np.max(advantages[:self.ptr])
            
            # Only log warnings for extremely small advantages, not every time
            if abs(adv_mean) < 1e-4 and adv_std < 1e-4:
                logging.warning("WARNING: Advantages are extremely small! This will prevent learning.")
                logging.warning("Possible causes: Critic not learning, rewards too small, or gamma too low")
    
    def get_batch(self, batch_size: int) -> Dict[str, torch.Tensor]:
        """Get a random batch of experiences"""
        indices = np.random.choice(self.ptr, batch_size, replace=False)
        
        batch = {
            'local_observations': torch.FloatTensor(self.local_observations[indices]),
            'global_states': torch.FloatTensor(self.global_states[indices]),
            'actions': torch.LongTensor(self.actions[indices]),
            'old_log_probs': torch.FloatTensor(self.log_probs[indices]),
            'advantages': torch.FloatTensor(self.advantages[indices]),
            'returns': torch.FloatTensor(self.returns[indices]),
            'values': torch.FloatTensor(self.values[indices])
        }
        

        actor_hidden_batch = []
        critic_hidden_batch = []
        
        for idx in indices:
            # Extract actor hidden states for all agents at this timestep
            agent_hidden_states = []
            for agent_id in range(self.num_agents):
                h = torch.FloatTensor(self.actor_hidden_states[idx, agent_id, 0])
                c = torch.FloatTensor(self.actor_hidden_states[idx, agent_id, 1])
                agent_hidden_states.append((h, c))
            actor_hidden_batch.append(agent_hidden_states)
            
            # Extract critic hidden state at this timestep
            h = torch.FloatTensor(self.critic_hidden_states[idx, 0])
            c = torch.FloatTensor(self.critic_hidden_states[idx, 1])
            critic_hidden_batch.append((h, c))
        
        batch['actor_hidden_states'] = actor_hidden_batch
        batch['critic_hidden_states'] = critic_hidden_batch
        
        return batch
    
    def clear(self):
        """Clear the buffer"""
        self.ptr = 0
        self.size = 0
        # Hidden states are now arrays, so we just reset the pointer
        # The arrays will be overwritten when new experiences are stored


class StandardMAPPOAgent:
    """
    Standard MAPPO Agent - no reward shaping, standard training
    """
    def __init__(self, num_agents: int, local_obs_dim: int, global_state_dim: int,
                 lr_actor: float = 1e-4, lr_critic: float = 3e-4, gamma: float = 0.99,
                 gae_lambda: float = 0.95, clip_epsilon: float = 0.2, entropy_coef: float = 0.05,
                 value_coef: float = 0.5, cooperation_bonus: float = 0.0, max_grad_norm: float = 0.5):
        
        self.num_agents = num_agents
        self.local_obs_dim = local_obs_dim
        self.global_state_dim = global_state_dim
        
        # Hyperparameters
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.cooperation_bonus = cooperation_bonus  # Set to 0.0 for no reward shaping

        self.max_grad_norm = max_grad_norm
        
        # Networks
        self.actor = StandardActorNetwork(local_obs_dim, lstm_hidden_dim=64)
        self.critic = StandardCriticNetwork(global_state_dim, lstm_hidden_dim=64)
        
        # Optimizers
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=lr_actor)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=lr_critic)
        
        # Rollout buffer
        self.buffer = StandardRolloutBuffer(
            max_size=2048, 
            num_agents=num_agents,
            local_obs_dim=local_obs_dim,
            global_state_dim=global_state_dim
        )
        
        # Training mode flag
        self.training_mode = True
        self.update_count = 0
        
        logging.info(f"Initialized Standard MAPPO Agent with {num_agents} agents")
        logging.info(f"Local obs dim: {local_obs_dim}, Global state dim: {global_state_dim}")
    
    def get_initial_hidden_states(self) -> Tuple[List[Tuple[np.ndarray, np.ndarray]], Tuple[np.ndarray, np.ndarray]]:
        """Get initial hidden states for all agents"""
        device = next(self.actor.parameters()).device
        
        # Actor hidden states for each agent
        actor_hidden_states = []
        for _ in range(self.num_agents):
            h, c = self.actor.get_initial_hidden_state(1, device)
            actor_hidden_states.append((h.squeeze(0).cpu().numpy(), c.squeeze(0).cpu().numpy()))
        
        # Critic hidden state
        critic_h, critic_c = self.critic.get_initial_hidden_state(1, device)
        critic_hidden_state = (critic_h.squeeze(0).cpu().numpy(), critic_c.squeeze(0).cpu().numpy())
        
        return actor_hidden_states, critic_hidden_state
    
    def get_gradient_norms(self) -> Dict[str, float]:
        """Get gradient norms for actor and critic networks"""
        actor_norm = 0.0
        critic_norm = 0.0
        
        # Calculate actor gradient norm
        for param in self.actor.parameters():
            if param.grad is not None:
                actor_norm += param.grad.data.norm(2).item() ** 2
        actor_norm = actor_norm ** 0.5
        
        # Calculate critic gradient norm
        for param in self.critic.parameters():
            if param.grad is not None:
                critic_norm += param.grad.data.norm(2).item() ** 2
        critic_norm = critic_norm ** 0.5
        
        return {'actor': actor_norm, 'critic': critic_norm}
    
    def get_action(self, local_obs: np.ndarray, deterministic: bool = False, 
                  hidden_states: Optional[List[Tuple[np.ndarray, np.ndarray]]] = None) -> Tuple[np.ndarray, np.ndarray, List[Tuple[np.ndarray, np.ndarray]]]:
        """Get actions for all agents with recurrent hidden states"""
        with torch.no_grad():
            local_obs_tensor = torch.FloatTensor(local_obs)
            actions = []
            log_probs = []
            new_hidden_states = []
            
            for i in range(self.num_agents):
                if hidden_states is not None and i < len(hidden_states):
                    h, c = hidden_states[i]
                    h_tensor = torch.FloatTensor(h).unsqueeze(0)
                    c_tensor = torch.FloatTensor(c).unsqueeze(0)
                    hidden_state = (h_tensor, c_tensor)
                else:
                    hidden_state = None
                
                action, log_prob, new_hidden = self.actor.get_action(local_obs_tensor[i:i+1], hidden_state, deterministic)
                actions.append(action[0].item())
                log_probs.append(log_prob[0].item())
                new_hidden_states.append((new_hidden[0].squeeze(0).numpy(), new_hidden[1].squeeze(0).numpy()))
            
        return np.array(actions), np.array(log_probs), new_hidden_states
    
    def get_value(self, global_state: np.ndarray, hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """Get value estimates for all agents with recurrent hidden states"""
        with torch.no_grad():
            global_state_tensor = torch.FloatTensor(global_state).unsqueeze(0)
            
            if hidden_state is not None:
                h, c = hidden_state
                h_tensor = torch.FloatTensor(h).unsqueeze(0)
                c_tensor = torch.FloatTensor(c).unsqueeze(0)
                hidden_state_tensor = (h_tensor, c_tensor)
            else:
                hidden_state_tensor = None
            
            values, new_hidden = self.critic(global_state_tensor, hidden_state_tensor)
            
        return values.squeeze().numpy(), (new_hidden[0].squeeze(0).numpy(), new_hidden[1].squeeze(0).numpy())
    
    def store_experience(self, local_obs: np.ndarray, global_state: np.ndarray, 
                        actions: np.ndarray, rewards: np.ndarray, 
                        values: np.ndarray, log_probs: np.ndarray, dones: np.ndarray,
                        actor_hidden_states: Optional[List[Tuple[np.ndarray, np.ndarray]]] = None,
                        critic_hidden_states: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                        shaped_rewards: Optional[np.ndarray] = None):
        """
        Store experience in the buffer with optional hidden states
        
        Args:
            rewards: Base rewards (actual game rewards following rules)
            shaped_rewards: Shaped rewards for learning (if None, use base rewards)
        """
        # Use shaped rewards for learning if provided, otherwise use base rewards
        learning_rewards = shaped_rewards if shaped_rewards is not None else rewards
        
        self.buffer.store(local_obs, global_state, actions, learning_rewards, values, log_probs, dones,
                         actor_hidden_states, critic_hidden_states)
    
    def update(self, num_epochs: int = 10, batch_size: int = 64) -> Dict[str, float]:
        """Update networks using the buffer"""
        if self.buffer.size == 0:
            return {}
        
        # Compute advantages
        self.buffer.compute_advantages(self.gamma, self.gae_lambda)
        
        # Training metrics
        total_actor_loss = 0
        total_critic_loss = 0
        total_entropy = 0
        num_updates = 0
        
        # Progress bar for agent updates
        with tqdm(total=num_epochs, desc="Agent Update", leave=False, ncols=60) as update_pbar:
            for epoch in range(num_epochs):
                # Use smaller batch size if buffer is small, but ensure we get multiple batches
                effective_batch_size = min(batch_size, max(1, self.buffer.size // 2))  # At least 2 batches
                num_batches = max(2, self.buffer.size // effective_batch_size)
                
                for _ in range(num_batches):
                    batch = self.buffer.get_batch(effective_batch_size)
                    
                    # Actor update
                    actor_loss, entropy = self._update_actor(batch)
                    total_actor_loss += actor_loss
                    total_entropy += entropy
                    
                    # Critic update
                    critic_loss = self._update_critic(batch)
                    total_critic_loss += critic_loss
                    
                    num_updates += 1
                
                # Update progress bar
                update_pbar.set_postfix({
                    'Actor Loss': f'{total_actor_loss/(epoch+1):.4f}',
                    'Critic Loss': f'{total_critic_loss/(epoch+1):.4f}'
                })
                update_pbar.update(1)
        
        self.update_count += 1
        
        # Average metrics
        metrics = {
            'actor_loss': total_actor_loss / num_updates,
            'critic_loss': total_critic_loss / num_updates,
            'entropy': total_entropy / num_updates,
            'buffer_size': self.buffer.size
        }
        

        if total_actor_loss == 0:
            logging.warning(f"DEBUG: Actor loss is 0! total_actor_loss={total_actor_loss}, num_updates={num_updates}")
            logging.warning(f"DEBUG: Buffer size={self.buffer.size}, num_epochs={num_epochs}, batch_size={batch_size}")
        
        return metrics
    
    def _update_actor(self, batch: Dict[str, torch.Tensor]) -> Tuple[float, float]:
        """Update actor network"""
        local_observations = batch['local_observations']
        actions = batch['actions']
        old_log_probs = batch['old_log_probs']
        advantages = batch['advantages']
        actor_hidden_states = batch['actor_hidden_states']
        
        # Normalize advantages properly
        advantage_std = advantages.std()
        if advantage_std > 1e-8:
            advantages = (advantages - advantages.mean()) / (advantage_std + 1e-8)
        # No artificial scaling - let the advantages be natural
        

        batch_size = local_observations.size(0)
        num_agents = local_observations.size(1)
        
        # Reshape to process all agents in the batch together
        # Shape: (batch_size * num_agents, obs_dim)
        obs_flat = local_observations.view(-1, local_observations.size(-1))
        actions_flat = actions.view(-1)
        advantages_flat = advantages.view(-1)
        old_log_probs_flat = old_log_probs.view(-1)
        
        # Get hidden states for the flattened batch
        if actor_hidden_states:
            # Extract hidden states for each batch item and agent
            h_states = []
            c_states = []
            for i in range(batch_size):
                for j in range(num_agents):
                    if i < len(actor_hidden_states) and j < len(actor_hidden_states[i]):
                        h, c = actor_hidden_states[i][j]
                        if isinstance(h, np.ndarray):
                            h_states.append(torch.FloatTensor(h))
                            c_states.append(torch.FloatTensor(c))
                        else:
                            h_states.append(h.squeeze())
                            c_states.append(c.squeeze())
                    else:
                        # Default hidden state
                        h_states.append(torch.zeros(64))
                        c_states.append(torch.zeros(64))
            
            # Stack hidden states
            h_batch = torch.stack(h_states).unsqueeze(0)  # (1, batch_size*num_agents, hidden_dim)
            c_batch = torch.stack(c_states).unsqueeze(0)
            hidden_state = (h_batch, c_batch)
        else:
            hidden_state = None
        
        # Get current policy with hidden states
        new_log_probs, entropy, _ = self.actor.evaluate_actions(obs_flat, actions_flat, hidden_state)
        
        # Compute ratio
        ratio = torch.exp(new_log_probs - old_log_probs_flat)
        
        # Compute surrogate losses
        surr1 = ratio * advantages_flat
        surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages_flat
        
        # Actor loss (standard PPO surrogate loss)
        actor_loss = -torch.min(surr1, surr2).mean()
        

        if actor_loss.item() == 0:
            logging.warning(f"DEBUG: Actor loss is 0! surr1_mean={surr1.mean().item():.6f}, surr2_mean={surr2.mean().item():.6f}")
            logging.warning(f"DEBUG: ratio_mean={ratio.mean().item():.6f}, advantages_mean={advantages_flat.mean().item():.6f}")
        
        entropy_loss = -self.entropy_coef * entropy.mean()
        
        total_loss = actor_loss + entropy_loss
        
        # Update actor
        self.actor_optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
        self.actor_optimizer.step()
        
        return actor_loss.item(), entropy.mean().item()
    
    def _update_critic(self, batch: Dict[str, torch.Tensor]) -> float:
        """Update critic network"""
        global_states = batch['global_states']
        returns = batch['returns']
        critic_hidden_states = batch['critic_hidden_states']
        

        batch_size = global_states.size(0)
        
        # Get hidden states for the batch
        if critic_hidden_states:
            # Extract hidden states for each batch item
            h_states = []
            c_states = []
            for i in range(batch_size):
                if i < len(critic_hidden_states):
                    h, c = critic_hidden_states[i]
                    if isinstance(h, np.ndarray):
                        h_states.append(torch.FloatTensor(h))
                        c_states.append(torch.FloatTensor(c))
                    else:
                        h_states.append(h.squeeze())
                        c_states.append(c.squeeze())
                else:
                    # Default hidden state
                    h_states.append(torch.zeros(64))
                    c_states.append(torch.zeros(64))
            
            # Stack hidden states
            h_batch = torch.stack(h_states).unsqueeze(0)  # (1, batch_size, hidden_dim)
            c_batch = torch.stack(c_states).unsqueeze(0)
            hidden_state = (h_batch, c_batch)
        else:
            hidden_state = None
        
        # Get current values with hidden states
        values, _ = self.critic(global_states, hidden_state)
        values = values.squeeze()
        

        # The critic outputs one value per global state, but returns has shape (batch_size, num_agents)
        returns_mean = returns.mean(dim=1)  # Average across agents
        
        # Critic loss (MSE)
        critic_loss = F.mse_loss(values, returns_mean)
        
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
        logging.info(f"Standard MAPPO Agent saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model parameters"""
        checkpoint = torch.load(filepath)
        self.actor.load_state_dict(checkpoint['actor_state_dict'])
        self.critic.load_state_dict(checkpoint['critic_state_dict'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer_state_dict'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer_state_dict'])
        
        if 'update_count' in checkpoint:
            self.update_count = checkpoint['update_count']
        
        logging.info(f"Standard MAPPO Agent loaded from {filepath}")
    
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
    
    def get_lstm_hidden_dim(self) -> int:
        """Get the LSTM hidden dimension"""
        return self.actor.lstm_hidden_dim
