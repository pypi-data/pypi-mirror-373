from enum import Enum

from .report_schema import (
    StatusPerm,
    StatusCrawl,
    StatusConvert,
    StatusExtract,
    StatusConvertTxt,
    StatusConvertMeta,
)

'''Common use
Use for common
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''


class DefaultStr(Enum):
    N_A = "N/A"
    UNKNOWN = "unknown"


class DateMaxMin(Enum):
    DATE_MAX = '2000-01-01'
    DATE_MIN = '2100-12-31'


class StrBoolean(Enum):
    TRUE = "true"
    FALSE = "false"
