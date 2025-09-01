from typing import List, Literal
from .api_base_model import ApiBaseModelNameLabelDesc, ApiBaseModel


class ParameterMap(ApiBaseModel):
    tag: str
    reference: str
    instanceType: Literal["ParameterMap"]


class SyntaxTemplateDictionary(ApiBaseModelNameLabelDesc):
    parameterMaps: List[ParameterMap]
    instanceType: Literal["SyntaxTemplateDictionary"]
