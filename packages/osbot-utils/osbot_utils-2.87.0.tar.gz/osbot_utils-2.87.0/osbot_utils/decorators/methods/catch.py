from functools import wraps


def catch(function):
    """Catches any errors and returns an object with the error
    return: { 'status': 'error', 'error': f'{exception}', 'exception': exception }"""
    @wraps(function)
    def wrapper(*args,**kwargs):
        try:
            return function(*args,**kwargs)
        except Exception as exception:
            return {'status': 'error', 'error': f'{exception}', 'exception': exception}         # todo return status_error    (could have some side effect on existing codebase)
    return wrapper