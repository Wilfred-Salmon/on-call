from datetime import date
from dataclasses import dataclass

@dataclass(frozen=True)
class Interval:
    start: date
    end: date

    def __repr__(self) -> str:
        return(f"{str(self.start)} -> {str(self.end)}")