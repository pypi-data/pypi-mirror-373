from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class CaseInsensitiveEnum(str, Enum):
    @classmethod
    def _missing_(cls, value: Any) -> Optional[str]:
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.lower() == value:
                    return member
        return None


class Aggregation(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    MILLENNIUM = "millennium"


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
