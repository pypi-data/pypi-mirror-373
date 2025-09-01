from pydantic import BaseModel


class RelocationResource(BaseModel):
    column_name: str
    amount: float
