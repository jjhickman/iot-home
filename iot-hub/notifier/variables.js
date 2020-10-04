'use strict';
class Variables {
    constructor() {
        this.rabbitmqHost = process.env.RABBITMQ_HOST || 'localhost';
        this.rabbitmqUser = process.env.RABBITMQ_USER || 'guest';
        this.rabbitmqPassword = process.env.RABBITMQ_PASSWORD || 'guest';
        this.rabbitmqQueue = process.env.RABBITMQ_QUEUE || 'output';
        this.snsTopicArn = process.env.SNS_TOPIC_ARN || 'arn:aws:sns:us-east-1:498707537134:iot-home';
        this.s3Bucket = process.env.S3_BUCKET || 'jjhickman-iot-home';
        this.logDirectory = process.env.LOG_DIR || './log';
        this.logLevel = process.env.LOG_LEVEL || 'debug';
        this.hubEndpoint = process.env.HUB_REST_ENDPOINT || 'localhost:8881';
        this.awsRegion = process.env.AWS_REGION || 'us-east-1';
    }
}

module.exports = Variables;