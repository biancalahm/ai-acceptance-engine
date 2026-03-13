from enum import Enum


class TipoRequisito(Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    AMBOS = "ambos"


def detectar_tipo(requisito_texto: str) -> TipoRequisito:
    texto = requisito_texto.upper()

    if "[BACKEND]" in texto:
        return TipoRequisito.BACKEND

    if "[FRONTEND]" in texto:
        return TipoRequisito.FRONTEND

    return TipoRequisito.AMBOS