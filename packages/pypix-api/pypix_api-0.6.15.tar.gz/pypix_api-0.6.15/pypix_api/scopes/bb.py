"""Definição de escopos para a API do Banco do Brasil."""

from pypix_api.scopes.base import BankScopesBase, ScopeGroup


class BBScopes(BankScopesBase):
    """Definição de escopos para a API do Banco do Brasil."""

    # Informações do banco
    BANK_NAME = 'Banco do Brasil'
    BANK_CODE = '001'
    BANK_CODES = ['001', 'bb', 'banco_do_brasil']

    # PIX - Funcionalidades relacionadas ao PIX
    PIX = ScopeGroup(
        name='pix',
        scopes=['pix.read', 'pix.write'],
        description='Funcionalidades do PIX do Banco do Brasil',
    )

    # Conta Corrente - Funcionalidades de conta corrente
    CONTA_CORRENTE = ScopeGroup(
        name='conta_corrente',
        scopes=['cco_extrato', 'cco_consulta'],
        description='Funcionalidades de conta corrente',
    )

    # Boleto - Funcionalidades de boleto bancário
    BOLETO = ScopeGroup(
        name='boleto',
        scopes=[
            'boletos_inclusao',
            'boletos_consulta',
            'boletos_alteracao',
            'webhooks_alteracao',
            'webhooks_consulta',
            'webhooks_inclusao',
        ],
        description='Funcionalidades de boleto bancário',
    )

    @classmethod
    def get_pix_scopes(cls) -> ScopeGroup:
        """Retorna os escopos PIX do Banco do Brasil."""
        return cls.PIX
