const os = require('os');
const winston = require('winston');
require('winston-daily-rotate-file');
const path = require('path');

const dateFormat = () => {
    return new Date(Date.now()).toUTCString()
}
class Logger {
    constructor(config) {
        const logger = winston.createLogger({
            transports: [
                new winston.transports.Console({level: config.logLevel}),
                new winston.transports.DailyRotateFile({
                    filename: path.join(config.logDirectory, `${os.hostname()}-%DATE%.log`),
                    datePattern: 'YYYY-MM-DD-HH',
                    zippedArchive: true,
                    maxSize: '20m',
                    maxFiles: '14d',
                    level: config.logLevel
                  })
            ],
            format: winston.format.printf((info) => {
                let message = `${dateFormat()} | ${info.level.toUpperCase()} | ${info.message}`;
                message = info.obj ? message + `data:${JSON.stringify(info.obj)}` : message;
                return message
            })
        });
        this.logger = logger;
    }
    async info(message) {
        this.logger.log('info', message);
    }
    async info(message, obj) {
        this.logger.log('info', message, {
            obj
        });
    }
    async debug(message) {
        this.logger.log('debug', message);
    }
    async debug(message, obj) {
        this.logger.log('debug', message, {
            obj
        });
    }
    async error(message) {
        this.logger.log('error', message);
    }
    async error(message, obj) {
        this.logger.log('error', message, {
            obj
        });
    }
}
module.exports = Logger;