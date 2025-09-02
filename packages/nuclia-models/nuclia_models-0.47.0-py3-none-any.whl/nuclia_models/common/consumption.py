from typing import Literal

from pydantic import BaseModel


class TokensDetail(BaseModel):
    input: float
    output: float
    image: float


class Consumption(BaseModel):
    normalized_tokens: TokensDetail
    customer_key_tokens: TokensDetail


class ConsumptionGenerative(Consumption):
    type: Literal["consumption"] = "consumption"
