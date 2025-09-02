import numpy as np
import matplotlib.pyplot as plt

def _nearfield_range_sbes_1(transducer_diameter, wavelength):
    return (transducer_diameter**2) / wavelength

def _nearfield_range_sbes_2(transducer_diameter, wavelength):
    return np.pi * (transducer_diameter**2) / (4*wavelength)

# same as 2, but formula is rearanged to use beam width, frequency and sound speed directly
def _nearfield_range_sbes_3(beam_width_degrees, frequency, sound_speed):
    return 0.64 * sound_speed / (np.pi * frequency * ((np.sin(np.radians(beam_width_degrees/2)))**2))

def _estimate_diameter(kappa, beam_width_degrees):
    return 3.2 / (kappa*np.sin(np.radians(beam_width_degrees/2)))

def _compute_kappa(wavelength):
    return 2*np.pi/wavelength

def _compute_wavelength(frequency, sound_speed):
    return sound_speed/frequency


def nearfield_range_sbes(beam_width_degrees, frequency_khz, sound_speed_ms = 1470, model=2):
    """
    Calculate the nearfield range for a single beam echo sounder. (Circular piston transducer)

    Parameters
    ----------
    beam_width_degrees : float
        Beam width in degrees.
    frequency_khz : float
        Frequency of the sound wave in kHz.
    sound_speed_ms : float, optional
        Speed of sound in water in m/s, by default 1470.
    model : int, optional
        Model to use for calculation (1 or 2), by default 2.
        
    Model 1: Simmonds and MacLennan (2005) in Demer et al. (2015)
    Model 2: Medwin and Clay (1998) in Demer et al. (2015)

    Returns
    -------
    float
        Nearfield range in meters.

    Raises
    ------
    ValueError
        If the model is not 1 or 2.
    """
    
    if model == 1:
        nearfield_range = _nearfield_range_sbes_1
    elif model == 2:
        nearfield_range = _nearfield_range_sbes_2
    elif model == 3:
        # Same as 2 but with rearranged formula
        return _nearfield_range_sbes_3(beam_width_degrees, frequency_khz * 1000, sound_speed_ms)
    else:
        raise ValueError("model must be 1 or 2 or 3")

    wavelength = _compute_wavelength(frequency_khz * 1000, sound_speed_ms)
    kappa = _compute_kappa(wavelength)
    transducer_diameter = _estimate_diameter(kappa, beam_width_degrees)
    return nearfield_range(transducer_diameter, wavelength)

def nearfield_range_sbes(beam_width_degrees, frequency_khz, sound_speed_ms = 1470, model=2):
    """
    Calculate the nearfield range for a single beam echo sounder. (Circular piston transducer)

    Parameters
    ----------
    beam_width_degrees : float
        Beam width in degrees.
    frequency_khz : float
        Frequency of the sound wave in kHz.
    sound_speed_ms : float, optional
        Speed of sound in water in m/s, by default 1470.
    model : int, optional
        Model to use for calculation (1 or 2), by default 2.
        
    Model 1: Simmonds and MacLennan (2005) in Demer et al. (2015)
    Model 2: Medwin and Clay (1998) in Demer et al. (2015)

    Returns
    -------
    float
        Nearfield range in meters.

    Raises
    ------
    ValueError
        If the model is not 1 or 2.
    """
    
    if model == 1:
        nearfield_range = _nearfield_range_sbes_1
    elif model == 2:
        nearfield_range = _nearfield_range_sbes_2
    elif model == 3:
        # Same as 2 but with rearranged formula
        return _nearfield_range_sbes_3(beam_width_degrees, frequency_khz * 1000, sound_speed_ms)
    else:
        raise ValueError("model must be 1 or 2 or 3")

    wavelength = _compute_wavelength(frequency_khz * 1000, sound_speed_ms)
    kappa = _compute_kappa(wavelength)
    transducer_diameter = _estimate_diameter(kappa, beam_width_degrees)
    return nearfield_range(transducer_diameter, wavelength)

def minimum_recommended_calibration_range(beam_width_degrees, frequency_khz, sound_speed_ms = 1470, model=2):
    """
    Calculate the minimum recommended calibration range for a single beam echo sounder.

    Parameters
    ----------
    beam_width_degrees : float
        Beam width in degrees.
    frequency_khz : float
        Frequency of the sound wave in kHz.
    sound_speed_ms : float, optional
        Speed of sound in water in m/s, by default 1470.
    model : int, optional
        Model to use for calculation (1 or 2), by default 2.

    Model 1: Simmonds and MacLennan (2005) in Demer et al. (2015)
    Model 2: Medwin and Clay (1998) in Demer et al. (2015)
    
    Returns
    -------
    float
        Minimum recommended calibration range in meters.

    Raises
    ------
    ValueError
        If the model is not 1 or 2.
    """
    
    
    if model == 1:
        factor = 2
    elif model == 2:
        factor = 3
    elif model == 3:
        # Same as 2 but with rearranged formula
        factor = 3
    else:
        raise ValueError("model must be 1 or 2 or 3")
    
    return nearfield_range_sbes(beam_width_degrees, frequency_khz, sound_speed_ms) * factor

def plot_nearfield_range(
    frequencies_kHz=[333, 200, 120, 70, 38, 18, 12], 
    beamwidth_range=(2, 12), 
    yticks=[1, 1.5, 2, 3, 4, 6, 8, 10, 15, 20],
    sound_speed_ms=1470,
    model=2,
    ax=None,
    name=""
):
    """
    Plot the estimated nearfield range for different frequencies and beam widths.
    """
    if ax is None:
        plt.close("recommended sphere range")
        fig, ax = plt.subplots(num="recommended sphere range", figsize=(8, 6))
    else:
        fig = ax.figure

    bw = {}
    ranges = {}
    for fr in frequencies_kHz:
        bw[fr] = np.linspace(beamwidth_range[0], beamwidth_range[1], 1000)
        ranges[fr] = nearfield_range_sbes(bw[fr], fr, model=model, sound_speed_ms=sound_speed_ms)
        ax.plot(bw[fr], ranges[fr], label=f"{name}{fr} kHz")

    ax.set_xlim(*beamwidth_range)
    ax.set_yscale("log")
    if yticks is not None:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:g}"))
        ax.set_yticks(yticks)
        ax.set_ylim(np.min(yticks), np.max(yticks))
    ax.set_xticks(np.arange(beamwidth_range[0], beamwidth_range[1] + 1, 1))
    ax.grid(True)
    ax.set_xlabel("Beam width (°)")
    ax.set_ylabel("Nearfield range sbes (m)")
    return fig, ax



def plot_nearfield_range(
    frequencies_kHz=[333, 200, 120, 70, 38, 18, 12], 
    beamwidth_range=(2, 12), 
    yticks=[1, 1.5, 2, 3, 4, 6, 8, 10, 15, 20],
    sound_speed_ms=1470,
    model=2,
    ax=None,
    name=""
):
    """
    Plot the estimated nearfield range for different frequencies and beam widths.
    """
    if ax is None:
        plt.close("recommended sphere range")
        fig, ax = plt.subplots(num="recommended sphere range", figsize=(8, 6))
    else:
        fig = ax.figure

    bw = {}
    ranges = {}
    for fr in frequencies_kHz:
        bw[fr] = np.linspace(beamwidth_range[0], beamwidth_range[1], 1000)
        ranges[fr] = nearfield_range_sbes(bw[fr], fr, model=model, sound_speed_ms=sound_speed_ms)
        ax.plot(bw[fr], ranges[fr], label=f"{name}{fr} kHz")

    ax.set_xlim(*beamwidth_range)
    ax.set_yscale("log")
    if yticks is not None:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:g}"))
        ax.set_yticks(yticks)
        ax.set_ylim(np.min(yticks), np.max(yticks))
    ax.set_xticks(np.arange(beamwidth_range[0], beamwidth_range[1] + 1, 1))
    ax.grid(True)
    ax.set_xlabel("Beam width (°)")
    ax.set_ylabel("Nearfield range sbes (m)")
    return fig, ax




def plot_recommended_sphere_range(
    frequencies_kHz=[333, 200, 120, 70, 38, 18, 12], 
    beamwidth_range=(2, 12), 
    yticks=[1, 1.5, 2, 3, 4, 6, 8, 10, 15, 20],
    sound_speed_ms=1470,
    model=2,
    ax=None,
    name="",
):
    """
    Plot the recommended sphere range for different frequencies and beam widths.
    """
    if ax is None:
        plt.close("recommended sphere range")
        fig, ax = plt.subplots(num="recommended sphere range", figsize=(8, 6))
    else:
        fig = ax.figure

    bw = {}
    ranges = {}
    for fr in frequencies_kHz:
        bw[fr] = np.linspace(beamwidth_range[0], beamwidth_range[1], 1000)
        ranges[fr] = minimum_recommended_calibration_range(bw[fr], fr, model=model, sound_speed_ms=sound_speed_ms)
        ax.plot(bw[fr], ranges[fr], label=f"{name}{fr} kHz")

    ax.set_xlim(*beamwidth_range)
    ax.set_yscale("log")
    if yticks is not None:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:g}"))
        ax.set_yticks(yticks)
        ax.set_ylim(np.min(yticks), np.max(yticks))
    ax.set_ylim(np.min(yticks), np.max(yticks))
    ax.set_xticks(np.arange(beamwidth_range[0], beamwidth_range[1] + 1, 1))
    ax.grid(True)
    ax.set_xlabel("Beam width (°)")
    ax.set_ylabel("Minimum recommended calibration range (m)")
    
    return fig, ax

