# PD Loss Balancing

[![PyPI version](https://badge.fury.io/py/PD-loss-balancing.svg)](https://badge.fury.io/py/PD-loss-balancing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A PyTorch library for automatic loss balancing using PID control theory. Dynamically adjust the weighting between multiple loss functions during training to maintain desired target relationships.

## Features

- **Automatic Loss Balancing**: Uses PID control to automatically adjust loss weights
- **Multiple Target Strategies**: Constant, relative, and linear trajectory targets
- **Flexible Controllers**: PD, P-only, and fixed weighting controllers
- **PyTorch Integration**: Seamless integration with PyTorch training loops
- **Type Safety**: Full type hints for better development experience

## Installation

```bash
pip install PD-loss-balancing
```

## Quick Start

```python
import torch
from PD_loss_balancing import PDLossWeighter, ConstantTarget

# Create a PD controller to balance two losses
target = ConstantTarget(1.0)  # Keep loss1 close to 1.0
weighter = PDLossWeighter(
    target=target,
    kp=0.01,    # Proportional gain
    kd=0.001,   # Derivative gain
    initial_balance=0.5  # Start with equal weighting
)

# In your training loop
for batch in dataloader:
    # Compute your losses
    loss1 = criterion1(outputs1, targets1)
    loss2 = criterion2(outputs2, targets2)
    
    # Get adaptive balance parameter
    alpha = weighter.get_balance_param(actual_value=loss1.item())
    
    # Combine losses: alpha * loss1 + (1-alpha) * loss2
    combined_loss = weighter.get_combined_loss(loss1, loss2, alpha)
    
    # Backpropagate
    combined_loss.backward()
    optimizer.step()
```

## Core Components

### Target Strategies

Define what value you want your controlled loss to maintain:

#### ConstantTarget
Maintains a fixed target value:
```python
from PD_loss_balancing import ConstantTarget

target = ConstantTarget(2.5)  # Keep loss at 2.5
```

#### RelativeTarget
Maintains a ratio relative to another loss:
```python
from PD_loss_balancing import RelativeTarget

# Keep loss1 = 0.8 * loss2
target = RelativeTarget(ratio=0.8)

# Usage requires target_reference_values
alpha = weighter.get_balance_param(
    actual_value=loss1.item(),
    target_reference_values=loss2.item()
)
```

#### LinearTrajectoryTarget
Changes target linearly over time:
```python
from PD_loss_balancing import LinearTrajectoryTarget

# Start at 1.0, end at 0.1 over 1000 steps
target = LinearTrajectoryTarget(
    initial=1.0, 
    final=0.1, 
    num_steps=1000
)
```

### Controllers

#### PDLossWeighter
Full PID controller with proportional and derivative terms:
```python
from PD_loss_balancing import PDLossWeighter, ConstantTarget

weighter = PDLossWeighter(
    target=ConstantTarget(1.0),
    kp=0.01,           # Proportional gain
    kd=0.001,          # Derivative gain
    min_alpha=0.0,     # Minimum balance parameter
    max_alpha=1.0,     # Maximum balance parameter
    arithmetic_error=False,  # Use geometric error calculation
    update_max=0.1     # Maximum update per step
)
```

#### PLossWeighter  
Proportional-only controller (simpler, more stable):
```python
from PD_loss_balancing import PLossWeighter, ConstantTarget

weighter = PLossWeighter(
    target=ConstantTarget(1.0),
    kp=0.01,
    initial_balance=0.5
)
```

#### FixedLossWeighter
Fixed weighting (no adaptation):
```python
from PD_loss_balancing import FixedLossWeighter

weighter = FixedLossWeighter(initial_balance=0.7)  # 70% loss1, 30% loss2
```

## Advanced Usage

### Monitoring Controller State

Get detailed controller information:
```python
alpha, info = weighter.get_balance_param(
    actual_value=loss1.item(),
    return_info_dict=True
)

print(f"Error: {info['pd_controller/error']}")
print(f"Target: {info['pd_controller/target']}")
print(f"Derivative: {info['pd_controller/derivative']}")
```

### Custom Target Implementation

Create your own target strategy:
```python
from PD_loss_balancing import Target

class CustomTarget(Target):
    def __init__(self, base_value: float):
        self.base_value = base_value
        self.step_count = 0
    
    def get_target(self, **target_input) -> float:
        self.step_count += 1
        # Custom logic here
        return self.base_value * (1 + 0.01 * self.step_count)
```

## Error Calculation Methods

The controller supports two error calculation methods:

### Arithmetic Error (Default: False)
```python
error = actual_value - target_value
```
Simple difference, suitable when loss magnitudes are similar.

### Geometric Error (Default: True)
```python
error = actual_value / target_value  # (simplified)
```
Scale-invariant error calculation, better for losses with different magnitudes.

## Use Cases

### GAN Training
Balance generator and discriminator losses:
```python
# Keep discriminator loss around 0.7
target = ConstantTarget(0.7)
weighter = PDLossWeighter(target, kp=0.02, kd=0.005)

alpha = weighter.get_balance_param(actual_value=d_loss.item())
combined = alpha * g_loss + (1-alpha) * d_loss
```

### Multi-task Learning
Balance task-specific losses:
```python
# Keep classification loss 2x larger than regression loss
target = RelativeTarget(ratio=2.0)
weighter = PDLossWeighter(target, kp=0.01)

alpha = weighter.get_balance_param(
    actual_value=cls_loss.item(),
    target_reference_values=reg_loss.item()
)
```

### Curriculum Learning
Gradually change loss emphasis:
```python
# Reduce auxiliary loss importance over 5000 steps
target = LinearTrajectoryTarget(initial=1.0, final=0.1, num_steps=5000)
weighter = PDLossWeighter(target, kp=0.005)
```

## Parameters Guide

### Controller Gains
- **kp (Proportional gain)**: How strongly to react to current error
  - Higher values: Faster response, possible oscillation
  - Typical range: 0.001 - 0.1
  
- **kd (Derivative gain)**: How strongly to react to error trends  
  - Higher values: Better stability, slower response
  - Typical range: 0.0001 - 0.01

### Bounds
- **min_alpha/max_alpha**: Constrain balance parameter range
- **error_max**: Clip error values to prevent extreme updates
- **update_max**: Maximum change in balance parameter per step

## Examples

See the `examples/` directory for complete training scripts:
- `dcgan.py`: GAN training with loss balancing
- `gradient_ascent.py`: Adversarial training example

## Requirements

- Python ≥ 3.8
- PyTorch ≥ 1.9.0
- NumPy
- Weights & Biases (optional, for logging)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{pd_loss_balancing,
    title={PD Loss Balancing: Automatic Loss Weighting with PID Control},
    author={Addie Foote},
    year={2024},
    url={https://github.com/addiefoote/PD-loss-balancing}
}
```