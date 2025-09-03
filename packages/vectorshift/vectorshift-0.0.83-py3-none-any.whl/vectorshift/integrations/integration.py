from vectorshift.object import ObjectInfo
from typing import Literal


class IntegrationObject(ObjectInfo):
    object_type: Literal['Integration'] = 'Integration'