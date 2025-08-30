

from .functions import (_drain, _on_finished, start, stop)

def initFuncs(self):
    try:
        for f in (_drain, _on_finished, start, stop):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
