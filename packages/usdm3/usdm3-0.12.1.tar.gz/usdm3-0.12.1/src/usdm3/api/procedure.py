from typing import Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc
from .code import Code


class Procedure(ApiBaseModelNameLabelDesc):
    procedureType: str
    code: Code
    studyInterventionId: Union[str, None] = None
    instanceType: Literal["Procedure"]
