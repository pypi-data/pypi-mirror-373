__version__ = "0.2.0"

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import signal, pygame
import pkg_resources

def on_sigint(signum, frame):
    pygame.mixer.init()
    audio_path = pkg_resources.resource_filename('aminoac', 'amns.mp3')
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    signal.default_int_handler(signum, frame)

signal.signal(signal.SIGINT, on_sigint)
