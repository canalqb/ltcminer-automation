"""
LTCMiner Auto-Withdraw Script
Plataforma: ltcminer.com
Baseado na análise dos JavaScripts da plataforma
"""

import requests
import os
import time
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any

class LTCMinerAutoWithdraw:
    def __init__(self):
        self.email = os.getenv('LTCMINER_EMAIL')
        self.password = os.getenv('LTCMINER_PASSWORD')
        self.withdraw_address = os.getenv('WITHDRAWAL_ADDRESS', 'M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw')
        self.network = os.getenv('NETWORK', 'litecoin')
        self.session = requests.Session()
        
        # Configurações da API baseada na análise dos JS
        self.base_url = 'https://ltcminer.com'
        self.api_base = 'https://api.ltcminer.com/task'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        
        self.session.headers.update(self.headers)
        
        # Variáveis de estado do usuário (extraídas dos JS)
        self.current_ltc_balance = 0.0
        self.current_monthly_payout = 0.0
        self.current_ltc_price = 0.0
        self.balance_accumulator = 0.0
        self.user_id = None
        self.is_logged_in = False
        
        print(f'[INFO] LTCMiner Auto-Withdraw iniciado em {datetime.now()}')
    
    def login(self) -> bool:
        """Realiza login na plataforma"""
        print(f'[INFO] Tentando login com {self.email}...')
        
        # Tentar login via /auth endpoint (encontrado nos JS)
        login_url = f'{self.base_url}/auth'
        data = {
            'login': self.email,
            'password': self.password,
            'remember': 'true'
        }
        
        try:
            response = self.session.post(
                login_url,
                data=data,
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )
            
            # Verificar se houve login bem-sucedido
            if response.status_code in [200, 302, 303]:
                # Verificar se há cookies de sessão
                cookies = self.session.cookies.get_dict()
                if cookies:
                    print(f'[INFO] Cookies de sessão obtidos: {list(cookies.keys())}')
                    self.is_logged_in = True
                    print(f'[OK] Login realizado com sucesso!')
                    return True
            
            # Se falhar, tentar método alternativo
            print(f'[WARN] Login direto falhou, tentando método alternativo...')
            
            # Tentar acessar dashboard e verificar se já está logado
            dashboard_response = self.session.get(
                f'{self.base_url}/dashboard',
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )
            
            if 'User' in dashboard_response.text or 'total_balance' in dashboard_response.text.lower():
                self.is_logged_in = True
                print(f'[OK] Login detectado via dashboard!')
                return True
            
            print(f'[ERROR] Falha no login: {response.status_code}')
            print(f'[DEBUG] Resposta: {response.text[:500]}')
            return False
            
        except Exception as e:
            print(f'[ERROR] Exceção no login: {e}')
            return False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtém dados do dashboard"""
        print(f'[INFO] Obtendo dados do dashboard...')
        
        try:
            response = self.session.get(
                f'{self.base_url}/dashboard',
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Extrair dados do JSON ou HTML
                try:
                    # Tentar extrair JSON
                    json_match = re.search(r'window\.__LATEST_DATA\s*=\s*(\{.*?\});', content)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        if data.get('user'):
                            self.user_id = data['user'].get('id')
                            self.current_ltc_balance = float(data['user'].get('total_balance_ltc', 0) or 0)
                            self.current_monthly_payout = float(data['user'].get('plan', {}).get('monthly_payout', 0) or 0)
                        if data.get('global'):
                            self.current_ltc_price = float(data['global'].get('ltc', {}).get('price', 0) or 0)
                        print(f'[INFO] Dados do dashboard extraídos: {self.current_ltc_balance} LTC')
                    
                    # Alternativa: buscar por padrões no HTML
                    elif 'total_balance' in content:
                        balance_match = re.search(r'total_balance[^<]*<[^>]*>([^<]+)', content)
                        if balance_match:
                            self.current_ltc_balance = float(balance_match.group(1))
                            print(f'[INFO] Saldo encontrado: {self.current_ltc_balance} LTC')
                    
                    return {'success': True, 'data': content}
                except Exception as e:
                    print(f'[WARN] Erro ao extrair JSON: {e}')
                    return {'success': True, 'data': content}
            
            return {'success': False, 'error': f'Status: {response.status_code}'}
            
        except Exception as e:
            print(f'[ERROR] Erro ao obter dashboard: {e}')
            return {'success': False, 'error': str(e)}
    
    def withdraw_ltc(self, amount: float) -> bool:
        """
        Realiza saque de LTC
        Endpoint baseado na análise dos JS: /task com métodos POST
        """
        if amount <= 0:
            print(f'[WARN] Valor de saque deve ser positivo: {amount}')
            return False
        
        print(f'[INFO] Tentando sacar {amount} LTC para {self.withdraw_address}...')
        
        try:
            # Endpoint de saque baseado na análise: /task avec parâmetros de ação
            # Formato: https://api.ltcminer.com/task?action=withdraw
            withdraw_url = f'{self.api_base}/?action=withdraw'
            
            payload = {
                'address': self.withdraw_address,
                'amount': str(amount),
                'network': self.network,
                'action': 'withdraw'
            }
            
            # Adicionar cookies de sessão automaticamente via session
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
                        print(f'[OK] Saque de {amount} LTC realizado com sucesso!')
                        return True
                    else:
                        error_msg = result.get('message', result.get('error', 'Erro desconhecido'))
                        print(f'[WARN] Erro no saque: {error_msg}')
                        return False
                except json.JSONDecodeError:
                    # Se não for JSON, verificar texto
                    if 'success' in response.text.lower() or 'ok' in response.text.lower():
                        print(f'[OK] Saque realizado com sucesso!')
                        return True
                    else:
                        print(f'[WARN] Resposta inesperada: {response.text[:200]}')
                        return False
            
            print(f'[ERROR] Resposta inesperada: {response.status_code}')
            return False
            
        except Exception as e:
            print(f'[ERROR] Exceção no saque: {e}')
            return False
    
    def auto_withdraw_logic(self) -> bool:
        """
        Lógica de saque automático baseada no balance accumulator
        Do JS: window.__balanceAccumulator acumula e realiza saque quando >= 1e-8
        """
        print(f'[INFO] Iniciando lógica de saque automático...')
        
        # 1. Obter dados do dashboard
        dashboard_data = self.get_dashboard_data()
        if not dashboard_data['success']:
            print(f'[ERROR] Falha ao obter dados do dashboard')
            return False
        
        # 2. Verificar se há saldo disponível
        if self.current_ltc_balance <= 0:
            print(f'[INFO] Sem saldo disponível para saque: {self.current_ltc_balance} LTC')
            return False
        
        # 3. Calcular saque baseado no balance accumulator
        # Do JS: e = window.__currentMonthlyPayout/30/86400/window.__currentLtcPrice
        # Se o accumulator >= 1e-8, realiza saque
        if self.current_monthly_payout > 0 and self.current_ltc_price > 0:
            daily_payout_ltc = self.current_monthly_payout / 30 / 86400 / self.current_ltc_price
            self.balance_accumulator += daily_payout_ltc
            
            if self.balance_accumulator >= 1e-8:
                # Calcula quantidade de saque
                amount_to_withdraw = self.balance_accumulator
                self.balance_accumulator = 0.0
                
                print(f'[INFO] Saque calculado: {amount_to_withdraw:.8f} LTC')
                
                # 4. Realizar saque
                success = self.withdraw_ltc(amount_to_withdraw)
                
                if success:
                    print(f'[OK] Saque de {amount_to_withdraw:.8f} LTC realizado com sucesso!')
                    return True
                else:
                    print(f'[WARN] Falha no saque, tentando novamente...')
                    return False
        
        print(f'[INFO] Nenhum saque necessário. Balance accumulator: {self.balance_accumulator:.8f}')
        return True
    
    def run(self) -> bool:
        """Executa o processo completo de automação"""
        print(f'=== {datetime.now()} ===')
        
        # 1. Login
        if not self.login():
            print(f'[ERROR] FALHA NO LOGIN')
            return False
        
        # 2. Verificar dados do dashboard
        self.get_dashboard_data()
        
        # 3. Executar lógica de saque
        self.auto_withdraw_logic()
        
        print(f'=== {datetime.now()} ===')
        print(f'[INFO] Processo concluído com sucesso!')
        return True
    
    def run_scheduled(self):
        """Executa o processo de forma agendada"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                success = self.run()
                if success:
                    return True
                print(f'[WARN] Tentativa {attempt + 1} falhou, reencontrando...')
                time.sleep(5)
            except Exception as e:
                print(f'[ERROR] Exceção na tentativa {attempt + 1}: {e}')
                time.sleep(5)
        return False


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
        print(f'[OK] Processo concluído com sucesso!')
    else:
        print(f'[ERROR] Falha no processo')


if __name__ == '__main__':
    main()
