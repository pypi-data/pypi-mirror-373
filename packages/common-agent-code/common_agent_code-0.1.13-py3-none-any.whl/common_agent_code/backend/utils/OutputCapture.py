import io 
import sys
class OutputCapture:
    def __init__(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def __enter__(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._stdout
        sys.stderr = self._stderr
