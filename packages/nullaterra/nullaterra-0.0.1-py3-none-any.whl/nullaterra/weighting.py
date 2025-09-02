from abc import ABC, abstractmethod

import numpy as np


class BeamformerWeightingScheme(ABC):
    @abstractmethod
    def update_weights(
        self, acm: np.ndarray, current_weights: np.ndarray
    ) -> np.ndarray: ...


class UniformWeights(BeamformerWeightingScheme):
    """Simplest weighting scheme. Described in Van Trees sections 3.1.1.1"""

    def update_weights(
        self, acm: np.ndarray, current_weights: np.ndarray
    ) -> np.ndarray:
        return np.ones(len(current_weights)) / len(current_weights)


class MaxSNRWeights(BeamformerWeightingScheme):
    def update_weights(
        self, acm: np.ndarray, current_weights: np.ndarray
    ) -> np.ndarray:
        return current_weights


class MinimumVarianceWeights(BeamformerWeightingScheme):
    """This will maximize the gain in a particular direction
    while minimizing the overall variance of the output.

    Mathematically

    $min_{w} w^H R w$ s.t. $B(\theta, w) = 1$
    where $\theta$ is the desired gain direction
    and $w$ the beamforming weights.

    Refs:
    https://au.mathworks.com/help/phased/ug/array_pattern-synthesis-part2.html
    """

    def __init__(self, angle_of_gain: float):
        self.angle_of_gain = angle_of_gain

    def update_weights(
        self, acm: np.ndarray, current_weights: np.ndarray
    ) -> np.ndarray:
        return current_weights


class LinearConstraintMinimumVarianceWeights(MinimumVarianceWeights):
    """This takes on the minimum variance structure
    but allows nulls to be placed in particular directions.

    """

    def __init__(self, null_directions: list[float], angle_of_gain: float):
        self.null_directions = null_directions
        super().init(angle_of_gain)

    def update_weights(
        self, acm: np.ndarray, current_weights: np.ndarray
    ) -> np.ndarray:
        """ """


class DirectionalNullWeights(BeamformerWeightingScheme):
    def __init__(self, array, null_directions: list[float], angle_of_gain: float):
        self.null_directions = null_directions
        self.angle_of_gain = angle_of_gain
        self.array_positions = array

    def update_weights(
        self, acm: np.ndarray, current_weights: np.ndarray
    ) -> np.ndarray:
        """Forms weights that are orthogonal to the null direction and point
        in the direction of gain.

        Refs:
        https://au.mathworks.com/help/phased/ug/array-pattern-synthesis.html
        """
        ## form weights towards angle_of_gain
        gain_weights = np.ndarray([])
        ## form weights towards null_directions
        null_weights = np.ndarray([])
        return gain_weights - null_weights @ null_weights.T @ gain_weights / (
            null_weights.T @ null_weights
        )
