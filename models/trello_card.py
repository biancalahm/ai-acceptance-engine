# models/trello_card.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class TrelloCard(BaseModel):
    titulo:   str = Field(..., alias="name")
    descricao: str = Field(..., alias="desc")
    idList:   str = Field(..., alias="idList")
    pos:      Optional[str] = Field(default="bottom", alias="pos")

    model_config = {"populate_by_name": True}

    @field_validator("titulo", "descricao", "idList")
    def nao_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError("Campo não pode ser vazio")
        return v