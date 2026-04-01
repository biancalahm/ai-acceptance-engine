# agent/context.py
from dataclasses import dataclass, field


@dataclass
class RequisitoContext:
    requisito_original:       str       = ""
    modulo:                   str       = ""
    descricao_sistema:        str       = ""
    perfis:                   list[str] = field(default_factory=list)
    regras_negocio:           list[str] = field(default_factory=list)
    entidades:                list[str] = field(default_factory=list)
    funcionalidades_backend:  list[str] = field(default_factory=list)
    funcionalidades_frontend: list[str] = field(default_factory=list)
    

    def esta_vazio(self) -> bool:
        return not self.requisito_original

    def para_prompt(self) -> str:
        regras = " ".join(f"- {r}" for r in self.regras_negocio)
        return f"""Módulo: {self.modulo}
        Sistema: {self.descricao_sistema}
        Perfis: {', '.join(self.perfis)}
        Entidades: {', '.join(self.entidades)}
        Regras de negócio:
        {regras}
        Requisito original: {self.requisito_original}"""

@dataclass
class CardContext:
    
    backends:   list[dict] = field(default_factory=list)  # para o para_prompt() do frontend
    stories_be: list[dict] = field(default_factory=list)  # stories prontas para publicar
    stories_fe: list[dict] = field(default_factory=list)  # stories prontas para publicar


    def registrar(self, titulo: str, descricao: str) -> None:
        """Extrai e armazena informações técnicas de um card de backend para fornecer ao frontend."""
        self.backends.append({"titulo": titulo, "descricao": descricao})
    
    def registrar_story_backend(self, story: dict)-> None:
        """Registrar os cards backend prontos para criação final ."""
        self.stories_be.append(story)

    def registrar_story_frontend(self, story: dict)-> None:
        """Registrar os cards frontend prontos para criação final ."""
        self.stories_be.append(story)

    def esta_vazio(self) -> bool:
        return len(self.endpoints) == 0
    

    def para_prompt(self) -> str:
        if not self.backends:
            return "Nenhum card de backend criado ainda."
        linhas = ["Cards de backend já criados:"]
        for b in self.backends:
            linhas.append(f"- {b['titulo']}")
        return " ".join(linhas)


# Instâncias globais compartilhadas entre todas as skills
req_ctx  = RequisitoContext()
card_ctx = CardContext()


def reset_contexts() -> None:
    global req_ctx, card_ctx
    req_ctx  = RequisitoContext()
    card_ctx = CardContext()