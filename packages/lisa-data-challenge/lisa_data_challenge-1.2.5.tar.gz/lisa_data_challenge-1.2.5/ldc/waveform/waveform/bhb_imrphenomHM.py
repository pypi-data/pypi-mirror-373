"""Compute waveforms h+ and hx for binary black holes using IMRphenomHM."""
# pylint:disable=E0401

import warnings
warnings.filterwarnings("ignore", "Wswiglal-redir-stdio")

import copy
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline as spline

import lisaconstants as constants

from ldc.common import tools
from ldc.common.tools import (
    signal_inverse_spa,
    window_planck_vec,
)
from ldc.common.series import FrequencySeries, TimeSeries
from ldc.waveform import lisabeta
from ldc.waveform.waveform.bhb_imrphenomD import BHB_IMRPhenomD

# pylint:disable=E1101
# pylint:disable=C0103
# pylint:disable=W0201


class BHB_IMRPhenomHM(BHB_IMRPhenomD):
    """Compute waveforms h+ and hx of a black hole binary with higher
    modes (> [2,2]) using lisabeta.
    """

    def _init_lisabeta(self):
        """Initialiaze a fast BHB waveform container and its freq and time
        domain grids.

        """
        self._fastbhb = lisabeta.FastBHB("mbhb", approx="IMRPhenomHM")
        self._tdi_tgrid = np.arange(0, self.Tobs, self.dt)
        self._tdi_fgrid = np.fft.rfftfreq(len(self._tdi_tgrid), d=self.dt)
        if not hasattr(self, "modes"):
            self.set_modes()

    def set_modes(self, modes=[(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3)]):
        """Change list of modes.
        Default is [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3)]
        """
        self.modes = modes

    def make_td_h22(self, harm, n_lookb=30_000):
        """Use (2,2) mode to get time where to split between merger and
        inspiral.

        :param dict harm: lisabeta dict signal for the (2,2) mode.
        :return TimeSeries H22_full: (2,2) modes
        :return int i_match: splitting index
        :return float t_match: splitting time
        """
        # pylint:disable=too-many-locals

        Hlm_fd, SPA_hlm, splA_SPA, splP_SPA, t_end = self._get_common_part(
            harm
        )
        Hlm_td = Hlm_fd.ts.ifft(dt=self.dt).values
        Hlm_td *= self.dt
        ind_SPA = np.argwhere(self._tdi_tgrid <= t_end)[:, 0]

        # determine the matching point
        # based on matching amplitudes and derivatives of the waveforms
        iend = np.argwhere(self._tdi_tgrid >= t_end)[0, 0]
        ampl_diff = (Hlm_td[iend - n_lookb : iend] - SPA_hlm[-n_lookb:]) / np.abs(
            SPA_hlm[-n_lookb:]
        )

        spl_merg = spline(
            self._tdi_tgrid[iend - n_lookb : iend], Hlm_td[iend - n_lookb : iend], k=3
        )
        hM_prime = spl_merg.derivative(n=1)(self._tdi_tgrid[iend - n_lookb : iend])
        spa_deriv = splA_SPA.derivative(n=1)(
            self._tdi_tgrid[iend - n_lookb : iend]
        ) / splA_SPA(self._tdi_tgrid[iend - n_lookb : iend]) - np.tan(
            splP_SPA(self._tdi_tgrid[iend - n_lookb : iend])
        ) * splP_SPA.derivative(
            n=1
        )(
            self._tdi_tgrid[iend - n_lookb : iend]
        )

        # diff of \dot{h}_22/h_22
        wvf_prime_diff = (
            hM_prime / Hlm_td[iend - n_lookb : iend] - spa_deriv
        ) / np.abs(spa_deriv)
        ind_min = np.argwhere(
            np.abs(wvf_prime_diff) <= 1.0e-3
        )  # everything below 1.e-3 is ok
        iminA = np.argmin(
            np.abs(ampl_diff[ind_min])
        )  # find min amplitude in these intervals
        imin = ind_min[iminA][0]
        i_match = iend - n_lookb + imin

        return i_match, self._tdi_tgrid[i_match]

    def _get_common_part(self, harm, minf=1e-4, match_time=None, show=False):
        """Return hlm for an arbitrary waveform mode together with its SPA
        complement.

        :param dict harm: lisabeta dict signal for the (l,m) mode.
        :return TimeSeries Hlm: (l,m) mode
        :return array SPA: SPA complement
        :return array SPA_A: SPA amplitude spline interpolator
        :return array SPA_P: SPA phase spline interpolator
        :return float t_end: last time used for SPA
        """
        # pylint:disable=too-many-locals

        fr = harm["freq"]
        tf = harm["tf"]
        find = np.argwhere((self._tdi_fgrid >= fr[0]) & (self._tdi_fgrid <= fr[-1]))[
            :, 0
        ]
        fr_src = self._tdi_fgrid[find]
        spl_phase = spline(fr, harm["phase"], k=5)(fr_src)
        spl_amp = spline(fr, harm["amp"], k=5)(fr_src)

        maxfr = 5e-2
        deltaminf = 1e-5
        deltamaxf = 4e-3
        w = window_planck_vec(fr_src, minf, maxfr, deltaminf, deltamaxf)

        if show:
            fig, ax = plt.subplots(1)
            plt.loglog(fr_src, spl_amp)
            plt.loglog(fr_src, w * spl_amp)
            plt.ylim([min(spl_amp), max(spl_amp)])
            plt.title("window applied in FD before iFFT")

        Hlm_fd = FrequencySeries(np.zeros((len(self._tdi_fgrid)), dtype=complex),
                                  fs=self._tdi_fgrid)
        Hlm_fd[find] = w * spl_amp * np.exp(-1.0j * spl_phase)
       
        ### compute inspiral part using SPA
        tspa, amp_hp_td, ph_hp_td = signal_inverse_spa(
            np.array([fr_src, spl_amp, spl_phase]).T, sign=1
        ).T

        spline_phi_fd = spline(fr_src, spl_phase, k=3)  # phase interpolation
        tf = 1.0 / (2 * np.pi) * spline_phi_fd.derivative(n=1)(fr_src)

        ind0 = np.argwhere(tf >= 0)[0, 0]
        ind0 = max(ind0, 1) # ind0=0 not autorized
        tm_at_minf = tf[np.argwhere(fr_src >= minf)[0, 0]]

        if match_time is None:
            t_end = tm_at_minf + 0.8 * (self.tc - tm_at_minf)
        else:
            t_end = match_time + 5000
            
        iend = np.argwhere(tf >= t_end)[0, 0]
        splA_SPA = spline(tf[ind0 - 1 : iend], amp_hp_td[ind0 - 1 : iend], k=5)
        splP_SPA = spline(tf[ind0 - 1 : iend], ph_hp_td[ind0 - 1 : iend], k=5)
        ind_SPA = np.argwhere(self._tdi_tgrid <= t_end)[:, 0]
        SPA_hlm = (
            self.dt
            * splA_SPA(self._tdi_tgrid[ind_SPA])
            * np.cos(splP_SPA(self._tdi_tgrid[ind_SPA]))
        )

        return Hlm_fd, SPA_hlm, splA_SPA, splP_SPA, t_end

    def mode_amplitude(self):
        """Return the Ylm coeff for each lm mode as dict."""
        out = {}
        for mode in [(2, 2)] + self.modes:
            l = mode[0]
            m = mode[1]
            spin_wsh_p = tools.spinWeightedSphericalHarmonic(
                -2, l, m, self.incl, self.phi0
            )
            spin_wsh_m = tools.spinWeightedSphericalHarmonic(
                -2, l, -m, self.incl, self.phi0
            )
            Kp = 0.5 * ( spin_wsh_p + (-1) ** l * np.conj(spin_wsh_m) )
            Kc = 0.5j * ( spin_wsh_p - (-1) ** l * np.conj(spin_wsh_m) )
            out[mode] = [Kp, Kc]
        return out

    def compute_hphc_td(self, t, source_parameters=None, approx_t=False, set_attr=True):
        """Return hp, hx for a time samples in t.

        Source parameters can be updated at the same time.

        >>> MBHB = HpHc.type("my-mbhb", "MBHB", "IMRPhenomHM")
        >>> hp_m,hc_m = MBHB.compute_hphc_td(np.arange(0,100,10), pMBHB)
        """
        # pylint:disable=too-many-locals

        # set parameters
        if source_parameters is not None:
            self.set_param(source_parameters)

        # use lisabeta to generate the signal in the FD
        self._init_lisabeta()

        sig = self._fastbhb.get_full_tdi(
            template=self.source_parameters, with_wftdi=True
        )
        sig = sig["wftdi"]

        Ks = self.mode_amplitude()

        imatch, match_time = self.make_td_h22(sig[(2,2)])
        self.match_time = match_time
        
        h_plus_S = TimeSeries(np.zeros((len(self._tdi_tgrid))), t0=0, dt=self.dt)
        h_cross_S = TimeSeries(np.zeros((len(self._tdi_tgrid))), t0=0, dt=self.dt)
        for md in self.modes:
            harm = sig[md]

            if md == (2, 1):
                q = self.m1s / self.m2s
                mchirp = (self.m1s + self.m2s) * (q / (1 + q) ** 2) ** 0.6
                minf = 9e-6 * (4.0e6 / mchirp)
            if md in [(3, 3), (4, 3)]:
                minf = 1.5e-4
            if md == (4, 4):
                minf = 2.0e-4
            if md == (2, 2):
                minf = 1.0e-4
                
            Hlm_fd, SPA_hlm, splA_SPA, splP_SPA, t_end = self._get_common_part(
                harm, minf=minf, match_time=match_time
            )
            i_end  = np.argwhere(self._tdi_tgrid >= t_end)[0,0]
            ind_SPA = np.argwhere(self._tdi_tgrid<= t_end)[:,0]
            Kp, Kc = Ks[md]

            hp_fd = copy.deepcopy(Hlm_fd)
            hp_fd *= np.conjugate(Kp)
            hc_fd = copy.deepcopy(Hlm_fd)
            hc_fd *= np.conjugate(Kc)

            t_spa = self._tdi_tgrid[ind_SPA]
            SPA_hp = splA_SPA(t_spa)*np.real(Kp * np.exp(1.j*splP_SPA(t_spa)) ) 
            SPA_hc = splA_SPA(t_spa)*np.real(Kc * np.exp(1.j*splP_SPA(t_spa)) )

            yxl = 0.5 * ( 1.0 + np.tanh( 0.002 * ( self._tdi_tgrid - match_time ) ) )
            hp_td = hp_fd.ts.ifft(dt=self.dt)*yxl
            hc_td = hc_fd.ts.ifft(dt=self.dt)*yxl

            yxr = 0.5 * ( 1.0 - np.tanh( 0.002 * ( t_spa - match_time ) ) )
            hp_td[ind_SPA] = hp_td[ind_SPA] + (yxr * SPA_hp)
            hc_td[ind_SPA] = hc_td[ind_SPA] + (yxr * SPA_hc)

            h_plus_S += hp_td
            h_cross_S += hc_td

        hpS, hcS = self.source2SSB(h_plus_S, h_cross_S)

        if approx_t:
            self.t, self.hp, self.hc = self._tdi_tgrid, hpS, hcS
            return self.hp, self.hc
        self._interp_hphc(self._tdi_tgrid, hpS, hcS, t, kind="spline")
        return self.hp, self.hc

    @property
    def citation(self):
        """Return waveform citation info."""
        return "arXiv:1806.10734"
