import functools
import os


class LockException(Exception):
    ...


class Lock:
    """Does the same as `lock`, but as a context manager."""
    def __init__(self, lockfile: str):
        self.lockfile = lockfile

    def __enter__(self):
        if os.path.exists(self.lockfile):
            raise LockException(f"Could not acquire lockfile: {self.lockfile}")
        with open(self.lockfile, "w") as f:
            f.write("LOCKED")

    def __exit__(self, *args, **kwargs):
        remote_attempts = 0
        while os.path.exists(self.lockfile) and remote_attempts < 10:
            os.remove(self.lockfile)
            remote_attempts += 1


def lock(lockfile: str):
    """Primitive mechanism to avoid concurrent execution of a function."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if os.path.exists(lockfile):
                raise LockException(f"Could not acquire lockfile: {lockfile}")

            with open(lockfile, "w") as f:
                f.write("LOCK")

            result = func(*args, **kwargs)

            # Multiple attempts just to be super sure I guess?
            remote_attempts = 0
            while os.path.exists(lockfile) and remote_attempts < 10:
                os.remove(lockfile)
                remote_attempts += 1

            return result
        return wrapper
    return decorator
