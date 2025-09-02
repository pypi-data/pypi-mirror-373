from enum import IntEnum


# noinspection PyPep8Naming
class v_def(IntEnum):
    """
    Verbosity definitions used across pyCFS.data module

    - ``all``:     all messages
    - ``debug``:   debug messages
    - ``more``:    more messages
    - ``release``: release messages
    - ``min``:     minimum messages
    """

    all = 1000
    debug = 500
    more = 200
    release = 100
    min = 10

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def _missing_(cls, value):
        return cls.release
