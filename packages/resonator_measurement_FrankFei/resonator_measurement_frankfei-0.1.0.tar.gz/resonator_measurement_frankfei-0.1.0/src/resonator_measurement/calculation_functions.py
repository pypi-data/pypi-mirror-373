# This file provides helper functions to find frequencies of resonators on VNA. 

import numpy as np
import re
from scipy.signal import find_peaks, savgol_filter
from scipy.stats import zscore
import matplotlib.pyplot as plt

def readout(file_path):
    # given the file path of the file that exports result
    # the file from vna is in the format of "frequency, (QIj)"
    # return [[frequrncy, ]]
    freq = np.array([])
    in_phase = np.array([])
    quadrature = np.array([])
    
    with open(file_path) as file:
        lines = file.readlines()[1:]
        for line in lines:
            matches = re.findall(r'(?:[+-]?\d+\.\d+)(?:e[+-]\d+)?', line)
            
            #####
            ## r'(\d+\.\d+),\s*\((-?(?:\d+\.\d+)(?:e[+-]\d+)?)([+-](?:\d+\.\d+)(?:e[+-]\d+)?)'
            ## r'(\d+\.\d+),\s*\((-?\d+\.\d+)([+-]\d+\.\d+)j\)'

            #test
            # print(f'{matches} and {test}')
            # if not matches:
                # print(f"⚠️ No match on line {test}: {repr(line)}")
                # continue
            #
            #####

            number = [float(num) for num in matches]
            frequency = number[0]
            real = number[1]
            imaginary = number[2]

            freq = np.append(freq, frequency)
            in_phase = np.append(in_phase, real)
            quadrature = np.append(quadrature, imaginary)
        
        lst = [freq, in_phase, quadrature]
            
    return lst


def freq_ampl(lst):
    freq = lst[0]
    inphase = lst[1]
    quadrature = lst[2]
    ampl_lst = np.array([])

    for i in range(len(freq)):
        ampl = np.sqrt((inphase[i])**2 + (quadrature[i])**2)
        ampl_lst = np.append(ampl_lst, ampl)
    
    return np.array([freq, ampl_lst])


def find_freq(lst, prominence):
    # given the lst [freq, ampl_lst]
    # return the actual dip of the function
    freq = lst[0]
    ampl = lst[1]

    ### dBm_smooth = savgol_filter(x=ampl, window_length=4, polyorder=3)
    ### inverted = -dBm_smooth
    inverted = -ampl

    # ## test
    # test = np.array([])
    # for i in range(len(freq)):
    #     test = np.append(test, np.array([[freq[i], inverted[i]]]))
    # np.savetxt("test", test, delimiter=",")
    # ##

    dips, properties = find_peaks(inverted, prominence=prominence)
    dips_freq = freq[dips]
    print(dips_freq)
    dips_ampl = inverted[dips]
    # plt.plot([freq, inverted])
    # plt.plot([dips_freq, dips_ampl])

    plt.figure(figsize=(8, 5))      # Optional: set figure size
    plt.plot(freq, inverted, color='blue', linestyle='-', label='Graph 1')
    plt.scatter(dips_freq, dips_ampl, color='orange', linestyle='-', marker='o', label='graph 2')
    plt.title('plot')                # Set plot title
    plt.xlabel('frequency')              # Label for x-axis
    plt.ylabel('inverted')              # Label for y-axis
    plt.grid(True)                  # Optional: add grid
    plt.show()                      # Display the plot

    return dips_freq
    

def find_outliers_zscore(x, y, threshold=3):
    # given a data set x set and y set, and give a threshold
    # return the outliers of the index of the data
    z_scores_x = np.abs(zscore(x))
    z_scores_y = np.abs(zscore(y))
    outlier_indices = np.where((z_scores_x > threshold) | (z_scores_y > threshold))
    return outlier_indices


def remove_outliers(x, y, outliers):
    # given a data set of x and y set, and outlier indices
    # return a lst [x,y] 
    filtered_x = np.delete(x, outliers)
    filtered_y = np.delete(y, outliers)
    return [filtered_x, filtered_y]
