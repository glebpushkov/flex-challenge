from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic_settings import BaseSettings

from app.api.auth import BasicAuthMiddleware
from app.api.errors import validation_exception_handler
from app.api.handlers import router
from app.database import models
from app.database.session import engine


class Settings(BaseSettings):
    host_url: str = "http://0.0.0.0:8000/"
    basic_auth_username: str = "webapi"
    basic_auth_password: str = "secret"


settings = Settings()

# todo: replace with alembic
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='Trades API',
    version='0.0.1',
    servers=[
        {'url': settings.host_url, 'description': 'Trades API service'}
    ],
)
app.include_router(router)
app.add_middleware(BasicAuthMiddleware, settings=settings)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
