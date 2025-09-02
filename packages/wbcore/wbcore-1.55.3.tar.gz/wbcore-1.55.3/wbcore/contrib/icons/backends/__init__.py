class AbstractBackend:
    @classmethod
    @property
    def fallback_icon(cls):
        raise NotImplementedError()
