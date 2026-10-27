"""
LTCMiner Auto-Withdraw - Implementation Module
Plataforma: ltcminer.com
Baseado na análise dos JavaScripts da plataforma
"""

import requests
import os
import time
import json
import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class LTCMinerAutoWithdraw:
    """
    Classe para automação de saques na plataforma LTCMiner.
    Baseado na análise dos JavaScripts da plataforma.
    """

    def __init__(self, env_file: str = None):
        # Load environment variables
        if env_file:
            load_dotenv(env_file)

        self.email = os.getenv('LTCMINER_EMAIL')
        self.password = os.getenv('LTCMINER_PASSWORD')
        self.withdraw_address = os.getenv('WITHDRAWAL_ADDRESS', 'M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw')
        self.network = os.getenv('NETWORK', 'litecoin')
        self.retries = int(os.getenv('MAX_RETRIES', '3'))

        self.session = requests.Session()
        self.base_url = 'https://ltcminer.com'
        self.api_base = 'https://api.ltcminer.com/task'

        # Headers padrão
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://ltcminer.com',
            'Connection': 'keep-alive',
        }

        # Variáveis de estado
        self.current_ltc_balance = 0.0
        self.current_monthly_payout = 0.0
        self.current_ltc_price = 0.0
        self.balance_accumulator = 0.0
        self.is_logged_in = False

        # Configuração de logging
        self.setup_logging()

    def setup_logging(self):
        """Configura o sistema de logging"""
        self.logger = logging.getLogger('LTCMinerAutoWithdraw')
        self.logger.setLevel(logging.INFO)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)

    def get_session(self):
        """Retorna a sessão do cliente"""
        return self.session

    def login(self) -> bool:
        """
        Realiza login na plataforma LTCMiner.
        Retorna True se login bem-sucedido, False caso contrário.
        """
        self.logger.info(f'Iniciando login com {self.email}...')

        # Form data de login
        login_data = {
            'login': self.email,
            'password': self.password,
            'RememberMe': 'true',
        }

        try:
            # Tentar login via /auth endpoint
            response = self.session.post(
                f'{self.base_url}/auth',
                data=login_data,
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )

            # Verificar se houve redirecionamento para o dashboard
            if response.url and '/dashboard' in response.url:
                self.is_logged_in = True
                self.logger.info('Login realizado com sucesso!')
                return True

            # Verificar se há cookies de sessão
            cookies = self.session.cookies.get_dict()
            if cookies and 'session' in cookies:
                self.is_logged_in = True
                self.logger.info('Login realizado com sucesso!')
                return True

            # Tentar método alternativo
            self.logger.warning('Login direto falhou, tentando método alternativo...')

            # Acessar dashboard para verificar se já está logado
            dashboard_response = self.session.get(
                f'{self.base_url}/dashboard',
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )

            if any(kw in dashboard_response.text.lower() for kw in ['user', 'total_balance', 'balance']):
                self.is_logged_in = True
                self.logger.info('Login detectado via dashboard!')
                return True

            self.logger.error('Falha no login: credenciais inválidas ou hCaptcha obrigatório')
            return False

        except Exception as e:
            self.logger.error(f'Exceção no login: {e}')
            return False

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Obtém dados do dashboard do usuário.
        Retorna um dicionário com os dados extraídos.
        """
        self.logger.info('Obtendo dados do dashboard...')

        try:
            response = self.session.get(
                f'{self.base_url}/dashboard',
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )

            if response.status_code != 200:
                self.logger.error(f'Erro ao obter dashboard: {response.status_code}')
                return {}

            content = response.text

            # Extrair dados do JSON
            data = {}
            try:
                # Tentar extrair JSON do HTML
                json_match = re.search(r'window\.__LATEST_DATA\s*=\s*(\{.*?\});\s*</script>', content, re.DOTALL)
                if json_match:
                    extracted = json.loads(json_match.group(1))
                    if extracted.get('user'):
                        data['user_id'] = extracted['user'].get('id')
                        data['total_balance_ltc'] = float(
                            extracted['user'].get('total_balance_ltc', 0) or 0
                        )
                        data['monthly_payout'] = float(
                            extracted['user'].get('plan', {}).get('monthly_payout', 0) or 0
                        )
                    if extracted.get('global'):
                        data['ltc_price'] = float(
                            extracted['global'].get('ltc', {}).get('price', 0) or 0
                        )

                # Alternativa: buscar por padrões no HTML
                if not data.get('total_balance_ltc'):
                    balance_match = re.search(
                        r'(\d+\.\d+)\s*LTC', content, re.IGNORECASE
                    )
                    if balance_match:
                        data['total_balance_ltc'] = float(balance_match.group(1))

            except Exception as e:
                self.logger.warning(f'Erro ao extrair JSON: {e}')

            # Atualizar variáveis de estado
            self.current_ltc_balance = data.get('total_balance_ltc', 0)
            self.current_monthly_payout = data.get('monthly_payout', 0)
            self.current_ltc_price = data.get('ltc_price', 0)

            self.logger.info(f'Dados obtidos: {self.current_ltc_balance:.8f} LTC, '
                           f'payout: {self.current_monthly_payout:.2f}, '
                           f'price: {self.current_ltc_price:.2f}')
            return data

        except Exception as e:
            self.logger.error(f'Erro ao obter dashboard: {e}')
            return {}

    def withdraw_ltc(self, amount: float) -> bool:
        """
        Realiza saque de LTC.
        Retorna True se saque bem-sucedido, False caso contrário.
        """
        if amount <= 0:
            self.logger.warning(f'Valor de saque deve ser positivo: {amount}')
            return False

        self.logger.info(f'Tentando sacar {amount:.8f} LTC para {self.withdraw_address}...')

        try:
            # Endpoint de saque
            withdraw_url = f'{self.api_base}/?action=withdraw'

            payload = {
                'address': self.withdraw_address,
                'amount': str(amount),
                'network': self.network,
                'action': 'withdraw'
            }

            response = self.session.post(
                withdraw_url,
                data=payload,
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success') or result.get('ok'):
                        self.logger.info(f'Saque de {amount:.8f} LTC realizado com sucesso!')
                        return True
                    else:
                        error_msg = result.get('message', result.get('error', 'Erro desconhecido'))
                        self.logger.warning(f'Erro no saque: {error_msg}')
                        return False
                except json.JSONDecodeError:
                    if 'success' in response.text.lower() or 'ok' in response.text.lower():
                        self.logger.info('Saque realizado com sucesso!')
                        return True
                    else:
                        self.logger.warning(f'Resposta inesperada: {response.text[:200]}')
                        return False

            self.logger.error(f'Resposta inesperada: {response.status_code}')
            return False

        except Exception as e:
            self.logger.error(f'Exceção no saque: {e}')
            return False

    def auto_withdraw_logic(self) -> bool:
        """
        Lógica de saque automático baseada no balance accumulator.
        Implementação baseada na análise dos JavaScripts:
        - e = window.__currentMonthlyPayout/30/86400/window.__currentLtcPrice
        - Se balanceAccumulator >= 1e-8, realiza saque
        """
        self.logger.info('Iniciando lógica de saque automático...')

        # 1. Obter dados do dashboard
        dashboard_data = self.get_dashboard_data()
        if not dashboard_data:
            self.logger.warning('Falha ao obter dados do dashboard')
            return False

        # 2. Verificar se há saldo disponível
        if self.current_ltc_balance <= 0:
            self.logger.info(f'Sem saldo disponível para saque: {self.current_ltc_balance:.8f} LTC')
            return False

        # 3. Calcular saque baseado no balance accumulator
        if self.current_monthly_payout > 0 and self.current_ltc_price > 0:
            daily_payout_ltc = self.current_monthly_payout / 30 / 86400 / self.current_ltc_price
            self.balance_accumulator += daily_payout_ltc

            if self.balance_accumulator >= 1e-8:
                amount_to_withdraw = self.balance_accumulator
                self.balance_accumulator = 0.0

                self.logger.info(f'Saque calculado: {amount_to_withdraw:.8f} LTC')

                # 4. Realizar saque
                success = self.withdraw_ltc(amount_to_withdraw)

                if success:
                    self.logger.info(f'Saque de {amount_to_withdraw:.8f} LTC realizado com sucesso!')
                    return True
                else:
                    self.logger.warning('Falha no saque, tentando novamente...')
                    return False

        self.logger.info(f'Nenhum saque necessário. Balance accumulator: {self.balance_accumulator:.8f}')
        return True

    def run(self) -> bool:
        """
        Executa o processo completo de automação.
        """
        self.logger.info(f'=== {datetime.now()} ===')
        self.logger.info('=== Início do processo de automação ===')

        # 1. Login
        if not self.login():
            self.logger.error(f'FALHA NO LOGIN')
            return False

        # 2. Obter dados do dashboard
        self.get_dashboard_data()

        # 3. Executar lógica de saque
        self.auto_withdraw_logic()

        self.logger.info(f'=== {datetime.now()} ===')
        self.logger.info('=== Processo concluído com sucesso! ===')
        return True

    def run_scheduled(self, max_retries: int = 3) -> bool:
        """
        Executa o processo de forma agendada.
        """
        for attempt in range(max_retries):
            try:
                success = self.run()
                if success:
                    return True
                self.logger.warning(f'Tentativa {attempt + 1} falhou, reencontrando...')
                time.sleep(5)
            except Exception as e:
                self.logger.error(f'Exceção na tentativa {attempt + 1}: {e}')
                time.sleep(5)
        return False

    def run_daily(self):
        """
        Método principal para execução diária.
        """
        self.logger.info(f'Start: {datetime.now()}')
        self.run_scheduled()
        self.logger.info(f'End: {datetime.now()}')
        self.logger.info('=== Processo concluído ===')


def main():
    """Função principal"""
    bot = LTCMinerAutoWithdraw()

    # Verificar se todos os ambientes necessários estão definidos
    required_envs = ['LTCMINER_EMAIL', 'LTCMINER_PASSWORD', 'WITHDRAWAL_ADDRESS']
    missing = [env for env in required_envs if not os.getenv(env)]

    if missing:
        print(f'[ERROR] Ambientes faltando: {missing}')
        print('[INFO] Configure os secrets no GitHub Actions:')
        print('  - LTCMINER_EMAIL')
        print('  - LTCMINER_PASSWORD')
        print('  - WITHDRAWAL_ADDRESS')
        return

    # Executar
    if bot.run_scheduled():
        print('[OK] Processo concluído com sucesso!')
    else:
        print('[ERROR] Falha no processo')


if __name__ == '__main__':
    main()
