from abc import ABC, abstractmethod

import numpy as np
import torch
import wandb


class Target(ABC):
    """Abstract base class for defining target values in loss balancing.

    Subclasses must implement get_target() to specify how the target
    is computed based on two loss values.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_target(self, **target_input) -> float:
        """Compute target value based on two loss values.

        Args:
            target_input: input to calculate target from

        Returns:
            Target value for loss balancing
        """
        pass


class RelativeTarget(Target):
    """Target that returns a scaled version of the second loss.

    Sets target = ratio * loss2, allowing you to specify the desired
    relationship between loss1 and loss2.
    """

    def __init__(self, ratio: float = 1):
        """Initialize relative target.

        Args:
            ratio: How much bigger loss2 should be relative to loss1.
                  ratio=1 means equal losses, ratio=2 means loss2 should be 2x loss1.
        """
        self.ratio = ratio

    def get_target(self, **target_input) -> float:
        """Return ratio * target_reference_values as the target for loss1.

        Args:
            target_reference_values: value to be relative to (ei other loss values)

        Returns:
            Target value as ratio * target_reference_values
        """
        target_reference_values = target_input.pop("target_reference_values", None)
        return self.ratio * target_reference_values


class ConstantTarget(Target):
    """Target that's constant"""

    def __init__(self, value: float):
        """Initialize constant trajectory target.

        Args:
            value: target value

        """
        self.target = value

    def get_target(self, **target_input) -> float:
        """
        Returns:
            Target value.
        """
        return self.target


class LinearTrajectoryTarget(Target):
    """Target that changes linearly from an initial to final value over time.

    Useful when you want the target to evolve during training, starting
    at one value and gradually moving to another over num_steps calls.
    """

    def __init__(self, initial: float, final: float, num_steps: int):
        """Initialize linear trajectory target.

        Args:
            initial: Starting target value
            final: Target value after num_steps calls
            num_steps: Number of get_target() calls to reach final value
        """
        self.initial = initial
        self.target = initial
        self.num_steps = num_steps
        self.cur_step = 0
        self.step = (final - initial) / (1.0 * num_steps)

    def get_target(self, **target_input) -> float:
        """Return current target value and advance along trajectory.

        Args:
            target_input: value to get target from, should be none

        Returns:
            Current target value. Increments internally for next call.
        """
        step = target_input.pop("step", None)
        if step is not None:
            if step > self.num_steps:
                step = self.num_steps
            return self.initial + (step * self.step)
        else:
            self.cur_step += 1
            if self.cur_step <= self.num_steps:
                self.target += self.step
            return self.target


class LossWeighter(ABC):
    @abstractmethod
    def get_balance_param(self, **kwargs) -> float:
        pass

    def get_combined_loss(self, loss1: float, loss2: float, alpha: float) -> float:
        """Compute the combined loss based on the given losses.

        Args:
            loss1: First loss value, increasing this loss should makes the actual value (thats compared to target) go up
            loss2: Second loss value, increasing this loss should makes the actual (thats compared to target)  value go down
            alpha: balance parameter

        Returns:
            combined_loss
        """
        combined_loss = alpha * loss1 + (1 - alpha) * loss2
        return combined_loss


class FixedLossWeighter(LossWeighter):
    def __init__(self, initial_balance=0.5):
        self.initial_balance = initial_balance

    def get_balance_param(
        self,
        **kwargs,
    ) -> float:
        return self.initial_balance


class PDLossWeighter(LossWeighter):
    """PD controller for automatically balancing two losses.

    Adjusts a mixing parameter (alpha) to keep loss1 close to a target value.
    The combined loss becomes: alpha * loss1 + (1 - alpha) * loss2.
    Uses PD control to adjust alpha based on how far loss1 is from target.
    """

    def __init__(
        self,
        target: Target,
        kp: float = 0.001,
        kd: float = 0.02,
        initial_balance: float = 0.5,
        len_errors: int = 5,
        min_alpha: float = 0,
        max_alpha: float = 1,
        arithmetic_error: bool = False,
        error_max: float = 4,  # set to how much error you anticipate
        derivative_max: float = 2,
        update_max: float = 0.2,
    ):
        """Initialize loss balancer.

        Args:
            target: Strategy for computing the target value for loss1
            kp: Proportional gain - how strongly to react to current error
            kd: Derivative gain - how strongly to react to error trend
            initial_balance: Starting alpha value (0=only loss2, 1=only loss1)
            len_errors: How many recent errors to keep for derivative calculation
            min_alpha: Minimum allowed alpha value
            max_alpha: Maximum allowed alpha value
            arithmetic_error: If True, error = loss1 - target.
                            If False, uses geometric error (ratio-based)
            error_max: Maximum error for clipping (currently unused)
            derivative_max: Maximum derivative value (clips large positive changes)
        """
        assert min_alpha <= initial_balance <= max_alpha
        assert 0 <= min_alpha <= max_alpha <= 1
        assert error_max > 0
        assert derivative_max >= 0
        self.update_max = update_max
        self.target = target
        self.alpha = initial_balance
        self.kp = kp
        self.kd = kd
        self.len_errors = len_errors
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.errors = []
        self.arithmetic_error = arithmetic_error
        self.error_max = error_max
        self.derivative_max = derivative_max

    def get_error_and_deriv(
        self,
        actual_value: float,
        **target_input_kwargs,
    ) -> float:
        """Compute error and derivative for PD control.
        Args:
            actual_value: value to compare to target
            target_input_kwargs: any inputs needed to compute the taget from
        Returns:
            Tuple of (error, derivative) where:
            - error: How far actual_value is from target (computed with target_input) (clipped to bounds)
            - derivative: Rate of change of error (clipped to bounds)
        """
        target_value = self.target.get_target(**target_input_kwargs)
        if isinstance(actual_value, torch.Tensor):
            actual_value = actual_value.detach().cpu().item()

        if self.arithmetic_error:
            # Simple difference: positive when actual_value > target_value
            error = actual_value - target_value
        else:
            # Geometric error: captures relative differences better for varied loss scales
            # error ratio
            error = (
                -target_value / (actual_value + 1e-2)
                if target_value > actual_value
                else actual_value / (target_value + 1e-2)
            )
        error = np.clip(error, -self.error_max, self.error_max)

        if len(self.errors) > 0:
            derivative = np.clip(
                error - self.errors[-1],
                -self.derivative_max,
                self.derivative_max,
            )
        else:
            derivative = 0

        self.errors.append(error)
        if len(self.errors) > self.len_errors:
            self.errors.pop(0)

        return error, derivative, target_value

    def get_balance_param(
        self,
        actual_value: float,
        **target_input_kwargs,
    ) -> float:
        """Update balance parameter and return it.
        Uses PD control: alpha += kp * error + kd * derivative

        Args:
            actual value: value of the controlled
            target_input_kwargs: any inputs to the target function

        Returns:
            Updated balance parameter (clipped to [min_alpha, max_alpha])
        """
        return_info_dict = target_input_kwargs.pop("return_info_dict", False)
        error, derivative, target_value = self.get_error_and_deriv(
            actual_value, **target_input_kwargs
        )
        # if self.arithmetic_error:  # do arithmetic update if using arithmetic error
        additive = (self.kp * error) + (self.kd * derivative)
        additive = np.clip(additive, -self.update_max, self.update_max)
        self.alpha = self.alpha + additive
        # else:  # do multiplicitive update if using geometric error
        #     pid_correction = (self.kp * error) + (self.kd * derivative)
        #     mult = 1 + pid_correction
        #     inv_mult = 1 - pid_correction

        #     # Clip multipliers to valid range
        #     update_min = 1 / (1 + self.update_max)
        #     update_max = 1 + self.update_max
        #     mult = np.clip(mult, update_min, update_max)
        #     inv_mult = np.clip(inv_mult, update_min, update_max)

        #     midpoint = 0.5 * (self.min_alpha + self.max_alpha)
        #     if self.alpha < midpoint:
        #         # Alpha is small: scale directly (better for small values)
        #         self.alpha = self.alpha * mult
        #     else:
        #         # Alpha is large: scale distance to maximum (prevents overshoot near max)
        #         distance_to_max = self.max_alpha - self.alpha
        #         new_distance = distance_to_max * inv_mult
        #         self.alpha = self.max_alpha - new_distance

        self.alpha = np.clip(self.alpha, self.min_alpha, self.max_alpha)
        # error is positive if actual > target. thus the alpha goes up. alpha should weight the one that makes the actual go up
        if return_info_dict:
            info_dict = {
                "pd_controller/error": error,
                "pd_controller/kp": self.kp,
                "pd_controller/derivative": derivative,
                "pd_controller/kd": self.kd,
                "pd_controller/target": target_value,
            }

            return self.alpha, info_dict
        return self.alpha


class PLossWeighter(PDLossWeighter):
    def __init__(
        self,
        target: Target,
        kp: float = 0.001,
        initial_balance: float = 0.5,
        min_alpha: float = 0,
        max_alpha: float = 1,
        arithmetic_error: bool = False,
        error_max: float = 4,
        update_max: float = 0.2,
    ):
        super().__init__(
            target=target,
            kp=kp,
            kd=0,
            initial_balance=initial_balance,
            len_errors=1,
            min_alpha=min_alpha,
            max_alpha=max_alpha,
            arithmetic_error=arithmetic_error,
            error_max=error_max,
            derivative_max=0,
            update_max=update_max,
        )
