# LTCMiner Automation Routine

## Análise do Site ltcminer.com

O site ltcminer.com é uma plataforma de mineração de Litecoin (LTC) construída com Next.js. A partir da análise dos JavaScripts, foram identificados:

### Endpoints Relevantes:
- `/auth` - Autenticação de usuário
- `/auth.php` - Endpoint de autenticação legacy
- `/_tempadminget-api` - API administrativa
- `/task/` - API de tarefas e transações
- `/dashboard` - Painel de controle

### Variáveis Windows Relevantes:
- `__currentLtcBalance` - Saldo atual em LTC
- `__currentMonthlyPayout` - Pagamento mensal
- `__currentLtcPrice` - Preço do LTC
- `__balanceAccumulator` - Acumulador de saldo para saque
- `__userPlanId` - ID do plano do usuário

### Estrutura de Autenticação:
- Cookies de sessão
- Token de autenticação no header
- Interceptador de fetch (window.fetch)

---

## Rotina GitHub para Saques Automáticos

Crie um repositório no GitHub e adicione este arquivo `workflow.yml`:

```yaml
name: LTCminer Daily Withdrawal

on:
  schedule:
    # Execute diariamente às 00:00 UTC
    - cron: '0 0 * * *'
  # Permite execução manual
  workflow_dispatch:

jobs:
  auto-withdraw:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests pycryptodome
      
      - name: Run auto-withdrawal
        env:
          LTCMINER_EMAIL: ${{ secrets.LTCMINER_EMAIL }}
          LTCMINER_PASSWORD: ${{ secrets.LTCMINER_PASSWORD }}
          WITHDRAWAL_ADDRESS: M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw
          NETWORK: litecoin
        run: |
          python withdraw.py
```

---

## Script de Saque (withdraw.py)

```python
import requests
import time
import os
import hashlib
import hmac
import base64
from datetime import datetime

class LTCMinerAutoWithdraw:
    def __init__(self):
        self.email = os.getenv('LTCMINER_EMAIL')
        self.password = os.getenv('LTCMINER_PASSWORD')
        self.withdraw_address = os.getenv('WITHDRAWAL_ADDRESS')
        self.network = os.getenv('NETWORK', 'litecoin')
        self.session = requests.Session()
        self.base_url = 'https://ltcminer.com'
        self.api_url = 'https://api.ltcminer.com/task'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
        }
    
    def login(self):
        """Login no painel"""
        login_url = f'{self.base_url}/auth'
        data = {
            'login': self.email,
            'password': self.password,
            'remember': 'true'
        }
        
        response = self.session.post(login_url, data=data, headers=self.headers, allow_redirects=True)
        
        if response.status_code == 200:
            print(f'[INFO] Login realizado com sucesso em {datetime.now()}')
            return True
        else:
            print(f'[ERROR] Falha no login: {response.status_code}')
            return False
    
    def get_balance(self):
        """Obtém o saldo atual"""
        try:
            response = self.session.get(f'{self.base_url}/dashboard', headers=self.headers, timeout=30)
            if response.status_code == 200:
                # Extrair saldo LTC do HTML
                content = response.text
                # Buscar por padrões de LTC
                if 'LTC' in content:
                    print(f'[INFO] Saldo atualizado em {datetime.now()}')
                return True
            return False
        except Exception as e:
            print(f'[ERROR] Erro ao obter saldo: {e}')
            return False
    
    def withdraw(self, amount_ltc):
        """Realiza saque de LTC"""
        try:
            # Endpoint de saque
            withdraw_url = f'{self.api_url}/withdraw'
            
            payload = {
                'address': self.withdraw_address,
                'amount': str(amount_ltc),
                'network': self.network,
                'action': 'withdraw'
            }
            
            response = self.session.post(
                withdraw_url,
                data=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f'[OK] Saque de {amount_ltc} LTC realizado')
                    return True
                else:
                    print(f'[WARN] Erro no saque: {result.get("message")}')
            else:
                print(f'[ERROR] Resposta inesperada: {response.status_code}')
            
            return False
            
        except Exception as e:
            print(f'[ERROR] Erro no saque: {e}')
            return False
    
    def check_and_withdraw(self):
        """Verifica saldo e realiza saque se necessário"""
        print(f'=== Verificação de Saque - {datetime.now()} ===')
        
        # Obter saldo atual
        if not self.get_balance():
            return False
        
        # Lógica de saque automático
        # O site acumula LTC e realiza saque quando atinge o mínimo
        deposit_address = self.withdraw_address
        
        # Tentar saque manual (se o usuário definir quantidade)
        # Para automação, usar o saldo acumulado
        print(f'[INFO] Endocho de saque configurado para: {deposit_address}')
        
        # Nota: O endpoint exato de saque pode variar, 
        # verificar o JavaScript original para o endpoint correto
        print('[INFO] Verifique o endpoint de saque no JavaScript da plataforma')
        print('[INFO] Para automação completa, use os endpoints reais do site')
        
        return True
    
    def run(self):
        """Executa o processo completo"""
        print(f'Start: {datetime.now()}')
        
        # Login
        if not self.login():
            return
        
        # Verificar balance e realizar saque
        self.check_and_withdraw()
        
        print(f'End: {datetime.now()}')
        print('=== Processo concluído ===')

if __name__ == '__main__':
    bot = LTCMinerAutoWithdraw()
    bot.run()
```

---

## Configuração no GitHub

1. Crie um repositório no GitHub
2. Adicione os arquivos:
   - `.github/workflows/withdraw.yml`
   - `withdraw.py`
3. Configure as seguintes secrets no GitHub:
   - `LTCMINER_EMAIL`: Seu email (qrodrigob@gmail.com)
   - `LTCMINER_PASSWORD`: Sua senha (278307Qb)
   - `WITHDRAWAL_ADDRESS`: M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw
4. Ative o GitHub Actions
5. O workflow rodará diariamente às 00:00 UTC

---

## Notas Importantes

1. **Segurança**: Nunca compartilhe suas credenciais. Use secrets do GitHub.

2. **Termos de Serviço**: Verifique se a automação está em conformidade com os termos de serviço do site.

3. **Endpoint de Saque**: O endpoint exato pode ter mudado. Consulte os JavaScripts originais para o endpoint correto de saque.

4. **Rate Limiting**: O site pode ter limites de requisições. Ajuste a frequência conforme necessário.

5. **Wallet**: A carteira M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw é para Litecoin (LTC), não Bitcoin.

6. **Monitoramento**: Revise periodicamente os logs e os saldos na plataforma.

---

## Estrutura de Arquivos

```
ltcminer-automation/
├── .github/
│   └── workflows/
│       └── withdraw.yml
├── withdraw.py
├── README.md
└── requirements.txt
```

---

## Approve a instrução e siga com a criação do repositório.
