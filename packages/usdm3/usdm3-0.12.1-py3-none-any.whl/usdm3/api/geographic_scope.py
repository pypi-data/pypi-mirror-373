from typing import Literal, Union
from .api_base_model import ApiBaseModel
from .code import Code
from .alias_code import AliasCode
from .quantity import Quantity


class GeographicScope(ApiBaseModel):
    type: Code
    code: Union[AliasCode, None] = None
    instanceType: Literal["GeographicScope"]


class SubjectEnrollment(GeographicScope):
    quantity: Quantity
    instanceType: Literal["SubjectEnrollment"]
