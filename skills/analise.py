# skills/analise.py
from langchain.tools import tool
from agent.context import req_ctx
from services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)
_llm = LLMService()


@tool
def skill_analisar_requisito(requisito: str) -> str:
    """
    SEMPRE a primeira skill a ser chamada.
    Analisa o requisito completo e extrai módulo, regras de negócio,
    entidades, perfis de acesso e popula o contexto global.
    Chame UMA vez antes de qualquer outra skill.
    """
    logger.info("Analisando requisito...")
    dados = _llm.analisar_requisito(requisito)

    req_ctx.requisito_original       = requisito
    req_ctx.modulo                   = dados.get("modulo", "")
    req_ctx.descricao_sistema        = dados.get("descricao_sistema", "")
    req_ctx.perfis                   = dados.get("perfis", [])
    req_ctx.regras_negocio           = dados.get("regras_negocio", [])
    req_ctx.entidades                = dados.get("entidades", [])

    return f"""Análise concluída.
Módulo: {req_ctx.modulo}
Sistema: {req_ctx.descricao_sistema}
Regras identificadas: {len(req_ctx.regras_negocio)}
Entidades: {', '.join(req_ctx.entidades)}

Próximo passo: chame skill_levantar_backend."""