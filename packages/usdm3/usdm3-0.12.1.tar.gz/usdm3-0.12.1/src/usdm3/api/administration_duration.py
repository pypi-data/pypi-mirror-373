from typing import Literal, Union
from .api_base_model import ApiBaseModel
from .quantity import Quantity


class AdministrationDuration(ApiBaseModel):
    quantity: Union[Quantity, None] = None
    description: str
    durationWillVary: bool
    reasonDurationWillVary: str
    instanceType: Literal["AdministrationDuration"]
