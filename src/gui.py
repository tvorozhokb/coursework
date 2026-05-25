import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from scipy.io import wavfile
from src.config import RATE, CHUNK, USE_FILE, FILENAME
from src.algorithm import analyze_spectrum, freq_to_note

class AudioVisualizer:
    def __init__(self):
        plt.style.use('default')
        self.fig, self.ax2 = plt.subplots(1, figsize=(8, 7))
        plt.subplots_adjust(bottom=0.2)

        self.xf = np.linspace(0, RATE // 2, CHUNK // 2)
        self.line_fft, = self.ax2.plot(self.xf, np.zeros(CHUNK // 2), color='#2D1AFF', lw=1.5)
        self.ax2.set_xlim(0, 10000) 
        self.ax2.set_ylim(0, 12)
        
        self.last_note = ""
        self._setup_button()

    def _setup_button(self):
        self.ax_button = plt.axes([0.4, 0.05, 0.2, 0.075]) 
        self.btn_play = Button(self.ax_button, 'PLAY', color='#444444', hovercolor='#666666')
        self.btn_play.label.set_color('white')
        self.btn_play.on_clicked(self.run_analysis)

    def update_ui(self, data):
        yf_abs, peak_freq, peak_idx, calc_time_ms, mem_used_kb = analyze_spectrum(data, USE_FILE)
        
        buffer_duration_ms = (CHUNK / RATE) * 1000.0
        cpu_load_estimation = (calc_time_ms / buffer_duration_ms) * 100.0
        
        print(f"Array memory: {mem_used_kb:.2f} KB | "
              f"Time to count: {calc_time_ms:.3f} ms | "
              f"Buffer time: {buffer_duration_ms:.1f} ms | "
              f"Estimated CPU Load: {cpu_load_estimation:.2f}%")
        
        self.line_fft.set_ydata(yf_abs)
        
        if peak_freq > 0 and yf_abs[peak_idx] > 0.05:
            note = freq_to_note(peak_freq)
            if note != self.last_note:
                self.ax2.set_title(f"Нота: {note} ({peak_freq:.1f} Гц)", color='black')
                self.last_note = note
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def run_analysis(self, event):
        if USE_FILE:
            print(f"Analyzing file: {FILENAME}")
            file_rate, file_data = wavfile.read(FILENAME)
            
            for i in range(0, len(file_data) - CHUNK, CHUNK):
                if not plt.fignum_exists(self.fig.number): break
                block = file_data[i : i + CHUNK]
                self.update_ui(block)
                plt.pause(CHUNK / file_rate) 
        else:
            print("MICROPHONE MODE")

    def show(self):
        plt.show()
