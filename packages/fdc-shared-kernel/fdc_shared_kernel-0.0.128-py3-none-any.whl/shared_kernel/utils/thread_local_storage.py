import threading


class ThreadLocalStorage:
    """
    Utility class for managing thread-local storage with class-level methods and variables.
    """

    # Class-level thread-local storage
    _storage = threading.local()

    @classmethod
    def set(cls, key: str, value: any) -> None:
        """
        Sets a value in the thread-local storage.

        :param key: The key for the value.
        :param value: The value to be stored.
        """
        if not hasattr(cls._storage, "data"):
            cls._storage.data = {}
        cls._storage.data[key] = value

    @classmethod
    def set_all(cls, values: dict) -> None:
        """
        Sets multiple key-value pairs in the thread-local storage.

        :param values: A dictionary of key-value pairs to store.
        """
        if not hasattr(cls._storage, "data"):
            cls._storage.data = {}
        cls._storage.data.update(values)

    @classmethod
    def get(cls, key: str, default=None) -> any:
        """
        Retrieves a value from the thread-local storage.

        :param key: The key for the value.
        :param default: The default value to return if the key is not found.
        :return: The value associated with the key, or the default value.
        """
        if hasattr(cls._storage, "data") and key in cls._storage.data:
            return cls._storage.data[key]
        return default

    @classmethod
    def get_all(cls) -> dict:
        """
        Retrieves all key-value pairs from the thread-local storage.

        :return: A dictionary of all thread-local data.
        """
        return getattr(cls._storage, "data", {}).copy() if hasattr(cls._storage, "data") else {}

    @classmethod
    def clear(cls) -> None:
        """
        Clears all values from the thread-local storage.
        """
        if hasattr(cls._storage, "data"):
            cls._storage.data.clear()
