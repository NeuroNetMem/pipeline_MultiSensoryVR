# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 10:39:03 2023

@author: Neuropixel
"""

import numpy as np
from scipy.interpolate import interp1d


def create_session_description(session_path, save=True):
    """
    From a session create a dictionary corresponding to the acquisition description.

    Parameters
    ----------
    session_path : str, pathlib.Path
        A path to a session to describe.
    save : bool
        If true, saves the acquisition description file to _ibl_experiment.description.yaml.

    Returns
    -------
    dict
        The legacy acquisition description.
    """
    import ibllib.io.session_params as sess_params
    dict_ad = get_acquisition_description()
    if save:
        sess_params.write_params(session_path=session_path, data=dict_ad)
    return dict_ad


def get_acquisition_description():
    """
    """
   
    devices = {
        'neuropixel': {
            'probe00': {'collection': 'raw_ephys_data/probe00', 'sync_label': 'imec_sync'},
            'probe01': {'collection': 'raw_ephys_data/probe01', 'sync_label': 'imec_sync'}
        },
    }
    acquisition_description = {  # this is the current ephys pipeline description
        'devices': devices,
        'sync': {
            'nidq': {'collection': 'raw_ephys_data', 'extension': 'bin', 'acquisition_software': 'spikeglx'}
        },
        'procedures': ['Ephys recording with acute probe(s)']
    }
  
    key = 'multiSensoryVR'
     
    acquisition_description['tasks'] = [{key: {
        'collection': 'raw_behavior_data',
        'sync_label': 'bpod', 'main': True  
    }}]
    acquisition_description['version'] = '1.0.0'
    return acquisition_description


def smooth_pupil(signal, std_thresh=5, nan_thresh=1, fr=30):
    """Smooth pupil traces

    Parameters
    ----------
    std_thresh : int
        threshold (in standard deviations) beyond which a point is labeled as an outlier
    nan_thresh : int
        threshold (in seconds) above which we will not interpolate nans, but keep them
    fr : int
        frame rate of the camera
   
    Returns
    -------
    np.array
        smoothed, interpolated signal for each time point, shape (t,)

    """
 
    # run savitzy-golay filter on non-nan timepoints to denoise
    signal_sm0 = smooth_interpolate_signal_sg(signal)
 
    # find outliers, set to nan
    errors = signal - signal_sm0
    std = np.nanstd(errors)
    signal1 = np.copy(signal)
    signal1[(errors < (-std_thresh * std)) | (errors > (std_thresh * std))] = np.nan
    
    # run savitzy-golay filter again on (possibly reduced) non-nan timepoints to denoise
    signal_sm1 = smooth_interpolate_signal_sg(signal1)
 
    # don't interpolate long strings of nans
    t = np.diff(1 * np.isnan(signal1))
    begs = np.where(t == 1)[0]
    ends = np.where(t == -1)[0]
    if begs.shape[0] > ends.shape[0]:
        begs = begs[:ends.shape[0]]
    for b, e in zip(begs, ends):
        if (e - b) > (fr * nan_thresh):
            signal_sm1[(b + 1):(e + 1)] = np.nan  # offset by 1 due to earlier diff
 
    # signal_sm1 is the final smoothed pupil diameter estimate
    return signal_sm1
 

def smooth_interpolate_signal_sg(signal, window=31, order=5, interp_kind='linear'):
    """Run savitzy-golay filter on signal, interpolate through nan points.

    Parameters
    ----------
    signal : np.ndarray
        original noisy signal of shape (t,), may contain nans
    window : int
        window of polynomial fit for savitzy-golay filter
    order : int
        order of polynomial for savitzy-golay filter
    interp_kind : str
        type of interpolation for nans, e.g. 'linear', 'quadratic', 'cubic'
    Returns
    -------
    np.array
        smoothed, interpolated signal for each time point, shape (t,)

    """

    signal_noisy_w_nans = np.copy(signal)
    timestamps = np.arange(signal_noisy_w_nans.shape[0])
    good_idxs = np.where(~np.isnan(signal_noisy_w_nans))[0]
    # perform savitzky-golay filtering on non-nan points
    signal_smooth_nonans = non_uniform_savgol(
        timestamps[good_idxs], signal_noisy_w_nans[good_idxs], window=window, polynom=order)
    signal_smooth_w_nans = np.copy(signal_noisy_w_nans)
    signal_smooth_w_nans[good_idxs] = signal_smooth_nonans
    # interpolate nan points
    interpolater = interp1d(
        timestamps[good_idxs], signal_smooth_nonans, kind=interp_kind, fill_value='extrapolate')

    signal = interpolater(timestamps)

    return signal


def non_uniform_savgol(x, y, window, polynom):
    """Applies a Savitzky-Golay filter to y with non-uniform spacing as defined in x.
    This is based on
    https://dsp.stackexchange.com/questions/1676/savitzky-golay-smoothing-filter-for-not-equally-spaced-data
    The borders are interpolated like scipy.signal.savgol_filter would do
    https://dsp.stackexchange.com/a/64313
    Parameters
    ----------
    x : array_like
        List of floats representing the x values of the data
    y : array_like
        List of floats representing the y values. Must have same length as x
    window : int (odd)
        Window length of datapoints. Must be odd and smaller than x
    polynom : int
        The order of polynom used. Must be smaller than the window size
    Returns
    -------
    np.array
        The smoothed y values
    """

    if len(x) != len(y):
        raise ValueError('"x" and "y" must be of the same size')

    if len(x) < window:
        raise ValueError('The data size must be larger than the window size')

    if type(window) is not int:
        raise TypeError('"window" must be an integer')

    if window % 2 == 0:
        raise ValueError('The "window" must be an odd integer')

    if type(polynom) is not int:
        raise TypeError('"polynom" must be an integer')

    if polynom >= window:
        raise ValueError('"polynom" must be less than "window"')

    half_window = window // 2
    polynom += 1

    # Initialize variables
    A = np.empty((window, polynom))  # Matrix
    tA = np.empty((polynom, window))  # Transposed matrix
    t = np.empty(window)  # Local x variables
    y_smoothed = np.full(len(y), np.nan)

    # Start smoothing
    for i in range(half_window, len(x) - half_window, 1):
        # Center a window of x values on x[i]
        for j in range(0, window, 1):
            t[j] = x[i + j - half_window] - x[i]

        # Create the initial matrix A and its transposed form tA
        for j in range(0, window, 1):
            r = 1.0
            for k in range(0, polynom, 1):
                A[j, k] = r
                tA[k, j] = r
                r *= t[j]

        # Multiply the two matrices
        tAA = np.matmul(tA, A)

        # Invert the product of the matrices
        tAA = np.linalg.inv(tAA)

        # Calculate the pseudoinverse of the design matrix
        coeffs = np.matmul(tAA, tA)

        # Calculate c0 which is also the y value for y[i]
        y_smoothed[i] = 0
        for j in range(0, window, 1):
            y_smoothed[i] += coeffs[0, j] * y[i + j - half_window]

        # If at the end or beginning, store all coefficients for the polynom
        if i == half_window:
            first_coeffs = np.zeros(polynom)
            for j in range(0, window, 1):
                for k in range(polynom):
                    first_coeffs[k] += coeffs[k, j] * y[j]
        elif i == len(x) - half_window - 1:
            last_coeffs = np.zeros(polynom)
            for j in range(0, window, 1):
                for k in range(polynom):
                    last_coeffs[k] += coeffs[k, j] * y[len(y) - window + j]

    # Interpolate the result at the left border
    for i in range(0, half_window, 1):
        y_smoothed[i] = 0
        x_i = 1
        for j in range(0, polynom, 1):
            y_smoothed[i] += first_coeffs[j] * x_i
            x_i *= x[i] - x[half_window]

    # Interpolate the result at the right border
    for i in range(len(x) - half_window, len(x), 1):
        y_smoothed[i] = 0
        x_i = 1
        for j in range(0, polynom, 1):
            y_smoothed[i] += last_coeffs[j] * x_i
            x_i *= x[i] - x[-half_window - 1]

    return y_smoothed