import numpy as np
from scipy.fft import rfft, rfftfreq


def spectrum(t, y):
    """
    Calculate amplitude spectrum of real value signal.

    Unlike ``scipy.fft.rfft()``, preserves amplitude (A) of a coherent signal
    ``A*sin(f*t)`` independent of sampling rate and time interval.
    I.e. at frequency 'f' we will get 'A'.

    It also strips away zero frequency component.

    Returns
    -------
    array of frequencies and corresponding amplitudes
    """
    N = t.size
    dt = np.mean(np.diff(t))
    freq = rfftfreq(N, dt)
    # y= y - np.mean(y)
    yf = rfft(y)
    yf *= 2 / N  # produce normalized amplitudes
    return freq[1:], yf[1:]  # strip of boring freq=0


def noise_density_spectrum(t, y):
    """
    Calculate noise amplitude spectral density (ASD) spectrum.

    The end results has units of [units of y]/sqrt(Hz).
    I.e. it calculates sqrt(PSD) where PSD is power spectrum density.
    Preserves the density independent of sampling rate and time interval.

    It also strips away zero frequency component, since it uses ``spectrum``

    Returns
    -------
    reduced array of frequencies and corresponding ASDs
    """
    freq, yf = spectrum(t, y)
    yf = yf * np.sqrt(t[-1] - t[0])  # scales with 1/sqrt(RBW)
    return freq, yf


def noise_spectrum_smooth(fr, Ampl, Nbins=100):
    """
    Smooth amplitude spectral density (ASD) spectrum.

    Could be thought as a running average with logarithmic spacing, so high
    frequency components average  bins with more "hits" and thus smoothed the most.

    Since we assume the input spectrum of the nose (ASD),
    we do power average (rmsq on amplitudes).

    Assumes that the input frequencies are in positive and equidistant set.
    Also assumes that frequencies do not contain 0.

    Parametes
    ---------
    fr : list or array
        array of frequencies
    Ampl : list or array
        array of corresponding noise amplitudes ASD
    Nbin : integer
        number of the bins (default is 100) in which frequencies are split

    Returns
    -------
    reduced array of frequencies and corresponding ASDs
    """

    frEdges = np.logspace(np.log10(fr[0]), np.log10(fr[-1]), Nbins)
    frCenter = np.zeros(frEdges.size - 1)
    power = np.zeros(frEdges.size - 1)
    for i, (frStart, frEnd) in enumerate(zip(frEdges[0:-1], frEdges[1:])):
        # print (f"{i=} {frStart=} {frEnd}")
        ind = (frStart <= fr) & (fr <= frEnd)
        frCenter[i] = np.mean(fr[ind])
        power[i] = np.mean(np.power(np.abs(Ampl[ind]), 2))
    ind = np.logical_not(np.isnan(frCenter))
    frCenter = frCenter[ind]
    power = power[ind]
    # print(f'{frCenter=} {power=}')
    return frCenter, np.sqrt(power)
