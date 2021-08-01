from starlette.responses import JSONResponse


class HidoveException(Exception):
    def __init__(self, status_code: int, message, data=None):
        if data is None:
            data = []
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data


def request_validation_error_handler(request, exc):
    return hidove_exception_handler(request,
                                    HidoveException(status_code=400, message=str(exc), data=exc.errors().pop()))


def http_exception_handler(request, exc):
    return hidove_exception_handler(request, HidoveException(status_code=exc.status_code, message=exc.detail))


def hidove_exception_handler(request, exc: HidoveException):
    return JSONResponse(
        status_code=200,
        content={'code': exc.status_code, "msg": exc.message, 'data': exc.data},
    )
