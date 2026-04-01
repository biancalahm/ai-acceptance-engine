import requests
import logging
from models.trello_card import TrelloCard
import utils.utils as utils
logger = logging.getLogger(__name__) 
class TrelloService:

    """Objetivo: Integrar o projeto ao Trello com diversas funções"""
    BASE_URL = "https://api.trello.com/1"
    
    # Mapeamento de cores padrão para labels
    LABEL_COLORS = {
        "backend": "red",
        "frontend": "blue",
        "validacao": "yellow",
        "crud": "green",
        "critico": "orange",
        "formulario": "purple",
        "componente": "pink",
        "implementacao": "sky",
        "testes": "lime",
        "documentacao": "black",
        "urgent": "red",
        "importante": "orange"
    }

    def __init__(self, api_key, token):
        self.api_key = api_key
        self.token = token

    def _auth_params(self) -> dict:
        """Retorna os parâmetros de autenticação reutilizáveis."""
        return {"key": self.api_key, "token": self.token}
    
    def create_card(self, name:str , desc:str, list_id: str) -> dict:
        
        """Objetivo: Executar o endpoint create card"""
        print(name, desc)
        desc = utils.limpar_aspas(desc)
        card = TrelloCard(titulo=name, descricao=desc, idList=list_id)
        logger.info("Criando card '%s' na lista '%s'...", card.titulo, list_id)
        payload_card = card.model_dump(by_alias=True, exclude_none=True)
        response = requests.post(
            f"{self.BASE_URL}/cards",
            headers={"Accept": "application/json"},
            params=self._auth_params(),
            json=payload_card,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        logger.info("Card criado com sucesso: %s", data.get("shortUrl"))
        return data
    
    def create_label(self, board_id: str, name: str, color: str = None) -> dict:
        """
        Cria uma label (tag) no Trello.
        
        Args:
            board_id: ID do board do Trello
            name: Nome da label
            color: Cor da label (opcional). Valores aceitos: 
                   'green', 'yellow', 'orange', 'red', 'purple', 
                   'blue', 'pink', 'lime', 'sky', 'black'
        
        Returns:
            Dicionário com dados da label criada
        
        Raises:
            Exception: Se houver erro na criação da label
        """
        # Normalizar nome
        name_normalized = name.strip().lower()
        
        # Se a cor não for fornecida, usa o mapeamento padrão
        if color is None:
            color = self.LABEL_COLORS.get(name_normalized, "sky")
        
        # Validar cor
        valid_colors = ['green', 'yellow', 'orange', 'red', 'purple', 
                       'blue', 'pink', 'lime', 'sky', 'black']
        if color not in valid_colors:
            logger.warning("Cor '%s' inválida. Usando 'sky' como padrão.", color)
            color = "sky"
        
        payload = {
            "name": name_normalized,
            "color": color
        }
        
        logger.info("Criando label '%s' com cor '%s' no board '%s'...", 
                   name_normalized, color, board_id)
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/boards/{board_id}/labels",
                headers={"Accept": "application/json"},
                params=self._auth_params(),
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            logger.info("[OK] Label '%s' criada com sucesso (ID: %s, Cor: %s)", 
                       name_normalized, data.get("id"), color)
            return data
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                # Já existe uma label com esse nome
                logger.warning("Label '%s' já existe no board. Recuperando...", name_normalized)
                # Tenta recuperar a label existente
                existing_labels = self.get_board_labels(board_id)
                for label in existing_labels:
                    if label.get("name", "").lower() == name_normalized:
                        return label
            logger.error("Erro HTTP ao criar label '%s': %s", name_normalized, str(e))
            raise
        
        except Exception as e:
            logger.error("Erro ao criar label '%s': %s", name_normalized, str(e))
            raise
    
    def add_label_to_card(self, card_id: str, label_id: str) -> dict:
        """
        Adiciona uma label (tag) a um card existente.
        
        Args:
            card_id: ID do card no Trello
            label_id: ID da label a ser adicionada
        
        Returns:
            Dicionário com dados da label adicionada
        
        Raises:
            Exception: Se houver erro na associação
        """
        if not card_id or not label_id:
            logger.error("card_id ou label_id inválido. card_id: %s, label_id: %s", card_id, label_id)
            raise ValueError("card_id e label_id são obrigatórios")
        
        logger.info("Associando label '%s' ao card '%s'...", label_id, card_id)
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/cards/{card_id}/idLabels",
                headers={"Accept": "application/json"},
                params={**self._auth_params(), "value": label_id},
                timeout=10,
            )
            response.raise_for_status()
            
            logger.info("[OK] Label '%s' associada ao card '%s' com sucesso", label_id, card_id)
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                # Label já está associada ao card
                logger.warning("Label '%s' já está associada ao card '%s'", label_id, card_id)
                return {"status": "already_associated"}
            logger.error("Erro HTTP ao associar label: %s", str(e))
            raise
        
        except Exception as e:
            logger.error("Erro ao associar label '%s' ao card '%s': %s", label_id, card_id, str(e))
            raise
    
    def get_board_labels(self, board_id: str) -> list:
        """
        Recupera todas as labels de um board.
        
        Args:
            board_id: ID do board do Trello
        
        Returns:
            Lista com todas as labels do board
        """
        logger.info("Recuperando labels do board '%s'...", board_id)
        
        response = requests.get(
            f"{self.BASE_URL}/boards/{board_id}/labels",
            headers={"Accept": "application/json"},
            params=self._auth_params(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        logger.info("Recuperadas %d labels do board", len(data))
        return data
    
    def get_or_create_label(self, board_id: str, label_name: str, color: str = None) -> dict:
        """
        Obtém uma label existente ou cria uma nova se não existir.
        
        Fluxo:
        1. Recupera todas as labels do board
        2. Procura por label com mesmo nome (case-insensitive)
        3. Se encontrar, retorna a label existente
        4. Se não encontrar, cria nova label com cor apropriada
        
        Args:
            board_id: ID do board do Trello
            label_name: Nome da label
            color: Cor da label (opcional - usa mapeamento padrão se não fornecido)
        
        Returns:
            Dicionário com dados da label (criada ou encontrada)
        
        Raises:
            Exception: Se houver erro na API do Trello
        """
        # Normalizar nome da label
        label_name_normalized = label_name.strip().lower()
        
        logger.info("Procurando label '%s' no board '%s'...", label_name_normalized, board_id)
        
        try:
            # [1] RECUPERAR LABELS EXISTENTES
            existing_labels = self.get_board_labels(board_id)
            
            # [2] PROCURAR LABEL COM MESMO NOME
            for label in existing_labels:
                existing_label_name = label.get("name", "").strip().lower()
                
                if existing_label_name == label_name_normalized:
                    logger.info("[OK] Label '%s' encontrada (ID: %s)", label_name_normalized, label.get("id"))
                    return label
            
            # 3️⃣ LABEL NÃO ENCONTRADA - CRIAR NOVA
            logger.info("Label '%s' não encontrada. Criando nova...", label_name_normalized)
            
            # Determinar cor (usa mapeamento ou padrão)
            if color is None:
                color = self.LABEL_COLORS.get(label_name_normalized, "sky")
            
            new_label = self.create_label(
                board_id=board_id,
                name=label_name_normalized,
                color=color
            )
            
            logger.info("[OK] Label '%s' criada com sucesso (ID: %s, Cor: %s)", 
                       label_name_normalized, new_label.get("id"), color)
            
            return new_label
        
        except Exception as e:
            logger.error("[ERROR] Erro ao obter/criar label '%s': %s", label_name_normalized, str(e))
            raise
    