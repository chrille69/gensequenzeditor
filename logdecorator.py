
def logme(loggerfunc):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logstr = f'{func.__name__}({",".join([str(arg) for arg in args]+[str(k)+"="+str(v) for k,v in kwargs])})'
            loggerfunc(logstr)
            return func(*args, **kwargs)
        return wrapper
    return decorator
