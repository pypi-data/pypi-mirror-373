from xync_schema.models import Ex


class NoCoinOnEx(ValueError):
    def __init__(self, ex: Ex, coinex: str | int):
        self.message = f"Ex: {ex.name}, coin: {coinex}."


class NoCurOnEx(ValueError):
    def __init__(self, ex: Ex, curex: str | int):
        self.message = f"Ex: {ex.name}, cur: {curex}."


class NoPairOnEx(ValueError):
    def __init__(self, ex: Ex, coinex: str | int, curex: str | int):
        self.message = f"Ex: {ex.name}, coin: {coinex}, cur: {curex}."
