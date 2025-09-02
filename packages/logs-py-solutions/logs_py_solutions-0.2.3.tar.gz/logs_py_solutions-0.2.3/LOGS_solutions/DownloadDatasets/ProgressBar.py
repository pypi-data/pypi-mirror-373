import threading
import time
import sys
from colorama import init


init()


class ProgressBar:
    _progress = False
    _thread = None
    _processed_files = 0
    _event = threading.Event()
    _lock = threading.Lock()

    @classmethod
    def progress_bar(cls, message: str):
        """Creates a progress bar for the console.

        :param message: The message to display in front of the progress bar.
        """
        steps = [" ", " ", " ", " ", " "]
        length = len(steps)
        direction = 1
        index = 0

        while cls._progress:
            if direction == 1:
                steps[index] = "*"
            else:
                steps[index] = " "

            with cls._lock:
                files_count = cls._processed_files

            sys.stdout.write(
                f"\r{message} {' '.join(steps)} | Datasets processed: {files_count}"
            )
            sys.stdout.flush()
            index += direction

            if index == length:
                direction = -1
                index = length - 1
            elif index == -1:
                direction = 1
                index = 0

            time.sleep(0.2)

    @classmethod
    def start_progressbar(cls, message: str = ""):
        """Starts the progress bar.

        :param message: The message to display in front of the progress bar.
        """
        if not cls._progress:
            cls._progress = True
            cls._thread = threading.Thread(target=cls.progress_bar, args=(message,))
            cls._thread.daemon = True
            cls._thread.start()

    @classmethod
    def stop_progressbar(cls):
        """Stops the progress bar."""
        time.sleep(0.5)
        if cls._progress:
            cls._progress = False
            cls._thread.join()
        sys.stdout.write(f"\nDownloaded {cls._processed_files} datasets.\n")
        sys.stdout.flush()

    @classmethod
    def update_processed_files(cls):
        """Updates the number of processed files."""
        with cls._lock:
            cls._processed_files += 1
