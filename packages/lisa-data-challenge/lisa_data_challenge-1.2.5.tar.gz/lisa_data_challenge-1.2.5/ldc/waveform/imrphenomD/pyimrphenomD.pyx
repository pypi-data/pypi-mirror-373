#
# Copyright (C) 2017 Michael Puerrer.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with with program; see the file COPYING. If not, write to the
#  Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#  MA  02111-1307  USA
#

#pylint:disable=C0103
#pylint:disable=W0201


"""
    Standalone IMRPhenomD inspiral-merger-ringdown GW waveform model
    for binary black hole coalescences.
"""

import numpy as np
cimport numpy as np
from math import cos


_citation = '10.7935/GT1W-FZ16'

cdef extern from "IMRPhenomD_internals.h":
    cdef double _MSUN_SI "MSUN_SI"
    cdef double _MTSUN_SI "MTSUN_SI"
    cdef double _MRSUN_SI "MRSUN_SI"
    cdef double _PC_SI "PC_SI"

    ctypedef struct COMPLEX16FrequencySeries:
        double complex *data;
        char *name;
        long epoch;
        double f0;
        double deltaF;
        size_t length;

    COMPLEX16FrequencySeries *CreateCOMPLEX16FrequencySeries(
        const char *name,
        long epoch,
        double f0,
        double deltaF,
        size_t length
    );

    COMPLEX16FrequencySeries *ResizeCOMPLEX16FrequencySeries(COMPLEX16FrequencySeries *fs, size_t length);
    void DestroyCOMPLEX16FrequencySeries(COMPLEX16FrequencySeries *fs);

    ctypedef struct AmpPhaseFDWaveform:
        double* freq;
        double* amp;
        double* phase;
        size_t length;

    AmpPhaseFDWaveform* CreateAmpPhaseFDWaveform(
        size_t length
    );

    void DestroyAmpPhaseFDWaveform(AmpPhaseFDWaveform* wf);

    ctypedef struct RealVector:
        double* data;
        size_t length;

    RealVector* CreateRealVector(
        size_t length
    );

    void DestroyRealVector(RealVector* v);

# Expose some useful constants hidden in C-space
MSUN_SI = _MSUN_SI
MTSUN_SI = _MTSUN_SI
MRSUN_SI = _MRSUN_SI
PC_SI = _PC_SI

cdef extern from "IMRPhenomD.h":
    int IMRPhenomDGenerateFD(
        COMPLEX16FrequencySeries **htilde, # [out] FD waveform
        const double phi0,                 # Orbital phase at fRef (rad)
        const double fRef_in,              # reference frequency (Hz)
        const double deltaF,               # Sampling frequency (Hz)
        const double m1_SI,                # Mass of companion 1 (kg)
        const double m2_SI,                # Mass of companion 2 (kg)
        const double chi1,                 # Aligned-spin parameter of companion 1
        const double chi2,                 # Aligned-spin parameter of companion 2
        const double f_min,                # Starting GW frequency (Hz)
        const double f_max,                # End frequency; 0 defaults to Mf = \ref f_CUT
        const double distance              # Distance of source (m)
    );

cdef extern from "IMRPhenomD.h":
    int IMRPhenomDGenerateh22FDAmpPhase(
        AmpPhaseFDWaveform** h22,          # [out] FD waveform - h22 amp/phase
        RealVector* freq,                  # frequencies on which to evaluate the waveform (Hz)
        const double phi0,                 # Orbital phase at fRef (rad)
        const double fRef_in,              # reference frequency (Hz)
        const double m1_SI,                # Mass of companion 1 (kg)
        const double m2_SI,                # Mass of companion 2 (kg)
        const double chi1,                 # Aligned-spin parameter of companion 1
        const double chi2,                 # Aligned-spin parameter of companion 2
        const double distance              # Distance of source (m)
    );


cdef class pyIMRPhenomD:
    """ Generate IMRPhenomD inspiral-merger-ringdown frequency-domain waveform.
    """

    cdef COMPLEX16FrequencySeries *htilde # pointer to waveform structure

    # cdef phi0                 # Orbital phase at fRef (rad)
    # cdef fRef                 # Reference frequency (Hz)
    # cdef deltaF               # Sampling frequency (Hz)
    # cdef m1_SI                # Mass of companion 1 (kg)
    # cdef m2_SI                # Mass of companion 2 (kg)
    # cdef chi1                 # Aligned-spin parameter of companion 1
    # cdef chi2                 # Aligned-spin parameter of companion 2
    # cdef f_min                # Starting GW frequency (Hz)
    # cdef f_max                # End frequency; 0 defaults to Mf = \ref f_CUT
    # cdef distance             # Distance of source (m)
    # cdef name, length, f0
    # cdef fHz, hptilde, hctilde

    def __init__(self):
        """Constructor
        """
        self.htilde = NULL

    def __dealloc__(self):
        """Destructor
        """
        if self.htilde != NULL:
            DestroyCOMPLEX16FrequencySeries(self.htilde)

    @property
    def citation(self):
        return _citation
      
    def get_fd_waveform(self, phi0, fRef, deltaF, m1_SI, m2_SI, chi1, chi2,
                        f_min, f_max, distance, inclination):
        """ Return h+, hx in freq. domain.

        Args:
            phi0: Orbital phase at fRef (rad)
            fRef_in: Reference frequency (Hz)
            deltaF: Sampling frequency (Hz)
            m1_SI: Mass of companion 1 (kg)
            m2_SI: Mass of companion 2 (kg)
            chi1: Aligned-spin parameter of companion 1
            chi2: Aligned-spin parameter of companion 2
            f_min: Starting GW frequency (Hz)
            f_max: End frequency; 0 defaults to Mf = ref f_CUT
            distance: Distance of source (m)
            inclination: Inclination of source (rad)
        """
        ret = IMRPhenomDGenerateFD( &self.htilde, phi0, fRef, deltaF,
                                    m1_SI, m2_SI, chi1, chi2,
                                    f_min, f_max,  distance);
        if ret != 0:
            raise ValueError("Call to IMRPhenomDGenerateFD() failed.")

        # Freq. array
        fHz = self.htilde.f0 + np.arange(self.htilde.length) * self.htilde.deltaF

        # Direct copy of C double complex array to numpy via a MemoryView
        cdef double complex[::1] view = <(double complex)[:self.htilde.length]> self.htilde.data
        hptilde = np.asarray(view)
        # we multiply with the necessary factor below to make this \tilde h_+(f)

        # Produce both polarizations
        cfac = cos(inclination)
        pfac = 0.5 * (1.0 + cfac**2)
        hctilde = np.zeros_like(hptilde)
        hctilde = - 1j * cfac * hptilde
        hptilde *= pfac
        return fHz.copy(), hptilde, hctilde
                        
    
cdef RealVector* ConvertNumpyArrayToRealVector(arr):
    cdef int n
    cdef RealVector* vec
    cdef double* vecdata
    n = len(arr)
    vec = CreateRealVector(n)
    vecdata = vec.data
    for i in range(n):
        vecdata[i] = arr[i]
    return vec


cdef class pyIMRPhenomDh22AmpPhase:
    """Generate IMRPhenomD inspiral-merger-ringdown frequency-domain
    waveform, in Amp/Phase form for h22.
    """

    cdef AmpPhaseFDWaveform* h22 # pointer to waveform structure
    cdef RealVector* cfreq       # pointer to input frequencies in C structure
    cdef freq, amp, phase


    def __init__(self, freq):
        """Constructor
        """
        # arguments are checked in the C waveform generator
        self.freq = np.copy(freq)
        self.h22 = NULL

        # Copy frequencies from numpy array to C structure
        self.cfreq = ConvertNumpyArrayToRealVector(freq)


    def __dealloc__(self):
        """Destructor
        """
        if self.h22 != NULL:
            DestroyAmpPhaseFDWaveform(self.h22)
            DestroyRealVector(self.cfreq)

    @property
    def citation(self):
        return _citation
            
    def get_fd_waveform(self, phi0, fRef, m1_SI, m2_SI, chi1, chi2, distance):
        """
        Return amplitude and phase in freq. domain.
        
        Args:
            phi0: Orbital phase at fRef (rad)
            fRef_in: Reference frequency (Hz)
            m1_SI: Mass of companion 1 (kg)
            m2_SI: Mass of companion 2 (kg)
            chi1: Aligned-spin parameter of companion 1
            chi2: Aligned-spin parameter of companion 2
            distance: Distance of source (m)
        """
        f_min = self.freq[0]
        f_max = self.freq[-1]
        length = len(self.freq)

        ret = IMRPhenomDGenerateh22FDAmpPhase(&self.h22, self.cfreq,
                                              phi0, fRef, m1_SI, m2_SI,
                                              chi1, chi2, distance);
        if ret != 0:
            raise ValueError("Call to IMRPhenomDGenerateFD() failed.")

        # Direct copy of C double array to numpy via a MemoryView
        cdef double[::1] view_amp = <(double)[:self.h22.length]> self.h22.amp
        cdef double[::1] view_phase = <(double)[:self.h22.length]> self.h22.phase
        amp = np.asarray(view_amp)
        phase = np.asarray(view_phase)
        
        return self.freq.copy(), amp.copy(), phase.copy()
