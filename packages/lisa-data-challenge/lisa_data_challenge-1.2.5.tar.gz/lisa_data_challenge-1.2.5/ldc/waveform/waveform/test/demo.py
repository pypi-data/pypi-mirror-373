import numpy as np
import matplotlib.pyplot as plt

from ldc.waveform.waveform import get_td_waveform, get_fd_tdixyz
from ldc.waveform.waveform.hphc import HpHc
import ldc.io.hdf5 as hdfio
from mbhb_lisabeta import hphc_td_lisabeta
from ldc.waveform.lisabeta import FastBHB

if 1:
    pGB = dict({'Amplitude': 1.07345e-22,#, "strain"),
                'EclipticLatitude': 0.312414,#, "radian"),
                'EclipticLongitude': -2.75291,# "radian"),
                'Frequency': 0.00135962,# "Hz"),
                'FrequencyDerivative': 8.94581279e-19,# "Hz^2"),
                'Inclination': 0.523599 ,# "radian"),
                'InitialPhase': 3.0581565,# "radian"),
                'Polarization': 3.5621656})#,# "radian")})

    delta_t = 15
    start_time = 0
    duration = 3600*24*30*6
    source_type = "GB"
    approximant = 'TD_fdot'

    hp, hc = get_td_waveform(delta_t, start_time, duration,
                             source_type, approximant, **pGB)
    plt.figure()
    hp.plot()
    hc.plot()
    plt.legend()


    X, Y, Z = get_fd_tdixyz(delta_t, duration, source_type, approximant, **pGB)
    plt.figure()
    X.real.plot()
    X.imag.plot()
