import os
import logging

class Variables:
    def __init__(self):
        self.gpio_pin = os.getenv('IR_GPIO_PIN')
        if self.gpio_pin == None:
            self.gpio_pin = 23
        else:
            self.gpio_pin = int(self.gpio_pin)

        self.stream_port = os.getenv('STREAM_PORT')
        if self.stream_port == None:
            self.stream_port = 3000
        else:
            self.stream_port = int(self.stream_port)

        self.stream_fps = os.getenv('STREAM_FPS')
        if self.stream_fps == None:
            self.stream_fps = 24
        else:
            self.stream_fps = int(self.stream_fps)
        
        self.hub_url = os.getenv('HUB_REST_ENDPOINT')
        if self.hub_url == None:
            self.hub_url = 'http://localhost:8080'

        self.cooldown_seconds = os.getenv('COOLDOWN_SECONDS')
        if self.cooldown_seconds == None:
            self.cooldown_seconds = 3000
        else:
            self.cooldown_seconds = int(self.cooldown_seconds)

        self.log_level = os.getenv('LOG_LEVEL')
        if self.log_level == None:
            self.log_level = logging.DEBUG
        elif self.log_level == 'INFO':
            self.log_level = logging.INFO
        elif self.log_level == 'ERROR':
            self.log_level = logging.ERROR
        else:
            self.log_level = logging.DEBUG