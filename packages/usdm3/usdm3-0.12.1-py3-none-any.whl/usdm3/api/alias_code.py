from typing import List, Literal
from .api_base_model import ApiBaseModel
from .code import Code


class AliasCode(ApiBaseModel):
    standardCode: Code
    standardCodeAliases: List[Code] = []
    instanceType: Literal["AliasCode"]
