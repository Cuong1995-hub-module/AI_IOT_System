from abc import ABC, abstractmethod

class CameraBackend(ABC):

    @abstractmethod
    def open_camera(self, index: int) -> bool:
        pass

    @abstractmethod
    def get_current_camera(self) -> int:
        pass

    @abstractmethod
    def get_camera_list(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def release(self):
        pass
