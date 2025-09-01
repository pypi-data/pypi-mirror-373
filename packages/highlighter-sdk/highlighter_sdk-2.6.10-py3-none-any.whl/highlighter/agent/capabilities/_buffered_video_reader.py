import os
import tempfile
import threading

import cv2


class StreamAsFile:
    def __init__(self):
        """
        Initialize the StreamAsFile object by creating a named pipe without opening it.
        This avoids blocking during instantiation.

        The fifo pipe has a max size of 64Kb and will block untill there space
        for the next chunk thus minimizing memory usage.
        """
        # Create a temporary directory to hold the named pipe
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pipe_path = os.path.join(self.temp_dir.name, "videopipe")
        # Create the named pipe (non-blocking operation)
        os.mkfifo(self.pipe_path)
        self.w = None  # File descriptor for writing, initialized as None

    def open_pipe(self):
        """
        Open the pipe for writing. This will block until a reader is available.
        """
        if self.w is None:
            self.w = os.open(self.pipe_path, os.O_WRONLY)

    def write(self, data):
        """
        Write bytes to the pipe. Opens the pipe if not already open.
        """
        if self.w is None:
            self.open_pipe()  # This may block until a reader is available

        try:
            os.write(self.w, data)
        except BrokenPipeError:
            self.close()
            raise

    def close(self):
        """
        Close the write end of the pipe and clean up the temporary directory.
        """
        if self.w is not None:
            os.close(self.w)
            self.w = None
        self.temp_dir.cleanup()

    @property
    def filepath(self):
        """
        Return the path to the named pipe, which can be used by cv2.VideoCapture.
        """
        return self.pipe_path

    def __enter__(self):
        """
        Enter the runtime context for use with 'with' statement.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context and clean up resources.
        """
        self.close()


class BufferedVideoCapture:
    """Wrapper around OpenCV VideoCapture that allows you it to read a
    video from a bytes buffer.

    USAGE:

    reader = BufferedVideoReader(sys.stdin.buffer)
    ret, frame = reader.cap()
    """

    def __init__(self, buffer):
        self._buffer = buffer
        self._is_opened = False

        def _stream_bytes(stream, buffer):
            try:
                while True:
                    data = buffer.read(4096)
                    if not data:
                        break
                    stream.write(data)  # This will block until a reader is available
            except BrokenPipeError:
                pass
            finally:
                stream.close()

        self._stream = StreamAsFile()
        self._writer_thread = threading.Thread(target=_stream_bytes, args=(self._stream, buffer))
        self._writer_thread.start()

        # Open the pipe for reading with cv2.VideoCapture in the main thread
        self._cap = cv2.VideoCapture(self._stream.filepath)
        self._is_opened = True

    def isOpened(self):
        """pascalCase to mimmic cv2.VideoCapture.isOpened"""
        return self._is_opened

    def read(self):
        return self._cap.read()

    def get(self, *args, **kwargs):
        return self._cap.get(*args, **kwargs)

    def __del__(self):
        self.release()

    def release(self):
        self._cap.release()
        self._writer_thread.join()  # Wait for the writing thread to finish
