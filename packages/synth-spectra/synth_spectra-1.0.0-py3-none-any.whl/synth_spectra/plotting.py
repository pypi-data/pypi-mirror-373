import matplotlib.pyplot as plt
from typing import Tuple
from matplotlib.figure import Figure
from matplotlib.axes import Axes

def plot_spectrum(
        spectrum_data : dict = {}
    ) -> Tuple[Figure,Axes]:
    """
    A reusable function to plot spectrum data.

    Args:
        spectrum_data (dict): Dictionary containing the spectral arrays.

    Returns:
        matplotlib plot
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(spectrum_data['x'], spectrum_data['y_observed'], label='Observed')
    ax.plot(spectrum_data['x'], spectrum_data['y_true'], label='True', linestyle='--')
    ax.set_title("Synthetic Spectrum")
    ax.set_xlabel("Wavelength / Velocity")
    ax.set_ylabel("Intensity")
    ax.legend()
    ax.grid(True)
   
    return fig,ax