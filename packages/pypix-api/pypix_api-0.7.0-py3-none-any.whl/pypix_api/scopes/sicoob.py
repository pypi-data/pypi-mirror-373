"""Definição de escopos para a API do Sicoob.

Este módulo contém as definições de escopos necessários para diferentes
funcionalidades da API do Sicoob, organizados por categoria.
"""

from pypix_api.scopes.base import BankScopesBase, ScopeGroup


class SicoobScopes(BankScopesBase):
    """Definição de escopos para a API do Sicoob."""

    # Informações do banco
    BANK_NAME = 'Sicoob'
    BANK_CODE = '756'
    BANK_CODES = ['756', 'sicoob']

    # Constantes para escopos
    SCOPE_COB_WRITE = 'cob.write'
    SCOPE_COB_READ = 'cob.read'
    SCOPE_COBV_WRITE = 'cobv.write'
    SCOPE_COBV_READ = 'cobv.read'
    SCOPE_LOTECOBV_WRITE = 'lotecobv.write'
    SCOPE_LOTECOBV_READ = 'lotecobv.read'
    SCOPE_PIX_WRITE = 'pix.write'
    SCOPE_PIX_READ = 'pix.read'
    SCOPE_WEBHOOK_READ = 'webhook.read'
    SCOPE_WEBHOOK_WRITE = 'webhook.write'
    SCOPE_PAYLOADLOCATION_WRITE = 'payloadlocation.write'
    SCOPE_PAYLOADLOCATION_READ = 'payloadlocation.read'

    # PIX - Funcionalidades relacionadas ao PIX
    PIX = ScopeGroup(
        name='pix',
        scopes=[
            SCOPE_COB_WRITE,
            SCOPE_COB_READ,
            SCOPE_COBV_WRITE,
            SCOPE_COBV_READ,
            SCOPE_LOTECOBV_WRITE,
            SCOPE_LOTECOBV_READ,
            SCOPE_PIX_WRITE,
            SCOPE_PIX_READ,
            SCOPE_WEBHOOK_READ,
            SCOPE_WEBHOOK_WRITE,
            SCOPE_PAYLOADLOCATION_WRITE,
            SCOPE_PAYLOADLOCATION_READ,
        ],
        description='Funcionalidades completas do PIX incluindo cobranças, webhooks e payload location',
    )

    # Subgrupos do PIX para uso mais granular
    PIX_COB = ScopeGroup(
        name='pix_cob',
        scopes=[SCOPE_COB_WRITE, SCOPE_COB_READ],
        description='Cobranças imediatas PIX',
    )

    PIX_COBV = ScopeGroup(
        name='pix_cobv',
        scopes=[SCOPE_COBV_WRITE, SCOPE_COBV_READ],
        description='Cobranças com vencimento PIX',
    )

    PIX_LOTE_COBV = ScopeGroup(
        name='pix_lote_cobv',
        scopes=[SCOPE_LOTECOBV_WRITE, SCOPE_LOTECOBV_READ],
        description='Lote de cobranças com vencimento PIX',
    )

    PIX_BASIC = ScopeGroup(
        name='pix_basic',
        scopes=[SCOPE_PIX_WRITE, SCOPE_PIX_READ],
        description='Operações básicas PIX',
    )

    PIX_WEBHOOK = ScopeGroup(
        name='pix_webhook',
        scopes=[SCOPE_WEBHOOK_READ, SCOPE_WEBHOOK_WRITE],
        description='Webhooks PIX',
    )

    PIX_PAYLOAD = ScopeGroup(
        name='pix_payload',
        scopes=[SCOPE_PAYLOADLOCATION_WRITE, SCOPE_PAYLOADLOCATION_READ],
        description='Payload location PIX',
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
        description='Funcionalidades completas de boleto bancário',
    )

    # Subgrupos do Boleto
    BOLETO_BASIC = ScopeGroup(
        name='boleto_basic',
        scopes=['boletos_inclusao', 'boletos_consulta', 'boletos_alteracao'],
        description='Operações básicas de boleto',
    )

    BOLETO_WEBHOOK = ScopeGroup(
        name='boleto_webhook',
        scopes=['webhooks_alteracao', 'webhooks_consulta', 'webhooks_inclusao'],
        description='Webhooks de boleto',
    )

    # Conta Corrente - Funcionalidades de conta corrente
    CONTA_CORRENTE = ScopeGroup(
        name='conta_corrente',
        scopes=['cco_consulta', 'cco_transferencias', 'openid'],
        description='Funcionalidades de conta corrente',
    )

    # Combinações comuns
    PIX_COMPLETO = ScopeGroup(
        name='pix_completo',
        scopes=PIX.scopes,
        description='Todas as funcionalidades PIX',
    )

    TODOS_ESCOPOS = ScopeGroup(
        name='todos',
        scopes=PIX.scopes + BOLETO.scopes + CONTA_CORRENTE.scopes,
        description='Todos os escopos disponíveis',
    )

    @classmethod
    def get_pix_scopes(cls) -> ScopeGroup:
        """Retorna os escopos PIX do Sicoob."""
        return cls.PIX

    @classmethod
    def get_scope_group(cls, name: str) -> ScopeGroup:
        """Obtém um grupo de escopos pelo nome.

        Args:
            name: Nome do grupo de escopos

        Returns:
            ScopeGroup: Grupo de escopos correspondente

        Raises:
            AttributeError: Se o grupo não existir
        """
        return getattr(cls, name.upper())

    @classmethod
    def list_available_groups(cls) -> list[str]:
        """Lista todos os grupos de escopos disponíveis."""
        return [
            attr
            for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), ScopeGroup)
        ]

    @classmethod
    def combine_scopes(cls, *groups: ScopeGroup) -> str:
        """Combina múltiplos grupos de escopos em uma string.

        Args:
            *groups: Grupos de escopos a serem combinados

        Returns:
            str: Escopos combinados separados por espaço
        """
        all_scopes = []
        for group in groups:
            all_scopes.extend(group.scopes)
        # Remove duplicatas mantendo a ordem
        unique_scopes = list(dict.fromkeys(all_scopes))
        return ' '.join(unique_scopes)
