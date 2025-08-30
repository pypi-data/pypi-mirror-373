import inspect


class RequiredArgError(Exception):
    def __init__(self, argname, obj, func):
        self.argname = argname
        self.funcname = func.__name__
        self.objname = type(obj).__name__
        sig = inspect.signature(type(obj).__init__)
        self.in_init = argname in sig.parameters.keys()

        message = f'Argument "{self.argname}" is required.\n'
        message += f'Call "{self.funcname}({self.argname}=...)"\n'
        if self.in_init:
            message += f'Or initialize with "{self.objname}({self.argname}=...)"'
        super().__init__(message)


class RequiredArgErrors(Exception):
    def __init__(self, errors):
        message = "Required arguments were missing:\n\n"
        message += "\n\n".join([str(e) for e in errors])
        super().__init__(message)


class ConversionDependencyError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
