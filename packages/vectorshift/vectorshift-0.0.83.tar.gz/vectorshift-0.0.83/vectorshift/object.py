from pydantic import BaseModel
from typing import Union, Optional

class ObjectVersion(BaseModel):
    major: int
    minor: int
    patch: int

    def to_dict(self) -> dict:
        return {
            'major': self.major,
            'minor': self.minor,
            'patch': self.patch
        }


class ObjectInfo(BaseModel):
    object_type: Union[str, int]
    object_id: str
    branch_id: str = None
    version: Optional[ObjectVersion] = None
    state_id: str = None

    def to_dict(self) -> dict:
        return {
            'object_id': self.object_id,
            'object_type': self.object_type,
            'branch_id': self.branch_id,
            'version': self.version,
            'state_id': self.state_id
        }