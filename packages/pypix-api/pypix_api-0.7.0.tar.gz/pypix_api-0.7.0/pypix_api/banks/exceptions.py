class PixAPIException(Exception):
    """Exceção base para erros da API Pix."""

    def __init__(self, type_: str, title: str, status: int, detail: str):
        self.type = type_
        self.title = title
        self.status = status
        self.detail = detail
        super().__init__(f'{title} ({status}): {detail} [{type_}]')


class PixAcessoNegadoException(PixAPIException):
    """Erro de acesso negado (403)."""


class PixRecursoNaoEncontradoException(PixAPIException):
    """Erro de recurso não encontrado (404)."""


class PixErroValidacaoException(PixAPIException):
    """Erro de validação (400)."""


class PixErroServicoIndisponivelException(PixAPIException):
    """Erro de serviço indisponível (503)."""


class PixErroDesconhecidoException(PixAPIException):
    """Erro desconhecido da API Pix."""


class PixRespostaInvalidaError(PixAPIException):
    """Erro quando a resposta da API não está no formato esperado"""
