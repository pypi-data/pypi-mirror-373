from typing import List, Literal
from .api_base_model import ApiBaseModel
from .analysis_population import AnalysisPopulation
from .intercurrent_event import IntercurrentEvent


class Estimand(ApiBaseModel):
    summaryMeasure: str
    analysisPopulation: AnalysisPopulation
    interventionId: str
    variableOfInterestId: str
    intercurrentEvents: List[IntercurrentEvent]
    instanceType: Literal["Estimand"]
