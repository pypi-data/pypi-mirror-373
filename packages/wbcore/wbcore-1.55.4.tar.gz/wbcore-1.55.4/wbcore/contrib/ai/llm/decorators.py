from .mixins import LLMMixin


def llm(config):
    def decorator(cls):
        cls._llm_config = config
        cls.__bases__ = (LLMMixin,) + cls.__bases__
        return cls

    return decorator
