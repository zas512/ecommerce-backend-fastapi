from uuid import UUID
from pydantic import BaseModel, ConfigDict


class JwtIdentity(BaseModel):
    id: UUID
    role: str
    model_config = ConfigDict(frozen=True)
