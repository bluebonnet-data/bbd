class _ApiKey:
    def __init__(self):
        self._key = None

    @property
    def key(self):
        if self._key is None:
            raise ValueError("Census api key has not been set!")
        else:
            return self._key

    @key.setter
    def key(self, key_value: str):
        if not isinstance(key_value, str):
            raise ValueError(
                f"Cannot set census api key to {key_value} of type {type(key_value)}. "
                "Value should be a 'str'"
            )
        else:
            self._key = key_value


api_key = _ApiKey()
