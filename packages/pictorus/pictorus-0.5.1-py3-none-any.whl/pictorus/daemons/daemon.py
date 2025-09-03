from abc import ABC, abstractmethod
from typing import Union


class Daemon(ABC):
    def create_service(self, service_name: str, description: str, bin_path: str):
        """
        Runs the daemon:
        1. Stopping the service
        2. Creating the service file
        3. Reloading the daemon
        4. Starting the service
        5. Enabling the service

        Some of these steps are optional depending on the daemon implementation
        """
        self.stop_service(service_name)
        self.create_service_file(service_name, description, bin_path)
        self.reload_daemon(service_name)
        self.start_service(service_name)
        self.enable_service(service_name)

    @abstractmethod
    def create_service_file(self, service_name: str, description: str, bin_path: str):
        """
        Create a daemon service file
        """
        pass

    @abstractmethod
    def stop_service(self, service_name: str):
        """
        Stops the daemon service
        """
        pass

    @abstractmethod
    def start_service(self, service_name: str):
        """
        Starts the daemon service
        """
        pass

    @abstractmethod
    def enable_service(self, service_name: str):
        pass

    @abstractmethod
    def reload_daemon(self, service_name: str):
        pass

    @abstractmethod
    def run(self, cmd: list, check=True, cwd=None):
        """
        The subprocess to run the daemon
        """
        pass

    @abstractmethod
    def logs(self, service_name: str, number_of_lines: Union[int, None]) -> str:
        """
        Fetches the logs of the daemon service
        """
        pass
