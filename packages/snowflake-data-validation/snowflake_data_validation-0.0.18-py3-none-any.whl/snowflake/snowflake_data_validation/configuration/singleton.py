class Singleton(type):

    """Singleton metaclass.

    This metaclass ensures that only one instance of a class exists.
    Any class using this metaclass will return the same instance
    every time it is instantiated, effectively implementing the
    Singleton design pattern.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
