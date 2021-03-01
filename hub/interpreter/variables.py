import os

class Variables:
    def __init__(self):

        self.model_dir = os.getenv('MODELS_DIRECTORY')
        if self.model_dir == None:
            self.model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'models'))
        
        self.model = os.getenv('MODEL')
        if self.model == None:
            self.model = 'ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite'

        self.labels = os.getenv('LABELS')
        if self.labels == None:
            self.labels = 'coco_labels.txt'

        self.output_dir = os.getenv('OUTPUT_DIRECTORY')
        if self.output_dir == None:
            self.output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))
 
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST')
        if self.rabbitmq_host == None:
            self.rabbitmq_host = "rabbitmq"

        self.rabbitmq_user = os.getenv('RABBITMQ_USER')
        if self.rabbitmq_user == None:
            self.rabbitmq_user = "guest"

        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')
        if self.rabbitmq_password == None:
            self.rabbitmq_password = "guest"
        
        self.timeout_seconds = os.getenv('TIMEOUT_SECONDS')
        if self.timeout_seconds == None:
            self.timeout_seconds = 30
        else:
            self.timeout_seconds = int(self.timeout_seconds)