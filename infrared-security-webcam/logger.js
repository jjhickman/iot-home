const winston = require('winston');
const path = require('path');

// define the custom settings for each transport (file, console)
var options = {
  file: {
    level: 'info',
    filename: path.join(__dirname, 'log', 'infrared-security-webcam.log'),
    handleExceptions: true,
    json: true,
    maxsize: 5242880,
    maxFiles: 5,
    colorize: true,
  },
  console: {
    level: 'debug',
    handleExceptions: true,
    json: false,
    colorize: true,
  },
};

// instantiate a new Winston Logger with the settings defined above
var logger = new winston.Logger({
  transports: [
    new winston.transports.File(options.file),
    new winston.transports.Console(options.console)
  ],
  exitOnError: false, // do not exit on handled exceptions
});

//  used by morgan
logger.stream = {
  write: function(message, encoding) {
    logger.info(message);
  },
};

module.exports = logger;