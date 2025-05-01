from typing import TypeVar, Generic

T = TypeVar("T")


class nullable(Generic[T]):
    def __init__(self, value: T | None) -> None:
        self.__has_value = value is not None
        if value is not None:
            self.__value = value

    @staticmethod
    def null() -> "nullable[T]":
        return nullable[T](None)

    @property
    def value(self) -> T:
        if self.__has_value:
            return self.__value
        raise Exception()

    @value.setter
    def value(self, value: T | None) -> None:
        if value is not None:
            self.__value = value
        self.__has_value = value is not None

    @property
    def has_value(self) -> bool:
        return self.__has_value

    def __eq__(self, other: T | "nullable[T]") -> bool:
        if self.__has_value:
            if other is T:
                return self.__value.__eq__(other)
            elif other is nullable[T] and other.has_value:
                return self.__value.__eq__(other.value)
        return False

    def __ne__(self, other: T | "nullable[T]") -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.value.__str__() if self.__has_value else "None"
