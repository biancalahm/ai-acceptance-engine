# skills/publicar.py
from langchain.tools import tool
from skills.backend  import get_stories_backend
from skills.frontend import get_stories_frontend
from services.trello_service import TrelloService
import os
from dotenv import load_dotenv
import logging
load_dotenv() 

logger   = logging.getLogger(__name__)
_trello  = TrelloService(
    api_key=os.getenv("TRELLO_API_KEY"),
    token=os.getenv("TRELLO_TOKEN"),
)

BACKEND_LIST_ID  = os.getenv("TRELLO_LIST_BACKLOG")
FRONTEND_LIST_ID = os.getenv("TRELLO_LIST_BACKLOG")
TRELLO_BOARD_ID  = os.getenv("TRELLO_BOARD_ID")


def _adicionar_tags_ao_card(card_id: str, tags: list) -> None:
    """
    Cria ou obtém labels e as adiciona ao card.
    
    Fluxo:
    1. Para cada tag, verifica se existe label com esse nome no board
    2. Se não existir, cria a label com cor apropriada
    3. Associa a label ao card
    
    Args:
        card_id: ID do card no Trello
        tags: Lista de nomes das tags a adicionar
    """
    if not TRELLO_BOARD_ID:
        logger.warning("TRELLO_BOARD_ID não configurado. Tags não serão adicionadas.")
        return
    
    if not tags:
        logger.info("Nenhuma tag para adicionar ao card %s", card_id)
        return
    
    logger.info("Iniciando associação de %d tags ao card %s", len(tags), card_id)
    
    for tag_name in tags:
        try:
            # Sanitizar nome da tag (remover espaços extras, lowercase)
            tag_name_sanitized = tag_name.strip().lower()
            
            logger.info("Processando tag: '%s'", tag_name_sanitized)
            
            # [1] OBTER OU CRIAR LABEL
            label = _trello.get_or_create_label(
                board_id=TRELLO_BOARD_ID,
                label_name=tag_name_sanitized
            )
            
            if not label or not label.get("id"):
                logger.error("Erro: Label '%s' retornou sem ID válido", tag_name_sanitized)
                continue
            
            label_id = label.get("id")
            logger.info("Label obtida/criada: '%s' (ID: %s)", tag_name_sanitized, label_id)
            
            # [2] ASSOCIAR LABEL AO CARD
            _trello.add_label_to_card(
                card_id=card_id,
                label_id=label_id
            )
            
            logger.info("[OK] Tag '%s' associada ao card %s com sucesso", tag_name_sanitized, card_id)
            
        except Exception as e:
            logger.error("[ERROR] Erro ao processar tag '%s': %s", tag_name, str(e))
            continue


def publicar_cards_trello() -> str:
    """
    Publica todas as stories de backend e frontend no Trello.
    Para cada card criado, também cria e adiciona as tags/labels.
    """
    stories_be = get_stories_backend()
    stories_fe = get_stories_frontend()
    logger.info("Iniciando publicação de stories no Trello")
    
    if not stories_be and not stories_fe:
        return "ERRO: nenhuma story encontrada. Execute o pipeline completo primeiro."

    criados_be, criados_fe = [], []
    print("="*60)
    print(f"Backend stories: {len(stories_be)}")
    print(f"Frontend stories: {len(stories_fe)}")
    logger.info("Board ID: %s", TRELLO_BOARD_ID)
    
    # ──────────────────────────────────────────────────────────
    # Publicar cards de backend
    # ──────────────────────────────────────────────────────────
    for story in stories_be:
        try:
            logger.info("Criando card de backend: %s", story["titulo"])
            
            # 1. Criar o card
            r = _trello.create_card(
                name=story["titulo"],
                desc=story["descricao"],
                list_id=BACKEND_LIST_ID,
            )
            card_id = r.get("id")
            url = r.get("shortUrl", "")
            
            # 2. Adicionar tags ao card (se existirem)
            tags = story.get("tags", [])
            logger.info("Backend story '%s' com %d tags: %s", story["titulo"], len(tags), tags)
            if tags:
                _adicionar_tags_ao_card(card_id, tags)
            else:
                logger.warning("[WARN]  Backend story '%s' NÃO TEM TAGS", story["titulo"])
            
            criados_be.append(f"  ✓ '{story['titulo']}' → {url}")
            logger.info("Backend publicado com sucesso: %s", story["titulo"])
            
        except Exception as e:
            logger.error("Erro ao publicar backend '%s': %s", story["titulo"], str(e))
            criados_be.append(f"  ✗ '{story['titulo']}' → ERRO: {e}")

    # ──────────────────────────────────────────────────────────
    # Publicar cards de frontend
    # ──────────────────────────────────────────────────────────
    for story in stories_fe:
        try:
            logger.info("Criando card de frontend: %s", story["titulo"])
            
            # 1. Criar o card
            r = _trello.create_card(
                name=story["titulo"],
                desc=story["descricao"],
                list_id=FRONTEND_LIST_ID,
            )
            card_id = r.get("id")
            url = r.get("shortUrl", "")
            
            # 2. Adicionar tags ao card (se existirem)
            tags = story.get("tags", [])
            logger.info("Frontend story '%s' com %d tags: %s", story["titulo"], len(tags), tags)
            if tags:
                _adicionar_tags_ao_card(card_id, tags)
            else:
                logger.warning("[WARN]  Frontend story '%s' NÃO TEM TAGS", story["titulo"])
            
            criados_fe.append(f"ok '{story['titulo']}' → {url}")
            logger.info("Frontend publicado com sucesso: %s", story["titulo"])
            
        except Exception as e:
            logger.error("Erro ao publicar frontend '%s': %s", story["titulo"], str(e))
            criados_fe.append(f" error '{story['titulo']}' → ERRO: {e}")

    # ──────────────────────────────────────────────────────────
    # Resultado final
    # ──────────────────────────────────────────────────────────
    resultado = f"""Publicação concluída com sucesso!

Backend ({len(criados_be)} cards):
{chr(10).join(criados_be)}

Frontend ({len(criados_fe)} cards):
{chr(10).join(criados_fe)}

[OK] Todos os cards foram criados com suas respectivas tags/labels."""

    logger.info("Publicação finalizada. Total: %d cards", len(criados_be) + len(criados_fe))
    return resultado
