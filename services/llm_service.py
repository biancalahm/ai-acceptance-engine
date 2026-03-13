from langchain_ollama import OllamaLLM
import json
import utils.utils   as utils
import logging

logger = logging.getLogger(__name__) 


class LLMService:
    def __init__(self):
        self.model = OllamaLLM(model="llama3")
    
    
    def generate_json_base(self, requisito: str):
        logger.info("Creating base card")
        """Goals: Read the base prompt, which contains general instructions and the user's requirements  for create backend and frontend cards """
        """Objetivo: Ler o prompt base, que contém instruções gerais e o requisito do usuário para criação dos cards de back-end e front-end"""
        template = utils.load_prompt("prompts/json_base.txt")
        prompt = template.replace("{requisito}", json.dumps(requisito, indent=2))
        response = self.model.invoke(prompt)
        return response
    
    def generate_backend_prompt(self, requisito: str):
        logger.info("Creating back-end card")
        """Goals: To read the back-end prompt containing general instructions for the back-end cards """
        """Objetivo: Leitura do prompt backend que contém instruções gerais para os cards de back-end"""
        template = utils.load_prompt("prompts/backend_prompt.txt")
        prompt = template.replace("{requisito}", json.dumps(requisito, indent=2))
        response = self.model.invoke(prompt)
        data = utils.clean_and_load_json(response)
        return data
        
    def generate_frontend_prompt(self, requisito: str):
        logger.info("Creating front-end card")
        """Goals: To read the front-end prompt containing general instructions for the front-end cards """
        """Objetivo: Leitura do prompt frontend que contém instruções gerais para os cards de front-end"""
        template = utils.load_prompt("prompts/frontend_prompt.txt")
        prompt = template.replace("{requisito}", json.dumps(requisito, indent=2))
        response = self.model.invoke(prompt)
        data = utils.clean_and_load_json(response)
        return data
      