import os

USE_FILE = False   
FILENAME = os.path.join('assets', 'snare_drum.wav')
DEVICE_ID = 9 # номер микрофона в списке устройств из python -m sounddevice  
RATE = 48000   
CHUNK = 16384
ERROR = RATE / CHUNK
GAIN = 100
