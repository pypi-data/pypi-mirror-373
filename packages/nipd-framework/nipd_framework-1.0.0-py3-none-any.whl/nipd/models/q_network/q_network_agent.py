import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import deque

class QNetwork(nn.Module):
    """
    Recurrent Q-Network that learns a decision matrix for Prisoner's Dilemma
    Input: [own_prev_action, neighbor_prev_action, step_normalized, num_neighbors_normalized]
    Output: Q-values for [cooperate, defect] actions
    """
    
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64, lstm_hidden_dim: int = 64):
        super(QNetwork, self).__init__()
        
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
        
        # Initialize weights for stable learning
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
    
    def forward(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
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
        return self.forward(x, hidden_state)
    
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


class QNetworkAgent:
    """
    Q-Network agent that learns optimal actions based on decision matrix
    """
    
    def __init__(self, agent_id: int, input_dim: int = 4, hidden_dim: int = 64, 
                 lr: float = 1e-3, gamma: float = 0.99, epsilon: float = 0.1):
        self.agent_id = agent_id
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        
        # Initialize Q-network
        self.q_network = QNetwork(input_dim, hidden_dim)
        self.target_network = QNetwork(input_dim, hidden_dim)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer
        self.optimizer = torch.optim.Adam(self.q_network.parameters(), lr=lr)
        
        # Experience replay buffer
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # Hidden states for recurrent networks
        self.hidden_state = None
        self.target_hidden_state = None
        
        # Training metrics
        self.training_losses = []
        self.cooperation_rate = 0.5  # Initial neutral prior
        
        # Decision matrix tracking
        self.decision_matrix = {
            (0, 0): {'cooperate': 0, 'defect': 0},  # I cooperated, neighbor cooperated
            (0, 1): {'cooperate': 0, 'defect': 0},  # I cooperated, neighbor defected
            (1, 0): {'cooperate': 0, 'defect': 0},  # I defected, neighbor cooperated
            (1, 1): {'cooperate': 0, 'defect': 0}   # I defected, neighbor defected
        }
        
        logging.info(f"Q-Network Agent {agent_id} initialized with input_dim={input_dim}, hidden_dim={hidden_dim}")
    
    def get_action(self, observation: np.ndarray, deterministic: bool = False, 
                   hidden_state: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> Tuple[int, Optional[float], Tuple[np.ndarray, np.ndarray]]:
        """Get action from observation with hidden state"""
        # Agent simulator now provides 4-dimensional observations directly
        q_obs = observation
        
        # Convert observation to tensor
        obs_tensor = torch.tensor(q_obs, dtype=torch.float32).unsqueeze(0)
        
        # Convert hidden state if provided
        if hidden_state is not None:
            # Ensure hidden states are 3D: (num_layers, batch_size, hidden_dim)
            h_tensor = torch.FloatTensor(hidden_state[0]).unsqueeze(0)  # Add batch dimension
            c_tensor = torch.FloatTensor(hidden_state[1]).unsqueeze(0)  # Add batch dimension
            hidden_tensor = (h_tensor, c_tensor)
        else:
            hidden_tensor = self.hidden_state
        
        # Extract key features for decision matrix
        own_prev = int(q_obs[0]) if q_obs[0] in [0, 1] else 0
        neighbor_prev = int(q_obs[1]) if q_obs[1] in [0, 1] else 0
        
        # Get action from Q-network with hidden state
        if deterministic:
            action, q_values, new_hidden = self.q_network.get_action(obs_tensor, epsilon=0.0, hidden_state=hidden_tensor)
        else:
            action, q_values, new_hidden = self.q_network.get_action(obs_tensor, epsilon=self.epsilon, hidden_state=hidden_tensor)
        
        # Update hidden state
        self.hidden_state = new_hidden
        
                # Convert hidden state back to numpy - detach gradients first
        new_hidden_np = (new_hidden[0].squeeze(0).detach().cpu().numpy(), 
                         new_hidden[1].squeeze(0).detach().cpu().numpy())
        
        # Update decision matrix
        self._update_decision_matrix(own_prev, neighbor_prev, action)
        
        # Update cooperation rate
        self.cooperation_rate = 0.9 * self.cooperation_rate + 0.1 * (1 - action)
        
        return action, None, new_hidden_np  # No log probability for Q-learning
    
    def _update_decision_matrix(self, own_prev: int, neighbor_prev: int, action: int):
        """Update decision matrix with current action"""
        key = (own_prev, neighbor_prev)
        if key in self.decision_matrix:
            if action == 0:  # Cooperate
                self.decision_matrix[key]['cooperate'] += 1
            else:  # Defect
                self.decision_matrix[key]['defect'] += 1
    
    def store_experience(self, state: np.ndarray, action: int, reward: float, 
                        next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.memory.append((state, action, reward, next_state, done))
    
    def train_step(self) -> Optional[float]:
        """Train the Q-network on a batch of experiences"""
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch from memory
        batch = np.random.choice(len(self.memory), self.batch_size, replace=False)
        
        # Convert lists to numpy arrays first for better performance
        states_list = [self.memory[i][0] for i in batch]
        actions_list = [self.memory[i][1] for i in batch]
        rewards_list = [self.memory[i][2] for i in batch]
        next_states_list = [self.memory[i][3] for i in batch]
        dones_list = [self.memory[i][4] for i in batch]
        
        # Convert to tensors efficiently
        states = torch.tensor(np.array(states_list), dtype=torch.float32)
        actions = torch.tensor(np.array(actions_list), dtype=torch.long)
        rewards = torch.tensor(np.array(rewards_list), dtype=torch.float32)
        next_states = torch.tensor(np.array(next_states_list), dtype=torch.float32)
        dones = torch.tensor(np.array(dones_list), dtype=torch.bool)
        
        # Current Q-values (ignoring hidden states for batch training)
        current_q_values, _ = self.q_network.get_q_values(states)
        current_q = current_q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Next Q-values (using target network, ignoring hidden states for batch training)
        with torch.no_grad():
            next_q_values, _ = self.target_network.get_q_values(next_states)
            next_q = next_q_values.max(1)[0]
            target_q = rewards + (self.gamma * next_q * ~dones)
        
        # Compute loss
        loss = F.mse_loss(current_q, target_q)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # Store loss
        self.training_losses.append(loss.item())
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network with current network weights"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def get_cooperation_rate(self) -> float:
        """Get current cooperation rate"""
        return self.cooperation_rate
    
    def get_decision_matrix(self) -> Dict:
        """Get current decision matrix"""
        return self.decision_matrix.copy()
    
    def reset(self):
        """Reset agent state for new episode"""
        # Keep the learned Q-network but reset episode-specific state
        self.hidden_state = None
        self.target_hidden_state = None
    
    def set_eval_mode(self):
        """Set agent to evaluation mode"""
        self.q_network.eval()
        self.epsilon = 0.0  # No exploration during evaluation
    
    def set_train_mode(self):
        """Set agent to training mode"""
        self.q_network.train()
        self.epsilon = 0.1  # Restore exploration during training
    
    def save(self, filepath: str):
        """Save the Q-network"""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'decision_matrix': self.decision_matrix,
            'cooperation_rate': self.cooperation_rate,
            'training_losses': self.training_losses
        }, filepath)
        logging.info(f"Q-Network Agent {self.agent_id} saved to {filepath}")
    
    def load(self, filepath: str):
        """Load the Q-network"""
        checkpoint = torch.load(filepath, map_location='cpu')
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.decision_matrix = checkpoint.get('decision_matrix', self.decision_matrix)
        self.cooperation_rate = checkpoint.get('cooperation_rate', 0.5)
        self.training_losses = checkpoint.get('training_losses', [])
        logging.info(f"Q-Network Agent {self.agent_id} loaded from {filepath}")
    
    def get_info(self) -> Dict[str, any]:
        """Get agent information"""
        return {
            'id': self.agent_id,
            'type': 'q_network',
            'cooperation_rate': self.cooperation_rate,
            'decision_matrix': self.decision_matrix,
            'training_losses': self.training_losses
        }
    
    def get_initial_hidden_states(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get initial hidden states for LSTM networks"""
        batch_size = 1
        device = next(self.q_network.parameters()).device
        
        hidden_state = self.q_network.get_initial_hidden_state(batch_size, device)
        
        # Convert to numpy arrays for storage - ensure correct dimensions
        h_np = hidden_state[0].squeeze(0).cpu().numpy()  # Remove batch dimension
        c_np = hidden_state[1].squeeze(0).cpu().numpy()  # Remove batch dimension
        
        return (h_np, c_np)
    
    def get_lstm_hidden_dim(self) -> int:
        """Get LSTM hidden dimension"""
        return 64
    
    def get_gradient_norms(self) -> Dict[str, float]:
        """Get gradient norms for networks"""
        q_norm = 0.0
        
        if self.q_network is not None:
            q_norm = torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), float('inf'))
        
        return {
            'q_grad_norm': q_norm
        }
    
    def get_policy_entropy(self) -> float:
        """Compute policy entropy from Q-values using softmax"""
        if not hasattr(self, 'last_q_values') or self.last_q_values is None:
            return 0.0
        
        # Convert Q-values to probabilities using softmax
        probs = F.softmax(self.last_q_values, dim=-1)
        
        # Compute entropy: -sum(p * log(p))
        entropy = -torch.sum(probs * torch.log(probs + 1e-8))
        
        return entropy.item()
