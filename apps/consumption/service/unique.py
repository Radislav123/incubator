class Unique:
    id: int
    _hash: int
    unique_counter = 0

    def __new__(cls, *args, **kwargs) -> "Unique":
        instance = super().__new__(cls)
        instance.id = cls.unique_counter
        instance._hash = instance.id
        cls.unique_counter += 1

        # noinspection PyTypeChecker
        return instance

    def __hash__(self) -> int:
        return self._hash
