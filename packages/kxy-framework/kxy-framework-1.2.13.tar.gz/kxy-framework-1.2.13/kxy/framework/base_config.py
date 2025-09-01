from logging import Logger
import os
from abc import ABC, abstractmethod

from .kxy_logger import KxyLogger

class BaseConfig(ABC):
    BussinessLog = False
    @abstractmethod
    def SSO_URL(self):
        pass

    @abstractmethod
    def SystemCode(self):
        pass
    @abstractmethod
    def JWT_SECRET_KEY(self):
        pass
    @abstractmethod
    def JWT_ALGORITHM(self):
        pass
    AppLogger:KxyLogger = None

    def env_first(self):
        for name in [f for f in dir(self) if not callable(f) and not f.startswith('__')]:
            v=os.environ.get(name)
            if v:
                setattr(self, name, v)