from typing import Optional

from pydantic import BaseModel, Field


class ConfigModel(BaseModel):
    # all fields are optional
    temperature: Optional[float]
    top_p: Optional[float]
    top_k: Optional[int]
    output_length: Optional[int]
