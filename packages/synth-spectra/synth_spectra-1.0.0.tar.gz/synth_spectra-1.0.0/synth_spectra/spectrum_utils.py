import numpy as np
from scipy.stats import norm
from . import config 

def gaussian(x : np.array, amplitude : float, mean : float, sigma : float
) -> np.array:
    """
    Generates a Gaussian function.

    Args:
        x (array): Array of values at which to evaluate the Gaussian function.
        amplitude (float): The amplitude of the Gaussian.
        mean (float): The mean value of the Gaussian, within the range of x.
        sigma (float): The standard deviation of the Gaussian.

    Returns: 
        array: An array of length x containing the evaluated Gaussian
    """
    if np.isclose(amplitude, 0.0, atol=1e-9): # Check if amplitude is effectively zero
        return np.zeros_like(x)
    if np.isclose(sigma, 0.0, atol=1e-9):
        sigma = 1e-9
    return amplitude * np.exp(-((x - mean)**2) / (2 * sigma**2))

def generate_synthetic_spectrum(
    x_range: tuple = (config.DATA_X_MIN, config.DATA_X_MAX),
    num_channels: int = config.NUM_CHANNELS,
    components: list = None,
    rms_noise_level: float = 0.1,
    seed: int = None
) -> dict:
    """
    Generates a synthetic spectrum with multiple Gaussian components and added Gaussian noise.

    Args:
        x_range (tuple, optional): (min_x, max_x) for the spectral axis. Defaults to (0.0, 100.0). 
        num_channels (int, optional): Number of data points (channels) in the spectrum. Defaults to 256. 
        components (list, optional): A list of dictionaries, where each dictionary defines a Gaussian component:
        {'amplitude': float, 'mean': float, 'sigma': float}. Defaults to None, wherein default components will be used.
        rms_noise_level (float, optional): The RMS (root-mean-square) noise level to add to the spectrum. Defaults to 0.1.
        seed (int, optional): Random seed for reproducibility of noise. If None, results will vary.

    Returns:
        dict: A dictionary containing:
        'x': np.ndarray (spectral axis)
        'y_true': np.ndarray (true, noiseless spectrum)
        'y_observed': np.ndarray (spectrum with noise)
        'rms_noise': float (the RMS noise level used)
        'chan_wid': float (channel width)
        'components_info': list (the list of components used to generate the spectrum)
    """
    if seed is not None:
        np.random.seed(seed)

    x = np.linspace(x_range[0], x_range[1], num_channels)
    chan_wid = (x_range[1] - x_range[0]) / (num_channels - 1)

    if components is None:
        components = [{'amplitude': 5.0, 'mean': 1500.0, 'sigma': 80.0}]
        print("Using default single Gaussian component.")

    y_true = np.zeros_like(x)
    for comp in components:
        amp = comp['amplitude']
        mean = comp['mean']
        sigma = comp['sigma']

        if sigma <= 0:
            print(f"Warning: Component with non-positive sigma ({sigma}) skipped.")
            continue

        y_true += amp * np.exp(-((x - mean)**2) / (2 * sigma**2))

    noise = norm.rvs(loc=0, scale=rms_noise_level, size=num_channels)
    y_observed = y_true + noise

    return {
        'x': x,
        'y_true': y_true,
        'y_observed': y_observed,
        'rms_noise': rms_noise_level,
        'chan_wid': chan_wid,
        'components_info': components
    }