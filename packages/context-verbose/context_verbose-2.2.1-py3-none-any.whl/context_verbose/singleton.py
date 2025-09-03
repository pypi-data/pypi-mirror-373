#!/usr/bin/env python3

"""
** Allows to create only one instance of an object. **
------------------------------------------------------
"""


class MetaSingleton(type):
    """
    ** MetaClass for making Printer as a singloton. **

    Notes
    -----
    The arguments needs to be hashable.

    Examples
    --------
    >>> from context_verbose.singleton import MetaSingleton
    >>> class A:
    ...     pass
    ...
    >>> class B(metaclass=MetaSingleton):
    ...     pass
    ...
    >>> A() is A()
    False
    >>> B() is B()
    True
    >>>
    """

    instance = None

    def __call__(cls, *args, **kwargs):
        """
        Parameters
        ----------
        *args : tuple
            Transmitted to Printer.__call__
        **kwargs : dict
            Transmitted to Printer.__call__
        """
        if MetaSingleton.instance is None:
            instance = cls.__new__(cls)
            MetaSingleton.instance = instance
        return MetaSingleton.instance(*args, **kwargs)
