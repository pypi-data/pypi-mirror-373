import abc


class AbstractScriptDriver(abc.ABC):
    _instances = {}
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]
    
    @abc.abstractmethod
    def getInstance(self):
        pass


class AbstractStaticChecker(abc.ABC):
    _instances = {}
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]
    
    @abc.abstractmethod
    def getInstance(self):
        pass

    @abc.abstractmethod
    def setHierarchy(hierarchy):
        pass


class AbstractDriver(abc.ABC):
    _instances = {}
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]
    
    @classmethod
    @abc.abstractmethod
    def setDevice(self):
        pass
    
    @classmethod
    @abc.abstractmethod
    def getScriptDriver(self) -> AbstractScriptDriver:
        pass
    
    @classmethod
    @abc.abstractmethod
    def getStaticChecker(self, hierarchy) -> AbstractStaticChecker:
        pass

    @classmethod
    @abc.abstractmethod
    def tearDown(self): ...
