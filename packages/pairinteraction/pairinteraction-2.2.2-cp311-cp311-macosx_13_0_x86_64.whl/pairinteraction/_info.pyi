# mypy: ignore-errors



class Info:
    with_mkl: bool = ...
    """(arg: object, /) -> bool"""

    has_eigen: bool = ...
    """(arg: object, /) -> bool"""

    has_lapacke_evd: bool = ...
    """(arg: object, /) -> bool"""

    has_lapacke_evr: bool = ...
    """(arg: object, /) -> bool"""

    has_feast: bool = ...
    """(arg: object, /) -> bool"""
