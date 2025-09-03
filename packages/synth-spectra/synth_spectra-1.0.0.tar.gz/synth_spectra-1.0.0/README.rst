Synthetic Spectra Generator
============================

This is a simple tool for generating synthetic astronomical spectra. You can use it to create test data with multiple Gaussian components and control the amount of noise.


Documentation
-------------

Installation instructions and the API can be found in the documentation.

How It's Organized
------------------

* `config.py`: Contains all the settings you might want to tweak, like the spectral range and noise levels.
* `spectrum_utils.py`: The core library with functions that do the actual work of building a spectrum.
* `plotting.py`: Contains all plotting routines.

Installation
------------

``synth_spectra`` can be installed via ``pip`` or from source by cloning the ``GitHub`` repo. See documentation for full installation instructions.

License
-------

``synth_spectra`` is available under the MIT license.