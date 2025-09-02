import numpy as np
import matplotlib.pyplot as plt


def convert_van_trees_coords_to_matlab_coords(
    azimuth_deg: float, elevation_deg: float
) -> tuple[float, float]:
    """Converts azimuth and elevation co-ordinates from the convention in Optimum Array Processing, Van Trees (2002)
    to those used in Matlab's Phased Array Toolbox. See the documentation for the steervec function for full details.
    <Add link to documentation here>

    The Matlab package assumes by default that the array lies in the y-z plane i.e. the x-axis is
    normal to the array. By contrast, Van Trees assumes that the array lies in the x-y plane so that the z-axis
    is normal to the array.

    The azimuth phi is the angle between the x-axis and the projection of the arrival vector into the x-y plane.
    The elevation theta is the angle between the projection into the xy-plane and the arrival vector.

    The elevation can be found using the dot product between the projection and the original vector.


    This can be implemented in Matlab as follows:

        phi_new = atand(tand(theta) * cosd(phi));
        theta_new = atand(sind(theta) * sind(phi) / sqrt(sind(theta)^2 * cosd(phi)^2 + cosd(theta)^2));


    """
    azimuth_rad = np.deg2rad(azimuth_deg)
    elevation_rad = np.deg2rad(elevation_deg)

    phi_new = np.arctan(np.tan(elevation_rad) * np.cos(azimuth_rad))
    theta_new = np.arctan(
        np.sin(elevation_rad)
        * np.sin(azimuth_rad)
        / np.sqrt(
            np.sin(elevation_rad) ** 2 * np.cos(azimuth_rad) ** 2
            + np.cos(elevation_rad) ** 2
        )
    )

    return (np.rad2deg(phi_new), np.rad2deg(theta_new))


def convert_matlab_to_van_trees_coords(
    azimuth_deg: float, elevation_deg: float
) -> tuple[float, float]:
    azimuth_rad = np.deg2rad(azimuth_deg)
    elevation_rad = np.deg2rad(elevation_deg)

    if azimuth_rad == 0 and elevation_rad == 0:
        return (0, 0)

    phi = np.atan(np.tan(elevation_rad) / np.sin(azimuth_rad))
    theta = np.atan(np.tan(azimuth_rad) / np.cos(phi))

    return (np.rad2deg(phi), np.rad2deg(theta))


def plot_antenna_response(array, weights: np.ndarray, wavelength):
    theta = np.linspace(-4 * np.pi, 4 * np.pi, 4 * 360)

    response = np.array(
        [array.steering_vector([0, np.pi / 2 - t], wavelength) for t in theta]
    )
    response = weights.T @ response.T
    plt.clf()
    plt.plot([np.pi / 2 - t for t in theta], response)
    plt.savefig("output.png")
