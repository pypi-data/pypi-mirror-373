from typing import Union
from usdm3.api.api_base_model import ApiBaseModel
from usdm3.api.study import Study


class Wrapper(ApiBaseModel):
    study: Study
    usdmVersion: str
    systemName: Union[str, None] = None
    systemVersion: Union[str, None] = None
