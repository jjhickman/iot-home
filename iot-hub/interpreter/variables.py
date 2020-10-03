import os
import logging

class Variables:
    def __init__(self):
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST')
        if self.rabbitmq_host == None:
            self.rabbitmq_host = 'localhost'

        self.input_queue = os.getenv('INPUT_QUEUE')
        if self.input_queue == None:
            self.input_queue = 'input'

        self.output_queue = os.getenv('OUTPUT_QUEUE')
        if self.output_queue == None:
            self.output_queue = 'output'

        self.log_level = os.getenv('LOG_LEVEL')
        if self.log_level == None:
            self.log_level = logging.DEBUG
        elif self.log_level == 'INFO':
            self.log_level = logging.INFO
        elif self.log_level == 'ERROR':
            self.log_level = logging.ERROR
        else:
            self.log_level = logging.DEBUG

        self.log_dir = os.getenv('LOG_DIR')
        if self.log_dir == None:
            self.log_dir = './log'

        self.models = os.getenv('MODELS_DIR')
        if self.models == None:
            self.models = './models'

        self.images = os.getenv('IMAGES_DIR')
        if self.images == None:
            self.images = './images'

        self.top_k = os.getenv('TOP_K_OBJECTS')
        if self.top_k == None:
            self.top_k = 10
        else:
            self.top_k = int(self.top_k)

        self.threshold = os.getenv('OBJECT_THRESHOLD')
        if self.threshold == None:
            self.threshold = 0.4
        else:
            self.threshold= float(self.threshold)

        self.job_timeout = os.getenv('JOB_TIMEOUT_SEC')
        if self.job_timeout == None:
            self.job_timeout = 30
        else:
            self.job_timeout = int(self.job_timeout)
        