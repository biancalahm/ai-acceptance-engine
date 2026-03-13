import json
import re
def clean_and_load_json(response: str):
    """
    Remove qualquer texto antes ou depois do JSON e retorna objeto Python.
    Funciona mesmo se o LLM colocar "Here is the JSON:" antes.
    """
    # Procura o primeiro bloco JSON válido entre chaves
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if not match:
        raise ValueError("Nenhum JSON encontrado na resposta")
    
    json_str = match.group()
    return json.loads(json_str)

def load_prompt(path:str)-> str:
        """"Objetivo: Ler os prompts modelos de cards criados
            Os prompts fornecem insumos para orientar o modelo de IA
            a executar um ação da maneira desejada sem interferência humana. 
            Path: prompts/
        """
        with open(path,"r", encoding="utf-8") as file: 
            return file.read()