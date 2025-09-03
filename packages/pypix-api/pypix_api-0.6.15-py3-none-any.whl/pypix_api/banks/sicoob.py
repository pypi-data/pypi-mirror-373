from pypix_api.banks.base import BankPixAPIBase


class SicoobPixAPI(BankPixAPIBase):
    """Implementação da API PIX do Sicoob.

    Args:
        oauth: Instância configurada de OAuth2Client para autenticação
        sandbox_mode: Se True, usa ambiente de sandbox (default: False)

    Attributes:
        BASE_URL: URL da API de produção
        SANDBOX_BASE_URL: URL da API de sandbox
        TOKEN_URL: URL para obtenção de token OAuth2
        SCOPES: Scopes necessários para autenticação
    """

    BASE_URL = 'https://api.sicoob.com.br/pix/api/v2'
    SANDBOX_BASE_URL = 'https://sandbox.sicoob.com.br/sicoob/sandbox/pix/api/v2'
    TOKEN_URL = (
        'https://auth.sicoob.com.br/auth/realms/cooperado/protocol/openid-connect/token'  # noqa: S105
    )

    def get_bank_code(self) -> str:
        return '756'

    def get_base_url(self) -> str:
        """Obtém a URL base da API de acordo com o modo de operação.

        Returns:
            str: URL base da API (produção ou sandbox)

        Note:
            O modo sandbox é controlado pelo parâmetro sandbox_mode passado no construtor
        """
        if self.sandbox_mode:
            return self.SANDBOX_BASE_URL
        return self.BASE_URL
