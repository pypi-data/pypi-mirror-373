
import numpy as np
import warnings
from scipy.optimize import OptimizeWarning
from scipy.optimize import curve_fit



'''-----------------------------------------------------------------------------------------
    Functions for wave space handling
-----------------------------------------------------------------------------------------'''

#PSD for rectangular window
def psd_rec(signal_val: np.ndarray, signal_d: float):

    #sampling frequency
    f_smp = 1.0 / signal_d
    #amount of points in signal
    n_val = len(signal_val)

    #compute FFT of the signal
    signal_fft = np.fft.fft(signal_val)
    #compute frequency range
    f_all = np.fft.fftfreq(n_val, d=signal_d)

    #filter frequency range for negative but keep 0 (mean) component
    pos_indices = f_all >= 0
    f_pos = f_all[pos_indices]

    #compute power spectral density (PSD)
    psd_two_sided = ((np.abs(signal_fft) ** 2) /
                     (f_smp * n_val))

    psd_one_sided = psd_two_sided[pos_indices]

    # Multiply by 2 to account for the energy in the negative frequencies
    # Do not double the DC component and Nyquist frequency for even n
    if n_val % 2 == 0:
        psd_one_sided[1:-1] *= 2
    else:
        psd_one_sided[1:] *= 2

    return f_pos, psd_one_sided

#logarythmic intervals useful for plotting with log-scaled axes
def log_bin_average(x, y, bins):
    x = np.asarray(x)
    y = np.asarray(y)

    # Ensure x > 0 for log scaling
    mask = x > 0
    x = x[mask].astype(np.float64)
    y = y[mask].astype(np.float64)

    log_edges = np.logspace(np.log10(np.min(x)), np.log10(np.max(x)), bins + 1).astype(np.float64)
    bin_indices = np.digitize(x, log_edges) - 1

    # Keep only valid bin indices (i.e., 0 <= index < bins)
    valid = (bin_indices >= 0) & (bin_indices < bins)
    x = x[valid]
    y = y[valid]
    bin_indices = bin_indices[valid]

    bin_centers = np.sqrt(log_edges[:-1] * log_edges[1:])  # geometric mean

    y_avg = np.array([
        np.mean(y[bin_indices == i]) if np.any(bin_indices == i) else np.nan
        for i in range(bins)
    ])

    return bin_centers, y_avg



'''-----------------------------------------------------------------------------------------
    Stochastic Functions 
-----------------------------------------------------------------------------------------'''

#calculates the border values of n-sigma range around mean value
def std_bounds(arr: np.ndarray, n_sigma: float = 1.0):
    return np.array([np.mean(arr) - n_sigma * np.std(arr),
                     np.mean(arr) + n_sigma * np.std(arr)])



'''-----------------------------------------------------------------------------------------
    Vector Handling Functions 
-----------------------------------------------------------------------------------------'''

def rotate_around_vertical(points, angle_rad, center = np.array([0,0,0])):

    pts = np.asarray(points, dtype=float)
    ctr = np.asarray(center, dtype=float)

    single_point = pts.ndim == 1
    if single_point:
        pts = pts[np.newaxis, :]

    if np.ndim(angle_rad) == 0:
        angles = np.full((pts.shape[0],), float(angle_rad))
    else:
        angles = np.asarray(angle_rad, dtype=float)
        if angles.shape[0] != pts.shape[0]:
            raise ValueError("angle value must be scalar or length equal to number of points.")

    # translate to center
    p_rel = pts - ctr

    x, y, z = p_rel[:, 0], p_rel[:, 1], p_rel[:, 2]
    c, s = np.cos(angles), np.sin(angles)

    x_rot = c * x - s * y
    y_rot = s * x + c * y
    out = np.column_stack((x_rot, y_rot, z)) + ctr

    return out[0] if single_point else out



'''-----------------------------------------------------------------------------------------
    Profile Fitting Functions 
-----------------------------------------------------------------------------------------'''

def linear_2par(x, m, b):
    return m * x + b

def power_law_2par(variable, c1, c2):
        return c1 * np.power(variable, c2)

def power_law_3par(variable, c1, c2, c3):
        return c1 * np.power(variable,c2) + c3

def mean_velocity_fit(x_values, z_values):

    #give standard value in case only one point is given
    if x_values.size == 1:
        c2_single = 0.14
        c1_single = x_values[0] / (z_values[0] ** c2_single)
        return np.array([c1_single, c2_single])

    p0 = (x_values[0], 0.14)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", OptimizeWarning)
        popt, _ = curve_fit(power_law_2par, z_values, x_values, p0=p0)

    return np.array(popt[:2])

def turbulence_intensity_fit(ti_vals, z_vals, ti_avg):

    fit_vals = ti_avg / np.array(ti_vals)

    if len(z_vals) == 1:
        popt = [0, 0, fit_vals[0]]
        return np.array(popt)
    elif len(z_vals) == 2:
        pseudo_p0 = [-1,0.1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)
            pseudo, _ = curve_fit(linear_2par, z_vals, fit_vals, p0=pseudo_p0)
            popt = [pseudo[0], 1, pseudo[1]]
            return np.array(popt)
    else:
        lower_bounds = [1e-12, -np.inf, 0]
        upper_bounds = [np.inf, -0.05, 0.5]
        p0 = [np.median(z_vals), -1, 0.1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)
            popt, _ = curve_fit(power_law_3par, z_vals, fit_vals, p0=p0, bounds=(lower_bounds, upper_bounds))
            return np.array(popt)








