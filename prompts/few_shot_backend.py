def few_shot_backend():

    return  """
## Exemplo de card RUIM (nunca gere assim):
{
  "titulo": "[BACKEND][RF##][Módulo] Cadastrar entidade",
  "endpoint": "modulo/cadastrar",
  "regras_especificas": ["validar campos obrigatórios", "verificar permissões"],
  "acoes": [{"acao": "usuário faz ação X", "resultado": "API retorna Y"}],
  "campos": [
    {"nome": "campo1", "tipo": "string", "obrigatoriedade": "Obrigatório", "min_max": ""}
  ],
  "criterios_qa": ["verificar se funciona corretamente"]
}

## Exemplo de card BOM (siga este padrão exatamente):
{
  "titulo": "[BACKEND][RF01PP][Produtos] Cadastrar Produto com validação de nome único",
  "endpoint": "produtos/cadastrar",
  "regras_especificas": [
    "RN01: Não é permitido cadastrar dois produtos com o mesmo nome — retornar 422 com mensagem 'Nome já cadastrado'",
    "RN02: O preço deve ser maior que zero — retornar 422 com mensagem 'Preço deve ser maior que zero'"
  ],
  "acoes": [
    {"acao": "usuário submete nome e preço válidos", "resultado": "API retorna 201 Created com o produto criado"},
    {"acao": "usuário submete nome já existente", "resultado": "API retorna 422 com mensagem 'Nome já cadastrado'"},
    {"acao": "usuário submete preço igual a zero", "resultado": "API retorna 422 com mensagem 'Preço deve ser maior que zero'"},
    {"acao": "usuário sem perfil ADMIN tenta cadastrar", "resultado": "API retorna 403 Forbidden"}
  ],
  "campos": [
    {"nome": "nome", "tipo": "string", "obrigatoriedade": "Obrigatório", "min_max": "3/100"},
    {"nome": "preco", "tipo": "decimal", "obrigatoriedade": "Obrigatório", "min_max": "0.01/999999"}
  ],
  "criterios_qa": [
    "Verificar se o sistema retorna 201 ao cadastrar produto com nome e preço válidos",
    "Verificar se o sistema retorna 422 ao cadastrar produto com nome já existente",
    "Verificar se o sistema retorna 422 ao submeter preço igual ou menor que zero",
    "Verificar se apenas usuários com perfil ADMIN conseguem acessar o endpoint"
  ]
}
"""

