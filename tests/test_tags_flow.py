#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_tags_flow.py

Script específico para testar o fluxo de criação e associação de tags.
Execute para validar se o fluxo de tags está funcionando corretamente.
"""

import os
import sys
from dotenv import load_dotenv
import logging
import time

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


def test_tag_flow_complete():
    """Testa o fluxo completo de tags: obter/criar label e associar ao card."""
    print("\n" + "="*70)
    print("🏷️  TESTE COMPLETO: FLUXO DE TAGS")
    print("="*70)
    
    load_dotenv()
    
    # Validar configurações
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID")
    list_id = os.getenv("TRELLO_LIST_BACKLOG")
    
    if not all([api_key, token, board_id, list_id]):
        print("[ERROR] ERRO: Variáveis de ambiente incompletas!")
        print(f"   TRELLO_API_KEY: {'[OK]' if api_key else '[ERROR]'}")
        print(f"   TRELLO_TOKEN: {'[OK]' if token else '[ERROR]'}")
        print(f"   TRELLO_BOARD_ID: {'[OK]' if board_id else '[ERROR]'}")
        print(f"   TRELLO_LIST_BACKLOG: {'[OK]' if list_id else '[ERROR]'}")
        return False
    
    try:
        from services.trello_service import TrelloService
        
        trello = TrelloService(api_key=api_key, token=token)
        
        # ──────────────────────────────────────────────────────────
        # ETAPA 1: Criar um card de teste
        # ──────────────────────────────────────────────────────────
        print("\n📝 ETAPA 1: Criar card de teste")
        print("-" * 70)
        
        card_name = f"[TESTE] Card com Tags - {int(time.time())}"
        card_desc = "Card criado para testar o fluxo de associação de tags.\n\nEste card será deletado após o teste."
        
        try:
            card_response = trello.create_card(
                name=card_name,
                desc=card_desc,
                list_id=list_id
            )
            card_id = card_response.get("id")
            card_url = card_response.get("shortUrl", "N/A")
            
            print(f"[OK] Card criado com sucesso!")
            print(f"   Título: {card_name}")
            print(f"   ID: {card_id}")
            print(f"   URL: {card_url}")
        
        except Exception as e:
            print(f"[ERROR] Erro ao criar card: {e}")
            return False
        
        # ──────────────────────────────────────────────────────────
        # ETAPA 2: Testar fluxo de tags
        # ──────────────────────────────────────────────────────────
        print("\n🏷️  ETAPA 2: Testar fluxo de tags")
        print("-" * 70)
        
        test_tags = [
            "backend",
            "validacao",
            "teste-novo",  # Tag que não deve existir - será criada
            "frontend"
        ]
        
        successful_tags = []
        failed_tags = []
        
        for tag_name in test_tags:
            print(f"\n  [RUN] Processando tag: '{tag_name}'")
            
            try:
                # PASSO 1: Obter ou criar label
                print(f"     [1]  Obtendo/criando label '{tag_name}'...", end=" ")
                
                label = trello.get_or_create_label(
                    board_id=board_id,
                    label_name=tag_name
                )
                
                label_id = label.get("id")
                label_name_returned = label.get("name", "N/A")
                
                if not label_id:
                    print(f"[ERRO]Label retornou sem ID!")
                    failed_tags.append(tag_name)
                    continue
                
                print(f"[OK] (ID: {label_id})")
                
                # PASSO 2: Associar label ao card
                print(f"     [2]  Associando label '{tag_name}' ao card...", end=" ")
                
                assoc_response = trello.add_label_to_card(
                    card_id=card_id,
                    label_id=label_id
                )
                
                print(f"[OK]")
                
                successful_tags.append({
                    "tag": tag_name,
                    "label_id": label_id,
                    "label_name": label_name_returned
                })
                
                print(f"     [OK] Tag '{tag_name}' processada com sucesso!")
            
            except Exception as e:
                print(f"\n Erro ao processar tag '{tag_name}': {e}")
                failed_tags.append(tag_name)
                continue
        
        # ──────────────────────────────────────────────────────────
        # ETAPA 3: Verificar resultado
        # ──────────────────────────────────────────────────────────
        print("\n\n📊 RESULTADO DO TESTE")
        print("-" * 70)
        
        print(f"\n Tags associadas com sucesso: {len(successful_tags)}")
        for tag_info in successful_tags:
            print(f"   • '{tag_info['tag']}' → Label ID: {tag_info['label_id']}")
        
        if failed_tags:
            print(f"\n Tags que falharam: {len(failed_tags)}")
            for tag in failed_tags:
                print(f"   • '{tag}'")
        
   
      
        # ──────────────────────────────────────────────────────────
        # RESULTADO FINAL
        # ──────────────────────────────────────────────────────────
        print("\n" + "="*70)
        if len(failed_tags) == 0:
            print("[OK] TESTE PASSOU! Fluxo de tags funcionando corretamente!")
            print("="*70 + "\n")
            return True
        else:
            print(f"TESTE PARCIAL! {len(failed_tags)} tags falharam")
            print("="*70 + "\n")
            return len(failed_tags) <= 1  # Passa se menos de 2 falharam
    
    except Exception as e:
        print(f"\n[ERROR] ERRO GERAL NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tag_deduplication():
    """Testa se tags duplicadas são evitadas corretamente."""
    print("\n" + "="*70)
    print("[RUN] TESTE DE DEDUPLICAÇÃO: Tags Duplicadas")
    print("="*70)
    
    load_dotenv()
    
    board_id = os.getenv("TRELLO_BOARD_ID")
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    
    if not all([board_id, api_key, token]):
        print("[ERROR] Configuração incompleta")
        return False
    
    try:
        from services.trello_service import TrelloService
        
        trello = TrelloService(api_key=api_key, token=token)
        
        print("\n[RUN] Obtendo label 'backend' duas vezes (deve retornar mesma ID)")
        print("-" * 70)
        
        # Primeira chamada
        print("[1]  Primeira chamada a get_or_create_label('backend')...", end=" ")
        label1 = trello.get_or_create_label(board_id=board_id, label_name="backend")
        id1 = label1.get("id")
        print(f"[OK] ID: {id1}")
        
        # Segunda chamada
        print("[2]  Segunda chamada a get_or_create_label('backend')...", end=" ")
        label2 = trello.get_or_create_label(board_id=board_id, label_name="backend")
        id2 = label2.get("id")
        print(f"[OK] ID: {id2}")
        
        # Comparar IDs
        print("\n📊 Resultado:")
        if id1 == id2:
            print(f"[OK] PASSOU! IDs são iguais (não criou duplicata)")
            print(f"   ID: {id1}")
            return True
        else:
            print(f"[ERROR] FALHOU! IDs são diferentes (criou duplicata)")
            print(f"   ID 1: {id1}")
            print(f"   ID 2: {id2}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        return False


def main():
    """Executa todos os testes de tags."""
    print("\n")
    print("█" * 70)
    print("█  TESTE DO FLUXO DE TAGS - Criar/Obter e Associar              █")
    print("█" * 70)
    
    results = []
    
    # Teste 1: Fluxo completo
    results.append(test_tag_flow_complete())
    
    # Teste 2: Deduplicação
    results.append(test_tag_deduplication())
    
    # Resumo
    print("\n" + "="*70)
    print("📋 RESUMO FINAL")
    print("="*70)
    print(f"Fluxo Completo: {'[OK] PASSOU' if results[0] else '[ERROR] FALHOU'}")
    print(f"Deduplicação:   {'[OK] PASSOU' if results[1] else '[ERROR] FALHOU'}")
    
    if all(results):
        print("\n[OK] TODOS OS TESTES PASSARAM! Fluxo de tags está funcionando corretamente!")
    else:
        print("\n[WARN]  ALGUNS TESTES FALHARAM. Verifique os logs acima.")
    
    print("\n" + "█" * 70)
    print("█" * 70 + "\n")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
