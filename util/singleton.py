class SingletonMeta(type):
    """
    Metaclass for defining classes which should only have a single active instance. This kind of thing is considered an
    antipattern and can cause very annoying bugs when testing so only use it if you know what you're doing.
    The instances are stored in a dict like `ClassName -> InstanceOf` and they persist between threads!
    Usage:
    >>> class MySingletonClass(metaclass=SingletonMeta):
    >>>
    >>>     def __init__(self):
    >>>         print('Constructor called!')
    >>>
    >>> inst_1 = MySingletonClass()
    >>> inst_2 = MySingletonClass()
    >>> print(inst_1 is inst_2)
    ---
    Constructor called!
    True
    ---
    In the case above, the cached instances will look something like:
    {
        'MySingletonClass': <__main__.MySingletonClass object at 0x0000014FA85E3670>
    }
    """

    _instances: dict[str, object] = {}

    def __call__(cls, *args, **kwargs) -> object:
        if cls.__name__ not in cls._instances:
            cls._instances[cls.__name__] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls.__name__]