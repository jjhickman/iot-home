'use strict';
class Variables {
    constructor() {
        this.rabbitmqHost = process.env.RABBITMQ_HOST || 'localhost';
        this.rabbitmqUser = process.env.RABBITMQ_USER || 'guest';
        this.rabbitmqPassword = process.env.RABBITMQ_PASSWORD || 'guest';
        this.rabbitmqQueue = process.env.RABBITMQ_QUEUE || 'output';
        this.snsTopicArn = process.env.SNS_TOPIC_ARN || '';
        this.s3Bucket = process.env.S3_BUCKET || 'jjhickman-iot-home';
        this.hubEndpoint = process.env.HUB_REST_ENDPOINT || 'localhost:8080';
    }
}

module.exports = Variables;
