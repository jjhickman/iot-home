import App from './src/server'

import * as bodyParser from 'body-parser'
import loggerMiddleware from './src/middleware/logger'

import PostController from './src/controller/post.controller'
import HomeController from './src/controller/home.controller'

const app = new App({
    port: 5000,
    controllers: [
        new HomeController(),
        new PostController()
    ],
    middleWares: [
        bodyParser.json(),
        bodyParser.urlencoded({ extended: true }),
        loggerMiddleware
    ]
})

app.listen()
