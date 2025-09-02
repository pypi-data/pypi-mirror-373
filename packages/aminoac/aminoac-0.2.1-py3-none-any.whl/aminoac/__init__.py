__version__ = "0.2.1"

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import signal, pygame
import importlib.resources

def on_sigint(signum, frame):
    pygame.mixer.init()
    # Use modern importlib.resources instead of deprecated pkg_resources
    audio_path = importlib.resources.files('aminoac') / 'amns.mp3'
    pygame.mixer.music.load(str(audio_path))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    signal.default_int_handler(signum, frame)

signal.signal(signal.SIGINT, on_sigint)
