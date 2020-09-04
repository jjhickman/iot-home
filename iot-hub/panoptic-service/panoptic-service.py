import pika
import socketio
import json
import time
#### Check for Josh or anomaly for up to X seconds
#### if anomaly detected:
##### record anomaly for Y seconds
#### close stream

def load_labels(path):
    print('Loading labels')
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

def load_encodings():
    print('Loading facial embeddings')

def create_interpreter(models_path, type):
    model = ''
    print('Loading model')
    return model

def load_job(job):
    data = json.load(job)
    source = ''
    print('Loading job')
    return source

def process_source(source):
    result = -1
    print('Processing stream')
    return result

def run(config, channel):
    for method_frame, properties, body in channel.consume(config['input_queue']):
        print(method_frame, properties, body)

        source = load_job(body)

        result = process_source(source)
        channel.basic_publish(exchange='',
                      routing_key=config['output_queue'],
                      body=result)
        # load right model based on job type

        channel.basic_ack(method_frame.delivery_tag)


if __name__ == '__main__':
    with open('./config.json') as contents:
        config = json.load(contents)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=config['rabbitmq_host']))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1) # tell RabbitMQ not to give more than one message at a time

    run(config, channel) # main service loop

    requeued_messages = channel.cancel()
    print('Requeued %i messages' % requeued_messages)
    connection.close()