

from .functions import (_on_run,)

def initFuncs(self):
    try:
        for f in (_on_run,):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
