from queue import Queue
import threading

class QueueFlow:
    def __init__(self, max_commands: int = 10):
        self.command_queue = Queue(maxsize=max_commands)  # Store commands
        self.worker_thread = threading.Thread(target=self._process_commands, daemon=True)
        self.worker_thread.start()

    def add_command(self, command: Command) -> None:
        """Add a command to the flow queue"""
        self.command_queue.put(command)  # Blocks if queue is full

    def _process_commands(self) -> None:
        """Worker loop to process commands sequentially"""
        while True:
            command = self.command_queue.get()  # Blocks if queue is empty
            try:
                command.execute()  # Run the command
            finally:
                self.command_queue.task_done()  # Mark command as processed

    def wait_for_completion(self) -> None:
        """Wait for all commands in the queue to finish"""
        self.command_queue.join()