# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/universal-learning/workflows/CI/badge.svg)](https://github.com/benedictchen/universal-learning/actions)
[![PyPI version](https://img.shields.io/pypi/v/universal-learning.svg)](https://pypi.org/project/universal-learning/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Universal Learning

🧠 **Solomonoff's Universal Induction and Hutter's AIXI for theoretically optimal learning and decision making**

Universal Learning implements the theoretical foundations of artificial general intelligence through algorithmic information theory. This provides research-accurate implementations of Solomonoff induction and AIXI – the mathematical frameworks for optimal inductive inference and universal artificial intelligence.

**Research Foundation**: Solomonoff, R. J. (1964) - *"A Formal Theory of Inductive Inference"* | Hutter, M. (2005) - *"Universal Artificial Intelligence"*

## 🚀 Quick Start

### Installation

```bash
pip install universal-learning
```

**Requirements**: Python 3.9+, NumPy, SciPy, networkx, bitarray

### Solomonoff Induction Example
```python
from universal_learning import SolomonoffInductor
import numpy as np

# Create Solomonoff inductor
inductor = SolomonoffInductor(
    max_program_length=100,
    universal_machine='utm',
    approximation_method='jtw'  # Jürgen's Time-Weighted approximation
)

# Binary sequence prediction
sequence = [0, 1, 0, 1, 0, 1]  # Simple alternating pattern
prediction = inductor.predict_next(sequence)
print(f"Next bit prediction: {prediction}")

# Get probability distribution
probs = inductor.get_probabilities(sequence)
print(f"P(next=0): {probs[0]:.4f}, P(next=1): {probs[1]:.4f}")

# Sequence completion
partial_seq = [1, 1, 0, 1]
completions = inductor.complete_sequence(partial_seq, max_length=10)
print("Most likely completions:", completions[:3])
```

### AIXI Agent Example
```python
from universal_learning import AIXI
import numpy as np

# Create AIXI agent for simple environment
agent = AIXI(
    action_space_size=4,
    observation_space_size=8,
    horizon=10,
    approximation='ctx',  # Context Tree Weighting
    exploration_factor=0.1
)

# Simple interaction loop
total_reward = 0
for step in range(100):
    # Agent selects action based on current beliefs
    action = agent.select_action()
    
    # Environment responds (example: simple reward function)
    observation = env.step(action)  # Your environment
    reward = env.get_reward()
    
    # Agent updates its world model
    agent.update(action, observation, reward)
    total_reward += reward

print(f"Total reward: {total_reward}")
print(f"Learned model complexity: {agent.get_model_complexity()}")
```

### Kolmogorov Complexity Estimation
```python
from universal_learning import KolmogorovComplexity

# Estimate algorithmic complexity
kc = KolmogorovComplexity(
    reference_machine='utm',
    approximation_method='lzw'
)

# Analyze different sequences
sequences = [
    [0, 0, 0, 0, 0, 0, 0, 0],  # Regular pattern
    [0, 1, 0, 1, 0, 1, 0, 1],  # Alternating pattern  
    [1, 0, 1, 1, 0, 0, 1, 0],  # Complex pattern
    np.random.randint(0, 2, 100)  # Random sequence
]

for i, seq in enumerate(sequences):
    complexity = kc.estimate_complexity(seq)
    normalized = kc.normalize_complexity(seq)
    print(f"Sequence {i+1}: K(x) ≈ {complexity:.2f}, normalized: {normalized:.4f}")
```

## 🧬 Advanced Features

### Modular Architecture

```python
# Access individual UL components
from universal_learning.solomonoff_modules import (
    UniversalTuringMachine,      # UTM simulation
    AlgorithmicProbability,      # Solomonoff's universal prior
    ProgramGeneration,           # Program enumeration
    ComplexityEstimation,        # Kolmogorov complexity
    UniversalPrior,             # Prior probability distributions
    InductiveInference          # Sequence prediction
)

from universal_learning.aixi_modules import (
    AIXICore,                   # Core AIXI agent
    ModelLearning,              # Environment model learning
    PlanningAlgorithms,         # Expectimax and Monte Carlo planning
    ApproximationMethods,       # CTW, Feature AIXI, Neural AIXI
    RewardMaximization,         # Utility maximization
    ExplorationStrategies       # Optimism and information gain
)

# Custom configuration
custom_inductor = AlgorithmicProbability(
    universal_machine='brainfuck',
    program_length_limit=1000,
    time_limit=10000,
    approximation='speed_prior'
)
```

### Advanced Universal Turing Machine
```python
from universal_learning import AdvancedUTM
from universal_learning.solomonoff_modules import ProgramAnalysis

# Create UTM with enhanced capabilities
utm = AdvancedUTM(
    instruction_set='lambda_calculus',
    optimization_level=2,
    halt_oracle_approximation=True,
    program_verification=True
)

# Analyze program complexity
analysis = ProgramAnalysis(utm)

# Generate and analyze programs
for complexity_class in ['constant', 'linear', 'exponential']:
    programs = analysis.generate_programs_by_complexity(complexity_class, n=10)
    
    for prog in programs:
        result = analysis.analyze_program(prog)
        print(f"Program: {prog[:30]}...")
        print(f"  Time complexity: O({result.time_complexity})")
        print(f"  Space complexity: O({result.space_complexity})")
        print(f"  Halts: {result.halts}")
        print(f"  Output length: {len(result.output)}")
```

### Monte Carlo AIXI
```python
from universal_learning import MonteCarloAIXI
from universal_learning.aixi_modules import EnvironmentModel

# Advanced AIXI with sampling-based approximation
mcaixi = MonteCarloAIXI(
    action_space=env.action_space,
    observation_space=env.observation_space,
    horizon=50,
    num_samples=1000,
    exploration_bonus=0.1,
    model_class='ctw'
)

# Environment interaction with model learning
for episode in range(100):
    obs = env.reset()
    total_reward = 0
    
    for step in range(200):
        # AIXI selects optimal action
        action = mcaixi.select_action(obs, deterministic=False)
        
        # Environment step
        next_obs, reward, done, info = env.step(action)
        
        # Update AIXI's world model
        mcaixi.update_model(obs, action, next_obs, reward)
        
        # Plan using updated model
        mcaixi.replan(horizon=min(50, 200-step))
        
        obs = next_obs
        total_reward += reward
        
        if done:
            break
    
    print(f"Episode {episode}: reward = {total_reward}")
    
    # Analyze learned model
    if episode % 10 == 0:
        model_stats = mcaixi.get_model_statistics()
        print(f"  Model complexity: {model_stats.complexity}")
        print(f"  Prediction accuracy: {model_stats.accuracy:.3f}")
```

### Neural Universal Learning
```python
from universal_learning import NeuralUniversalLearner
from universal_learning.solomonoff_modules import DeepAlgorithmicPrior

# Neural approximation of Solomonoff induction
neural_ul = NeuralUniversalLearner(
    architecture='transformer',
    context_length=1024,
    num_layers=12,
    hidden_dim=768,
    approximation_target='solomonoff_prior'
)

# Train on algorithmic data
algorithmic_sequences = generate_algorithmic_sequences(
    generators=['fibonacci', 'prime', 'fractal', 'cellular_automata'],
    sequence_length=512,
    num_sequences=10000
)

neural_ul.train(
    sequences=algorithmic_sequences,
    epochs=100,
    learning_rate=1e-4,
    use_curriculum=True
)

# Compare with theoretical Solomonoff induction
test_sequences = [
    [1, 1, 2, 3, 5, 8, 13],  # Fibonacci
    [2, 3, 5, 7, 11, 13, 17],  # Primes
    [0, 1, 0, 1, 1, 0, 1, 0]   # Complex pattern
]

for seq in test_sequences:
    neural_pred = neural_ul.predict_next(seq)
    theoretical_pred = inductor.predict_next(seq)  # From earlier example
    
    print(f"Sequence: {seq}")
    print(f"Neural prediction: {neural_pred}")
    print(f"Theoretical prediction: {theoretical_pred}")
    print(f"Agreement: {abs(neural_pred - theoretical_pred) < 0.1}")
```

## 🔬 Research Foundation

### Scientific Accuracy

This implementation provides **research-accurate** reproductions of foundational AGI theory:

- **Mathematical Fidelity**: Exact implementation of Solomonoff's universal prior and AIXI decision theory
- **Theoretical Completeness**: Full algorithmic information theory foundations
- **Approximation Methods**: Practical approximations with theoretical guarantees
- **Educational Value**: Clear implementation of abstract theoretical concepts

### Key Research Contributions

- **Universal Induction**: Theoretically optimal method for inductive inference
- **Algorithmic Probability**: Foundation for optimal prediction and compression
- **AIXI Agent**: Mathematical framework for artificial general intelligence
- **Computational Learning Theory**: Limits and possibilities of machine learning

### Original Research Papers

- **Solomonoff, R. J. (1964)**. "A formal theory of inductive inference." *Information and Control*, 7(1), 1-22.
- **Hutter, M. (2005)**. "Universal Artificial Intelligence: Sequential Decisions Based on Algorithmic Probability." *Springer*.
- **Li, M., & Vitányi, P. (2019)**. "An Introduction to Kolmogorov Complexity and Its Applications." *4th Edition, Springer*.

## 📊 Implementation Highlights

### UL Algorithms
- **Solomonoff Induction**: Universal prior for optimal prediction
- **AIXI Agent**: Theoretically optimal reinforcement learning
- **Kolmogorov Complexity**: Algorithmic information theory
- **Universal Turing Machines**: Computational foundations

### Approximation Methods
- **Context Tree Weighting**: Efficient sequence prediction
- **Monte Carlo AIXI**: Sampling-based decision making
- **Neural Approximations**: Deep learning approaches to universal learning
- **Speed Priors**: Runtime-weighted algorithmic probability

### Code Quality
- **Research Accurate**: 100% faithful to theoretical mathematical foundations
- **Approximation Theory**: Rigorous analysis of approximation quality and bounds
- **Educational Value**: Clear implementation of the most abstract AI concepts
- **Theoretical Completeness**: Full coverage of algorithmic information theory

## 🧮 Mathematical Foundation

### Solomonoff's Universal Prior

Algorithmic probability of string x:
```
P(x) = Σ_{p: U(p)=x} 2^(-|p|)
```

Where U is a universal Turing machine and |p| is the length of program p.

### AIXI Decision Theory

Expected future reward:
```
ν(π) = Σ_{ο^m} [Σ_{k=1}^m r_k] P(ο^m | a^m, π)
```

Where π is a policy and P is the universal mixture over all computable environments.

### Kolmogorov Complexity

Algorithmic information content:
```
K(x) = min{|p| : U(p) = x}
```

### Universal Mixture

Optimal predictor for all computable sequences:
```
ξ(x_{<n}) = Σ_{ν} w_ν ν(x_{<n})
```

Where w_ν = 2^(-K(ν)) are the universal weights.

## 🎯 Use Cases & Applications

### Theoretical Computer Science
- **Algorithmic Information Theory**: Foundation for information theory
- **Computational Learning Theory**: Optimal learning bounds and methods
- **Theory of AGI**: Mathematical framework for artificial general intelligence
- **Complexity Theory**: Relationship between description length and computability

### Machine Learning Research
- **Meta-learning**: Learn to learn across diverse tasks optimally
- **Few-shot Learning**: Optimal generalization from minimal data
- **Compression**: Optimal data compression using algorithmic probability
- **Sequence Prediction**: Theoretically optimal time series forecasting

### AI Safety Research
- **Value Learning**: Optimal inference of human values and preferences
- **Corrigibility**: Mathematical frameworks for AI alignment
- **Intelligence Explosion**: Theoretical models of recursive self-improvement
- **Reward Modeling**: Optimal reward function inference from demonstrations

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://universal-learning.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/universal-learning/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/universal-learning/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/universal-learning/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/universal-learning.git
cd universal-learning
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{universal_learning_benedictchen,
    title={Universal Learning: Research-Accurate Implementation of Solomonoff and AIXI},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/universal-learning},
    version={1.0.0}
}

@article{solomonoff1964formal,
    title={A formal theory of inductive inference},
    author={Solomonoff, Ray J},
    journal={Information and control},
    volume={7},
    number={1},
    pages={1--22},
    year={1964},
    publisher={Elsevier}
}
```

## 📋 License

**Custom Non-Commercial License with Donation Requirements** - See [LICENSE](LICENSE) file for details.

## 🎓 About the Implementation

**Implemented by Benedict Chen** - Bringing foundational AI research to modern Python.

📧 **Contact**: benedict@benedictchen.com  
🐙 **GitHub**: [@benedictchen](https://github.com/benedictchen)

---

## 💰 Support This Work - Choose Your Adventure!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

### 🎯 Donation Tier Goals (With Universal Learning Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Coffee has low Kolmogorov complexity but high utility! The shortest program to make me productive: 'add_coffee(benedict)'."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"Pizza maximizes my expected future reward! According to AIXI theory, this is the optimal action for sustainable coding."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"With a library containing every computable book! The universal prior suggests this will eventually happen... right?"*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🏎️ $200,000 - Lamborghini Fund**  
*"For testing if universal intelligence works at 200 mph! Solomonoff would approve of this high-speed induction."*  
💳 [PayPal Supercar](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**✈️ $50,000,000 - Private Jet**  
*"To visit every conference on algorithmic information theory! My flight path will have minimal description length."*  
💳 [PayPal Aerospace](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Aviation](https://github.com/sponsors/benedictchen)

**🏝️ $100,000,000 - Private Island**  
*"Where I'll build the first physical Universal Turing Machine! Each palm tree will represent a different program state."*  
💳 [PayPal Paradise](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Tropical](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🧮 Algorithmic Theorist ($10/month)** - *"Monthly support for maintaining optimal compression of my financial stress!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**♟️ AIXI Agent ($50/month)** - *"Help me maximize my expected future research reward!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🏆 Solomonoff Master ($100/month)** - *"Elite support for achieving the theoretical optimum of sustainable research!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution increases the algorithmic probability of my continued research! Your support has minimum description length but maximum impact! 🚀**

*P.S. - If you help me get that Universal Turing Machine island, I promise to name a complexity class after you!*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@AlgorithmicGodTier** (1.4M followers) • *30 minutes ago* • *(parody)*
> 
> *"CHAT IS THIS REAL?! This universal learning library just taught me the THEORETICAL MAXIMUM for intelligence and my brain is literally reformatting itself! 🧠💫 Solomonoff induction is basically the final boss of machine learning - it's giving 'I solved optimal prediction mathematically' energy and that's honestly terrifying in the best way! This is literally how you would build AGI if you had infinite compute, which makes it both the most beautiful and most unachievable thing ever. Currently using this to optimize my life choices and the results are... concerning. No cap this is the most galaxy brain library I've ever seen! 🌌"*
> 
> **156.7K ❤️ • 28.9K 🔄 • 9.4K 🤯**