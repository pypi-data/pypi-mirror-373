import sys, re
from datetime import datetime
import IPython
import textom
import matplotlib.pyplot as plt
from .src import misc as msc
from .src import handle as hdl

def main():
    """Launches TexTOM in iPython mode
    """
    msc.fancy_title()
    plt.ion()
    # Create a dictionary of all public functions and classes from textom
    textom_namespace = {k: v for k, v in vars(textom).items() if not k.startswith("_")}

    log_file_path = "textom_history.log"  # The file to store logs
    with open(log_file_path, "a") as log_file:
        # Redirect stdout and stderr
        sys.stdout = Tee(log_file, sys.stdout)
        sys.stderr = Tee(log_file, sys.stderr)

        # Start IPython with the namespace
        IPython.start_ipython(
            argv=[], 
            # argv=["--logappend", 'textom_history.log'], 
            user_ns=textom_namespace
            )
        
class Tee:
    """A class to write a log file from terminal in and output."""
    ansi_escape = re.compile(r'\x1b\[.*?[@-~]')  # Regex to match ANSI escape sequences

    def __init__(self, log_file, stream):
        self.log_file = log_file  # File object for logging
        self.stream = stream      # Original stream (e.g., sys.stdout or sys.stderr)

    def write(self, message):
        # Always write the raw message to the terminal
        self.stream.write(message)

        # Strip ANSI escape sequences for the log file
        stripped_message = self.ansi_escape.sub('', message)

        # Add a timestamp and write to the log file if not ignored
        if not self._should_ignore(stripped_message):
            timestamped_message = self._add_timestamp(stripped_message)
            self.log_file.write(timestamped_message)
            self.log_file.flush()  # Ensure it's written immediately

    def flush(self):
        """Flush both the log file and the original stream."""
        self.log_file.flush()
        self.stream.flush()

    def isatty(self):
        """Delegate the check to the original stream."""
        return self.stream.isatty()

    def fileno(self):
        """Delegate the fileno method to the original stream."""
        return self.stream.fileno()

    def _should_ignore(self, message):
        """Determine if a message should be ignored for logging."""
        ignore_patterns = [
            r'^In \[',       # IPython input prompts
            r'^Out\[\d+\]',  # IPython output prompts
        ]
        for pattern in ignore_patterns:
            if re.search(pattern, message):
                return True
        return False

    def _add_timestamp(self, message):
        """Add a timestamp to the message for logging."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Add timestamp only to non-empty lines
        return f"{timestamp} {message}" if message.strip() else message

def config():
    """Opens the config file to modify
    """
    config_path = hdl.get_file_path('textom','config.py')
    hdl.open_with_editor(config_path)

def documentation():
    """Opens the TexTOM documentation in a pdf viewer
    """
    doc_path = hdl.get_file_path('textom','documentation/textom_documentation.pdf')
    hdl.open_pdf(doc_path)