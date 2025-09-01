import re
from abc import abstractmethod


class CaseType:
    @staticmethod
    @abstractmethod
    def split(value: str) -> list[str]:
        ...

    @staticmethod
    @abstractmethod
    def join(parts: list[str]) -> str:
        ...


class CamelCase(CaseType):
    @staticmethod
    def split(value: str) -> list[str]:
        return [m.group() for m in re.finditer(r"(^[a-z]*)|([A-Z][a-z]*)", value)]

    @staticmethod
    def join(parts: list[str]) -> str:
        if len(parts) == 0:
            return ""
        return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


class ConstantCase(CaseType):
    @staticmethod
    def split(value: str) -> list[str]:
        return value.split("_")

    @staticmethod
    def join(parts: list[str]) -> str:
        return "_".join(p.upper() for p in parts)


class KebabCase(CaseType):
    @staticmethod
    def split(value: str) -> list[str]:
        return value.split("-")

    @staticmethod
    def join(parts: list[str]) -> str:
        return "-".join(p.lower() for p in parts)


class PascalCase(CaseType):
    @staticmethod
    def split(value: str) -> list[str]:
        return [m.group() for m in re.finditer(r"(^[a-z]*)|([A-Z][a-z]*)", value)]

    @staticmethod
    def join(parts: list[str]) -> str:
        return "".join(p.capitalize() for p in parts)


class SnakeCase(CaseType):
    @staticmethod
    def split(value: str) -> list[str]:
        return value.split("_")

    @staticmethod
    def join(parts: list[str]) -> str:
        return "_".join(p.lower() for p in parts)


def convert_case(value: str, source: type[CaseType], target: type[CaseType]) -> str:
    return target.join(source.split(value))
