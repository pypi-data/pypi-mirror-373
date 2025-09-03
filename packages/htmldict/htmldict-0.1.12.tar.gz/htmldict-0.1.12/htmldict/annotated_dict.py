from typing import Any

from flatten_dict import flatten

class AnnotatedDict(dict):
    def __init__(self, **kwargs):
        super().__init__()
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs.get(kwarg))

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __getattribute__(self, key):
        if key.startswith('_') or key in ('keys', 'values', 'items', 'get', 'to_flat_dict'):
            return super().__getattribute__(key)
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def flatten(self,
            reducer: Any = "tuple",
            inverse: bool = False,
            max_flatten_depth: Any = None,
            enumerate_types: Any = (),
            keep_empty_types: Any = ()
        ) -> dict:
        return flatten(
            self,
            reducer,
            inverse,
            max_flatten_depth,
            enumerate_types,
            keep_empty_types
        )