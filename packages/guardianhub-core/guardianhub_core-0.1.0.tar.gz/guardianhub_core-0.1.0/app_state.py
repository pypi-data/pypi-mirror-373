# guardian-core/app_state.py
#
# A simple singleton class for managing application-wide state.
# This ensures that all parts of the application can access a single,
# consistent state object.

class AppState:
    """
    Manages a global, application-wide state using the singleton pattern.
    """
    _instance = None
    _state = {}

    def __new__(cls):
        """
        Ensures only a single instance of AppState exists.
        """
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
        return cls._instance

    def set(self, key, value):
        """
        Sets a key-value pair in the global state.
        """
        self._state[key] = value

    def get(self, key, default=None):
        """
        Retrieves a value from the global state.
        """
        return self._state.get(key, default)

    def __repr__(self):
        """
        Provides a string representation of the current state.
        """
        return f"AppState(state={self._state})"
