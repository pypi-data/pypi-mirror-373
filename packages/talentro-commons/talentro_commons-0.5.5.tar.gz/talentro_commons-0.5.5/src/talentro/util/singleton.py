from threading import Lock


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton:
    _instances = {}

    @staticmethod
    def singleton_instance(class_obj, *args, **kwargs):
        if class_obj not in Singleton._instances:
            Singleton._instances[class_obj] = class_obj(*args, **kwargs)
        return Singleton._instances[class_obj]
