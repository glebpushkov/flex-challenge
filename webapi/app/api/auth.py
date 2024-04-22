import base64
import secrets
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class BasicAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            scheme, credentials = auth_header.split()
            if scheme.lower() == 'basic':
                decoded = base64.b64decode(credentials).decode('ascii')
                username, password = decoded.split(':')
                correct_username = secrets.compare_digest(username, self.settings.basic_auth_username)
                correct_password = secrets.compare_digest(password, self.settings.basic_auth_password)
                if correct_username and correct_password:
                    return await call_next(request)
        response = Response(content='Unauthorized', status_code=401)
        response.headers['WWW-Authenticate'] = 'Basic'
        return response
