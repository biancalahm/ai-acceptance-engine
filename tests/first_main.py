from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3")

prompt = """
Você é um analista técnico de software.

Sua tarefa é transformar o requisito abaixo em JSON estruturado.

Responda APENAS em JSON válido.
Não escreva nenhuma explicação fora do JSON.

Formato obrigatório:

{
  "epic": "nome da épica",
  "stories": [
    {
      "title": "título da task",
      "description": "descrição detalhada",
      "criteria": ["critério 1", "critério 2"]
    }
  ]
}

Requisito:
"O sistema deve permitir que o administrador envie notícias para a lixeira."
"""

response = model.invoke(prompt)

print(response)