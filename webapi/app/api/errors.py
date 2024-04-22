from http import HTTPStatus
from starlette.responses import JSONResponse

from app.api.schemas_gen import Error


# we need this to re-map default 422 errors to be compliant with openapi schema.
# moreover, exc is an array of validation errors. For simplicity, we will just concat all jsons in one long string...
async def validation_exception_handler(request, exc):
    msg = [str(err) for err in exc.args] if len(exc.args) else exc.body
    err = Error(message=str(msg), status_code=HTTPStatus.BAD_REQUEST)
    return JSONResponse(err.model_dump(), status_code=HTTPStatus.BAD_REQUEST)
