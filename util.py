"""Utils FUNCTIONS"""


def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Utils(object):
    def __init__(self, disable_log=False):
        self.disable_log = disable_log
        self.empty_method = lambda *a : None
        
        log = lambda *msg: print(*msg)
        error = lambda *msg, err=None: print(self.colored(bcolors.FAIL, msg,
                                             prefix="[ERROR] ",
                                             suffix="\n" + str(err) if err else ""))
        warning = lambda *msg: print(self.colored(bcolors.WARNING, msg,
                                     prefix="[WARNING] "))
        info = lambda *msg: print(self.colored(bcolors.OKBLUE, msg))
        success = lambda *msg: print(self.colored(bcolors.OKGREEN, msg))

        self.log = self.logging_fn(log)
        self.error = self.logging_fn(error)
        self.warning = self.logging_fn(warning)
        self.info = self.logging_fn(info)
        self.success = self.logging_fn(success)

    def colored(self, color, msg, prefix="", suffix=""):
        return f'{color}{prefix}{Utils.prepare_log(*msg)}{suffix}{bcolors.ENDC}'

    def logging_fn(self, fn):
        if not self.disable_log:
            return fn
        else:
            return lambda *msg: None

    def disable(self):
        self.log = self.empty_fn
        self.error = self.empty_fn
        self.warning = self.empty_fn
        self.info = self.empty_fn
        self.success = self.empty_fn

    @staticmethod
    def prepare_log(*args):
        return (''.join(["{}" for _ in args])).format(*args)


u = Utils()
log = u.log
error = u.error
info = u.info
warning = u.warning
success = u.success
disable_log = u.disable