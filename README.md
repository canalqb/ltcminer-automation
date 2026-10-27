# ⚡ LTCMiner Automation - GitHub Actions

Repositório para automação de saques diários na plataforma **LTCMiner** (ltcminer.com).

## 📋 Visão Geral

A partir da análise dos JavaScripts da plataforma, foram identificados:

### Endpoints Principais:
- `GET /dashboard` - Painel de controle
- `POST /auth` - Authentication
- `GET /_tempadminget-api` - API de dados
- `POST /task/` - API de transações (nota: endpoint pode variar)

### Variáveis Clave:
- `__currentLtcBalance` - Saldo atual em LTC
- `__currentMonthlyPayout` - Pagamento mensal
- `__currentLtcPrice` - Preço do Litecoin
- `__balanceAccumulator` - Acumulador para saques

---

## 📁 Estrutura de Arquivos

```
ltcminer-automation/
├── .github/
│   └── workflows/
│       └── withdraw.yml
├── withdraw.py
├── requirements.txt
└── README.md
```

---

## 🚀 Como Usar

### 1. Criar Repositório no GitHub

```bash
git clone https://github.com/SEU_USUARIO/ltcminer-automation.git
cd ltcminer-automation
```

### 2. Criar Estrutura de Pastas

```bash
mkdir -p .github/workflows
```

### 3. Copiar Arquivos

Copie os arquivos:
- `.github/workflows/withdraw.yml`
- `withdraw.py`
- `requirements.txt`
- `README.md`

### 4. Configurar Secrets no GitHub

Vá em **Settings > Secrets and variables > Actions** e adicione:

| Secret | Valor |
|--------|-------|
| `LTCMINER_EMAIL` | Seu email (ex: qrodrigob@gmail.com) |
| `LTCMINER_PASSWORD` | Sua senha (ex: 278307Qb) |
| `WITHDRAWAL_ADDRESS` | Sua carteira LTC: `M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw` |

### 5. Ativar o Workflow

- Vá em **Actions > Auto-Withdrawal Daily**
- Clique em **Run workflow**

### 6. Agendar Execução

O workflow roda automaticamente diariamente às **00:00 UTC** (configurado no YAML).

---

## 🔐 Segurança

⚠️ **IMPORTANTE:**

- Nunca compartilhe seus secrets
- O GitHub criptografa os secrets
- Revogue acesso se suspeitar de violação
- Utilize 2FA no GitHub

---

## ⚠️ Avisos

1. **Termos de Serviço**: Verifique se a automação está em conformidade com os termos do site.
2. **Rate Limiting**: O site pode limitar requisições. Ajuste a frequência se necessário.
3. **Endpoint Exato**: O endpoint de saque pode ter mudado. Verifique sempre no JavaScript.
4. **Carteira**: A carteira `M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw` é para **Litecoin (LTC)**, não Bitcoin.
5. **Monitoramento**: Revise periodicamente os logs e o saldo na plataforma.

---

## 📊 Logs

O workflow gera logs detalhados que podem ser vistos no GitHub Actions:
- Login: `logs`
- Balance: `dashboard`
- Saque: `withdraw`

---

## 🔧 Configuração de Ajustes

### Mudar Frequência
Edite no `withdraw.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 00:00 UTC
```

### Mudar Carteira
Edite no `withdraw.py`:

```python
self.withdraw_address = 'SUA_CARTEIRA_LTC'
```

### Mudar Rede
```python
self.network = 'litecoin'  # ou 'bitcoin'
```

---

## 📈 Monitoramento

Verifique periodicamente:
1. GitHub Actions logs
2. Saldo na plataforma
3. Pequenos retiros confirmados
4. Status da conexão

---

## 🛠️ Requisitos

- Python 3.11+
- GitHub Actions

---

## 📝 Changelog

- v1.0 - Realização inicial da automação

---

## 📄 Licença

MIT License - Use como quiser

---

## ⚡ Como Começar

Veja o arquivo `withdraw.py` e o workflow `withdraw.yml` para entender a automação.

Não se esqueça de:
1. Configurar os secrets
2. Executar manualmente primeiro
3. Verificar se o saque funciona
4. Depois ativar o agendamento

---

### 📍 Endereço da Carteira (Litecoin):
`M8shjQMx1HNAA8qeGeLzuQ1w8LCr5Dcdqw`

### 🌐 Site:
`https://ltcminer.com`

---

*Feito com base na análise dos JavaScripts da plataforma ltcminer.com*
