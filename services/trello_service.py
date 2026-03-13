import requests
from models.trello_card import TrelloCard
class TrelloService:
    """Objetivo: Integrar o projeto ao Trello com diversas funções"""
    def __init__(self, api_key, token, list_id):
        self.api_key = api_key
        self.token = token
        self.list_id = list_id

    def create_card(self, name, desc):
        url = "https://api.trello.com/1/cards"
        
        card = TrelloCard( 
                name=name,
                descricao= desc,
                idList= self.list_id
        )
        
        query = {
            "key": self.api_key,
            "token": self.token
        }

        payload_card = card.model_dump(by_alias=True, exclude_none=True)
        response = requests.post(url,headers={"Accept": "application/json"}, params=query,json=payload_card)
    
        print("Status code:", response.status_code)
        print("Resposta bruta:", response.text)

        return response.text
    