from typing import List, Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc


class Condition(ApiBaseModelNameLabelDesc):
    text: str
    dictionaryId: Union[str, None] = None
    contextIds: List[str] = []
    appliesToIds: List[str] = []
    instanceType: Literal["Condition"]
