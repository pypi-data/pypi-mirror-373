class FinnrException(Exception):
    """This is used as the base class for all finnr exceptions. It can
    be used as a catchall for all other finnr problems.
    """


class MoneyRequired(FinnrException, TypeError):
    """Raised when you attempted to do math between a ``Money`` object
    and a scalar, in a situation where both objects must be ``Money``s.
    """


class ScalarRequired(FinnrException, TypeError):
    """Raised when you attempted to do math between two ``Money``
    objects in a situation where one of them must be a scalar (``int``,
    ``float``, ``Decimal``, etc).
    """


class MismatchedCurrency(FinnrException, ValueError):
    """Raised when you attempted to do math between two ``Money``
    objects of different currencies.
    """
