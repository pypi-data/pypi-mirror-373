from typing import Optional

from decentriq_util.error import SafeError


class ValidationError(SafeError):
    def __init__(self, safe: Optional[str] = None, unsafe: Optional[str] = None):
        """Create a validation error.

        When printing error messages in the enclave, "safe" messages will be
        displayed to the user even if INCLUDE_CONTAINER_LOGS_ON_ERROR is false
        (for example in a Python computation that runs in a published DCR).
        Unsafe messages will only be printed if INCLUDE_CONTAINER_LOGS_ON_ERROR is true,
        e.g. during a dev computation.
        """
        if unsafe is None:
            unsafe = safe
        self.unsafe_message = unsafe
        self.safe_message = safe

    def safe_str(self) -> str:
        return self.safe_message or "ValidationError"

    def __str__(self) -> str:
        return self.unsafe_message or "ValidationError"
