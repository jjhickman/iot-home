'use strict';
const variables = require('./variables');
const rabbitmq = require('amqplib');
const aws = require('aws-sdk');
const path = require('path');
const fs = require('fs');

let config = new variables();
const notify = (job, presignedUrl) => {
    let sns = new aws.SNS();
    let snsParams = {
        Message: `${job.message} - investigate: ${presignedUrl}`,
        Subject: `Potential intruder`,
        TargetArn: config.snsTopicArn
    }
    sns.publish(snsParams, (err, data) => {
        if (!err) {
            console.log(`Successfully notified SNS of ${snsParams}: ${data}`);
        } else {
            console.error(`Failed to notify topic ${config.snsTopicArn} with parameters ${snsParams}: ${err}`);
        }
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
                        Key: path.join('security', path.basename(job.file)),
                        Body: data
                    }
                    s3.upload(s3Params, (err, data) => {
                        if (!err) {
                            console.log(`Succesfully uploaded ${job.file}: ${data}`);
                            s3Params = {
                                Bucket: config.s3Bucket,
                                Key: path.join('security', path.basename(job.file)),
                                Expires: 86400
                            }
                            s3.getSignedUrl('getObject', s3Params, (err, url) => {
                                if (!err) {
                                   notify(job, url)
                                } else {
                                    console.error(`Error getting presigned url for ${s3Params.Key} in ${s3Params.Bucket}: ${err}`);
                                    notify(job, url);
                                }
                            });
                        } else {
                            console.error(`Failed to upload ${job.file} to ${config.s3Bucket}: ${err}`);
                            notify(job, '');
                        }
                    })
                } else {
                    console.error(`Failed reading from ${job.file}: ${err}`);
                    notify(job, '');
                }
            })
        } else {
            console.error(`${job.file} does not seem to exist!`);
        }
    });
};

const process = (msg) => {
    let job = JSON.parse(msg.content.toString());
    if (job.message && !job.message.includes('OKAY')) {
        if (job.file) {
           upload(job);
        } else {
            notify(job, '');
        }
    } else if (!job.message.includes('OKAY')) {
        console.error(`Unexpected contents in RabbitMQ job from queue ${config.rabbitmqQueue}: ${msg.content.toString()}`);
    }
};



let connectionUrl = `amqp://${config.rabbitmqUser}:${config.rabbitmqUser}@${config.rabbitmqHost}`;
console.log(`Connecting to RabbitMQ: ${connectionUrl}`);
let connection = rabbitmq.connect(connectionUrl);
connection.then((conn) => {
        return conn.createChannel();
    })
    .then((ch) => {
        console.log(`Connected to ${connectionUrl}`);
        return ch.assertQueue(config.rabbitmqQueue).then((ok) => {
            return ch.consume(config.rabbitmqQueue, (msg) => {
                if (msg !== null) {
                    console.log(`New message from ${config.rabbitmqQueue}: ${msg.content.toString()}`);
                    try {
                        process(msg);
                    } catch (e) {
                        console.error(`Failed to parse job from RabbitMQ queue ${config.rabbitmqQueue}: ${e}`);
                    }
                    ch.ack(msg);
                }
            });
        });
    })
    .catch((e) => {
        console.error(`Failed to connect to RabbitMQ: ${connectionUrl}. Exiting...`);
    });
