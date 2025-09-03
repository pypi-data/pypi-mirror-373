from pydantic import BaseModel

class LlamaChains(BaseModel):
    coin: str
    tvl: str
    type: str