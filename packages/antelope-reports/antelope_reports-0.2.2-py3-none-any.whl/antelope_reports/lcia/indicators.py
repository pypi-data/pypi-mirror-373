from pydantic import BaseModel


class LciaDefinition(BaseModel):
    origin: str
    external_ref: str
    method: str = 'LCIA Method'
    category: str = 'LCIA Category'
    name: str  # category
    unit: str
    indicator: str
