import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from scipy.io import wavfile
from src.config import RATE, CHUNK, ERROR, USE_FILE, FILENAME
from src.algorithm import analyze_spectrum, freq_to_note

UP_arrow = " ▲"
DOWN_arrow = " ▼"
CHECK_freq = " ✔"

def get_ideal_freq(note_name):
    notes_map = {'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13, 
                    'E': 329.63, 'F': 349.23, 'F#': 369.99, 
                  'G': 392.00, 'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88}
    import re
    match = re.match(r"([A-G]#?)(\d+)", note_name)
    if not match:
        return None
    name, octave = match.groups()
    octave = int(octave)
    
    if name in notes_map:
        return notes_map[name] * (2.0 ** (octave - 4))
    return None

class AudioVisualizer:
    def __init__(self):
        plt.style.use('default')
        
        self.fig, self.ax = plt.subplots(num="Drum Tuner", figsize=(4, 3))
        plt.subplots_adjust(bottom=0.25)
        
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(2)

        if USE_FILE:
            self.text_display = self.ax.text(
                0.5, 0.5, "РЕЖИМ ОТЛАДКИ\n(анализ файла)\n\nНажмите PLAY", 
                ha='center', va='center', 
                fontsize=14, fontweight='bold',
                color='black'
            )
        else:
            self.text_display = self.ax.text(
                0.5, 0.5, "Начинайте настройку!", 
                ha='center', va='center', 
                fontsize=14, fontweight='bold',
                color='black'
            )
        
        self.last_note = ""

        if USE_FILE:
            self._setup_button()

    def _setup_button(self):
        self.ax_button = plt.axes([0.3, 0.05, 0.4, 0.1]) 
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
        

        if peak_freq > 0 and yf_abs[peak_idx] > 0.05:
            note = freq_to_note(peak_freq)
    
            ideal_f = get_ideal_freq(note)
            correction = ""
            if ideal_f is not None:
                if peak_freq > ideal_f + ERROR:
                    correction = UP_arrow
                elif peak_freq < ideal_f - ERROR:
                    correction = DOWN_arrow
                elif abs(peak_freq - ideal_f) < ERROR:
                    correction = CHECK_freq

            display_str = f"{peak_freq:.1f} Гц\n\n"
            self.text_display.set_text(display_str)
            
            self.text_display.set_text(f"{peak_freq:.1f} Гц\n{note}{correction}")
            self.text_display.set_fontsize(30)
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
