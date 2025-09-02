import logging
import os
from friendly_exception import FriendlyException
from abc import ABC, abstractmethod

class BaseConfig(ABC):
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

    def env_first(self):
        for name in [f for f in dir(self) if not callable(f) and not f.startswith('__')]:
            v=os.environ.get(name)
            if v:
                setattr(self, name, v)
                
class dev(BaseConfig):
    SSO_URL='gfdgdfgdfgdfgdf'
    SystemCode='xxxxxxxxxxxx'
    
if __name__ == '__main__':
    config = dev()
    print(config.SystemCode)