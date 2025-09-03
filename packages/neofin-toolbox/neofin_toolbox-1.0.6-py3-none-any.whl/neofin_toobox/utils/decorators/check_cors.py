from neofin_toobox.utils.helpers import handle_cors_options

def route_with_check_cors(bp, path, allowed_origins, **kwargs):
    def wrapper(func):
        bp.route(path, **kwargs)(func)

        def options_handler(*args, **kw):
            return handle_cors_options(bp, allowed_origins)
        bp.route(path, methods=['OPTIONS'])(options_handler)

        return func
    return wrapper
