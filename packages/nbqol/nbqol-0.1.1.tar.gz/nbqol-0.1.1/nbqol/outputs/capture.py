import sys, io
import logging
import shutil
import threading
import builtins
from contextlib import contextmanager

__all__ = [
    'capture_output', 
    'ThreadSafeStringIO', 
    'CapturedOutput', 
    'CapturedLogs', 
    'OutputCapture'
]

# Capture Outputs ------------------------------

class ThreadSafeStringIO(io.StringIO):
    """A thread-safe version of StringIO for capturing output in multithreaded environments.
    
    This class extends io.StringIO to provide thread safety by using a lock when writing
    to the underlying buffer.
    
    Args:
        *args: Arguments to pass to io.StringIO
        **kwargs: Keyword arguments to pass to io.StringIO
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def write(self, *args, **kwargs):
        """Thread-safe write operation to the StringIO buffer.
        
        Args:
            *args: Arguments to pass to the parent write method
            **kwargs: Keyword arguments to pass to the parent write method
            
        Returns:
            The return value from the parent write method
        """
        with self.lock:
            return super().write(*args, **kwargs)

class CapturedOutput:
    """A class representing captured output from stdout or stderr.
    
    This class wraps a StringIO object and provides string representation
    for the captured output.
    
    Args:
        string_io (ThreadSafeStringIO): The StringIO object containing the captured output
    """
    def __init__(self, string_io):
        self._string_io = string_io

    def __str__(self):
        """Return the string representation of the captured output.
        
        Returns:
            str: The contents of the captured output
        """
        return self._string_io.getvalue()

    def __repr__(self):
        """Return the string representation of the captured output.
        
        Returns:
            str: The contents of the captured output
        """
        return self.__str__()

class CapturedLogs(CapturedOutput):
    """A class representing captured log output with associated log records.
    
    This class extends CapturedOutput to include the original log records
    that were captured, allowing for more detailed inspection.
    
    Args:
        string_io (ThreadSafeStringIO): The StringIO object containing the captured logs
        records (list): List of logging.LogRecord objects that were captured
    """
    def __init__(self, string_io, records):
        super().__init__(string_io)
        self.records = records

    def __str__(self):
        """Return the string representation of the captured logs.
        
        Returns:
            str: The contents of the captured logs
        """
        return self._string_io.getvalue()

class OutputCapture:
    """A class for capturing and storing outputs from stdout, stderr, and logging.
    
    This class provides a container for outputs captured from different sources,
    with properties to access each output type as well as a formatted combined output.
    """
    def __init__(self):
        """Initialize an OutputCapture object with empty buffers for each output type."""
        self._stdout = ThreadSafeStringIO()
        self._stderr = ThreadSafeStringIO()
        self._logs = ThreadSafeStringIO()
        self._log_records = []

    @property
    def stdout(self):
        """Get the captured standard output.
        
        Returns:
            CapturedOutput: An object containing the captured stdout
        """
        return CapturedOutput(self._stdout)

    @property
    def stderr(self):
        """Get the captured standard error.
        
        Returns:
            CapturedOutput: An object containing the captured stderr
        """
        return CapturedOutput(self._stderr)

    @property
    def logs(self):
        """Get the captured logs.
        
        Returns:
            CapturedLogs: An object containing the captured logs and their records
        """
        return CapturedLogs(self._logs, self._log_records)

    @property
    def text(self):
        """Get a formatted string representation of all captured outputs.
        
        This property generates a formatted multi-section string containing all
        non-empty output sections (stdout, stderr, logs) with appropriate headers.
        
        Returns:
            str: A formatted string containing all captured outputs
        """
        sections = [
            ("STDOUT", self._stdout),
            ("STDERR", self._stderr),
            ("LOGS", self._logs)
        ]

        term_width = shutil.get_terminal_size((80, 20)).columns

        output = [] # non-empty entries
        
        for name, io_obj in sections:
            if io_obj.getvalue():
                separator = '-' * (term_width - len(name) - 1)
                output.append(f"{name}:{separator}\n{io_obj.getvalue().strip()}")
        
        return "\n\n".join(output)

    def __str__(self):
        """Return the string representation of all captured outputs.
        
        Returns:
            str: A formatted string containing all captured outputs
        """
        return self.text

    def __repr__(self):
        """Return the string representation of all captured outputs.
        
        Returns:
            str: A formatted string containing all captured outputs
        """
        return self.__str__()

class AllCaptureHandler(logging.Handler):
    """A logging handler that captures logs from all loggers.
    
    This handler captures logs from all loggers and writes them to a StringIO object,
    while also keeping the original log records for later inspection.
    
    Args:
        string_io (ThreadSafeStringIO): The StringIO object to write logs to
        record_list (list): A list to store the original log records
    """
    def __init__(self, string_io, record_list):
        super().__init__()
        self.string_io = string_io
        self.record_list = record_list

    def emit(self, record):
        """Process a log record by storing it and writing the formatted message.
        
        Args:
            record (logging.LogRecord): The log record to process
        """
        self.record_list.append(record)
        original_handlers = logging.getLogger(record.name).handlers
        for handler in original_handlers:
            if handler != self:
                formatted_message = handler.format(record)
                self.string_io.write(formatted_message + '\n')

    def handle(self, record):
        """Handle a log record (overridden to always return True).
        
        Args:
            record (logging.LogRecord): The log record to handle
            
        Returns:
            bool: Always returns True
        """
        self.emit(record); return True

def create_print_capture(string_io):
    """Create a new print function that captures output to a StringIO object.
    
    Args:
        string_io (ThreadSafeStringIO): The StringIO object to capture print output to
        
    Returns:
        tuple: A tuple containing (new_print_function, original_print_function)
    """
    original_print = builtins.print
    def new_print(*args, **kwargs):
        kwargs['file'] = string_io
        original_print(*args, **kwargs)
    return new_print, original_print

@contextmanager
def capture_output(apply=True, **kwargs):
    """Context manager to capture all outputs (stdout, stderr, and logs).
    
    This function provides a simple interface to capture all outputs in a
    context, returning them as an OutputCapture object.
    
    Args:
        apply (bool): Whether to actually capture outputs. If False, yields None.
        **kwargs: Additional keyword arguments to pass to _capture_all_outputs.
                  verbose (bool): Whether to print a message when capturing starts.
                  allow_print (bool): Whether to allow regular print statements to still
                  appear in the console.
    
    Yields:
        OutputCapture or None: An object containing all captured outputs, or None if apply=False.
    
    Examples:
        >>> from nbqol.outputs import capture_output
        >>> with capture_output() as captured:
        ...     print("This will be captured")
        ...     import logging
        ...     logging.warning("This warning will be captured")
        >>> print(captured.stdout)
        >>> This will be captured
        >>> print(captured.logs)
        >>> WARNING:root:This warning will be captured
    """
    if not apply: # override the capture
        yield None 
    else: # actually run the capture
        with _capture_all_outputs(**kwargs) as output:
            yield output

@contextmanager
def _capture_all_outputs(**kwargs):
    """Implementation of output capture as a context manager.
    
    This internal function does the actual work of capturing outputs by
    temporarily replacing sys.stdout, sys.stderr, the print function,
    and adding a capture handler to all loggers.
    
    Args:
        **kwargs: Keyword arguments
            - verbose (bool): Whether to print a message when capturing starts
            - allow_print (bool): Whether to allow print statements to also go to the
              original stdout
              
    Yields:
        OutputCapture: An object containing all captured outputs
    """
    output = OutputCapture()
    
    if kwargs.get('verbose', False):
        print('Capturing all outputs.')
    
    output = OutputCapture() # init
    
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    original_displayhook = sys.displayhook

    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()

    all_loggers = [logging.getLogger(name) for name 
                   in logging.root.manager.loggerDict]
    
    original_logger_levels = {logger: logger.level 
                              for logger in all_loggers}

    new_print, og_print = create_print_capture(output._stdout)

    try: # Capture all logging
        capture_handler = AllCaptureHandler(output._logs, output._log_records)
        for logger in all_loggers + [root_logger]:
            logger.addHandler(capture_handler)

        # Capture stdout and stderr
        sys.stdout = output._stdout
        sys.stderr = output._stderr

        # Capture print statements
        builtins.print = new_print

        # override if allow print
        if kwargs.get('allow_print'):
            builtins.print = og_print

        # Custom display hook for Jupyter
        def custom_displayhook(value):
            if value is not None:
                output._stdout.write(repr(value) + '\n')
        sys.displayhook = custom_displayhook

        yield output

    finally: # Restore original settings
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        sys.displayhook = original_displayhook

        # restore original print:
        builtins.print = og_print
        
        for logger in all_loggers + [root_logger]:
            logger.removeHandler(capture_handler)