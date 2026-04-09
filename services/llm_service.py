from langchain_ollama import ChatOllama
import utils.utils as utils
import logging

logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self, model_name: str = "llama3.1"):
        self.model          = ChatOllama(model=model_name, temperature=0)
        self.template_exemplo = utils.load_prompt("prompts/exemplo_card.md")

    # ──────────────────────────────────────────────────────────
    # UTILITÁRIOS INTERNOS
    # ──────────────────────────────────────────────────────────

    def _invocar(self, prompt: str) -> str:
        """Chama o modelo e retorna texto puro."""
        response = self.model.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    def _extrair_json_seguro(self, texto: str) -> dict:
        """
        Extrai JSON válido do texto com múltiplas estratégias de fallback.
        Delega para utils.extract_json_answer que trata aspas simples,
        blocos markdown e correção via LLM.
        """
        return utils.extract_json_answer(texto, self.model, max_retries=2)

    # ──────────────────────────────────────────────────────────
    # ETAPA 1 — Análise do requisito
    # ──────────────────────────────────────────────────────────

    def analisar_requisito(self, requisito: str) -> dict:
        """
        Analisa o requisito completo e extrai módulo, descrição do sistema,
        perfis de acesso, regras de negócio e entidades do domínio.
        Retorna dicionário estruturado para popular o RequirementsContext.
        """
        logger.info("Analisando requisito: '%s'", requisito[:80])

        prompt = f"""Você é um analista de sistemas sênior experiente.
Analise o requisito abaixo e retorne SOMENTE um JSON estruturado.

## Requisito a analisar:
{requisito}

## Exemplo de card para referência de estilo e estrutura:
{self.template_exemplo}

## Instruções
- Extraia o módulo ao qual este requisito pertence
- Identifique todos os perfis de acesso mencionados
- Liste todas as regras de negócio presentes no requisito
- Identifique as entidades do domínio (substantivos principais)
- Liste as funcionalidades de backend (uma por responsabilidade técnica)
- Liste as funcionalidades de frontend (uma por tela ou componente principal)
- Para os campos use o requisito original como única fonte de verdade — NÃO adicione ou remova nada que não esteja lá

## Retorne SOMENTE este JSON, sem texto antes ou depois, usando aspas duplas:
{{
  "modulo": "nome do módulo ou sistema extraído do requisito",
  "descricao_sistema": "uma frase descrevendo o que o sistema faz",
  "perfis": ["PERFIL1", "PERFIL2"],
  "regras_negocio": [
    "RN01: regra extraída do requisito",
    "RN02: regra extraída do requisito"
  ],
  "entidades": ["Entidade1", "Entidade2"],
  "funcionalidades_backend": [
    "Cadastrar Entidade X com validação Y",
    "Editar Entidade X verificando regra Z"
  ],
  "funcionalidades_frontend": [
    "Tela de cadastro de Entidade X",
    "Tela de listagem com filtros"
  ]
}}"""

        texto = self._invocar(prompt)
        return self._extrair_json_seguro(texto)


        # ──────────────────────────────────────────────────────────
    # ETAPA 2 — Levantamento e validação de funcionalidades
    # ──────────────────────────────────────────────────────────

    def levantar_cards_backend(self, contexto: dict) -> list[str]:
        """
        Lista funcionalidades de backend baseadas estritamente no requisito.
        """
        logger.info("Levantando funcionalidades de backend para: '%s'", contexto.get("modulo", ""))

        regras    = "\n".join(f"- {r}" for r in contexto.get("regras_negocio", []))
        entidades = ", ".join(contexto.get("entidades", []))

        prompt = f"""Você é um líder técnico sênior analisando um requisito.

        ## Requisito original (sua ÚNICA fonte de verdade):
        {contexto.get("requisito_original", "")}

        ## Contexto extraído:
        Módulo: {contexto.get("modulo", "")}
        Entidades: {entidades}
        Regras:
        {regras}

        ## Instruções OBRIGATÓRIAS
        - Liste APENAS funcionalidades EXPLICITAMENTE descritas no requisito original
        - Se o requisito diz "cadastrar e consultar" → liste exatamente essas 2
        - NÃO adicione funcionalidades que "fariam sentido" mas não estão no requisito
        - NÃO infira endpoints, associações ou operações não mencionadas
        - Use os nomes das entidades exatamente como aparecem no requisito
        - NÃO adicione telas que não estejam no requisito original
        - utilize apenas os campos do requisito original como única fonte de verdade — NÃO adicione ou remova nada que não esteja lá



        ## Retorne SOMENTE este JSON, sem texto antes ou depois:
        {{
        "funcionalidades": [
            "funcionalidade 1 extraída diretamente do requisito",
            "funcionalidade 2 extraída diretamente do requisito"
        ]
        }}"""

        texto           = self._invocar(prompt)
        dados           = self._extrair_json_seguro(texto)
        funcionalidades = dados.get("funcionalidades", [])

        return self._validar_funcionalidades(
            funcionalidades,
            contexto.get("requisito_original", "")
        )

    def levantar_cards_frontend(self, contexto: dict, contexto_backend: str = "") -> list[str]:
        """
        Lista funcionalidades de frontend baseadas no requisito e endpoints do backend.
        """
        logger.info("Levantando funcionalidades de frontend para: '%s'", contexto.get("modulo", ""))

        regras    = "\n".join(f"- {r}" for r in contexto.get("regras_negocio", []))
        entidades = ", ".join(contexto.get("entidades", []))

        prompt = f"""Você é um líder técnico sênior.
        Com base no requisito e nos endpoints de backend disponíveis,
        liste as funcionalidades de frontend necessárias.

        ## Requisito original (sua ÚNICA fonte de verdade):
        {contexto.get("requisito_original", "")}

        ## Contexto extraído:
        Módulo: {contexto.get("modulo", "")}
        Sistema: {contexto.get("descricao_sistema", "")}
        Entidades: {entidades}
        Perfis: {", ".join(contexto.get("perfis", []))}
        Regras:
        {regras}

        ## Endpoints de backend disponíveis (o frontend deve consumir estes):
        {contexto_backend if contexto_backend else "Nenhum endpoint registrado ainda."}

        ## Instruções OBRIGATÓRIAS
        - Liste APENAS funcionalidades EXPLICITAMENTE descritas no requisito original
        - Liste UMA funcionalidade por tela ou componente principal
        - Cada funcionalidade deve ter o endpoint igual ao backend correspondente
        - NÃO adicione telas que não estejam no requisito original
        - utilize apenas os campos do requisito original como única fonte de verdade — NÃO adicione ou remova nada que não esteja lá


        ## Retorne SOMENTE este JSON, sem texto antes ou depois, usando aspas duplas:
        {{
        "funcionalidades": [
            "Tela de cadastro de [Entidade] consumindo POST /endpoint",
            "Tela de listagem de [Entidade] consumindo GET /endpoint"
        ]
        }}"""

        texto           = self._invocar(prompt)
        dados           = self._extrair_json_seguro(texto)
        funcionalidades = dados.get("funcionalidades", [])

        return self._validar_funcionalidades(
            funcionalidades,
            contexto.get("requisito_original", "")
        )

    def _validar_funcionalidades(
        self,
        funcionalidades: list[str],
        requisito_original: str
    ) -> list[str]:
        """
        Segunda passagem — filtra funcionalidades não presentes no requisito.
        """
        lista = "\n".join(f"{i+1}. {f}" for i, f in enumerate(funcionalidades))

        prompt = f"""Você é um revisor técnico rigoroso.

        ## Requisito original:
        {requisito_original}

        ## Lista de funcionalidades geradas:
        {lista}

        ## Sua tarefa
        Remova qualquer funcionalidade que NÃO esteja explicitamente no requisito.
        Mantenha APENAS o que o requisito menciona diretamente.

        Exemplos do que REMOVER:
        - Funcionalidades inferidas não mencionadas no requisito
        - Sub-operações não pedidas (ex: "Reordenar" se não mencionado)
        - Endpoints auxiliares genéricos (ex: "delete_snake_case")

        ## Retorne SOMENTE este JSON, sem texto antes ou depois:
        {{
        "funcionalidades_validadas": [
            "apenas funcionalidades presentes no requisito original"
        ],
        "removidas": [
            "funcionalidade removida — motivo: não está no requisito"
        ]
        }}"""

        texto    = self._invocar(prompt)
        dados    = self._extrair_json_seguro(texto)
        removidas = dados.get("removidas", [])

        if removidas:
            logger.warning("Funcionalidades removidas por extrapolação:")
            for r in removidas:
                logger.warning("  - %s", r)

        return dados.get("funcionalidades_validadas", funcionalidades)


    def detalhar_card_backend(self, funcionalidade: str, contexto: str) -> dict:
        """
        Dado uma funcionalidade e o contexto do requisito, levanta
        endpoint, campos, ações e critérios de QA específicos.
        Retorna dicionário estruturado para formatar_story_backend.
        """
        logger.info("Detalhando card de backend: '%s'", funcionalidade[:60])

        prompt = f"""Você é um líder técnico sênior detalhando uma funcionalidade de backend.
        Seu objetivo é criar um card estruturado, detalhado e pronto para desenvolvimento.

        ## Funcionalidade:
        {funcionalidade}

        ## Contexto do sistema (módulo, regras, entidades, perfis):
        {contexto}

        ## Instruções OBRIGATÓRIAS
        - Use as regras e entidades do contexto — não invente regras genéricas
        - Defina o endpoint REST seguindo o padrão: POST/GET/PUT/DELETE /modulo/acao_snake_case
        - Liste os campos com tipo, obrigatoriedade, validações específicas e limites reais
        - Descreva ações e resultados esperados baseados nas regras do contexto
        - Liste critérios de QA verificáveis, específicos e testáveis
        - Gere tags descritivas para categorizar o card
        - Título DEVE seguir: [BACKEND][Modulo] FUNCIONALIDADE

        ## Validações Esperadas
        Para cada campo, considere:
         - utilize apenas os campos do requisito original como única fonte de verdade — NÃO adicione ou remova nada que não esteja lá
        - Obrigatoriedade real (se o requisito diz "campo obrigatório", marque como obrigatório)
        - Comprimento mínimo e máximo
        - Formato esperado (email, URL, data, etc.)
        - Valores pré-definidos (enums)

        ## Retorne SOMENTE este JSON, sem texto antes ou depois, usando aspas duplas:
        {{
        "titulo": "[BACKEND][Modulo] FUNCIONALIDADE",
        "endpoint": "METODO /modulo/acao_snake_case",
        "descricao_resumida": "Uma frase clara descrevendo exatamente o que este endpoint faz",
        "regras_especificas": [
            "RN01: regra específica desta funcionalidade extraída do contexto",
            "RN02: regra específica desta funcionalidade extraída do contexto",
            "RN03: validação de negócio ou restrição específica"
        ],
        "acoes": [
            {{"acao": "usuário submete dados válidos respeitando as regras", "resultado": "API retorna 201 Created com ID do recurso"}},
            {{"acao": "usuário submete campo obrigatório vazio", "resultado": "API retorna 400 Bad Request com mensagem"}},
            {{"acao": "usuário tenta acessar sem perfil autorizado", "resultado": "API retorna 403 Forbidden"}},
            {{"acao": "usuário submete dados violando RN01", "resultado": "API retorna 422 Unprocessable Entity com erro específico"}}
        ],
        "campos": [
            {{"nome": "campo1", "tipo": "string", "obrigatoriedade": "Obrigatório", "validacao": "min 3 chars, max 150, sem caracteres especiais", "exemplo": "João Silva"}},
            {{"nome": "campo2", "tipo": "email", "obrigatoriedade": "Obrigatório", "validacao": "formato email válido, único no sistema", "exemplo": "joao@example.com"}},
            {{"nome": "campo3", "tipo": "enum", "obrigatoriedade": "Obrigatório", "validacao": "valores permitidos: ATIVO, INATIVO", "exemplo": "ATIVO"}}
        ],
        "criterios_qa": [
            "Verificar se retorna 201 e ID do recurso ao cadastrar com dados válidos",
            "Verificar se rejeita com 400 ao submeter campo obrigatório vazio",
            "Verificar se rejeita com 403 usuários sem perfil autorizado",
            "Verificar se valida comprimento e formato de cada campo conforme especificado",
            "Verificar se aplica RN01, RN02, RN03 corretamente",
            "Verificar se campos únicos não permitem duplicatas",
            "Verificar se retorna mensagens de erro descritivas para cada validação"
        ],
        "tags": [
            "backend",
            "modulo-nome"
        ]
        }}"""

        texto = self._invocar(prompt)
        return self._extrair_json_seguro(texto)

    def formatar_story_backend(self, detalhamento: dict, contexto: dict) -> dict:
        """
        Recebe o detalhamento estruturado e o contexto do requisito,
        e monta a descrição final no padrão .md do exemplo_card.
        A formatação é feita em Python — sem depender do LLM para escapar
        caracteres especiais dentro do JSON.
        Retorna {"titulo": str, "descricao": str, "tags": list} pronto para o Trello.
        """
        titulo              = detalhamento.get("titulo", "")
        endpoint            = detalhamento.get("endpoint", "")
        descricao_resumida  = detalhamento.get("descricao_resumida", "")
        modulo              = contexto.get("modulo", "")
        perfis              = ", ".join(contexto.get("perfis", ["PERFIL1", "PERFIL2"]))
        
        # Obter tags do detalhamento com fallback robusto
        tags = detalhamento.get("tags", [])
        if not tags:
            tags = ["backend", "implementacao"]
            if modulo:
                tags.append(modulo.lower().replace(" ", "-"))
        
        # Normalizar tags: strings em minúsculas, remover vazias
        tags = [str(t).strip().lower() for t in tags if t]
        logger.debug("Tags para story backend: %s", tags)

        regras_md = "\n".join(
            f"- [ ] {r}"
            for r in detalhamento.get("regras_especificas", [])
        )

        acoes_md = "#### Fluxo esperado\n\n" + "\n".join(
        f"- {a.get('acao') or 'ACAO'} -> {a.get('resultado') or 'RESULTADO'}"
        for a in detalhamento.get("acoes", [])
        if a.get('acao') or a.get('resultado')
    )

        campos_md = "Campos do Endpoint\n\n" + "\n\n".join(
                f"""- Campo: {c.get('nome', 'NOME')}
            - Tipo: {c.get('tipo', 'TIPO')}
            - Obrigatório: {c.get('obrigatoriedade', 'Sim | Não')}
            - Mín: {c.get('min', 'N/A')}
            - Máx: {c.get('max', 'N/A')}
            - Descrição: {c.get('descricao', c.get('validacao', 'DESCRIÇÃO'))}"""
                for c in detalhamento.get("campos", [])
            )

        criterios_md = "\n".join(
            f"- [ ] {c}"
            for i, c in enumerate(detalhamento.get("criterios_qa", []))
        )

        descricao = f"""## {titulo}

**Descrição:** {descricao_resumida}
**Prioridade:** Essencial | Evidente
**Módulo:** {modulo}
**Endpoint:** `{endpoint}`

---

### Critério de Aceite – QA
- [ ] **Perfis de acesso:** {perfis}
- [ ] Atender todos os requisitos e regras de negócio associadas
- [ ] Todos os critérios de QA devem passar

### Requisito Funcional
**RF##PP | Essencial | Evidente**

{descricao_resumida}

### Regras de Negócio
{regras_md if regras_md else "- Nenhuma regra específica"}

### Contrato da API

**Endpoint:** `{endpoint}`

**Ações e Resultados Esperados:**

#### Fluxo esperado

{acoes_md}

### Campos do Endpoint


{campos_md }

### Critérios de Qualidade (QA)

Verificações obrigatórias para validação da funcionalidade:

{criterios_md if criterios_md else "- [ ] Validação padrão"}

### Tags 
{', '.join(tags) if tags else "Nenhuma tag"}
"""

        logger.info("Story de backend formatada: %s", titulo)
        return {"titulo": titulo, "descricao": descricao, "tags": tags}

    def generate_backend_card(self, funcionalidade: str, contexto_str: str) -> dict:
        """
        Orquestra detalhar + formatar para uma funcionalidade de backend.
        Converte o contexto string de volta para dict para o formatar_story.
        Retorna {"epic": str, "stories": [{"titulo": str, "descricao": str}]}.
        """
        contexto_dict = self._extrair_json_seguro(contexto_str) if isinstance(contexto_str, str) else contexto_str

        detalhamento = self.detalhar_card_backend(funcionalidade, contexto_str)
        story        = self.formatar_story_backend(detalhamento, contexto_dict)

        return {
            "epic":    contexto_dict.get("modulo", funcionalidade),
            "stories": [story],
        }

    # ──────────────────────────────────────────────────────────
    # ETAPA 3 — Geração de cards de frontend
    # ──────────────────────────────────────────────────────────

    def detalhar_card_frontend(
        self,
        funcionalidade: str,
        contexto: str,
        contexto_backend: str,
    ) -> dict:
        """
        Dado uma funcionalidade de frontend, o contexto do requisito e os
        endpoints do backend já criados, levanta campos, tarefas técnicas
        e critérios de QA específicos.
        Retorna dicionário estruturado para formatar_story_frontend.
        """
        logger.info("Detalhando card de frontend: '%s'", funcionalidade[:60])

        prompt = f"""Você é um líder técnico sênior detalhando uma funcionalidade de frontend.
        Seu objetivo é criar um card estruturado para equipe de frontedn, detalhado e pronto para desenvolvimento considerando funcionalidade, contexto do sistem, contexto backend.

        ## Funcionalidade:
        {funcionalidade}

        ## Contexto do sistema (módulo, regras, entidades, perfis):
        {contexto}

        ## Endpoints do backend disponíveis (use EXATAMENTE estes — não invente rotas):
        {contexto_backend if contexto_backend else "Nenhum backend registrado ainda."}

        ## Instruções OBRIGATÓRIAS
        - Use os endpoints do backend listados acima
        - Defina os campos do formulário com tipo e validação reais
        - Liste tarefas técnicas atômicas e implementáveis
        - Liste critérios de QA verificáveis específicos para o frontend
        - Gere tags descritivas para categorizar o card
        - Título DEVE seguir: [FRONTEND][Modulo] Funcionalidade

        ## Detalhes dos Campos
        Para cada campo do formulário, especifique:
        - utilize apenas os campos do requisito original como única fonte de verdade — NÃO adicione ou remova nada que não esteja lá
        - Obrigatoriedade real (se o requisito diz "campo obrigatório", marque como obrigatório)
        - Tipo de dado (text, email, select, date, number, etc.)
        - Validações específicas (padrão regex, comprimento, valores permitidos)
        - Comportamento (máscara, auto-complete, dependência de outros campos)

        ## Retorne SOMENTE este JSON, sem texto antes ou depois, usando aspas duplas:
        {{
        "titulo": "[FRONTEND][Modulo] FUNCIONALIDADE",
        "endpoint_consumido": "METODO /modulo/acao do backend acima",
        "requisito_original": "requisito",
        "descricao_resumida": "Uma frase clara descrevendo a tela/componente e seu propósito",
        "regras_ux": [
            "RN01: regra de UX ou integração específica (ex: campo A habilita campo B)",
            "RN02: regra de UX ou integração específica",
            "RN03: comportamento esperado em validações ou carregamento"
        ],
        "campos": [
            {{"nome": "campo1", "tipo": "text", "validacao": "min 3, max 150 chars, sem caracteres especiais", "obrigatoriedade": "Obrigatório", "exemplo": "João Silva"}},
            {{"nome": "campo2", "tipo": "email", "validacao": "formato email válido, único", "obrigatoriedade": "Obrigatório", "exemplo": "joao@example.com"}},
            {{"nome": "campo3", "tipo": "select", "validacao": "opções: ATIVO, INATIVO, PENDENTE", "obrigatoriedade": "Obrigatório", "exemplo": "ATIVO"}}
        ],
        "tarefas_tecnicas": [
            "Criar componente Form[NomeEntidade] com validação de campos",
            "Integrar com endpoint METODO /modulo/acao do backend",
            "Implementar estados: idle, loading, sucesso, erro",
            "Exibir mensagens de erro inline para cada validação",
            "Implementar feedback visual (spinner, toast, etc.)"
        ],
        "criterios_qa": [
            "Verificar se exibe erro inline ao submeter campo obrigatório vazio",
            "Verificar se exibe spinner durante chamada à API",
            "Verificar se valida comprimento máximo e padrão de cada campo",
            "Verificar se redireciona/fecha modal após sucesso",
            "Verificar se exibe mensagem de erro da API de forma legível",
            "Verificar se desabilita botão de envio durante carregamento",
            "Verificar se limpa formulário após envio com sucesso"
        ],
        "tags": [
            "frontend",
            "modulo-nome"
        ]
        }}"""

        texto = self._invocar(prompt)
        return self._extrair_json_seguro(texto)

    def formatar_story_frontend(self, detalhamento: dict, contexto: dict) -> dict:
        """
        Recebe o detalhamento estruturado e o contexto do requisito,
        e monta a descrição final no padrão .md do exemplo_card.
        A formatação é feita em Python — sem depender do LLM para escapar
        caracteres especiais dentro do JSON.
        Retorna {"titulo": str, "descricao": str, "tags": list} pronto para o Trello.
        """
        titulo             = detalhamento.get("titulo", "")
        endpoint_consumido = detalhamento.get("endpoint_consumido", "")
        descricao_resumida = detalhamento.get("descricao_resumida", "")
        modulo             = contexto.get("modulo", "")
        perfis             = ", ".join(contexto.get("perfis", ["PERFIL1", "PERFIL2"]))
        requisito_original  = contexto.get("requisito_original", "")
        # Obter tags do detalhamento com fallback robusto
        tags = detalhamento.get("tags", [])
        if not tags:
            tags = ["frontend", "implementacao"]
            if modulo:
                tags.append(modulo.lower().replace(" ", "-"))
        
        # Normalizar tags: strings em minúsculas, remover vazias
        tags = [str(t).strip().lower() for t in tags if t]
        logger.debug("Tags para story frontend: %s", tags)

        regras_md = "\n".join(
            f"- [ ] {r}"
            for r in detalhamento.get("regras_ux", [])
        )

        campos_md = "Campos do Endpoint\n\n" + "\n\n".join(
                f"""- Campo: {c.get('nome', 'NOME')}
            - Tipo: {c.get('tipo', 'TIPO')}
            - Obrigatório: {c.get('obrigatoriedade', 'Sim | Não')}
            - Mín: {c.get('min', 'N/A')}
            - Máx: {c.get('max', 'N/A')}
            - Descrição: {c.get('descricao', c.get('validacao', 'DESCRIÇÃO'))}"""
                for c in detalhamento.get("campos", [])
            )
        
        tarefas_md = "\n".join(
            f"- [ ] {t}"
            for t in detalhamento.get("tarefas_tecnicas", [])
        )

        criterios_md = "\n".join(
            f"- [ ] {c}"
            for i, c in enumerate(detalhamento.get("criterios_qa", []))
        )

        descricao = f"""
        
        ## {titulo}
**Descrição:** {descricao_resumida}
**Prioridade:** Essencial | Evidente
**Módulo:** {modulo}
**Endpoint Backend:** `{endpoint_consumido}`

---

### Critério de Aceite – QA
- [ ] **Perfis de acesso:** {perfis}
- [ ] Atender todos os requisitos e regras de negócio associadas
- [ ] Todos os critérios de QA devem passar


## Requisito original:
{requisito_original}
### Requisito Funcional
{descricao_resumida}

### Contexto de Integração Backend

Este componente consome o seguinte endpoint do backend:

**Endpoint:** `{endpoint_consumido}`

### Regras de UX / Integração

{regras_md if regras_md else "- Nenhuma regra específica"}

### Tarefas Técnicas

Atividades que devem ser implementadas para completar este card:

{tarefas_md if tarefas_md else "- [ ] Tarefa padrão"}

### Estrutura de Dados – Campos do Formulário / Tela

Campos do Endpoint

{campos_md}

### Critérios de Qualidade (QA)

Verificações obrigatórias para validação da funcionalidade no frontend:

{criterios_md}

### Tags 
{', '.join(tags) if tags else "Nenhuma tag"}

"""

        logger.info("Story de frontend formatada: %s", titulo)
        return {"titulo": titulo, "descricao": descricao, "tags": tags}

    def generate_frontend_card(
        self,
        funcionalidade: str,
        contexto_str: str,
        contexto_backend: str = "",
    ) -> dict:
        """
        Orquestra detalhar + formatar para uma funcionalidade de frontend.
        Retorna {"epic": str, "stories": [{"titulo": str, "descricao": str}]}.
        """
        contexto_dict = self._extrair_json_seguro(contexto_str) if isinstance(contexto_str, str) else contexto_str

        detalhamento = self.detalhar_card_frontend(
            funcionalidade, contexto_str, contexto_backend
        )
        story = self.formatar_story_frontend(detalhamento, contexto_dict)

        return {
            "epic":    contexto_dict.get("modulo", funcionalidade),
            "stories": [story],
        }