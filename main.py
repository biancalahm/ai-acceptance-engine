# main.py
from langchain_core.messages import SystemMessage, HumanMessage
from agent.tech_lead import build_agent, SYSTEM_PROMPT
from agent.context import reset_contexts
from skills.publicar import publicar_cards_trello 
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s"
)


def processar_requisito(requisito: str) -> None:
    reset_contexts()
    agent = build_agent()

    print(" " + "="*60)
    print("INICIANDO LÍDER TÉCNICO IA")
    print("="*60)

    response = agent.invoke({
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=requisito),
        ]
    })

    tool_calls = [m for m in response["messages"] if hasattr(m, "type") and m.type == "tool"]
    print(f" [INFO] {len(tool_calls)} skills executadas")
    
    print(" " + "="*60)
    print("PUBLICANDO NO TRELLO...")
    print("="*60)
    resultado = publicar_cards_trello()
    print(resultado)
if __name__ == "__main__":
    requisito = """ RF01P: O sistema deverá permitir que usuários com perfil de Gerente cadastrar e consultar Produtos.
    RN01P: Cada Produto deve conter os seguintes campos:
    [Ob] Nome (obrigatório, mín. 5 caracteres, máx. 200);  
    [Ob] Quantidade disponível (obrigatório, inteiro positivo) ;  
    [Ob] Preço compra (decimal positivo); 
    [Ob] Preço venda (decimal positivo); 
    [Ob] Categoria associada  (id de categoria pré-existente); 
    [Ob] Descrição (texto livre, máx. 1000 caracteres);
    [Ob] Mídias (min uma imagens, opcional mais imagens ou vídeos, no maximo 5MB de conteúdo ); """
    processar_requisito(requisito)
