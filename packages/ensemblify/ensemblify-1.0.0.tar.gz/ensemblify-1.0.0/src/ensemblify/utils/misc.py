"""Auxiliary functions with miscellaneous use."""

# IMPORTS
## Third Party Imports
import math
import numpy as np
import scipy

# FUNCTIONS
def kde(
    data: np.ndarray,
    weights: list | None = None,
    ) -> tuple[np.ndarray,np.ndarray,float]:
    """Calculate a Kernel Density Estimate (KDE) distribution for a given dataset.

    Weights for the given dataset can be provided to alter the contribution of each
    data point to the KDE distribution.

    Args:
        data (np.ndarray):
            Dataset to calculate KDE values for.
        weights (list, optional):
            Array with weights for each data point. Defaults to uniform weights.

    Returns:
        tuple[np.ndarray,np.ndarray,float,float]:
            x_coords (np.ndarray):
                X axis coordinates corresponding to the calculated kde distribution.
            norm_kde (np.ndarray):
                Normalized kde distribution.
            weighted_average (float):
                Weighted average of the given dataset.
            weighted_standard_error (float):
                Weighted standard error of the calculated average.

    Adapted from:
        https://github.com/FrPsc/EnsembleLab/blob/main/EnsembleLab.ipynb
    
    Reference for standard error of weighted average:
        https://seismo.berkeley.edu/~kirchner/Toolkits/Toolkit_12.pdf
        Copyright © 2006 Prof. James Kirchner
    """
    # By default weights are uniform
    if weights is None:
        weights = np.full(len(data),1/len(data))

    # Calculate the probability density function of our data
    # through Kernel Density Estimation using the provided weights
    pdf = scipy.stats.gaussian_kde(data,
                                   bw_method='silverman',
                                   weights=weights)

    # Create 50 point from min to max
    x_coords = np.linspace(start=np.min(data),
                           stop=np.max(data),
                           num=50)

    # Get the KDE distribution of our data by evaluating
    # the calculated pdf over the 50 points
    kde_dist = pdf.evaluate(x_coords)

    # Make sure the kde distribution is normalized
    norm_kde = kde_dist/np.sum(kde_dist)

    # Get the weighted average of our data
    weighted_average = np.average(data,weights=weights) # np.sum(weights * data) / np.sum(weights)

    # Calculate effective N and correction factor
    effective_sample_size = np.sum(weights)**2 / np.sum(weights**2)
    correction = effective_sample_size/(effective_sample_size - 1)

    # Get the weighted variance of our data
    weighted_variance = np.sum(weights * (data - weighted_average) ** 2) / np.sum(weights)

    # Get the weighted standard error of our average
    weighted_standard_error = np.sqrt((correction * weighted_variance) / effective_sample_size)

    return x_coords,norm_kde,weighted_average,weighted_standard_error


def get_array_extremum(arrays: list[np.ndarray], get_max: bool | None = True) -> float:
    """Get maximum or minimum value of the set with all values of all provided arrays.

    Args:
        arrays (list[np.ndarray]):
            List of arrays to analyze.
        get_max (bool, optional):
            Whether to get the maximum or minimum (if False) value. Defaults to True.

    Returns:
        float:
            Maximum or minimum value.
    """
    if get_max:
        ext = max(list(map(np.max,arrays)))
    else:
        ext = min(list(map(np.min,arrays)))
    return ext


def round_to_nearest_multiple(n: int, factor: int, up: bool | None = True) -> int:
    """Round a number to the nearest (up or down) multiple of a given factor.

    Args:
        n (int):
            Number to round.
        factor (int):
            The number n will be rounded to a multiple of factor.
        up (bool, optional):
            Whether to round up or down (if False). Defaults to True.

    Returns:
        rounded:
            rounded number.
    """
    if up:
        rounded = factor*(math.ceil(n/factor))
    else:
        rounded = factor*(math.floor(n/factor))
    return rounded
