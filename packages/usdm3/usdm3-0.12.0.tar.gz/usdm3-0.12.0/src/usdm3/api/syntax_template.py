from typing import Union, Literal
from .api_base_model import ApiBaseModelNameLabelDesc


class SyntaxTemplate(ApiBaseModelNameLabelDesc):
    text: str
    dictionaryId: Union[str, None] = None
    instanceType: Literal["SyntaxTemplate"]
