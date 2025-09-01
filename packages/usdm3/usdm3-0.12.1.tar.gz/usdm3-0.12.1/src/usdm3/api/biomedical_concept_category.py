from typing import List, Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc
from .alias_code import AliasCode


class BiomedicalConceptCategory(ApiBaseModelNameLabelDesc):
    childIds: List[str] = []
    memberIds: List[str] = []
    code: Union[AliasCode, None] = None
    instanceType: Literal["BiomedicalConceptCategory"]
