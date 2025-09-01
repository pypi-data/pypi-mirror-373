from typing import List, Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc
from .schedule_timeline_exit import ScheduleTimelineExit
from .scheduled_instance import ScheduledActivityInstance, ScheduledDecisionInstance
from .timing import Timing


class ScheduleTimeline(ApiBaseModelNameLabelDesc):
    mainTimeline: bool
    entryCondition: str
    entryId: str
    exits: List[ScheduleTimelineExit] = []
    timings: List[Timing] = []
    instances: List[Union[ScheduledActivityInstance, ScheduledDecisionInstance]] = []
    instanceType: Literal["ScheduleTimeline"]
