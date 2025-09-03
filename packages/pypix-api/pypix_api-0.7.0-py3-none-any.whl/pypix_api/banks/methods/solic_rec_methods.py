"""
Módulo de métodos para operações de Solicitação de Confirmação de Recorrência (SolicRec) PIX.

Este módulo define a classe `SolicRecMethods`, que implementa métodos para criar, consultar e revisar
solicitações de confirmação de recorrência via API Pix. Deve ser herdada por classes que implementam
a interface de comunicação com bancos que suportam o recurso de SolicRec.

Requisitos:
    - A classe base deve fornecer os métodos auxiliares `_create_headers()` e `get_base_url()`.
    - Atributo `session` deve ser uma instância de requests.Session ou compatível.

Exemplo de uso:
    class MeuBancoPixAPI(SolicRecMethods):
        ...

    api = MeuBancoPixAPI(...)
    resposta = api.criar_solicrec({...})

"""

from typing import Any


class SolicRecMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de Solicitação de Confirmação de Recorrência PIX.
    Esta classe deve ser herdada pela classe BankPixAPIBase.
    """

    def criar_solicrec(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Cria uma solicitação de confirmação de recorrência (SolicRec) via API Pix.

        Parâmetros:
            body (dict): Dados da solicitação de confirmação de recorrência conforme especificação Pix.

        Retorna:
            dict: Dados da solicitação criada retornados pela API.

        Exceções:
            HTTPError: Em caso de erro na requisição HTTP.

        Exemplo:
            body = {
                "calendario": {"expiracao": 3600},
                "devedor": {"cpf": "12345678909", "nome": "Fulano"},
                ...
            }
            resposta = self.criar_solicrec(body)
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/solicrec'

        resp = self.session.post(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)

        return resp.json()

    def consultar_solicrec(self, id_solic_rec: str) -> dict[str, Any]:
        """
        Consulta uma solicitação de confirmação de recorrência (SolicRec) existente.

        Parâmetros:
            id_solic_rec (str): ID da solicitação de confirmação de recorrência.

        Retorna:
            dict: Dados da solicitação retornados pela API.

        Exceções:
            HTTPError: Em caso de erro na requisição HTTP.

        Exemplo:
            dados = self.consultar_solicrec("123e4567-e89b-12d3-a456-426614174000")
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/solicrec/{id_solic_rec}'

        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp, error_class=None)

        return resp.json()

    def revisar_solicrec(
        self, id_solic_rec: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Revisa uma solicitação de confirmação de recorrência (SolicRec) existente.

        Parâmetros:
            id_solic_rec (str): ID da solicitação de confirmação de recorrência.
            body (dict): Dados da revisão da solicitação conforme especificação Pix.

        Retorna:
            dict: Dados da solicitação atualizada retornados pela API.

        Exceções:
            HTTPError: Em caso de erro na requisição HTTP.

        Exemplo:
            body = {
                "status": "REJEITADA",
                "motivo": "Motivo da rejeição"
            }
            resposta = self.revisar_solicrec("123e4567-e89b-12d3-a456-426614174000", body)
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/solicrec/{id_solic_rec}'

        resp = self.session.patch(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)

        return resp.json()
