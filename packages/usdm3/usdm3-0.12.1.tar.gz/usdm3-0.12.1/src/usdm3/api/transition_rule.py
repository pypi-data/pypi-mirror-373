from .api_base_model import ApiBaseModelNameLabelDesc
from typing import Literal


class TransitionRule(ApiBaseModelNameLabelDesc):
    text: str
    instanceType: Literal["TransitionRule"]
