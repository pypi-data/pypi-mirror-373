"""Protocol base para os métodos mixins do PIX API."""

from typing import Any, Protocol

import requests


class PixAPIProtocol(Protocol):
    """Protocol que define a interface esperada pelos métodos mixins."""

    session: requests.Session
    client_id: str | None
    sandbox_mode: bool
    oauth: Any  # OAuth2Client

    def _create_headers(self) -> dict[str, str]:
        """Cria os headers necessários para as requisições."""
        ...

    def get_base_url(self) -> str:
        """Obtém a URL base da API."""
        ...

    def get_bank_code(self) -> str:
        """Obtém o código do banco."""
        ...

    def _handle_error_response(
        self, response: requests.Response, **kwargs: Any
    ) -> None:
        """Trata respostas de erro da API."""
        ...
