"""Provide development tools for monitoring."""

from watchdog.events import FileSystemEventHandler, FileSystemEvent

from regscale.utils.files import print_file_contents


class FileModifiedHandler(FileSystemEventHandler):
    """Handler for file modification events

    :param str file_path: Path to the file to monitor
    """

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle a file modification event and print the file contents

        :param FileSystemEvent event: The event to handle
        :rtype: None
        """
        if not event.is_directory and event.src_path == self.file_path:
            print(f"{self.file_path} modified!")
            print_file_contents(self.file_path)
