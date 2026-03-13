#imports from external libraries 
from dotenv import load_dotenv
import os  
from config.logging_config import setup_logging
import logging

#initialization
load_dotenv()
setup_logging()

#imports of local services 
from services.llm_service import LLMService
from services.trello_service import TrelloService

logger = logging.getLogger(__name__) 

key =  os.getenv('TRELLO_API_KEY')
token = os.getenv('TRELLO_TOKEN')
board_id = os.getenv('TRELLO_ID_BOARD')

llm = LLMService()
trello = TrelloService(key, token, "69a8968aec3b3b60bcf0b08e" )


requirement = """RF02EA | Essencial | Evidente  

O sistema deverá permitir aos usuários com perfil de SUBMISSOR ou COORDENADOR cadastrar, editar, listar, submeter e excluir uma Notícia ou Evento. 

    RN01EA: Durante o cadastro o sistema deverá permitir associar a Notícia ou Evento a uma tag.  

    RNN03EA: uma Notícia ou Evento com status de SUBMETIDA (que ainda não foi aprovada ou rejeitada) não poderá ser editada por qualquer usuário. 

    RN04EA: Uma notícia REJEITADA deverá ser exibida para os perfis de acesso COORDENADOR e SUBMISSOR com uma justificativa. 

    RN05AE: A Notícia ou Evento deverá conter: 

    [Ob] Título da Notícia ou Evento 

    [Ob] Tags associadas (vindas via endpoint do sistma ObservaDH) 

    [Ob] Um campo livre de edição de texto: 

    Aplicar estilos de formatação de texto (negrito, itálico, sublinhado); 

    Inserção de listas ordenadas e não ordenadas; 

    Inclusão de links clicáveis; 

    Inclusão de vídeo do youtube embedding 

    Inserção e redimensionamento de imagens; 

    Suporte a títulos e subtítulos (hierarquia H1, H2, H3); 

    Alinhamento de parágrafos (esquerda, centralizado, direita); 

    Suporte a quebra de linha e parágrafos múltiplos; 

    Upload de uma imagem principal de capa ( em caso de não ser enviado uma capa, será indexada uma imagem padrão) 

    RN06AE:  O sistema deverá permitir que o usuário com perfil SUBMISSOR edite exclusivamente as Notícia ou Evento de sua própria autoria com o status de RASCUNHO, APROVADO ou REJEITADO.  

    RN07AE: O sistema deverá permitir que o usuário com perfil COORDENADOR edite qualquer Notícia ou Evento cadastrado no sistema, independentemente do autor, desde que a notícia esteja com status RASCUNHO, APROVADA ou REJEITADA. 

    RN08AE Uma Notícia e Eventos poderá estar associada a uma determinada Tag  

    RN09AE Durante o cadastro de uma notícia o sistema deverá distinguir notícia de evento.  """

base = llm.generate_json_base(requirement)
backend_card = llm.generate_backend_prompt(base)
frontend_card = llm.generate_frontend_prompt(base)


def assemble_description(story, tipo="frontend"):
    """
    Compile the final description for submission to Trello
    """

    if tipo == "backend":
        desc = story.get("descricao_tecnica", "")
    else:
        desc =story.get("descricao_funcional", "")


    

    return desc


# ---------- BACKEND ----------

for story in backend_card.get("stories", []):
    
    desc= assemble_description(story,"backend")

    trello.create_card(
        story["title"],
        desc
    )

# ---------- FRONTEND ----------

for story in frontend_card.get("stories", []):

    desc= assemble_description(story,"frontend")
    trello.create_card(
        story["title"],
        desc
    )
