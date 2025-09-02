import numpy as np
import matplotlib.pyplot as plt

from extraterrena import arrays, constants


def simulate_linear_array_construct(
    num_antennas: int,
    f: float,
    theta_deg: list[float],
    amplitude: float,
    time_points=np.ndarray,
    sigma: float = 0.5,
) -> np.ndarray:
    """Constructs a uniform linear array with num_antennas elements and spacing of wavelength / 2. Then simulates a series of signals from different directions
    and returns raw voltage data at each antenna.

    """
    wavelength = constants.c / f

    d = wavelength / 2
    array = arrays.UniformLinearArray(num_antennas, d)
    return simulate_linear_array(array, f, theta_deg, amplitude, time_points, sigma)


def simulate_linear_array(
    array: arrays.Array,
    f: float,
    theta_deg: list[float],
    amplitude: float,
    time_points: np.ndarray,
    sigma: float = 0.5,
) -> np.ndarray:
    """Simulates a signal hitting a uniform linear array from an angle theta."""

    wavelength = constants.c / f
    if not isinstance(theta_deg, list) and not isinstance(theta_deg, np.ndarray):
        theta_deg = [theta_deg]

    signal = amplitude * np.exp(1j * 2 * np.pi * f * time_points)

    output = np.zeros((array.num_antennas, time_points.shape[0]), dtype=np.complex128)

    for theta in theta_deg:
        theta_rad = np.deg2rad(theta)
        steer_vec = array.steering_vector(theta_rad, wavelength)
        voltages = steer_vec[np.newaxis].T @ signal[np.newaxis]

        output += voltages

    noise = np.random.multivariate_normal(
        np.zeros(array.num_antennas),
        np.diag(np.ones(array.num_antennas) * sigma),
        time_points.shape[0],
    ).T
    return output + noise


def simulate(
    array: arrays.Array,
    source_f_low: float,
    source_f_high: float,
    interferer_f_low: list[float],
    interferer_f_high: list[float],
    source_theta_deg: float,
    interferer_theta_deg: list[float],
    source_power: float,
    interferer_power: list[float],
    time_points: np.ndarray,
    sigma: float = 0.5,
    sampling_frequency: float = 1_000,
    center_freq: float = 1e9,
):
    if not isinstance(interferer_theta_deg, list) and not isinstance(
        interferer_theta_deg, np.ndarray
    ):
        interferer_theta_deg = [interferer_theta_deg]

    freqs = np.fft.fftfreq(len(time_points), d=1 / sampling_frequency)
    freqs_nozero = np.copy(freqs)
    freqs_nozero[freqs_nozero == 0] = 1e-12
    output = np.zeros((array.num_antennas, time_points.shape[0]), dtype=np.complex128)

    for power, theta, low_freq, high_freq in zip(
        interferer_power + [source_power],
        interferer_theta_deg + [source_theta_deg],
        interferer_f_low + [source_f_low],
        interferer_f_high + [source_f_high],
    ):
        X = np.zeros(len(time_points), dtype=complex)
        band_mask = (center_freq + freqs >= low_freq) & (
            center_freq + freqs <= high_freq
        )
        X[band_mask] = (
            np.random.randn(np.sum(band_mask)) + 1j * np.random.randn(np.sum(band_mask))
        ) / np.sqrt(2)
        theta_rad = np.deg2rad(theta)
        steer_vec = array.steering_vector(
            theta_rad, constants.c / (center_freq + freqs)
        )  # num_antennas x num_freqs
        X = steer_vec * X
        source_signal = np.fft.ifft(X, axis=1)
        current_power = np.mean(np.abs(source_signal) ** 2)
        source_signal = source_signal * np.sqrt(power / current_power)
        output += source_signal

    noise_real = np.random.multivariate_normal(
        np.zeros(array.num_antennas),
        np.diag(np.ones(array.num_antennas) * sigma**2),
        time_points.shape[0],
    ).T  # num_antennas x len(time_points)

    noise_imag = np.random.multivariate_normal(
        np.zeros(array.num_antennas),
        np.diag(np.ones(array.num_antennas) * sigma**2),
        time_points.shape[0],
    ).T  # num_antennas x len(time_points)

    noise = (noise_real + 1j * noise_imag) / np.sqrt(2)
    return output + noise
