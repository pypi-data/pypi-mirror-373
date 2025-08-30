"""
The Bauplan module does not come with pandas, but it can be used with pandas
workflows if pandas is installed.

This module provides a few utility functions that can be used to run SQL queries against
a Bauplan instance, and to visualize the results in a Python notebook through a magic cell syntax.
"""

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from pandas import DataFrame

from . import _client, exceptions

"""
_INTERNALNOTE: if you add a function here, you must also wrap it with the pandas_import_checker
decorator to make sure we gracefully handle the case where pandas is not installed.
"""


def _try_pandas_import() -> None:
    try:
        import pandas  # noqa
    except ModuleNotFoundError:
        raise exceptions.MissingPandasError from None


# Utility decorator ####
def pandas_import_checker(f: Callable) -> Callable:
    """
    Decorator checks if pandas is installed before running the function.

    The user may have already pandas installed, so we don't bundle it
    with our SDK - however, if they don't have it, we should let them know
    that conversion to pandas object will not work!
    """

    @wraps(f)
    def wrapped(*args, **kwargs) -> Any:
        # try import pandas first
        _try_pandas_import()
        # if pandas can be imported, run the function
        return f(*args, **kwargs)

    return wrapped


def magic_cell_import_checker(f: Callable) -> Callable:
    """
    Decorator replace the proper magic cell import with a dummy function if the magic cell
    import failed at import time.
    """

    @wraps(f)
    def wrapped(*args, **kwargs) -> None:
        raise exceptions.MissingMagicCellError from None

    return wrapped


# Notebook-specific functions ####


def in_notebook() -> bool:
    """
    From: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
    """
    try:
        from IPython import get_ipython  # type: ignore

        if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


# we try and import the magic cell first
try:
    # check if we are in a notebook context
    if not in_notebook():
        raise ModuleNotFoundError

    from IPython.core.magic import register_cell_magic  # type: ignore

except ModuleNotFoundError:
    # if it fails, we replace the magic cell import with a dummy function
    register_cell_magic = magic_cell_import_checker


@register_cell_magic
def bauplan_sql(line: int, cell: str) -> 'DataFrame':
    """
    This function is a magic cell that allows users to run SQL queries on Bauplan
    directly in a Python notebook cell - optionally, the branch can be specified
    next to the magic command, e.g.:

    ```sql
    %%bauplan_sql main

    SELECT c1 FROM t2 WHERE f=1
    ```

    The result of the query will be returned as a pandas DataFrame object, which gets
    nicely visualized in a Python notebook by default.

    This function is not intended to be called directly, but rather used as a magic cell.

    If you do not have pandas installed, this raises bauplan.exceptions.MissingPandasError.
    """
    _try_pandas_import()
    ref: Optional[str] = line if line is not None else 'main'
    query = cell.strip()
    client = _client.Client()
    return client.query(query=query, ref=ref).to_pandas().head()
