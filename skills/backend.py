# skills/backend.py
from langchain.tools import tool
from agent.context import req_ctx, card_ctx
from services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)
_llm = LLMService()

# Estado interno das skills de backend (acumulado durante a execução)
_funcionalidades: list[str] = []
_detalhamentos:   list[dict] = []
_stories:         list[dict] = []


@tool
def skill_levantar_backend(_: str = "") -> str:
    """
    Levanta todas as funcionalidades de backend necessárias para o requisito.
    Chame APÓS skill_analisar_requisito.
    Chame UMA única vez.
    """
    global _funcionalidades
    if req_ctx.esta_vazio():
        return "ERRO: execute skill_analisar_requisito primeiro."

    logger.info("Levantando funcionalidades de backend...")
    _funcionalidades = _llm.levantar_cards_backend(req_ctx.__dict__)

    lista = " ".join(f"- {f}" for f in _funcionalidades)
    return f"""{len(_funcionalidades)} funcionalidades de backend identificadas:
{lista}

Próximo passo: chame skill_detalhar_backend."""


@tool
def skill_detalhar_backend(_: str = "") -> str:
    """
    Para cada funcionalidade de backend levantada, detalha regras,
    campos, endpoint e critérios de aceite.
    Chame APÓS skill_levantar_backend.
    Chame UMA única vez.
    """
    global _detalhamentos
    if not _funcionalidades:
        return "ERRO: execute skill_levantar_backend primeiro."

    logger.info("Detalhando %d funcionalidades de backend...", len(_funcionalidades))
    _detalhamentos = []

    for func in _funcionalidades:
        logger.info("  Detalhando: %s", func)
        det = _llm.detalhar_card_backend(func, req_ctx.__dict__)
        _detalhamentos.append(det)

    return f"""{len(_detalhamentos)} funcionalidades detalhadas com regras e campos.

Próximo passo: chame skill_formatar_backend."""


@tool
def skill_formatar_backend(_: str = "") -> str:
    """
    Formata cada detalhamento no padrão .md e gera as stories finais
    prontas para publicação no Trello.
    Chame APÓS skill_detalhar_backend.
    Chame UMA única vez.
    """
    global _stories
    if not _detalhamentos:
        return "ERRO: execute skill_detalhar_backend primeiro."

    logger.info("Formatando stories de backend...")
    _stories = []

    for det in _detalhamentos:
        story = _llm.formatar_story_backend(det, req_ctx.__dict__)
        _stories.append(story)
        card_ctx.registrar_story_backend(story)
        card_ctx.registrar(titulo=story["titulo"], descricao=story["descricao"])


    titulos = " ".join(f"- {s['titulo']}" for s in _stories)
    return f"""{len(_stories)} stories de backend prontas:
{titulos}

Próximo passo: chame skill_levantar_frontend."""


def get_stories_backend() -> list[dict]:
    """Retorna as stories de backend para publicação."""
    return _stories