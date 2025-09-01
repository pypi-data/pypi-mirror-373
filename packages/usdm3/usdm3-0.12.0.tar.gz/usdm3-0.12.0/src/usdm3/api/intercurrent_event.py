from typing import Literal
from .api_base_model import ApiBaseModelNameLabelDesc


class IntercurrentEvent(ApiBaseModelNameLabelDesc):
    strategy: str
    instanceType: Literal["IntercurrentEvent"]
