from flask_restx import abort

class ErrorResponse:
    @staticmethod
    def error_response(error: tuple[dict]):
        response = error[0]
        status_code = response['status_code']
        message = response['message']
        data = response['data']
        abort(status_code, message, data=data)