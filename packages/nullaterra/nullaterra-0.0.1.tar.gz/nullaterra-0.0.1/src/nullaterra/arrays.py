import numpy as np


class Array:
    def __init__(self, positions: np.ndarray):
        if isinstance(positions, list):
            positions = np.array(positions)

        if len(positions.shape) == 1:
            positions = positions[:, np.newaxis]

        self.positions = np.array(
            [
                (
                    np.pad(position, (0, 3 - position.shape[0]), mode="constant")
                    if position.shape[0] < 3
                    else position
                )
                for position in positions
            ]
        )

        self.num_antennas = positions.shape[0]

    def steering_vector(
        self, theta_radians: list[float], wavelength: float
    ) -> np.ndarray:
        """
        This should be [phi, theta]

        Refs:
        https://www.antenna-theory.com/definitions/wavevector.php
        https://www.antenna-theory.com/definitions/steering.php
        """
        phi, theta = theta_radians

        return np.array(
            [
                np.exp(
                    -1.0j
                    * 2
                    * np.pi
                    * np.dot(
                        np.array(
                            [
                                np.sin(theta) * np.cos(phi),
                                np.sin(theta) * np.sin(phi),
                                np.cos(theta),
                            ]
                        ),
                        positions,
                    )
                    / wavelength
                )
                for positions in self.positions
            ]
        ).astype(np.complex128)

    def nf_steering_vector(
        self, r: float, angles_radians: list[float], wavelength: float
    ):
        """Creates the steering vector for the array based on a near-field
        source.

        This requires the distance and the angle to the near-field source.
        r = distance to source in m.
        """
        phi, theta = angles_radians
        distances = np.linalg.norm(
            self.positions
            - r
            * np.array(
                [
                    np.sin(theta) * np.cos(phi),
                    np.sin(theta) * np.sin(phi),
                    np.cos(theta),
                ]
            ),
            axis=1,
        )

        steer = np.exp(-1j * 2 * np.pi * distances / wavelength)
        return steer


class UniformLinearArray(Array):
    """A special case of an array that is set out in a straight line with equal spacing.

    Elements are laid on the x-axis and are centered around the origin.

    """

    def __init__(self, num_antennas: int, spacing: float):
        endpoint = (
            int(num_antennas / 2)
            if num_antennas % 2 == 0
            else int((num_antennas - 1) / 2)
        )
        if num_antennas % 2 == 0:
            array_positions = [n * spacing for n in range(-endpoint, endpoint)]
            array_positions = [a + spacing / 2 for a in array_positions]

        else:
            array_positions = [n * spacing for n in range(-endpoint, endpoint + 1)]

        super().__init__(array_positions)

    def steering_vector(self, theta_radians: float, wavelength: float) -> np.ndarray:
        """Gets the steering vector for a uniform linear array. For a uniform linear array the azimuth
        has no bearing on the steering vector, only the elevation.

        """

        return super().steering_vector([0, theta_radians], wavelength)
