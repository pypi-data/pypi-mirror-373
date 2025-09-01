from .api_base_model import ApiBaseModel
from typing import Literal


class ScheduleTimelineExit(ApiBaseModel):
    instanceType: Literal["ScheduleTimelineExit"]
