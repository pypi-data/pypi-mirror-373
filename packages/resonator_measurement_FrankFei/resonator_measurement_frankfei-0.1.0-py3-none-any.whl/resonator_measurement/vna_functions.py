import re
import csv_functions as csvf
import os
import scipy.constants as sc
import calculation_functions as calc

from pathlib import Path
from functools import reduce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from loguru import logger
from rich import print
from rich.progress import track

import qwip
from qwip.utils import slack_notify
from qwip.config import ConfigDB
from qwip.data import Datastore, HTTPStorageBackend
from qwip.config.schema import ConfigSchema
from qwip.qpu.qpu import QPU
from qwip.sequencer import (
    Location,
    SequenceElement,
    Sequence,
    ReadoutMarker,
    VirtualZWaveform,
    Waveform
)
from qwip.processing.processors import *
from qwip.visualization.readout import plot_IQ 
from qwip.visualization.utils import grid_plotter
from qwip.visualization.dataframe import DataFramePlotter
from qwip.backends.vna import VNABackend, VNAExecutable
from qwip.instruments.instrument_server import InstrumentServer
from qwip.analysis.fitting import ReflectionResonatorModel

plt.style.use('qwip.visualization.style')

from scipy import signal

import pyvisa

########################################

class VNA_Functions:
    def __init__(self, instrument_file_path):
        instruments = InstrumentServer.load(instrument_file_path)
        vna = VNABackend(device=instruments["vna"])
        exe = vna.download()
    
    def measurement_auto(self):
        '''
        use parameters download from vna to run measurement 
        can be excuted directly
        '''
        exe = self.vna.download()
        exe 
        result = self.vna.acquire()["vna"]
        return result


    def measurement_mannual(self, center, power=-60, span=6e5, ave=80, points=401, delay=None, if_bandwidth=500, meas='S21'):
        '''
        running measurement
        return result that aquired from vna
        need to input by hand
        '''
        if delay == None:
            self.exe.delay = self.vna.download().delay
        self.exe.meas = meas
        self.exe.points = points
        self.exe.span = span
        self.exe.center = center
        self.exe.averages = ave
        self.exe.power = power
        self.exe.if_bandwidth = if_bandwidth
        self.vna.upload(self.exe)
        result = self.vna.acquire()["vna"]
        return result
    

    # plot IQ graph
    # given result from a measurement
    # plot the graph
    # return the plot
    def plot_IQ_graph(self, result):
        fig = plot_IQ(result)
        axes = {ax.get_label(): ax for ax in fig.axes}
        print(axes)
        return axes


    # fitting 
    # given: result (from vna)

    def fit(self, result):
        model = ReflectionResonatorModel()

        data = result.data["IQ"]#.loc[7.7252e9:7.7254e9]
        S = data.to_numpy()
        fs = data.index.to_numpy()
        fit = model.fit(S, f=fs)

        fig = plot_IQ(result)
        axes = {ax.get_label(): ax for ax in fig.axes}


        S_fit = fit.eval(f=fs)
        axes["amplitude"].plot(fs, 20*np.log10(np.abs(S_fit)), color="orange", linestyle="--")
        axes["phase"].plot(fs, np.angle(S_fit), color="orange", linestyle="--")
        axes["IQ"].plot(S_fit.real, S_fit.imag, color="orange", linestyle="--")

        f0 = fit.params["fr"].value
        kappa = fit.params["kappa"].value

        axes["phase"].text(
            0.02, 0.8,
            (
                f"$f_r = {f0 / 1e9:.3f}$ GHz\n"
                f"$\kappa = {kappa / 1e3:.1f}$ KHz\n"
            ),
            transform=axes["phase"].transAxes,
            va="center"
        )
        
        print(fit.params['fp_r'])
        fit.params

        return fit


    # power sweep of resonator R(index) with frequency (center_freq) with (span=6e5) from (low=-80) to (high=20), 
    #   taking num=101 data points of power. 
    # The power sweep will use (high - low)/(num-1) to be the increament from the low. 
    # average each power data point (ave=80) times
    #
    # Example: power_sweep(6.5e9, 1, -80, 20, 501, 101, 80, 6e5)
    # this power sweep is sweeping the R1 resonator at frequency 6.5e9 from power -80 to 20 
    #   using 101 data points with increament of (20-(-80))/(101-1) = 1 dBm and average 80 times 

    def power_sweep(self, file_path, index,center_freq, span=6e5, points=501, low=-80, high=20, num=101, ave=150):
        # first making the directory to save all files
        os.makedirs(f"{file_path}/IQ", exist_ok=True)
        os.makedirs(f"{file_path}/parameters", exist_ok=True)
        os.makedirs(f"{file_path}/Q_i", exist_ok=True)

        ### setting the fixed parameters for power sweep: 
        ### start_freq, stop_freq, sweep_points, average_times
        powers = np.linspace(low, high, num)
        exe = VNAExecutable(
            start= center_freq - span / 2,
            stop= center_freq + span / 2,
            points=points,
            averages=ave
        )
        p0 = self.vna.device.power()
        sweeps = []

        for i, p in enumerate(track(powers)):
            ### measure using power p with all other parameters fixed
            exe.power = p

            #reduce the number of average times due to power increament
            if p < -50:
                exe.averages = ave
            elif p < -10 and ave > 100:
                exe.averages = ave -80
            elif ave > 150:
                exe.averages = ave - 140
            else: 
                exe.averages = ave

            self.vna.upload(exe)
            result = self.vna.acquire()["vna"]
            sweeps.append(result)
            
            ### making fitting
            model = ReflectionResonatorModel()
            data = result.data["IQ"]#.loc[7.7252e9:7.7254e9]
            S = data.to_numpy()
            fs = data.index.to_numpy()
            fit = model.fit(S, f=fs)
            
            ### save IQ
            result.to_csv(f'IQ/R{index}_power_{p}_IO.csv', mode='a', index=False, header=False)

            ### save parameters
            file_path_params = f'parameters/R{index}_power_{p}_params.csv'
            parameters = [fit.params]
            csvf.append_row_to_csv(file_path_params, parameters)

            ### save Q_i
            file_path_Q_i = f'Q_i/R{index}_power_{p}_Qis.csv'
            Qi = fit.params["Q_i"]
            Qi_lst = [Qi.value, Qi.stderr]
            csvf.append_row_to_csv(file_path_Q_i, Qi_lst)

            print(f'This is R{index} with power={p}')
            print(fit.params['Q_i'])
            

        self.vna.device.power(p0)


    # only use after the measurement
    # find resonator freuqency from vna
    # if there are too many frequencies, can increase prominence=0.0023, usually increase approximately by 0.001,
    #   repeat if no good frequency. 

    def find_resonators(self, file_path, prominence):
        # import data from the measurement
        readout = calc.readout(file_path) # readout = [[frequency, quadrature, in_phase]...]
        lst = calc.freq_ampl(readout) # lst = [[frequency, amplitude]...]
        dips_freq = calc.find_freq(lst,prominence)
        print(dips_freq)
        return dips_freq