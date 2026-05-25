import time
import numpy as np
from scipy.fft import fft
from src.config import RATE, CHUNK

def freq_to_note(f):
    if f < 20: return ""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    try:
        n = int(round(12 * np.log2(f / 440.0))) + 69
        return notes[n % 12] + str(n // 12 - 1)
    except: 
        return ""

def analyze_spectrum(data, use_file):
    gain = 100 if use_file else 20000
    
    if len(data.shape) > 1: 
        data = data[:, 0]
    if data.dtype == np.int16: 
        data = data / 32768.0

    start_time_ns = time.perf_counter_ns()

    windowed = data * np.hanning(len(data))
    yf = fft(windowed)
    yf_abs = (2.0 / CHUNK * np.abs(yf[0:CHUNK // 2])) * gain

    bessel_factors = [1.5934, 2.1356, 2.2955]
    hps = np.copy(yf_abs)
    xf = np.linspace(0, RATE // 2, CHUNK // 2)

    for factor in bessel_factors:
        scaled_xf = xf * factor
        interp_spectrum = np.interp(scaled_xf, xf, yf_abs, right=0)
        hps *= interp_spectrum
    
    start_bin = int(60 * CHUNK / RATE)
    hps_area = hps[start_bin:CHUNK//8]
    
    peak_freq = 0
    peak_idx = 0
    if len(hps_area) > 0 and np.max(hps_area) > 0:
        peak_idx = np.argmax(hps_area) + start_bin
        peak_freq = peak_idx * RATE / CHUNK

    end_time_ns = time.perf_counter_ns()
    calc_time_ms = (end_time_ns - start_time_ns) / 1e6
    mem_used_kb = (data.nbytes + windowed.nbytes + yf.nbytes + yf_abs.nbytes + hps.nbytes) / 1024.0
    
    return yf_abs, peak_freq, peak_idx, calc_time_ms, mem_used_kb
