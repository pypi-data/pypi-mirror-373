# config.py
# This file contains default configuration parameters for the synthetic spectra generation.

# Spectrum Paramters

# Number of data points (channels) in the spectrum
NUM_CHANNELS = 140

# The spectral range in physical units (e.g., Wavelength, Velocity)
DATA_X_MIN = 1204.82262682
DATA_X_MAX = 1907.05456744

# Physical Parameter Ranges 

# Range for the Root-Mean-Square (RMS) noise level
RMS_NOISE_MIN = 0.0007
RMS_NOISE_MAX = 0.0008

# Range for individual Gaussian component amplitudes (in intensity units)
COMP_AMP_MIN = 0.002
COMP_AMP_MAX = 0.05

# Range for the mean (center position) of Gaussian components
COMP_MEAN_MIN = 1250.0
COMP_MEAN_MAX = 1850.0

# Range for the sigma (standard deviation/width) of Gaussian components
COMP_SIGMA_MIN = 5.0
COMP_SIGMA_MAX = 30.0