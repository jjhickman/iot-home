from aiohttp import web

def json_error(message, status):
    return web.json_response({'error': message}, status=status)

async def error_middleware(app, handler):
    """Middleware that returns HTTP errors in json"""
    async def middleware_handler(request):
        try:
            response = await handler(request)
            if 400 <= response.status < 600:
                return json_error(response.reason, response.status)
            return response
        except web.HTTPException as ex:
            if 400 <= ex.status < 600:
                return json_error(ex.reason, ex.status)
            raise
    return middleware_handler

def setup_middlewares(app):
    app.middlewares.append(error_middleware)
