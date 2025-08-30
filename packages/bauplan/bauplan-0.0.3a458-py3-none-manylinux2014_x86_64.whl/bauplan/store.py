"""
This module contains methods to interact with Bauplan key-value object store. In particular, it
provides methods to save and load Python objects from the store: for example, you main save a
scikit model after training and load it later to make predictions, or you may pass a parameter
outside of the usual Arrow tables between nodes.

Note that some basic checks are performed to ensure that the object can be serialized and deserialized.

```python notest
import bauplan

# train a model
tree = DecisionTreeClassifier().fit(X, y)
# save the model in the store
bauplan.store.save_obj("tree", tree)

# later in the DAG, retrieve the model with the same key
tree = bauplan.load_obj("tree")
# use the Python object as intended, e.g. make predictions
y_hat = tree.predict(X_test)
```
"""

from typing import Any

from . import exceptions


def load_obj(key: str) -> Any:
    """
    Return the Python object previously stored at the given key.

    Parameters:
        key: the key associated with the object to retrieve.

    Returns:
        the Python object stored at the given key, deserialized from the store.

    """
    from ._runtime_private._store import load_obj as _load_obj

    try:
        return _load_obj(key)
    except Exception as e:
        if e.__class__.__name__ == 'UserObjectWithKeyExistsError':
            raise exceptions.UserObjectKeyNotExistsError(str(e)) from e

        if e.__class__.__name__ == 'MismatchedPythonVersionsError':
            raise exceptions.MismatchedPythonVersionsError(str(e)) from e

        raise exceptions.UnhandledRuntimeError(str(e)) from e


def save_obj(key: str, obj: Any) -> None:
    """
    Store a Python object with a key, to be later retrieved in other parts of the DAG.

    Parameters:
        key: the key associated with the object to store.
        obj: the Python object to store, must be serializable using pickling

    Returns:
        None

    Raises:
        ObjectTooBigError: If the object being pickled is too big, this error is raised
        ObjectCannotBeSerializedError: If the object cannot be serialized, this error is raised
        UserObjectKeyNotExistsError: If another DAG node already saved an object with key, this error is raised
        UnhandledRuntimeError: Raised if an exception is throw and it is not any of the above

    """
    from ._runtime_private._store import save_obj as _save_obj

    try:
        _save_obj(key, obj)
    except Exception as e:
        if e.__class__.__name__ == 'ObjectTooBigError':
            raise exceptions.ObjectTooBigError(str(e)) from e

        if e.__class__.__name__ == 'ObjectCannotBeSerializedError':
            raise exceptions.ObjectCannotBeSerializedError(str(e)) from e

        if e.__class__.__name__ == 'UserObjectWithKeyExistsError':
            raise exceptions.UserObjectWithKeyExistsError(str(e)) from e

        raise exceptions.UnhandledRuntimeError(str(e)) from e
