from typing import Literal, Union
from .api_base_model import ApiBaseModel
from .alias_code import AliasCode


class Quantity(ApiBaseModel):
    value: float
    unit: Union[AliasCode, None] = None
    instanceType: Literal["Quantity"]
