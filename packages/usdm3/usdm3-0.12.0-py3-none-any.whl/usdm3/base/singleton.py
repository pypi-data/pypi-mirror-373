class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = cls.__name__
        if name not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[name] = instance
        return cls._instances[name]

    # Method to assist with testing.
    @classmethod
    def _clear(cls, the_cls):
        name = the_cls.__name__
        if name in cls._instances:
            del cls._instances[name]
