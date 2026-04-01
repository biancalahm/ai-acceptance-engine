# skills/frontend.py
from langchain.tools import tool
from agent.context import req_ctx, card_ctx
from services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)
_llm = LLMService()

_funcionalidades: list[str] = []
_detalhamentos:   list[dict] = []
_stories:         list[dict] = []


@tool
def skill_levantar_frontend(_: str = "") -> str:
    """
    Levanta todas as funcionalidades de frontend necessárias.
    Chame APÓS skill_formatar_backend — precisa dos endpoints do backend.
    Chame UMA única vez.
    """
    global _funcionalidades
    if req_ctx.esta_vazio():
        return "ERRO: execute skill_analisar_requisito primeiro."

    contexto_be = card_ctx.para_prompt()
    logger.info("Levantando funcionalidades de frontend...")
    _funcionalidades = _llm.levantar_cards_frontend(req_ctx.__dict__, contexto_be)

    lista = " ".join(f"- {f}" for f in _funcionalidades)
    return f"""{len(_funcionalidades)} funcionalidades de frontend identificadas:
{lista}

Próximo passo: chame skill_detalhar_frontend."""


@tool
def skill_detalhar_frontend(_: str = "") -> str:
    """
    Para cada funcionalidade de frontend levantada, detalha regras de UX,
    campos, endpoint consumido e critérios de aceite.
    Chame APÓS skill_levantar_frontend.
    Chame UMA única vez.
    """
    global _detalhamentos
    if not _funcionalidades:
        return "ERRO: execute skill_levantar_frontend primeiro."

    contexto_be = card_ctx.para_prompt()
    logger.info("Detalhando %d funcionalidades de frontend...", len(_funcionalidades))
    _detalhamentos = []

    for func in _funcionalidades:
        logger.info("  Detalhando: %s", func)
        det = _llm.detalhar_card_frontend(func, req_ctx.__dict__, contexto_be)
        _detalhamentos.append(det)

    return f"""{len(_detalhamentos)} funcionalidades de frontend detalhadas.

Próximo passo: chame skill_formatar_frontend."""


@tool
def skill_formatar_frontend(_: str = "") -> str:
    """
    Formata cada detalhamento no padrão .md e gera as stories de frontend
    prontas para publicação no Trello.
    Chame APÓS skill_detalhar_frontend.
    Chame UMA única vez.
    """
    global _stories
    if not _detalhamentos:
        return "ERRO: execute skill_detalhar_frontend primeiro."

    logger.info("Formatando stories de frontend...")
    _stories = []

    for det in _detalhamentos:
        story = _llm.formatar_story_frontend(det, req_ctx.__dict__)
        _stories.append(story)
        card_ctx.registrar_story_frontend(story)

    titulos = " ".join(f"- {s['titulo']}" for s in _stories)
    return f"""{len(_stories)} stories de frontend prontas:
{titulos}

Próximo passo: chame skill_publicar_trello."""


def get_stories_frontend() -> list[dict]:
    return _stories