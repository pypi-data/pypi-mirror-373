from typing import Literal, Union
from .api_base_model import ApiBaseModelNameLabelDesc


class BiomedicalConceptSurrogate(ApiBaseModelNameLabelDesc):
    reference: Union[str, None] = None
    instanceType: Literal["BiomedicalConceptSurrogate"]
