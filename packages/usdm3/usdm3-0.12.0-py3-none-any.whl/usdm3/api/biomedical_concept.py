from typing import List, Literal
from .alias_code import AliasCode
from .api_base_model import ApiBaseModelNameLabel
from .biomedical_concept_property import BiomedicalConceptProperty


class BiomedicalConcept(ApiBaseModelNameLabel):
    synonyms: List[str] = []
    reference: str
    properties: List[BiomedicalConceptProperty] = []
    code: AliasCode
    instanceType: Literal["BiomedicalConcept"]
