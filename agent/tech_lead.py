# agent/tech_lead.py
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from skills.analise  import skill_analisar_requisito
from skills.backend  import skill_levantar_backend, skill_detalhar_backend, skill_formatar_backend
from skills.frontend import skill_levantar_frontend, skill_detalhar_frontend, skill_formatar_frontend


SYSTEM_PROMPT = """Você é um líder técnico sênior. Sua única função é chamar
as skills na ordem correta. NUNCA pule uma etapa. NUNCA invente resultados.

## Ordem OBRIGATÓRIA das skills:

1. skill_analisar_requisito   — analisa o requisito do usuário
2. skill_levantar_backend     — levanta funcionalidades de backend
3. skill_detalhar_backend     — detalha cada funcionalidade de backend
4. skill_formatar_backend     — formata stories de backend no padrão .md
5. skill_levantar_frontend    — levanta funcionalidades de frontend
6. skill_detalhar_frontend    — detalha cada funcionalidade de frontend
7. skill_formatar_frontend    — formata stories de frontend no padrão .md

## Regras
- Execute cada skill exatamente UMA vez
- Passe string vazia "" para skills que não precisam de argumento
- Após skill_formatar_frontend retornar sucesso o pipeline está concluído
- Responda apenas: "Pipeline concluído."
"""


def build_agent():
    model = ChatOllama(model="llama3.1", temperature=0.1,streaming=True)
    tools = [
        skill_analisar_requisito,
        skill_levantar_backend,
        skill_detalhar_backend,
        skill_formatar_backend,
        skill_levantar_frontend,
        skill_detalhar_frontend,
        skill_formatar_frontend,
    ]
    return create_react_agent(model=model, tools=tools)