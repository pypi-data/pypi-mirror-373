from typing import Literal
from .api_base_model import ApiBaseModelNameLabelDesc
from .quantity import Quantity
from .administration_duration import AdministrationDuration
from .alias_code import AliasCode


class AgentAdministration(ApiBaseModelNameLabelDesc):
    duration: AdministrationDuration
    dose: Quantity
    route: AliasCode
    frequency: AliasCode
    instanceType: Literal["AgentAdministration"]
