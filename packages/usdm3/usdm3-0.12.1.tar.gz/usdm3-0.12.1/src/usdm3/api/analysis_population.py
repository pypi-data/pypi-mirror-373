from .api_base_model import ApiBaseModelNameLabelDesc
from typing import Literal


class AnalysisPopulation(ApiBaseModelNameLabelDesc):
    text: str
    instanceType: Literal["AnalysisPopulation"]
