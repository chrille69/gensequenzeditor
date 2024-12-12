
def logme(loggerfunc):
    def decorator(func):
        def wrapper(*args, **kwargs):
            loggerfunc(func.__name__+' '+str(args)+str(kwargs))
            return func(*args, **kwargs)
        return wrapper
    return decorator
