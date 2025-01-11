from typing import Literal

from pydantic import BaseModel, ConfigDict

class GateStatus(BaseModel):
    model_config = ConfigDict(
        frozen=True,
    )

    now: Literal["open", "close"]
