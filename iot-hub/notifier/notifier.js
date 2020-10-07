'use strict';
const variables = require('./variables');
const logger = require('./logger');
const rabbitmq = require('amqplib');
const aws = require('aws-sdk');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

let config = new variables();
let log = new logger(config);
aws.config.update({
    region: config.awsRegion
});
log.debug(`Logging to ${config.logDirectory}`);

const notify = (job, presignedUrl) => {
    let sns = new aws.SNS();
    let snsParams = {
        Message: `${job.message} - investigate: ${presignedUrl}`,
        Subject: job.job_type,
        TargetArn: config.snsTopicArn
    }
    sns.publish(snsParams, (err, data) => {
        if (!err) {
            log.debug(`Successfully notified SNS of ${snsParams}: ${data}`);
        } else {
            log.error(`Failed to notify topic ${config.snsTopicArn} with parameters ${snsParams}: ${err}`);
        }
        axios.post(`${config.hubEndpoint}/notification`, {
                message: snsParams.Message,
                subject: snsParams.Subject,
                arn: snsParams.TargetArn
            })
            .then(res => {
              log.debug(`Hub ${config.hubEndpoint} status: ${res.statusCode}`);
              if (res.statusCode != 200) {
                  log.error(`Hub ${config.hubEndpoint} returned with the following error status: ${res.statusCode}`);
              }
            })
            .catch((err) => {
                log.error(`Failed to notify hub of new notification with params ${snsParams}: ${err}`);
            });
    });
};

const upload = (job) => {
    fs.access(job.file, (err) => {
        if (!err) {
            fs.readFile(job.file, (err, data) => {
                if (!err) {
                    let s3 = new aws.S3();
                    let s3Params = {
                        Bucket: config.s3Bucket,
                        Key: path.join(job.job_type, path.basename(job.file)),
                        Body: data
                    }
                    s3.upload(s3Params, (err, data) => {
                        if (!err) {
                            log.debug(`Succesfully uploaded ${job.file}: ${data}`);
                            s3Params = {
                                Bucket: config.s3Bucket,
                                Key: path.join(job.job_type, path.basename(job.file)),
                                Expires: 86400
                            }
                            s3.getSignedUrl('getObject', s3Params, (err, url) => {
                                if (!err) {
                                   notify(job, url)
                                } else {
                                    log.error(`Error getting presigned url for ${s3Params.Key} in ${s3Params.Bucket}: ${err}`);
                                    notify(job, url);
                                }
                            });
                        } else {
                            log.error(`Failed to upload ${job.file} to ${config.s3Bucket}: ${err}`);
                            notify(job, '');
                        }
                    })
                } else {
                    log.error(`Failed reading from ${job.file}: ${err}`);
                    notify(job, '');
                }
            })
        } else {
            log.error(`${job.file} does not seem to exist!`);
        }
    });
};

const process = (msg) => {
    let job = JSON.parse(msg.content.toString());
    if (job.job_type && job.message && !job.message.includes('OKAY')) {
        if (job.file) {
           upload(job);
        } else {
            notify(job, '');
        }
    } else if (!job.message.includes('OKAY')) {
        log.error(`Unexpected contents in RabbitMQ job from queue ${config.rabbitmqQueue}: ${msg.content.toString()}`);
    }
};

let connectionUrl = `amqp://${config.rabbitmqUser}:${config.rabbitmqUser}@${config.rabbitmqHost}`;
log.debug(`Connecting to RabbitMQ: ${connectionUrl}`);

let connection = rabbitmq.connect(connectionUrl);
connection.then((conn) => {
        return conn.createChannel();
    })
    .then((ch) => {
        log.debug(`Connected to ${connectionUrl}`);
        return ch.assertQueue(config.rabbitmqQueue).then((ok) => {
            return ch.consume(config.rabbitmqQueue, (msg) => {
                if (msg !== null) {
                    log.debug(`New message from ${config.rabbitmqQueue}: ${msg.content.toString()}`);
                    try {
                        process(msg);
                    } catch (e) {
                        log.error(`Failed to parse job from RabbitMQ queue ${config.rabbitmqQueue}: ${e}`);
                    }
                    ch.ack(msg);
                }
            });
        });
    })
    .catch((e) => {
        log.error(`Failed to connect to RabbitMQ: ${connectionUrl}. Exiting...`);
    });