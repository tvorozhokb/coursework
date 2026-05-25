import sounddevice as sd
from src.config import USE_FILE, DEVICE_ID, RATE, CHUNK
from src.gui import AudioVisualizer

def main():
    visualizer = AudioVisualizer()

    if not USE_FILE:
        print("Microphone working...")
        def callback(indata, frames, time, status):
            visualizer.update_ui(indata)
        
        with sd.InputStream(device=DEVICE_ID, callback=callback, channels=1, samplerate=RATE, blocksize=CHUNK):
            visualizer.show()
    else:
        print("Waiting for a PLAY button to be pressed")
        visualizer.show()

if __name__ == '__main__':
    main()
