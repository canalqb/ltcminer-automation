#!/usr/bin/env python3
"""
LTCMiner Auto-Withdraw - Implementação Principal

Este script realiza a automação de saques diários na plataforma LTCMiner.
Uso: python ltcminer_automation.py

Configuração de variáveis de ambiente:
    LTCMINER_EMAIL: Seu e-mail de login no LTCMiner
    LTCMINER_PASSWORD: Sua senha do LTCMiner
    WITHDRAWAL_ADDRESS: Endereço da carteira de destino (Litecoin)
    NETWORK: Rede (default: litecoin)

Exemplo:
    LTCMINER_EMAIL=user@example.com \
    LTCMINER_PASSWORD=******** \
    WITHDRAWAL_ADDRESS=M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw \
    python ltcminer_automation.py
"""

import os
import sys
import logging
import time
from datetime import datetime
from pathlib import Path

# Configurar diretório de trabalho
WORKING_DIR = Path(__file__).parent.parent if Path(__file__).parent.name == 'ltcminer_automation' else Path(__file__).parent
sys.path.insert(0, str(WORKING_DIR))

from ltcminer_automation import LTCMinerAutoWithdraw


def load_environment():
    """
    Carrega as variáveis de ambiente do .env file se existir.
    """
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print('[INFO] Variáveis de ambiente carregadas de .env')


def check_environment() -> bool:
    """
    Verifica se todas as variáveis de ambiente necessárias estão definidas.
    """
    required = {
        'LTCMINER_EMAIL': 'Email do LTCMiner',
        'LTCMINER_PASSWORD': 'Senha do LTCMiner',
        'WITHDRAWAL_ADDRESS': 'Endereço da carteira (Litecoin)',
    }

    missing = []
    for key, label in required.items():
        if not os.getenv(key):
            missing.append(f'{key} ({label})')

    if missing:
        print('[ERRO] Variáveis ambiente faltando:')
        for m in missing:
            print(f'  - {m}')
        print('\nConfigure-as no arquivo .env ou nas secrets do GitHub Actions.')
        return False

    return True


def main():
    """
    Função principal do script.
    """
    print('=' * 60)
    print('  LTCMiner Auto-Withdraw - Implementação Principal')
    print('=' * 60)
    print()

    # Carregar variáveis de ambiente
    load_environment()

    # Verificar ambientes
    if not check_environment():
        return 1

    # Criar instância do bot
    print('[INFO] Inicializando LTCMiner Auto-Withdraw...')
    bot = LTCMinerAutoWithdraw()

    print(f'[INFO] Email: {bot.email}')
    print(f'[INFO] Carteira: {bot.withdraw_address}')
    print(f'[INFO] Rede: {bot.network}')
    print()

    # Executar processo
    print('[INFO] Iniciando processo de automação...')
    print('=' * 60)
    try:
        success = bot.run_scheduled()
        if success:
            print('\n[OK] Processo concluído com sucesso!')
        else:
            print('\n[ERRO] Processo falhou após múltiplas tentativas.')
        return 0 if success else 1
    except KeyboardInterrupt:
        print('\n[INFO] Interrompido pelo usuário.')
        return 0
    except Exception as e:
        print(f'[ERRO] Exceção inesperada: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
