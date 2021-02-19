import json
from flask import request, current_app
from werkzeug.exceptions import HTTPException


#  全局异常处理
def framework_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, HTTPException):
        code = e.code
        message = e.description
        error_code = 1007
        return APIException(message, code, error_code)
    else:
        if not current_app.config["DEBUG"]:
            return ServerError(message=str(e))
        else:
            current_app.logger.warning(str(e))
            return ServerError(message=str(e))


class APIException(HTTPException):
    code = 500
    message = "sorry, we made a mistake!"
    error_code = 999

    def __init__(self, message=None, code=None, error_code=None, headers=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if message:
            self.message = message
        super(APIException, self).__init__(message, None)

    def get_body(self, environ=None):
        body = dict(
            message=self.message,
            # error_code=self.error_code,
            request=request.method + " " + self.get_url_no_param(),
        )
        text = json.dumps(body)
        return text

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [("Content-Type", "application/json")]

    def get_response(self, environ=None):
        if self.code == 500:
            current_app.logger.warning(str(self.message))
        return super(APIException, self).get_response(environ=environ)

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split("?")
        return main_path[0]


class Success(APIException):
    code = 201
    message = "ok"
    error_code = 0


class DeleteSuccess(APIException):
    code = 202
    message = "delete ok"
    error_code = 1


class UpdateSuccess(APIException):
    code = 200
    message = "update ok"
    error_code = 2


class ServerError(APIException):
    code = 500
    message = "sorry, we made a mistake!"
    error_code = 999


class ParameterException(APIException):
    code = 400
    message = "invalid parameter"
    error_code = 1000


class NotFound(APIException):
    code = 404
    message = "the resource are not found"
    error_code = 1001


class AuthFailed(APIException):
    code = 401
    message = "authorization failed"
    error_code = 1005


class Forbidden(APIException):
    code = 403
    error_code = 1004
    message = "forbidden, not in scope"
