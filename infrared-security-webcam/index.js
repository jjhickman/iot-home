const os = require('os');
const cv = require('opencv4nodejs');
const gpio = require('rpi-gpio');
const morgan = require('morgan');
const path = require('path');
const http = require('http');
const express = require('express');
const server = http.Server(app);
const io = require('socket.io')(server);
const logger = require('./logger');
const config = require('./config.json');

const app = express();
const capture = new cv.VideoCapture(0);
capture.set(cv.CAP_PROP_FRAME_WIDTH, config.width);
capture.set(cv.CAP_PROP_FRAME_HEIGHT, config.height);

const httpRequestUrl = `http://${config.iot_hub}/security/alert/${os.hostname()}`;
const cameraStreamEndpoint = `${os.hostname()}:${config.stream_port}`;
var monitoringEnabled = true;
var cooledDown = true;
const htmlPage = `<html>
<body>
    <img id='image'>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.7.4/socket.io.js'></script>
    <script>
        const socket = io.connect('${cameraStreamEndpoint}');
        socket.on('image', (image) => {
            const img = document.getElementById('image');
            img.src = 'data:image/jpeg;base64,' + image;
        });
    </script>
</body>
</html>`

const beginCapture = () => {
    logger.info(`Starting capture!`);
    setInterval(() => {
        const frame = capture.read();
        const image = cv.imencode('.jpg', frame).toString('base64');
        io.emit('image', image);
    }, 1000 / config.fps);
};

const notifyHub = () => {
    http.get(httpRequestUrl, (resp) => {
        if (resp.statusCode === 404) {
            logger.error(`Intruder detected!`);
        } else if (resp.statusCode === 500) {
            logger.error(`Server error!`);
        } else if (resp.statusCode === 200) {
            logger.info(`Hub received notification!`);
        } else {
            logger.error(`Unexpected result: ${resp.statusCode}`);
        }
      }).on("error", (err) => {
        logger.error(`Error: ${err.message}`);
      });
};

const startCooldown = () => {
    cooledDown = false;
    setTimeout(() => {
        logger.info(`GPIO cooldown expired. Ready to receive IR trigger...`)
        cooledDown = true;
    }, config.cooldown_ms);
};

app.use(express.json());
app.use(morgan('combined', {stream: logger.stream}));
app.use((err, req, res, next) => {
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};
  
    logger.error(`${err.status || 500} - ${err.message} - ${req.originalUrl} - ${req.method} - ${req.ip}`);
    res.status(err.status || 500);
    res.render('error');
});

app.get('/', (req, res) => {
    logger.info(`Request for stream: ${req}`)
    res.send(htmlPage);
});

app.post('/', (req, res) => {
    if (req.body.sleepTime && req.body.sleepTime > 0) {
        monitoringEnabled = false;
        logger.info(`Request to sleep from hub for ${req.body.sleepTime} ms`)
        setTimeout(() => {
            monitoringEnabled  = true;
            logger.info(`Awakened sensor monitoring after ${req.body.sleepTime} ms. Monitoring...`)
        }, req.body.sleepTime);
    } else {
        logger.error(`No alert time specified in POST: ${req}`);
    }
});

gpio.on('change', (channel, value) => {
    log.info(`Channel ${channel}:  ${value}`);
    if (value && cooledDown && monitoringEnabled) {
        startCooldown();
        notifyHub();
    }
});

app.listen(config.port, ()=> {
    logger.info(`Server listening on port ${config.server_port}`);
    gpio.setup(config.gpio_pin, gpio.DIR_IN, gpio.EDGE_RISING);
    beginCapture();
});