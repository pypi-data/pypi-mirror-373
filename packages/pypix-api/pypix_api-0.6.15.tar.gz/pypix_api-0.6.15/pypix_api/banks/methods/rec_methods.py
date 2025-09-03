"""
Módulo para métodos de recorrência da API Pix.

Este módulo implementa os métodos relacionados ao gerenciamento de recorrências
conforme especificado na API OpenAPI. Inclui operações para:
- Criar recorrências
- Consultar recorrência específica
- Revisar recorrências existentes
- Listar recorrências com filtros

Classes:
    RecMethods: Classe base com métodos para operações de recorrência
"""

from typing import Any


class RecMethods:  # pylint: disable=E1101
    """
    Classe que implementa métodos para operações de recorrência da API Pix.

    Esta classe fornece métodos para gerenciar recorrências, incluindo criação,
    consulta, revisão e listagem de recorrências com diversos filtros disponíveis.
    """

    def criar_recorrencia(self, id_rec: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Criar uma nova recorrência.
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/rec/{id_rec}'
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def revisar_recorrencia(self, id_rec: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Revisar uma recorrência existente.
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/rec/{id_rec}'
        resp = self.session.patch(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def consultar_recorrencia(
        self, id_rec: str, txid: str | None = None
    ) -> dict[str, Any]:
        """
        Consultar uma recorrência específica.
        """
        headers = self._create_headers()
        params = {}
        if txid:
            params['txid'] = txid
        url = f'{self.get_base_url()}/rec/{id_rec}'
        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def listar_recorrencias(
        self,
        inicio: str,
        fim: str,
        cpf: str | None = None,
        cnpj: str | None = None,
        location_presente: bool | None = None,
        status: str | None = None,
        convenio: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar lista de recorrências com filtros.
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        headers = self._create_headers()
        params = {'inicio': inicio, 'fim': fim}
        if cpf:
            params['cpf'] = cpf
        if cnpj:
            params['cnpj'] = cnpj
        if location_presente is not None:
            params['locationPresente'] = str(location_presente).lower()
        if status:
            params['status'] = status
        if convenio:
            params['convenio'] = convenio
        if pagina_atual is not None:
            params['paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['itensPorPagina'] = str(itens_por_pagina)

        url = f'{self.get_base_url()}/rec'
        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()

    def solicitar_retentativa_cobranca(self, txid: str, data: str) -> dict[str, Any]:
        """
        Solicitar retentativa de cobrança recorrente.

        Args:
            txid (str): Id da transação
            data (str): Data prevista para liquidação da ordem de pagamento
                    no formato YYYY-MM-DD segundo ISO 8601

        Returns:
            dict[str, Any]: Dados completos da cobrança recorrente

        Raises:
            ValueError: Se a data não estiver no formato correto
            HTTPError: Para códigos de erro HTTP (400, 403, 404, 503)
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/rec/{txid}/{data}'
        resp = self.session.post(url, headers=headers)
        self._handle_error_response(resp, error_class=None)
        return resp.json()
