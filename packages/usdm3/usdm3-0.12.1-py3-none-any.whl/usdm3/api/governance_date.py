from typing import List, Literal
from .api_base_model import ApiBaseModelNameLabelDesc
from datetime import date
from .code import Code
from .geographic_scope import GeographicScope


class GovernanceDate(ApiBaseModelNameLabelDesc):
    type: Code
    dateValue: date
    geographicScopes: List[GeographicScope]
    instanceType: Literal["GovernanceDate"]
