from datetime import date

class Interval:
    start: date
    end: date

    def __init__(self, start: date, end: date) -> None:
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return(f"{str(self.start)} -> {str(self.end)}")