from typing import Union, List, Literal
from .api_base_model import ApiBaseModelNameLabelDesc
from .transition_rule import TransitionRule


class StudyElement(ApiBaseModelNameLabelDesc):
    transitionStartRule: Union[TransitionRule, None] = None
    transitionEndRule: Union[TransitionRule, None] = None
    studyInterventionIds: List[str] = []
    instanceType: Literal["StudyElement"]
