from typing import Generic, TypeVar, Any
from weakref import WeakValueDictionary

from runtime.reflection.lite.core.threading import Lock

T = TypeVar("T")

class Cache(Generic[T]):
    __slots__ = [ "__map", "__lock" ]

    def __init__(self):
        self.__map = WeakValueDictionary[int | str, T]()
        self.__lock = Lock()

    def try_get(self, key: Any) -> T | None:
        with self.__lock:
            oid = get_id(key)
            if oid in self.__map and ( result := self.__map[oid] ):
                return result

    def set(self, key: Any, value: T) -> T:
        with self.__lock:
            self.__map[get_id(key)] = value
            return value


def get_id(obj: Any) -> int | str:
    return f"{str(obj)}_{id(obj)}"