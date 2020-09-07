import { Request, Response } from 'express'

const loggerMiddleware = (req: Request, resp: Response, next: any) => {
    next()
}

export default loggerMiddleware
