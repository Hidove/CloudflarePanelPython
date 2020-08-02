from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.staticfiles import StaticFiles

from App.exception import request_validation_error_handler, http_exception_handler, hidove_exception_handler, \
    HidoveException
from App.views.auth import router as auth
from App.views.domain_manage import router as domain_manage


def init_views(app):
    app.include_router(auth)
    app.include_router(domain_manage)

    @app.get('/')
    def index():
        with open("html/index.html", "r") as f:  # 打开文件
            data = f.read()  # 读取文件
        return HTMLResponse(data)
        # return RedirectResponse(app.docs_url)

    app.mount('/', StaticFiles(directory='html'), name='html')


def init_exception(app):
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(HidoveException, hidove_exception_handler)
