from pypix_api.banks.base import BankPixAPIBase


class BBPixAPI(BankPixAPIBase):
    """Implementação da API PIX do Banco do Brasil.

    Args:
        oauth: Instância configurada de OAuth2Client para autenticação
        sandbox_mode: Se True, usa ambiente de sandbox (default: False)

    Attributes:
        BASE_URL: URL da API de produção
        SANDBOX_BASE_URL: URL da API de sandbox
        TOKEN_URL: URL para obtenção de token OAuth2
        SCOPES: Scopes necessários para autenticação
    """

    BASE_URL = 'https://api.bb.com.br/pix/v1'
    SANDBOX_BASE_URL = 'https://api.sandbox.bb.com.br/pix/v1'
    TOKEN_URL = 'https://oauth.bb.com.br/oauth/token'  # noqa: S105

    def get_bank_code(self) -> str:
        return '001'

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
