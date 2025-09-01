from typing import List, Literal
from .api_base_model import ApiBaseModelNameLabelDesc
from .code import Code


class Indication(ApiBaseModelNameLabelDesc):
    codes: List[Code] = []
    isRareDisease: bool
    instanceType: Literal["Indication"]
