class SafeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_nested_dicts()


    def _convert_nested_dicts(self):
        for key, value in self.items():
            if isinstance(value, dict) and not isinstance(value, SafeDict):
                super().__setitem__(key, SafeDict(value))

    def __getitem__(self, key):
        if key not in self:
            self[key] = SafeDict()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, SafeDict):
            value = SafeDict(value)
        super().__setitem__(key, value)

    def __bool__(self):
        return bool(len(self))

    # for f{:.2f}
    def __format__(self, format_spec):
        if not self:
            return "0.00"
        raise TypeError("SafeDict cannot be formatted as a number")