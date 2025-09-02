from typing import Optional

from pydantic import BaseModel, Field


class ConfigModel(BaseModel):
    # all fields are optional
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    output_length: Optional[int] = None
