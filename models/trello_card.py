from pydantic import BaseModel
from typing import List
from pydantic import field_validator

class TrelloCard(BaseModel):

    titulo: str
    descricao: str
    idList: str
#    tags: List[str]
#    complexidade: int
#    story:str | None
#    epic: str | None

# @field_validator("complexidade")
# def validar_complexidade(cls, v):

#     if v not in [1,3,5,8,13]:
#         raise ValueError("complexidade inválida")

#     return v

# Schema para responder ao cliente
class TrelloCardResponseSchema(BaseModel):
    idList: str
    name: str
    desc: str
    # tags: List[str]
    # complexity: int
    # members: List[str]