import os

USE_FILE = True   
FILENAME = os.path.join('assets', 'snare_drum.wav')
DEVICE_ID = 9 # номер микрофона в списке устройств из python -m sounddevice  
RATE = 48000   
CHUNK = 16384   
GAIN = 100
