# get_requirements.py

from langchain_core.messages import SystemMessage, HumanMessage
from agent.tech_lead import build_agent, SYSTEM_PROMPT
from agent.context import reset_contexts
from skills.publicar import publicar_cards_trello 

def processar_requisito(requisito: str) -> dict:
    reset_contexts()
    agent = build_agent()

    response = agent.invoke({
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=requisito),
        ]
    })

    tool_calls = [
        m for m in response["messages"] 
        if hasattr(m, "type") and m.type == "tool"
    ]

    resultado_trello = publicar_cards_trello()

    return {
        "tools_executadas": len(tool_calls),
        "resultado_trello": resultado_trello
    }