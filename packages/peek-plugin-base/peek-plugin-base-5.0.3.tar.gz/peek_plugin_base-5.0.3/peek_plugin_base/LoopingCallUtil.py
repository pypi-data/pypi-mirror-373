from twisted.internet.defer import Deferred
from vortex.DeferUtil import vortexLogFailure


def peekCatchErrbackWithLogger(logger):
    """Peek Catch Errback With Logger

    A LoopingCall will stop if any errors are thrown from the method
    it calls.

    This decorator should ensure that no exceptions or failures
    are thrown into the LoopingCall, and all should continue on.

    """

    def wrapper(funcToWrap) -> Deferred:
        def func(*args, **kwargs):
            try:
                result = funcToWrap(*args, **kwargs)
                if result and isinstance(result, Deferred):
                    result.addErrback(
                        vortexLogFailure, logger, consumeError=True
                    )
                return result
            except Exception as e:
                logger.exception(e)

        return func

    return wrapper
