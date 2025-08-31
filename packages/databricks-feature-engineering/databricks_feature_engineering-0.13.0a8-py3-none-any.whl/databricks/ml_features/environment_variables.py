import os


class _EnvironmentVariable:
    """
    Represents an environment variable for the feature store client for custom configurations as needed.
    """

    def __init__(self, name, type_, default):
        self.name = name
        self.type = type_
        self.default = default

    @property
    def defined(self):
        return self.name in os.environ

    def get_raw(self):
        return os.getenv(self.name)

    def set(self, value):
        os.environ[self.name] = str(value)

    def unset(self):
        os.environ.pop(self.name, None)

    def get(self):
        """
        Reads the value of the environment variable if it exists and converts it to the desired
        type. Otherwise, returns the default value.
        """
        if (val := self.get_raw()) is not None:
            try:
                return self.type(val)
            except Exception as e:
                raise ValueError(
                    f"Failed to convert {val!r} to {self.type} for {self.name}: {e}"
                )
        return self.default

    def __str__(self):
        return f"{self.name} (default: {self.default}, type: {self.type.__name__})"

    def __repr__(self):
        return repr(self.name)

    def __format__(self, format_spec: str) -> str:
        return self.name.__format__(format_spec)


# The threshold (in MB) where a broadcast join will be performed for the asof join for point in time feature join
# Default is 20MB as benchmarks show diminishing returns with broadcast past this value.The default spark broadcast join threshold is 10MB
BROADCAST_JOIN_THRESHOLD = _EnvironmentVariable(
    "BROADCAST_JOIN_THRESHOLD", int, 20 * 1024 * 1024
)
