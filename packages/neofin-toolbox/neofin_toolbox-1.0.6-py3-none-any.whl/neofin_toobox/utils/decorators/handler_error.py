import pydantic
from chalice import NotFoundError, Response, BadRequestError

from neofin_toobox.exceptions.common_exceptions import CommonException


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError as e:
            return Response(body={'error': str(e)}, status_code=404)
        except BadRequestError as e:
            return Response(body={'error': str(e)}, status_code=400)
        except pydantic.ValidationError as e:
            return Response(body={'error': e.errors()}, status_code=422)
        except CommonException as e:
            return Response(body={'error': e.message}, status_code=e.status_code)

        except Exception as e:
            print("Error", str(e))
            import traceback
            traceback.print_tb(e.__traceback__)
            return Response(body={'error': 'Internal server error'}, status_code=500)
    return wrapper
