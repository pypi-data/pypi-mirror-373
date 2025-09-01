from typing import List, Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc, ApiBaseModel


class ConditionAssignment(ApiBaseModel):
    condition: str
    conditionTargetId: str
    instanceType: Literal["ConditionAssignment"]


class ScheduledInstance(ApiBaseModelNameLabelDesc):
    timelineId: Union[str, None] = None
    timelineExitId: Union[str, None] = None
    defaultConditionId: Union[str, None] = None
    epochId: Union[str, None] = None
    instanceType: Literal["ScheduledInstance"]


class ScheduledActivityInstance(ScheduledInstance):
    activityIds: List[str] = []
    encounterId: Union[str, None] = None
    instanceType: Literal["ScheduledActivityInstance"]


class ScheduledDecisionInstance(ScheduledInstance):
    conditionAssignments: List[ConditionAssignment]
    instanceType: Literal["ScheduledDecisionInstance"]
