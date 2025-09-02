from dataclasses import dataclass, field
import datetime


@dataclass
class Dates:
    start: datetime.datetime = field(default=None)
    end: datetime.datetime = field(default=None)
