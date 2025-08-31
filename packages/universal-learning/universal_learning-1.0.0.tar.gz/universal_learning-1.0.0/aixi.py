"""
===============================================================================
Author: Benedict Chen (benedict@benedictchen.com)
===============================================================================

💝 SUPPORT THIS WORK - PLEASE DONATE! 💝

PayPal Donation Link (COPY & PASTE):
https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Developing high-quality, research-backed software takes countless hours of study, 
implementation, testing, and documentation. Your support - whether a little or a LOT - 
makes this work possible and is deeply appreciated. 

Please consider donating based on how much this module impacts your life or work!

Buy Benedict a coffee, beer, or better! Your support makes advanced AI research 
accessible to everyone! ☕🍺🚀

===============================================================================
"""
"""
🤖 AIXI Agent - The Ultimate Artificial Intelligence
=====================================================

Based on: Marcus Hutter (2005) "Universal Artificial Intelligence: Sequential Decisions Based on Algorithmic Probability"

🎯 ELI5 Summary:
Imagine the smartest possible robot that can learn and adapt to ANY environment perfectly.
AIXI is the theoretical blueprint for such a robot! It combines the best prediction method
(Solomonoff induction) with the best decision-making (expectimax) to create an agent that
can master any learnable task optimally. It's like having a universal genius!

🔬 Research Background:
======================
Marcus Hutter's AIXI (2005) represents the theoretical pinnacle of artificial intelligence:

• 🎯 **UNIVERSAL OPTIMALITY**: Performs optimally in ANY computable environment
• 🧮 **MATHEMATICAL FOUNDATION**: Rigorous basis in algorithmic information theory  
• 🤖 **THEORETICAL LIMIT**: Defines the ultimate achievable intelligence
• 🎓 **RESEARCH IMPACT**: Fundamental framework for AGI research
• 📈 **PRACTICAL INSPIRATION**: Guides approximation algorithms for real agents

The AIXI Revolution:
- **Optimal Learning**: Uses Solomonoff induction for prediction
- **Optimal Planning**: Uses expectimax search for decisions
- **Universal Prior**: Works with any computable environment
- **Information Theory**: Balances exploration vs exploitation optimally

🏗️ Mathematical Framework:
==========================
AIXI agent selects action a_t that maximizes expected future reward:

a_t = argmax_a Σ_ω P(ω|h_t) max_{a_{t+1:m}} Σ_{o_{t+1:m}} P(o_{t+1:m}|h_t,a_t:m,ω) R(h_t,a_t:m,o_{t+1:m})

Where:
- ω: Environment programs
- P(ω|h_t): Posterior probability using Solomonoff induction
- R: Reward function
- h_t: History up to time t

🎨 ASCII Diagram - AIXI Architecture:
=====================================
    Environment ω₁, ω₂, ...
         ↕ observations/rewards
    ┌─────────────────────────┐
    │       AIXI AGENT        │
    │  ┌─────────────────────┐│
    │  │ Solomonoff Inductor ││ ← Universal Prediction
    │  │   P(o_{t+1}|h_t)   ││
    │  └─────────────────────┘│
    │           ↓             │
    │  ┌─────────────────────┐│
    │  │  Expectimax Search  ││ ← Optimal Planning  
    │  │   max E[R|a,h]     ││
    │  └─────────────────────┘│
    │           ↓             │
    │     Optimal Action      │
    └─────────────────────────┘
         ↕ actions

🚀 Key Features:
===============
✨ **Universal Intelligence**: Works optimally in any computable environment
🧠 **Theoretical Optimality**: Provably best possible performance  
🔍 **Bayesian Learning**: Updates beliefs using universal prior
⚡ **Expectimax Planning**: Considers all possible futures
🎯 **Exploration/Exploitation**: Optimal balance via information theory

📊 Applications:
===============
- AGI research benchmarking
- Optimal agent design principles
- Universal reinforcement learning
- Theoretical intelligence bounds
- Algorithm performance limits
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from collections import defaultdict
import random
import math

from .universal_learning import UniversalLearner, HypothesisProgram, Prediction
from .solomonoff_induction import SolomonoffInductor
from .kolmogorov_complexity import KolmogorovComplexityEstimator

@dataclass
class Action:
    """Represents an action in AIXI framework"""
    action_id: int
    action_data: Any
    description: str = ""
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Observation:
    """Represents an observation in AIXI framework"""
    observation_id: int
    observation_data: Any
    reward: float
    timestamp: int
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class HistoryStep:
    """Single step in agent's interaction history"""
    action: Optional[Action]
    observation: Observation
    step_number: int
    cumulative_reward: float

@dataclass
class EnvironmentModel:
    """Model of environment for AIXI planning"""
    program: str  # Program representing environment dynamics
    probability: float  # Prior probability of this model
    complexity: int  # Algorithmic complexity (Kolmogorov complexity approximation)
    accuracy: float  # Empirical accuracy on history
    description: str = ""

class AIXIEnvironment(ABC):
    """Abstract environment interface for AIXI agent"""
    
    @abstractmethod
    def reset(self) -> Observation:
        """Reset environment and return initial observation"""
        # Default implementation for basic environments
        # Subclasses should override for specific environment logic
        return Observation(percept=0, reward=0.0)
    
    @abstractmethod
    def step(self, action: Action) -> Observation:
        """Take action and return observation with reward"""
        # Default implementation - subclasses should override
        # Simple deterministic response based on action value
        percept = getattr(action, 'value', 0) % 10  # Wrap action to observation space
        reward = 1.0 if percept > 5 else 0.0  # Simple reward based on percept
        return Observation(percept=percept, reward=reward)
    
    @abstractmethod
    def get_action_space(self) -> List[Action]:
        """Get available actions"""
        # Default implementation - basic discrete action space
        return [Action(value=i) for i in range(10)]  # 10 discrete actions
    
    @abstractmethod  
    def get_observation_space(self) -> List[int]:
        """Get observation space dimensions"""
        # Default implementation - simple discrete observation space
        return [10]  # Single discrete observation dimension with 10 possible values

class AIXIAgent:
    """
    AIXI Agent - Theoretical optimal agent for general reinforcement learning
    
    Implements the AIXI framework which combines:
    1. Solomonoff induction for universal prediction
    2. Algorithmic information theory for model selection
    3. Expectimax search for optimal decision making
    4. Universal prior over all computable environments
    
    Note: This is a practical approximation of the theoretical AIXI agent,
    which is uncomputable in the general case.
    """
    
    def __init__(self,
                 action_space: List[Action],
                 observation_space: List[int],
                 horizon: int = 10,
                 max_models: int = 100,
                 solomonoff_approximation_depth: int = 50,
                 complexity_penalty: float = 1.0,
                 discount_factor: float = 0.95,
                 exploration_bonus: float = 0.1,
                 random_seed: Optional[int] = None):
        """
        Initialize AIXI Agent
        
        Args:
            action_space: Available actions
            observation_space: Observation space dimensions
            horizon: Planning horizon (search depth)
            max_models: Maximum number of environment models to maintain
            solomonoff_approximation_depth: Depth for Solomonoff approximation
            complexity_penalty: Weight for model complexity in selection
            discount_factor: Future reward discount factor
            exploration_bonus: Bonus for exploration
            random_seed: Random seed for reproducibility
        """
        self.action_space = action_space
        self.observation_space = observation_space
        self.horizon = horizon
        self.max_models = max_models
        self.solomonoff_approximation_depth = solomonoff_approximation_depth
        self.complexity_penalty = complexity_penalty
        self.discount_factor = discount_factor
        self.exploration_bonus = exploration_bonus
        
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        # Initialize components
        self.solomonoff_inductor = SolomonoffInductor(
            max_program_length=solomonoff_approximation_depth,
            time_limit=1.0  # 1 second per prediction
        )
        
        self.complexity_estimator = KolmogorovComplexityEstimator(
            approximation_method="lz_complexity"
        )
        
        # Agent state
        self.history = []  # List[HistoryStep]
        self.environment_models = []  # List[EnvironmentModel]
        self.step_count = 0
        self.total_reward = 0.0
        
        # Statistics
        self.decision_times = []
        self.model_updates = 0
        self.predictions_made = 0
        
        # Initialize universal prior over programs
        self._initialize_universal_prior()
        
    def _initialize_universal_prior(self):
        """Initialize universal prior over environment models"""
        # Start with some basic environment models
        basic_programs = [
            "return random_observation()",  # Random environment
            "return constant_observation(0)",  # Constant environment
            "return echo_last_action()",  # Echo environment
            "return modulo_environment(step % 2)",  # Periodic environment
        ]
        
        for i, program in enumerate(basic_programs):
            complexity = self.complexity_estimator.estimate_complexity(program)
            prior_prob = 2**(-complexity)  # Universal prior: 2^(-K(p))
            
            model = EnvironmentModel(
                program=program,
                probability=prior_prob,
                complexity=complexity,
                accuracy=0.5,  # Initial neutral accuracy
                description=f"Basic model {i}"
            )
            
            self.environment_models.append(model)
    
    def select_action(self, current_observation: Observation) -> Action:
        """
        Select optimal action using AIXI decision theory
        
        Implements the AIXI action selection:
        a_t = argmax_a Σ_e P(e|history) * expected_reward(a, e, horizon)
        
        Args:
            current_observation: Current observation from environment
            
        Returns:
            Selected optimal action
        """
        self.predictions_made += 1
        
        # Update models with new observation
        self._update_environment_models(current_observation)
        
        # Compute expected reward for each action using expectimax
        action_values = {}
        
        for action in self.action_space:
            # Compute expected value of this action across all models
            expected_value = 0.0
            total_model_probability = 0.0
            
            for model in self.environment_models:
                model_prob = self._compute_model_probability(model)
                
                if model_prob > 1e-10:  # Skip negligible models
                    # Estimate expected future reward under this model
                    future_value = self._expectimax_search(
                        action, model, self.horizon, current_observation
                    )
                    
                    expected_value += model_prob * future_value
                    total_model_probability += model_prob
            
            # Normalize by total probability
            if total_model_probability > 0:
                action_values[action.action_id] = expected_value / total_model_probability
            else:
                action_values[action.action_id] = 0.0
            
            # Add exploration bonus
            exploration_bonus = self._compute_exploration_bonus(action)
            action_values[action.action_id] += exploration_bonus
        
        # Select action with highest expected value
        best_action_id = max(action_values.keys(), key=lambda a: action_values[a])
        best_action = next(a for a in self.action_space if a.action_id == best_action_id)
        
        # Record decision
        self._record_decision(best_action, action_values)
        
        return best_action
    
    def _expectimax_search(self, action: Action, model: EnvironmentModel, 
                          depth: int, observation: Observation) -> float:
        """
        Expectimax search for future reward estimation
        
        Args:
            action: Action to evaluate
            model: Environment model to use
            depth: Remaining search depth
            observation: Current observation
            
        Returns:
            Expected future reward
        """
        if depth <= 0:
            return 0.0
        
        # Simulate taking action under this model
        predicted_obs = self._simulate_action(action, model, observation)
        immediate_reward = predicted_obs.reward
        
        if depth == 1:
            return immediate_reward
        
        # Recursively compute expected future reward
        future_values = []
        for next_action in self.action_space:
            future_value = self._expectimax_search(
                next_action, model, depth - 1, predicted_obs
            )
            future_values.append(future_value)
        
        # Max over actions, expectation over observations
        max_future_value = max(future_values) if future_values else 0.0
        discounted_future = self.discount_factor * max_future_value
        
        return immediate_reward + discounted_future
    
    def _simulate_action(self, action: Action, model: EnvironmentModel,
                        observation: Observation) -> Observation:
        """
        Simulate taking action under environment model
        
        This is a simplified simulation - in practice would run the model program
        
        Args:
            action: Action to simulate
            model: Environment model
            observation: Current observation
            
        Returns:
            Predicted next observation
        """
        # Simplified simulation based on model type
        if "random" in model.program:
            # Random observation
            obs_data = np.random.randint(0, 10)
            reward = np.random.uniform(-1, 1)
        elif "constant" in model.program:
            # Constant observation
            obs_data = 0
            reward = 0.0
        elif "echo" in model.program:
            # Echo last action
            obs_data = action.action_id
            reward = 0.1
        elif "modulo" in model.program:
            # Periodic environment
            obs_data = self.step_count % 3
            reward = 1.0 if obs_data == action.action_id % 3 else -0.1
        else:
            # Default random prediction
            obs_data = np.random.randint(0, len(self.observation_space))
            reward = np.random.uniform(-0.5, 0.5)
        
        return Observation(
            observation_id=len(self.history),
            observation_data=obs_data,
            reward=reward,
            timestamp=self.step_count + 1
        )
    
    def _update_environment_models(self, observation: Observation):
        """
        Update environment models based on new observation
        
        Args:
            observation: New observation to incorporate
        """
        self.model_updates += 1
        
        # Update accuracy of existing models
        for model in self.environment_models:
            # Check how well this model predicted the observation
            if len(self.history) > 0:
                last_step = self.history[-1]
                predicted_obs = self._simulate_action(
                    last_step.action, model, 
                    self.history[-2].observation if len(self.history) > 1 else observation
                )
                
                # Update model accuracy based on prediction error
                obs_error = abs(predicted_obs.observation_data - observation.observation_data)
                reward_error = abs(predicted_obs.reward - observation.reward)
                
                total_error = obs_error + reward_error
                accuracy_update = 1.0 / (1.0 + total_error)  # Higher accuracy for lower error
                
                # Exponential moving average
                alpha = 0.1
                model.accuracy = (1 - alpha) * model.accuracy + alpha * accuracy_update
        
        # Potentially generate new models using Solomonoff induction
        if len(self.history) > 10 and self.step_count % 10 == 0:
            self._generate_new_models()
    
    def _generate_new_models(self):
        """Generate new environment models using Solomonoff induction"""
        if len(self.environment_models) >= self.max_models:
            return
        
        # Extract sequence data from history
        history_sequence = []
        for step in self.history:
            if step.action:
                history_sequence.append(step.action.action_id)
            history_sequence.append(step.observation.observation_data)
        
        # Use Solomonoff induction to find patterns
        prediction = self.solomonoff_inductor.predict_next(history_sequence)
        
        # Generate new model based on discovered patterns
        if hasattr(prediction, 'hypothesis_program') and prediction.hypothesis_program:
            program = prediction.hypothesis_program.program_code
            complexity = self.complexity_estimator.estimate_complexity(program)
            
            # Create new model
            new_model = EnvironmentModel(
                program=program,
                probability=2**(-complexity),
                complexity=complexity,
                accuracy=0.5,
                description=f"Solomonoff-generated model {len(self.environment_models)}"
            )
            
            self.environment_models.append(new_model)
    
    def _compute_model_probability(self, model: EnvironmentModel) -> float:
        """
        Compute posterior probability of environment model
        
        Uses Bayes' theorem: P(model|history) ∝ P(history|model) * P(model)
        
        Args:
            model: Environment model
            
        Returns:
            Posterior probability of model
        """
        # Prior probability (algorithmic information theory)
        prior = model.probability
        
        # Likelihood based on accuracy
        likelihood = model.accuracy ** len(self.history)
        
        # Complexity penalty (Occam's razor)
        complexity_penalty = 2**(-self.complexity_penalty * model.complexity)
        
        # Posterior (unnormalized)
        posterior = prior * likelihood * complexity_penalty
        
        return posterior
    
    def _compute_exploration_bonus(self, action: Action) -> float:
        """
        Compute exploration bonus for action
        
        Args:
            action: Action to evaluate
            
        Returns:
            Exploration bonus value
        """
        # Count how often this action has been taken
        action_count = sum(1 for step in self.history 
                          if step.action and step.action.action_id == action.action_id)
        
        # UCB-style exploration bonus
        if action_count == 0:
            return self.exploration_bonus
        else:
            total_steps = len(self.history)
            exploration_bonus = self.exploration_bonus * math.sqrt(
                math.log(total_steps + 1) / action_count
            )
            return exploration_bonus
    
    def update_history(self, action: Action, observation: Observation):
        """
        Update agent's interaction history
        
        Args:
            action: Action taken
            observation: Observation received
        """
        self.step_count += 1
        self.total_reward += observation.reward
        
        step = HistoryStep(
            action=action,
            observation=observation,
            step_number=self.step_count,
            cumulative_reward=self.total_reward
        )
        
        self.history.append(step)
        
        # Prune history if it gets too long (for computational efficiency)
        max_history_length = 1000
        if len(self.history) > max_history_length:
            self.history = self.history[-max_history_length:]
    
    def _record_decision(self, action: Action, action_values: Dict[int, float]):
        """Record decision-making information for analysis"""
        decision_time = len(action_values) * 0.001  # Simplified timing
        self.decision_times.append(decision_time)
        
        # Could log more detailed decision information here
        
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        avg_reward_per_step = self.total_reward / max(self.step_count, 1)
        
        model_complexities = [model.complexity for model in self.environment_models]
        model_accuracies = [model.accuracy for model in self.environment_models]
        
        return {
            "total_steps": self.step_count,
            "total_reward": self.total_reward,
            "average_reward": avg_reward_per_step,
            "num_models": len(self.environment_models),
            "average_model_complexity": np.mean(model_complexities) if model_complexities else 0,
            "average_model_accuracy": np.mean(model_accuracies) if model_accuracies else 0,
            "model_updates": self.model_updates,
            "predictions_made": self.predictions_made,
            "average_decision_time": np.mean(self.decision_times) if self.decision_times else 0,
            "exploration_ratio": self._compute_exploration_ratio()
        }
    
    def _compute_exploration_ratio(self) -> float:
        """Compute ratio of exploratory actions"""
        if not self.history:
            return 0.0
        
        # Count actions taken more vs less frequently
        action_counts = defaultdict(int)
        for step in self.history:
            if step.action:
                action_counts[step.action.action_id] += 1
        
        if not action_counts:
            return 0.0
        
        total_actions = sum(action_counts.values())
        uniform_count = total_actions / len(self.action_space)
        
        # Measure deviation from uniform distribution
        deviations = [abs(count - uniform_count) for count in action_counts.values()]
        avg_deviation = np.mean(deviations)
        
        # Convert to exploration ratio (0 = pure exploitation, 1 = pure exploration)
        exploration_ratio = 1.0 - (avg_deviation / uniform_count) if uniform_count > 0 else 0.5
        return max(0.0, min(1.0, exploration_ratio))
    
    def get_model_summary(self) -> List[Dict[str, Any]]:
        """Get summary of current environment models"""
        model_summaries = []
        
        total_prob = sum(self._compute_model_probability(model) for model in self.environment_models)
        
        for i, model in enumerate(self.environment_models):
            prob = self._compute_model_probability(model)
            normalized_prob = prob / total_prob if total_prob > 0 else 0
            
            model_summaries.append({
                "model_id": i,
                "program": model.program[:50] + "..." if len(model.program) > 50 else model.program,
                "complexity": model.complexity,
                "accuracy": model.accuracy,
                "prior_probability": model.probability,
                "posterior_probability": normalized_prob,
                "description": model.description
            })
        
        # Sort by posterior probability
        model_summaries.sort(key=lambda x: x["posterior_probability"], reverse=True)
        
        return model_summaries
    
    def reset(self):
        """Reset agent state for new episode"""
        self.history.clear()
        self.step_count = 0
        self.total_reward = 0.0
        
        # Keep learned models but reset their accuracies
        for model in self.environment_models:
            model.accuracy = 0.5

# Utility classes and functions
class SimpleAIXIEnvironment(AIXIEnvironment):
    """Simple test environment for AIXI agent"""
    
    def __init__(self, pattern: str = "random"):
        self.pattern = pattern
        self.step_count = 0
        self.reset()
    
    def reset(self) -> Observation:
        self.step_count = 0
        return Observation(
            observation_id=0,
            observation_data=0,
            reward=0.0,
            timestamp=0
        )
    
    def step(self, action: Action) -> Observation:
        self.step_count += 1
        
        if self.pattern == "random":
            obs_data = np.random.randint(0, 3)
            reward = np.random.uniform(-1, 1)
        elif self.pattern == "echo":
            obs_data = action.action_id
            reward = 1.0 if action.action_id == 1 else -0.1
        elif self.pattern == "periodic":
            obs_data = self.step_count % 3
            reward = 1.0 if action.action_id == obs_data else -0.1
        else:
            obs_data = 0
            reward = 0.0
        
        return Observation(
            observation_id=self.step_count,
            observation_data=obs_data,
            reward=reward,
            timestamp=self.step_count
        )
    
    def get_action_space(self) -> List[Action]:
        return [
            Action(action_id=0, action_data="action_0"),
            Action(action_id=1, action_data="action_1"),
            Action(action_id=2, action_data="action_2")
        ]
    
    def get_observation_space(self) -> List[int]:
        return [0, 1, 2]

def run_aixi_experiment(environment: AIXIEnvironment, 
                       num_steps: int = 100,
                       agent_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run AIXI agent experiment
    
    Args:
        environment: Environment to run experiment in
        num_steps: Number of steps to run
        agent_config: Agent configuration
        
    Returns:
        Experiment results
    """
    if agent_config is None:
        agent_config = {}
    
    # Create AIXI agent
    agent = AIXIAgent(
        action_space=environment.get_action_space(),
        observation_space=environment.get_observation_space(),
        **agent_config
    )
    
    # Run experiment
    observation = environment.reset()
    rewards = []
    
    for step in range(num_steps):
        # Agent selects action
        action = agent.select_action(observation)
        
        # Environment responds
        new_observation = environment.step(action)
        
        # Agent updates history
        agent.update_history(action, new_observation)
        
        # Record reward
        rewards.append(new_observation.reward)
        
        observation = new_observation
    
    # Get final statistics
    performance_stats = agent.get_performance_statistics()
    model_summary = agent.get_model_summary()
    
    return {
        "rewards": rewards,
        "cumulative_reward": sum(rewards),
        "average_reward": np.mean(rewards),
        "performance_statistics": performance_stats,
        "model_summary": model_summary[:5],  # Top 5 models
        "num_steps": num_steps
    }

def compare_aixi_performance(environments: Dict[str, AIXIEnvironment],
                           num_steps: int = 100,
                           num_trials: int = 3) -> Dict[str, Any]:
    """
    Compare AIXI performance across multiple environments
    
    Args:
        environments: Dictionary of environment_name -> environment
        num_steps: Steps per trial
        num_trials: Number of trials per environment
        
    Returns:
        Comparison results
    """
    results = {}
    
    for env_name, environment in environments.items():
        env_results = []
        
        for trial in range(num_trials):
            trial_result = run_aixi_experiment(
                environment, num_steps,
                agent_config={"random_seed": trial}
            )
            env_results.append(trial_result["cumulative_reward"])
        
        results[env_name] = {
            "mean_reward": np.mean(env_results),
            "std_reward": np.std(env_results),
            "trials": env_results
        }
    
    return results