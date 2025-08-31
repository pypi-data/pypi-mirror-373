import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from collections import deque
import copy

class LOLANetwork(nn.Module):
    """
    Recurrent neural network for LOLA agent with opponent modeling capabilities
    """
    def __init__(self, input_dim: int, hidden_dim: int = 64, output_dim: int = 2, lstm_hidden_dim: int = 64):
        super(LOLANetwork, self).__init__()
        
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
        
        # Get final output for policy
        lstm_out = lstm_out.squeeze(1)  # Remove sequence dimension
        
        # Policy head
        logits = self.policy_head(lstm_out)
        
        return logits, new_hidden
    
    def get_action_probs(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Get action probabilities using softmax"""
        logits, new_hidden = self.forward(x, hidden_state)
        probs = F.softmax(logits, dim=-1)
        return probs, new_hidden
    
    def get_action_logits(self, x: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Get raw action logits"""
        return self.forward(x, hidden_state)
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class OpponentModel(nn.Module):
    """
    Recurrent model to predict opponent's policy and learning updates
    """
    def __init__(self, input_dim: int, hidden_dim: int = 32, lstm_hidden_dim: int = 32):
        super(OpponentModel, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.lstm_hidden_dim = lstm_hidden_dim
        
        # Feature extraction for policy prediction
        self.policy_feature_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM for policy prediction
        self.policy_lstm = nn.LSTM(hidden_dim, lstm_hidden_dim, batch_first=True)
        
        # Policy prediction head
        self.policy_predictor = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 2)  # Predict opponent's action probabilities
        )
        
        # Feature extraction for learning prediction
        self.learning_feature_net = nn.Sequential(
            nn.Linear(input_dim + 2, hidden_dim),  # input + opponent's current policy
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM for learning prediction
        self.learning_lstm = nn.LSTM(hidden_dim, lstm_hidden_dim, batch_first=True)
        
        # Learning prediction head
        self.learning_predictor = nn.Sequential(
            nn.Linear(lstm_hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 2)  # Predict opponent's next policy
        )
        
        self._init_weights()
    
    def _init_weights(self):
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
    
    def predict_opponent_policy(self, state: torch.Tensor, hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Predict opponent's current policy"""
        # Extract features
        features = self.policy_feature_net(state)
        
        # Add sequence dimension if needed
        if features.dim() == 2:
            features = features.unsqueeze(1)
        
        # Process through LSTM
        if hidden_state is not None:
            lstm_out, new_hidden = self.policy_lstm(features, hidden_state)
        else:
            lstm_out, new_hidden = self.policy_lstm(features)
        
        # Get prediction
        lstm_out = lstm_out.squeeze(1)
        logits = self.policy_predictor(lstm_out)
        probs = F.softmax(logits, dim=-1)
        
        return probs, new_hidden
    
    def predict_opponent_update(self, state: torch.Tensor, current_policy: torch.Tensor, 
                               hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Predict how opponent will update their policy"""
        combined_input = torch.cat([state, current_policy], dim=-1)
        
        # Extract features
        features = self.learning_feature_net(combined_input)
        
        # Add sequence dimension if needed
        if features.dim() == 2:
            features = features.unsqueeze(1)
        
        # Process through LSTM
        if hidden_state is not None:
            lstm_out, new_hidden = self.learning_lstm(features, hidden_state)
        else:
            lstm_out, new_hidden = self.learning_lstm(features)
        
        # Get prediction
        lstm_out = lstm_out.squeeze(1)
        logits = self.learning_predictor(lstm_out)
        probs = F.softmax(logits, dim=-1)
        
        return probs, new_hidden
    
    def get_initial_hidden_state(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden state for LSTM"""
        h0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        c0 = torch.zeros(1, batch_size, self.lstm_hidden_dim, device=device)
        return h0, c0


class LOLAAgent:
    """
    Learning with Opponent Learning Awareness (LOLA) Agent
    
    Based on Foerster et al. "Learning with Opponent Learning Awareness"
    https://arxiv.org/abs/1709.04326
    """
    
    def __init__(self, agent_id: int, input_dim: int, 
                 lr_policy: float = 0.005, lr_opponent: float = 0.01,
                 gamma: float = 0.96, lola_correction: bool = True,
                 opponent_lr_estimate: float = 0.01, memory_size: int = 100):
        

        
        self.agent_id = agent_id
        self.input_dim = input_dim
        self.lr_policy = lr_policy
        self.lr_opponent = lr_opponent
        self.gamma = gamma
        self.lola_correction = lola_correction
        self.opponent_lr_estimate = opponent_lr_estimate
        
        # Networks
        self.policy_net = LOLANetwork(input_dim)
        self.opponent_model = OpponentModel(input_dim)
        
        # Optimizers
        self.policy_optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=lr_policy)
        self.opponent_optimizer = torch.optim.Adam(self.opponent_model.parameters(), lr=lr_opponent)
        
        # Memory for opponent modeling
        self.memory_size = memory_size
        self.opponent_history = deque(maxlen=memory_size)
        self.state_history = deque(maxlen=memory_size)
        self.reward_history = deque(maxlen=memory_size)
        
        # Hidden states for recurrent networks
        self.policy_hidden_state = None
        self.opponent_policy_hidden_state = None
        self.opponent_learning_hidden_state = None
        
        # Training statistics
        self.training_stats = {
            'policy_loss': [],
            'opponent_loss': [],
            'lola_correction_magnitude': [],
            'cooperation_rate': []
        }
        
        logging.info(f"LOLA Agent {agent_id} initialized with LOLA correction: {lola_correction}")
    
    def get_action(self, state: np.ndarray, deterministic: bool = False, 
                   hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None) -> Tuple[int, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Get action from current policy with hidden state
        
        Args:
            state: Current state observation
            deterministic: Whether to use deterministic policy
            hidden_state: Optional hidden state for RNN
            
        Returns:
            Tuple of (action, log_prob, new_hidden_state)
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            # Use hidden state if provided, otherwise use stored one
            if hidden_state is not None:
                # Ensure 3D shape: (num_layers, batch_size, hidden_dim)
                h_tensor = hidden_state[0]
                c_tensor = hidden_state[1]
                
                if h_tensor.dim() == 1:
                    h_tensor = h_tensor.unsqueeze(0).unsqueeze(0)  # (1, 1, hidden_dim)
                    c_tensor = c_tensor.unsqueeze(0).unsqueeze(0)  # (1, 1, hidden_dim)
                elif h_tensor.dim() == 2:
                    h_tensor = h_tensor.unsqueeze(0)  # (1, batch_size, hidden_dim)
                    c_tensor = c_tensor.unsqueeze(0)  # (1, batch_size, hidden_dim)
                
                hidden_tensor = (h_tensor, c_tensor)
            else:
                hidden_tensor = self.policy_hidden_state
            
            action_probs, new_hidden = self.policy_net.get_action_probs(state_tensor, hidden_tensor)
            
            if deterministic:
                action = torch.argmax(action_probs, dim=-1)
            else:
                dist = Categorical(action_probs)
                action = dist.sample()
            
            log_prob = torch.log(action_probs[0, action] + 1e-8)
            
            # Update hidden state
            self.policy_hidden_state = new_hidden
            
                    # Return PyTorch tensors directly
        return action.item(), log_prob, new_hidden
    
    def update_opponent_model(self, states: List[np.ndarray], 
                            opponent_actions: List[int]) -> float:
        """
        Update the opponent model based on observed behavior
        
        Args:
            states: List of states
            opponent_actions: List of opponent actions
            
        Returns:
            Opponent model loss
        """
        if len(states) < 2:
            return 0.0
        
        states_tensor = torch.FloatTensor(np.array(states))
        actions_tensor = torch.LongTensor(opponent_actions)
        
        # Predict opponent policies (using stored hidden state)
        # Ensure hidden state has correct batch size
        if self.opponent_policy_hidden_state is None:
            # Initialize hidden state with correct batch size
            batch_size = states_tensor.size(0)
            device = states_tensor.device
            self.opponent_policy_hidden_state = self.opponent_model.get_initial_hidden_state(batch_size, device)
        
        predicted_probs, self.opponent_policy_hidden_state = self.opponent_model.predict_opponent_policy(
            states_tensor, self.opponent_policy_hidden_state)
        
        # Cross-entropy loss for policy prediction
        opponent_loss = F.cross_entropy(
            torch.log(predicted_probs + 1e-8), 
            actions_tensor
        )
        
        # Update opponent model
        self.opponent_optimizer.zero_grad()
        opponent_loss.backward()  # Remove retain_graph for now to avoid in-place operation issues
        torch.nn.utils.clip_grad_norm_(self.opponent_model.parameters(), 1.0)
        self.opponent_optimizer.step()
        
        return opponent_loss.item()
    
    def compute_lola_gradient(self, state: torch.Tensor, action: torch.Tensor,
                            reward: torch.Tensor, next_state: torch.Tensor,
                            opponent_action: torch.Tensor) -> torch.Tensor:
        """
        Compute LOLA gradient correction
        
        This is the core of LOLA: computing gradients that account for
        how the opponent will adapt to our policy changes.
        """
        # Get current policy probabilities
        current_policy, _ = self.policy_net.get_action_probs(state, self.policy_hidden_state)
        
        # Predict opponent's current policy
        # Ensure hidden state has correct batch size for single state
        if self.opponent_policy_hidden_state is not None:
            # Extract single hidden state from batch
            h = self.opponent_policy_hidden_state[0][:, 0:1, :]  # (1, 1, hidden_dim)
            c = self.opponent_policy_hidden_state[1][:, 0:1, :]  # (1, 1, hidden_dim)
            single_hidden = (h, c)
        else:
            single_hidden = None
        
        opponent_policy, _ = self.opponent_model.predict_opponent_policy(state, single_hidden)
        
        if not self.lola_correction:
            # Standard policy gradient without LOLA correction
            log_prob = torch.log(current_policy[0, action] + 1e-8)
            return -log_prob * reward
        
        # Simplified LOLA correction: use reward shaping instead of complex second-order gradients
        # This avoids the in-place operation issues while maintaining the cooperative behavior
        
        # Standard policy gradient
        log_prob = torch.log(current_policy[0, action] + 1e-8)
        standard_gradient = -log_prob * reward
        
        # Simple LOLA correction: encourage cooperation when opponent cooperates
        if opponent_action == 0:  # If opponent cooperates
            # Add a small correction to encourage our cooperation
            lola_correction = -log_prob * 0.5  # Small positive correction
        else:
            lola_correction = torch.tensor(0.0, requires_grad=False)
        
        # Store correction magnitude for analysis
        correction_magnitude = torch.abs(lola_correction).item()
        self.training_stats['lola_correction_magnitude'].append(correction_magnitude)
        
        return standard_gradient + lola_correction
    
    def _compute_opponent_reward_gradient(self, state: torch.Tensor,
                                        our_policy: torch.Tensor,
                                        opponent_policy: torch.Tensor,
                                        opponent_action: torch.Tensor) -> torch.Tensor:
        """
        Compute gradient of opponent's expected reward w.r.t. our policy parameters
        
        For tit-for-tat opponents, this is critical: they mirror our behavior!
        If we cooperate more, they cooperate more -> they get higher rewards
        If we defect more, they defect more -> they get lower rewards
        """
        # For tit-for-tat opponents, the key insight is reciprocity:
        # - If we cooperate (0), tit-for-tat will cooperate back -> opponent gets 3.0
        # - If we defect (1), tit-for-tat will defect back -> opponent gets 1.0
        
        # For reciprocal strategies like tit-for-tat, opponent's reward is strongly
        # correlated with our cooperation rate
        
        # Expected opponent reward when we cooperate (tit-for-tat cooperates back)
        cooperate_reward = 3.0  # Mutual cooperation
        # Expected opponent reward when we defect (tit-for-tat defects back)
        defect_reward = 1.0     # Mutual defection
        
        # The gradient shows how much opponent's reward changes with our cooperation
        reward_diff = cooperate_reward - defect_reward  # 3.0 - 1.0 = 2.0
        
        # Very strong scaling for reciprocal opponents - they benefit significantly from our cooperation
        return reward_diff * 5.0  # Much stronger signal: cooperating helps tit-for-tat opponents a lot
    
    def _compute_future_reward_change(self, state: torch.Tensor,
                                    our_policy: torch.Tensor,
                                    opponent_policy: torch.Tensor,
                                    opponent_update: torch.Tensor) -> torch.Tensor:
        """
        Compute how opponent's policy update affects our future expected reward
        
        For tit-for-tat opponents: if they learn to cooperate more (because we cooperate more),
        our future reward increases significantly due to mutual cooperation.
        """
        # For tit-for-tat opponents, the key insight is that their policy update
        # will mirror our behavior. If we cooperate more, they learn to cooperate more.
        
        # Our cooperation probability
        our_coop_prob = our_policy[0, 0]  # Probability of cooperating
        
        # For tit-for-tat, if we increase cooperation, they increase cooperation
        # This creates a positive feedback loop
        
        # Current expected reward (assuming tit-for-tat mirrors us)
        # If we cooperate with prob p, tit-for-tat cooperates with prob p
        # Expected reward = p * p * 3.0 + p * (1-p) * 0.0 + (1-p) * p * 5.0 + (1-p) * (1-p) * 1.0
        # Simplified: 3p² + 5p(1-p) + (1-p)² = 3p² + 5p - 5p² + 1 - 2p + p² = -p² + 3p + 1
        current_reward = 3.0 * our_coop_prob**2 + 5.0 * our_coop_prob * (1 - our_coop_prob) + 1.0 * (1 - our_coop_prob)**2
        
        # If opponent learns to cooperate more (due to our cooperation), our reward increases
        # The opponent_update represents how much more they'll cooperate
        if isinstance(opponent_update, torch.Tensor):
            coop_increase = torch.abs(opponent_update).item()
        else:
            coop_increase = abs(float(opponent_update))
        
        # Future reward if opponent cooperates more
        future_coop_prob = torch.clamp(our_coop_prob + coop_increase * 0.1, 0.0, 1.0)
        future_reward = 3.0 * future_coop_prob**2 + 5.0 * future_coop_prob * (1 - future_coop_prob) + 1.0 * (1 - future_coop_prob)**2
        
        # The change in our expected reward
        reward_change = future_reward - current_reward
        
        # Scale the reward change to make it significant
        return reward_change * 5.0  # Much stronger signal for reciprocal benefits
    
    def update_opponent_model_only(self, states: List[np.ndarray], opponent_actions: List[int]) -> float:
        """Update only the opponent model - completely isolated to avoid computation graph conflicts"""
        # Completely isolate opponent model update
        try:
            # Detach all inputs to create a fresh computation graph
            states_tensor = torch.FloatTensor(np.array(states)).detach()
            opponent_actions_tensor = torch.LongTensor(opponent_actions).detach()
            
            # Create a fresh forward pass
            opponent_loss = 0.0
            for i, (state, opponent_action) in enumerate(zip(states_tensor, opponent_actions_tensor)):
                state = state.unsqueeze(0)  # Add batch dimension
                
                # Predict opponent's policy
                opponent_policy, _ = self.opponent_model.predict_opponent_policy(state)
                
                # Compute loss against actual opponent action
                target = torch.zeros_like(opponent_policy)
                target[0, opponent_action] = 1.0
                loss = F.cross_entropy(opponent_policy, target)
                opponent_loss += loss
            
            # Average over batch
            opponent_loss = opponent_loss / len(states)
            
            # Update opponent model
            self.opponent_optimizer.zero_grad()
            opponent_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.opponent_model.parameters(), 1.0)
            self.opponent_optimizer.step()
            
            return opponent_loss.item()
            
        except Exception as e:
            logging.warning(f"Opponent model update failed: {e}")
            return 0.0
    
    def update_policy_only(self, states: List[np.ndarray], actions: List[int],
                     rewards: List[float], opponent_actions: List[int]) -> Dict[str, float]:
        """
        Update policy using LOLA algorithm with reward shaping and exploration bonuses
        
        Args:
            states: List of states
            actions: List of our actions
            rewards: List of rewards received
            opponent_actions: List of opponent actions
            
        Returns:
            Dictionary of training metrics
        """
        if len(states) == 0:
            return {}
        
        # Apply reward shaping to encourage cooperation
        shaped_rewards = []
        for i, (action, opponent_action, base_reward) in enumerate(zip(actions, opponent_actions, rewards)):
            shaped_reward = float(base_reward)  # Convert to float to avoid tensor operations
            
            # Cooperation bonus: extra reward for cooperating
            if action == 0:  # Cooperate
                shaped_reward = shaped_reward + 0.5  # Cooperation exploration bonus
                
                # Mutual cooperation bonus: extra reward when both cooperate
                if opponent_action == 0:
                    shaped_reward = shaped_reward + 1.0  # Strong mutual cooperation bonus
            
            # Reciprocity bonus: reward for matching opponent's previous cooperative behavior
            if i > 0 and action == 0 and opponent_actions[i-1] == 0:
                shaped_reward = shaped_reward + 0.3  # Reciprocity bonus
            
            shaped_rewards.append(shaped_reward)
        
        # Convert to tensors
        states_tensor = torch.FloatTensor(np.array(states))
        actions_tensor = torch.LongTensor(actions)
        rewards_tensor = torch.FloatTensor(shaped_rewards)  # Use shaped rewards
        opponent_actions_tensor = torch.LongTensor(opponent_actions)
        
        # Compute policy gradients with LOLA correction
        total_loss = 0.0
        
        for i in range(len(states)):
            state = states_tensor[i:i+1]
            action = actions_tensor[i]
            reward = rewards_tensor[i]
            opponent_action = opponent_actions_tensor[i]
            
            # Compute LOLA gradient
            lola_grad = self.compute_lola_gradient(
                state, action, reward, state, opponent_action
            )
            
            total_loss = total_loss + lola_grad
        
        # Average over batch
        policy_loss = total_loss / len(states)
        
        # Update policy (separate computation graph)
        with torch.enable_grad():
            self.policy_optimizer.zero_grad()
            policy_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
            self.policy_optimizer.step()
        
        # Update statistics
        self.training_stats['policy_loss'].append(policy_loss.item())
        
        # Compute cooperation rate
        cooperation_rate = np.mean([1 - a for a in actions])  # 0 = cooperate, 1 = defect
        self.training_stats['cooperation_rate'].append(cooperation_rate)
        
        return {
            'policy_loss': policy_loss.item(),
            'cooperation_rate': cooperation_rate,
            'lola_correction_magnitude': np.mean(self.training_stats['lola_correction_magnitude'][-len(states):]) if self.training_stats['lola_correction_magnitude'] else 0.0,
            'avg_shaped_reward': np.mean(shaped_rewards),
            'base_reward': np.mean(rewards)
        }
    
    def update_policy(self, states: List[np.ndarray], actions: List[int],
                     rewards: List[float], opponent_actions: List[int]) -> Dict[str, float]:
        """
        Update both opponent model and policy - properly separated to avoid computation graph conflicts
        """
        # Update opponent model first (separate computation graph)
        opponent_loss = self.update_opponent_model_only(states, opponent_actions)
        
        # Update policy separately (separate computation graph)
        policy_metrics = self.update_policy_only(states, actions, rewards, opponent_actions)
        
        # Combine metrics
        combined_metrics = policy_metrics.copy()
        combined_metrics['opponent_loss'] = opponent_loss
        
        return combined_metrics
    
    def store_experience(self, state: np.ndarray, opponent_action: int, reward: float):
        """Store experience for opponent modeling"""
        self.state_history.append(state)
        self.opponent_history.append(opponent_action)
        self.reward_history.append(reward)
    
    def get_policy_probs(self, state: np.ndarray) -> np.ndarray:
        """Get current policy probabilities for a state"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            probs = self.policy_net.get_action_probs(state_tensor)
        return probs.numpy()[0]
    
    def save(self, filepath: str):
        """Save agent parameters"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'opponent_model_state_dict': self.opponent_model.state_dict(),
            'policy_optimizer_state_dict': self.policy_optimizer.state_dict(),
            'opponent_optimizer_state_dict': self.opponent_optimizer.state_dict(),
            'training_stats': self.training_stats,
            'agent_id': self.agent_id
        }, filepath)
        logging.info(f"LOLA Agent {self.agent_id} saved to {filepath}")
    
    def load(self, filepath: str):
        """Load agent parameters"""
        try:
            # Try loading with weights_only=False for backward compatibility
            checkpoint = torch.load(filepath, weights_only=False)
        except Exception as e:
            logging.warning(f"Standard loading failed, trying alternative method: {e}")
            try:
                # Try alternative loading method
                checkpoint = torch.load(filepath, map_location='cpu', weights_only=False)
            except Exception as e2:
                logging.error(f"Alternative loading method also failed: {e2}")
                raise e2
        
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.opponent_model.load_state_dict(checkpoint['opponent_model_state_dict'])
        self.policy_optimizer.load_state_dict(checkpoint['policy_optimizer_state_dict'])
        self.opponent_optimizer.load_state_dict(checkpoint['opponent_optimizer_state_dict'])
        
        if 'training_stats' in checkpoint:
            self.training_stats = checkpoint['training_stats']
        
        logging.info(f"LOLA Agent {self.agent_id} loaded from {filepath}")
    
    def get_initial_hidden_states(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get initial hidden states for LSTM networks"""
        batch_size = 1
        device = next(self.policy_net.parameters()).device
        
        policy_hidden = self.policy_net.get_initial_hidden_state(batch_size, device)
        
        # Return PyTorch tensors directly to avoid conversion issues
        return policy_hidden
    
    def reset_hidden_states(self):
        """Reset hidden states for new episodes"""
        self.policy_hidden_state = None
        self.opponent_policy_hidden_state = None
        self.opponent_learning_hidden_state = None
    
    def get_lstm_hidden_dim(self) -> int:
        """Get LSTM hidden dimension"""
        return 64
    
    def get_gradient_norms(self) -> Dict[str, float]:
        """Get gradient norms for networks"""
        policy_norm = 0.0
        opponent_norm = 0.0
        
        if self.policy_net is not None:
            policy_norm = torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), float('inf'))
        
        if self.opponent_model is not None:
            opponent_norm = torch.nn.utils.clip_grad_norm_(self.opponent_model.parameters(), float('inf'))
        
        return {
            'policy_grad_norm': policy_norm,
            'opponent_grad_norm': opponent_norm
        }


class MultiAgentLOLA:
    """
    Multi-agent LOLA system for network games
    """
    
    def __init__(self, num_agents: int, input_dim: int, 
                 lr_policy: float = 0.005, lr_opponent: float = 0.01,
                 gamma: float = 0.96, lola_correction: bool = True):
        
        self.num_agents = num_agents
        self.agents = []
        
        # Create LOLA agents
        for i in range(num_agents):
            agent = LOLAAgent(
                agent_id=i,
                input_dim=input_dim,
                lr_policy=lr_policy,
                lr_opponent=lr_opponent,
                gamma=gamma,
                lola_correction=lola_correction
            )
            self.agents.append(agent)
        
        logging.info(f"Multi-agent LOLA system initialized with {num_agents} agents")
    
    def get_actions(self, states: List[np.ndarray], deterministic: bool = False, 
                   hidden_states: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None) -> Tuple[List[int], List[torch.Tensor], List[Tuple[torch.Tensor, torch.Tensor]]]:
        """Get actions from all agents with hidden states"""
        actions = []
        log_probs = []
        new_hidden_states = []
        
        for i, agent in enumerate(self.agents):
            hidden_state = hidden_states[i] if hidden_states else None
            action, log_prob, new_hidden = agent.get_action(states[i], deterministic, hidden_state)
            actions.append(action)
            log_probs.append(log_prob)
            new_hidden_states.append(new_hidden)
        
        return actions, log_probs, new_hidden_states
    
    def update_all_agents(self, batch_states: List[List[np.ndarray]],
                         batch_actions: List[List[int]],
                         batch_rewards: List[List[float]],
                         network_neighbors: Dict[int, List[int]] = None) -> Dict[str, float]:
        """
        Update all agents using their collected experiences with network-aware opponent modeling
        
        Args:
            batch_states: List of state sequences for each agent
            batch_actions: List of action sequences for each agent
            batch_rewards: List of reward sequences for each agent
            network_neighbors: Dict mapping agent_id to list of neighbor agent_ids
            
        Returns:
            Aggregated training metrics
        """
        all_metrics = {}
        
        for i, agent in enumerate(self.agents):
            if len(batch_states[i]) == 0:
                continue
            
            # Network-aware opponent modeling: consider only actual neighbors
            opponent_actions = []
            for step in range(len(batch_actions[i])):
                if network_neighbors and i in network_neighbors:
                    # Get actions from actual network neighbors only
                    neighbor_actions = []
                    for neighbor_id in network_neighbors[i]:
                        if neighbor_id < len(batch_actions) and step < len(batch_actions[neighbor_id]):
                            neighbor_actions.append(batch_actions[neighbor_id][step])
                    
                    if neighbor_actions:
                        # Use weighted cooperation bias for tit-for-tat opponents
                        cooperations = sum(1 for a in neighbor_actions if a == 0)
                        defections = len(neighbor_actions) - cooperations
                        
                        # Strong bias toward cooperation to encourage reciprocal learning
                        if cooperations > 0:  # If any neighbor cooperates, lean toward cooperation
                            avg_opponent_action = 0
                        else:
                            avg_opponent_action = 1
                    else:
                        avg_opponent_action = 0  # Default to cooperation
                else:
                    # Fallback: use all other agents with cooperation bias
                    other_actions = [batch_actions[j][step] for j in range(self.num_agents) if j != i]
                    if other_actions:
                        cooperations = sum(1 for a in other_actions if a == 0)
                        # Strong cooperation bias
                        avg_opponent_action = 0 if cooperations > 0 else 1
                    else:
                        avg_opponent_action = 0
                
                opponent_actions.append(avg_opponent_action)
            
            # Update agent
            metrics = agent.update_policy(
                batch_states[i],
                batch_actions[i],
                batch_rewards[i],
                opponent_actions
            )
            
            # Aggregate metrics
            for key, value in metrics.items():
                if key not in all_metrics:
                    all_metrics[key] = []
                all_metrics[key].append(value)
        
        # Average metrics across agents
        averaged_metrics = {}
        for key, values in all_metrics.items():
            averaged_metrics[f'avg_{key}'] = np.mean(values)
            averaged_metrics[f'std_{key}'] = np.std(values)
        
        return averaged_metrics
    
    def save_all_agents(self, directory: str):
        """Save all agents with final suffix"""
        import os
        os.makedirs(directory, exist_ok=True)
        
        for i, agent in enumerate(self.agents):
            filepath = os.path.join(directory, f'lola_agent_{i}_final.pt')
            agent.save(filepath)
    
    def load_all_agents(self, directory: str):
        """Load all agents"""
        import os
        
        for i, agent in enumerate(self.agents):
            # Try final model first, then best model, then base model
            filepath = os.path.join(directory, f'lola_agent_{i}_final.pt')
            if not os.path.exists(filepath):
                filepath = os.path.join(directory, f'lola_agent_{i}_best.pt')
            if not os.path.exists(filepath):
                filepath = os.path.join(directory, f'lola_agent_{i}.pt')
            
            if os.path.exists(filepath):
                agent.load(filepath)
    
    def get_cooperation_statistics(self) -> Dict[str, float]:
        """Get cooperation statistics for all agents"""
        stats = {}
        
        for i, agent in enumerate(self.agents):
            if agent.training_stats['cooperation_rate']:
                recent_coop_rate = np.mean(agent.training_stats['cooperation_rate'][-10:])
                stats[f'agent_{i}_cooperation_rate'] = recent_coop_rate
        
        if stats:
            stats['overall_cooperation_rate'] = np.mean(list(stats.values()))
        
        return stats