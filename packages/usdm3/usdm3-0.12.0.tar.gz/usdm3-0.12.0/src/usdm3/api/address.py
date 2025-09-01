from typing import Literal, Union
from .api_base_model import ApiBaseModel
from .code import Code


class Address(ApiBaseModel):
    text: Union[str, None] = None
    line: Union[str, None] = None
    city: Union[str, None] = None
    district: Union[str, None] = None
    state: Union[str, None] = None
    postalCode: Union[str, None] = None
    country: Union[Code, None] = None
    instanceType: Literal["Address"]
