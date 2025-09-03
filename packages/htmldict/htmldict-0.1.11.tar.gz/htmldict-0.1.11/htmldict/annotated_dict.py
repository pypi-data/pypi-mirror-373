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

    def to_flat_dict(self, obj, prefix='', separator='_'):
        flat_dict = {}

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}{separator}{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    flat_dict.update(self.to_flat_dict(value, new_key, separator))
                else:
                    flat_dict[new_key] = value
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                if isinstance(item, (dict, list)):
                    flat_dict.update(self.to_flat_dict(item, new_key, separator))
                else:
                    flat_dict[new_key] = item
        else:
            flat_dict[prefix] = obj

        return flat_dict