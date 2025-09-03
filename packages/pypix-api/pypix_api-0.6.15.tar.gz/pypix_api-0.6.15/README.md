<div align="center">
  <img src="docs/_static/images/logo.png" alt="PyPix-API" width="400"/>

  # pypix-api
</div>

[![CI Pipeline](https://github.com/laddertech/pypix-api/workflows/CI%20Pipeline/badge.svg)](https://github.com/laddertech/pypix-api/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/laddertech/pypix-api/branch/main/graph/badge.svg)](https://codecov.io/gh/laddertech/pypix-api)
[![PyPI version](https://badge.fury.io/py/pypix-api.svg)](https://badge.fury.io/py/pypix-api)
[![Python versions](https://img.shields.io/pypi/pyversions/pypix-api.svg)](https://pypi.org/project/pypix-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: MyPy](https://img.shields.io/badge/type%20checking-mypy-blue)](https://mypy-lang.org/)

Biblioteca em Python para comunicação com APIs bancárias, focada na integração com o PIX.

## Sumário

- [pypix-api](#pypix-api)
  - [Sumário](#sumário)
  - [Visão Geral](#visão-geral)
  - [Instalação](#instalação)
  - [Documentação](#documentação)
  - [Exemplo de Uso](#exemplo-de-uso)
    - [Banco do Brasil](#banco-do-brasil)
    - [Sicoob](#sicoob)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Configuração](#configuração)
    - [Parâmetros de Inicialização](#parâmetros-de-inicialização)
    - [URLs das APIs](#urls-das-apis)
  - [Testes](#testes)
  - [Contribuição](#contribuição)
  - [Segurança](#segurança)
  - [Licença](#licença)

## Visão Geral

O `pypix-api` facilita a integração de sistemas Python com APIs bancárias brasileiras, com ênfase no ecossistema do PIX. A biblioteca abstrai autenticação, comunicação segura (MTLS/OAuth2), e operações comuns de bancos como Banco do Brasil e Sicoob.

## Instalação

```bash
pip install pypix-api
```

Ou, para desenvolvimento:

```bash
git clone https://github.com/laddertech/pypix-api.git
cd pypix-api
pip install -e ".[dev]"
```

## Documentação

📚 **Documentação Completa**: [Sphinx Docs](docs/_build/html/index.html) (local) | [GitHub Pages](https://laddertech.github.io/pypix-api/)

### Guias Específicos

- 📋 **[Guia de Contribuição](CONTRIBUTING.md)** - Como contribuir para o projeto
- 🔒 **[Política de Segurança](SECURITY.md)** - Relatório de vulnerabilidades e boas práticas
- 📝 **[Histórico de Mudanças](CHANGELOG.md)** - Todas as versões e alterações
- 🔧 **Guias de Desenvolvimento**:
  - [CI/CD Pipeline](docs/CI_CD_GUIDE.md) - Configuração do pipeline
  - [Pre-commit Hooks](docs/PRE_COMMIT_GUIDE.md) - Hooks de qualidade
  - [Cobertura de Testes](docs/TESTING_COVERAGE_GUIDE.md) - Estratégia de testes
  - [Type Checking](docs/TYPE_CHECKING_GUIDE.md) - Verificação de tipos

### Referência da API

- 🏦 **[Bancos](docs/api/banks.rst)** - Banco do Brasil, Sicoob
- 🔐 **[Autenticação](docs/api/auth.rst)** - OAuth2, mTLS
- 📊 **[Modelos](docs/api/models.rst)** - Estruturas de dados PIX
- 🎯 **[Scopes](docs/api/scopes.rst)** - Gerenciamento de escopos OAuth2

### Exemplos

- 🏦 **[Banco do Brasil - Básico](docs/examples/bb_basic.rst)**
- 🏛️ **[Sicoob - Básico](docs/examples/sicoob_basic.rst)**
- 🪝 **[Configuração de Webhooks](docs/examples/webhooks.rst)**
- 🔄 **[Pagamentos Recorrentes](docs/examples/recurring.rst)**

Para gerar a documentação localmente:

```bash
make docs
make docs-serve  # Servidor local na porta 8000
```

## Exemplo de Uso

### Banco do Brasil

```python
from pypix_api.banks.bb import BancoDoBrasil

from pypix_api.auth.oauth2 import OAuth2Client

# Primeiro crie o cliente OAuth2
oauth = OAuth2Client(
    client_id="SEU_CLIENT_ID",
    cert="caminho/do/certificado.pem",
    pvk="caminho/da/chave.key"
)

# Depois instancie o banco passando o OAuth2Client
bb = BancoDoBrasil(oauth=oauth)

# Exemplo: Cobrança com Vencimento
payload = {
    "calendario": {
        "dataDeVencimento": "2025-12-31",
        "validadeAposVencimento": 30
    },
    "loc": {
        "id": 789
    },
    "devedor": {
        "logradouro": "Alameda Souza, Numero 80, Bairro Braz",
        "cidade": "Recife",
        "uf": "PE",
        "cep": "70011750",
        "cpf": "12345678909",
        "nome": "Francisco da Silva"
    },
    "valor": {
        "original": "123.45",
        "multa": {
            "modalidade": "2",
            "valorPerc": "15.00"
        },
        "juros": {
            "modalidade": "2",
            "valorPerc": "2.00"
        },
        "desconto": {
            "modalidade": "1",
            "descontoDataFixa": [
                {
                    "data": "2025-11-30",
                    "valorPerc": "30.00"
                }
            ]
        }
    },
    "chave": "5f84a4c5-c5cb-4599-9f13-7eb4d419dacc",
    "solicitacaoPagador": "Cobrança dos serviços prestados."
}

# Criar cobrança com vencimento
cobv = bb.criar_cobv(txid="uuid-unico", body=payload)
print(cobv)
```

### Sicoob

```python
from pypix_api.banks.sicoob import Sicoob

# Instanciação do Sicoob
sicoob = Sicoob(oauth=oauth)  # Reutilizando o mesmo OAuth2Client

# Exemplo: Cobrança imediata
payload_cob = {
    "calendario": {
        "expiracao": 3600
    },
    "devedor": {
        "cpf": "12345678909",
        "nome": "Francisco da Silva"
    },
    "valor": {
        "original": "37.00"
    },
    "chave": "5f84a4c5-c5cb-4599-9f13-7eb4d419dacc",
    "solicitacaoPagador": "Pagamento de serviços."
}

cob = sicoob.criar_cob(txid="uuid-unico-2", body=payload_cob)
print(cob)
```

## Estrutura do Projeto

```
pypix_api/
├── auth/           # Autenticação (MTLS, OAuth2)
├── banks/          # Integrações com bancos (BB, Sicoob, métodos PIX)
├── models/         # Modelos de dados do PIX
├── utils/          # Utilitários (HTTP client, helpers)
tests/              # Testes automatizados
openapi.yaml        # Especificação OpenAPI (se aplicável)
pyproject.toml      # Configuração do projeto Python
Makefile            # Comandos úteis para desenvolvimento
.env.exemplo        # Exemplo de variáveis de ambiente
```

## Configuração

### Parâmetros de Inicialização

1. Primeiro crie uma instância de OAuth2Client:
```python
from pypix_api.auth.oauth2 import OAuth2Client

oauth = OAuth2Client(
    client_id="SEU_CLIENT_ID",       # ID do cliente fornecido pelo banco
    cert="caminho/do/certificado.pem",  # Certificado digital (.pem)
    pvk="caminho/da/chave.key"       # Chave privada (.key)
)
```

2. Depois instancie o banco passando o OAuth2Client:
```python
banco = BancoDoBrasil(oauth=oauth)  # Ou Sicoob(oauth=oauth)
```

### URLs das APIs

As URLs base são configuradas automaticamente por cada banco:

- **Banco do Brasil**: Definido internamente pela classe `BBPixAPI`
- **Sicoob**: Definido internamente pela classe `SicoobPixAPI`

Crie um arquivo `.env` baseado em `.env.exemplo` com as credenciais e configurações necessárias para autenticação e acesso às APIs bancárias.

## Testes

Para rodar os testes automatizados:

```bash
make test
```
ou diretamente com pytest:
```bash
pytest
```

## Contribuição

Contribuições são bem-vindas! Por favor, consulte nosso **[Guia de Contribuição](CONTRIBUTING.md)** para informações detalhadas sobre:

- Como configurar o ambiente de desenvolvimento
- Padrões de código e commits
- Processo de Pull Request
- Executar testes e verificações de qualidade

Para entender nossos templates e automações GitHub, veja **[.github/GITHUB_TEMPLATES.md](.github/GITHUB_TEMPLATES.md)**.

Passos rápidos:

1. Fork este repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -am 'feat: adiciona nova funcionalidade'`)
4. Execute os testes (`make quality-full`)
5. Push para a branch (`git push origin feature/nova-funcionalidade`)
6. Abra um Pull Request

## Segurança

Para reportar vulnerabilidades de segurança, consulte nossa **[Política de Segurança](SECURITY.md)**.

**NÃO** reporte vulnerabilidades através de issues públicos.

## Licença

Este projeto está licenciado sob os termos da licença MIT.
