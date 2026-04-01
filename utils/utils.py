import json
import re

import logging
import json
import re
logger = logging.getLogger(__name__) 

def extract_json_answer(response: str, llm, max_retries: int = 2):
    """
    Extrai JSON da resposta do LLM.
    Se falhar, tenta corrigir via LLM (retry automático).
    """

    def clean_json(text: str):
        logging.info("Extraindo JSON ")
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            logging.error("Nenhum JSON encontrado na resposta ")
            raise ValueError("Nenhum JSON encontrado na resposta")

        json_str = match.group(0)

        # remove caracteres de controle
        json_str = re.sub(r"[\x00-\x1F\x7F]", "", json_str)

        return json.loads(json_str)

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return clean_json(response)

        except Exception as e:
            last_error = e

            if attempt >= max_retries:
                break
            logging.info("Não foi possivel extrair o JSON. Extraindo com LLM ")
            retry_prompt = f"""
                Corrija o conteúdo abaixo para um JSON válido.

                Regras:
                - Retorne apenas JSON válido
                - Não inclua explicações
                - Não inclua texto antes ou depois

                Conteúdo:
                {response}
                """
            response = llm.invoke(retry_prompt)

    raise ValueError(f"Falha ao extrair JSON após {max_retries} tentativas: {last_error}")


def load_prompt(path:str)-> str:
        """"
        Objective: Extract prompts from instruction files with created card templates
        The prompts provide input to guide the AI ​​model
        to perform an action in the desired manner without human intervention.
        Objetivo: Objetivo: Extrair prompt de arquivos de instrução com modelos de cards criados
        Os prompts fornecem insumos para orientar o modelo de IA
        a executar um ação da maneira desejada sem interferência humana. 
        Path: prompts/
        """
        with open(path,"r", encoding="utf-8") as file: 
            return file.read()
def limpar_aspas(desc: str) -> str:
    if not desc:
        return desc

    desc = desc.strip()

    # Remove aspas triplas primeiro
    if (desc.startswith('"""') and desc.endswith('"""')) or \
       (desc.startswith("'''") and desc.endswith("'''")):
        return desc[3:-3].strip()

    # Remove aspas simples ou duplas
    if (desc.startswith('"') and desc.endswith('"')) or \
       (desc.startswith("'") and desc.endswith("'")):
        return desc[1:-1].strip()

    return desc