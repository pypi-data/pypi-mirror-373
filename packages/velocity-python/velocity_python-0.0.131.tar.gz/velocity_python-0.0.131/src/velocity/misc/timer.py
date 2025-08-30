import time
from typing import Optional


class Timer:
    def __init__(self, label: str = "Timer"):
        """
        Initializes a Timer instance with an optional label and starts the timer.
        """
        self._label = label
        self._start: Optional[float] = None
        self._end: Optional[float] = None
        self._diff: Optional[float] = None
        self.start()

    def start(self) -> None:
        """Starts or restarts the timer."""
        self._start = time.time()
        self._end = None
        self._diff = None

    def stop(self) -> float:
        """Stops the timer and calculates the time elapsed."""
        if self._start is None:
            raise ValueError("Timer has not been started.")
        self._end = time.time()
        self._diff = self._end - self._start
        return self._diff

    def elapsed(self) -> float:
        """Returns the elapsed time in seconds without stopping the timer."""
        if self._start is None:
            raise ValueError("Timer has not been started.")
        return time.time() - self._start

    def __str__(self) -> str:
        """Returns a string representation of the time elapsed or final time."""
        if self._diff is not None:  # Timer has been stopped
            return f"{self._label}: {self._diff:.4f} s"
        else:  # Timer is still running, show elapsed time
            return f"{self._label}: {self.elapsed():.4f} s"


if __name__ == "__main__":
    t = Timer("My Label")
    time.sleep(0.003)
    print(t)  # Should display elapsed time
    time.sleep(3)
    t.stop()
    print(t)  # Should display the stopped time (final diff)
