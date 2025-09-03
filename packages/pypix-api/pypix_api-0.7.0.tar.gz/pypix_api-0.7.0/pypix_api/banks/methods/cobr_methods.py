"""
pypix_api.banks.cobr_methods
----------------------------

Este módulo fornece métodos para operações com cobranças recorrentes (CobR) via API Pix.

Funcionalidades principais:
- Criação de cobranças recorrentes com txid específico ou gerado pelo PSP.
- Revisão de cobranças recorrentes existentes.
- Consulta de cobranças recorrentes por txid.
- Listagem de cobranças recorrentes com filtros por período, status, CPF/CNPJ, entre outros.
- Solicitação de retentativa de cobrança em data específica.

As operações utilizam autenticação e comunicação HTTP com o PSP, sendo necessário fornecer os parâmetros exigidos por cada método.

Classes:
    CobRMethods: Implementa os métodos para manipulação de cobranças recorrentes.

Exemplo de uso:
    cobr_methods = CobRMethods()
    cobr_methods.criar_cobr({...})

"""

from datetime import date
from typing import Any


class CobRMethods:  # pylint: disable=E1101
    """Métodos para operações com cobranças recorrentes (CobR)."""

    def criar_cobr_com_txid(self, txid: str, body: dict[str, Any]) -> dict[str, Any]:
        """Criar cobrança recorrente com txid específico.

        Args:
            txid: Identificador da transação
            body: Dados da cobrança recorrente

        Returns:
            dict contendo os dados da cobrança criada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr/{txid}'
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def revisar_cobr(self, txid: str, body: dict[str, Any]) -> dict[str, Any]:
        """Revisar cobrança recorrente.

        Args:
            txid: Identificador da transação
            body: Dados para revisão da cobrança

        Returns:
            dict contendo os dados da cobrança revisada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr/{txid}'
        resp = self.session.patch(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def consultar_cobr(self, txid: str) -> dict[str, Any]:
        """Consultar cobrança recorrente através de um determinado txid.

        Args:
            txid: Identificador da transação

        Returns:
            dict contendo os dados da cobrança

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr/{txid}'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def criar_cobr(self, body: dict[str, Any]) -> dict[str, Any]:
        """Criar cobrança recorrente, onde o txid é definido pelo PSP.

        Args:
            body: Dados da cobrança recorrente

        Returns:
            dict contendo os dados da cobrança criada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr'
        resp = self.session.post(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def consultar_lista_cobr(
        self,
        inicio: str,
        fim: str,
        id_rec: str | None = None,
        cpf: str | None = None,
        cnpj: str | None = None,
        status: str | None = None,
        convenio: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """Consultar lista de cobranças recorrentes através de parâmetros.

        Args:
            inicio: Data e hora de início da consulta (formato ISO 8601)
            fim: Data e hora de fim da consulta (formato ISO 8601)
            id_rec: Identificador da recorrência (opcional)
            cpf: CPF do usuário recebedor (opcional)
            cnpj: CNPJ do usuário recebedor (opcional)
            status: Status da cobrança (opcional)
            convenio: Convênio usado na cobrança (opcional)
            pagina_atual: Página atual para paginação (opcional)
            itens_por_pagina: Quantidade de itens por página (opcional)

        Returns:
            dict contendo a lista de cobranças recorrentes

        Raises:
            ValueError: Se CPF e CNPJ forem fornecidos simultaneamente
            HTTPError: Para erros 400, 403, 404, 503
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr'

        params = {'inicio': inicio, 'fim': fim}

        # Adicionar parâmetros opcionais se fornecidos
        if id_rec is not None:
            params['idRec'] = id_rec
        if cpf is not None:
            params['cpf'] = cpf
        if cnpj is not None:
            params['cnpj'] = cnpj
        if status is not None:
            params['status'] = status
        if convenio is not None:
            params['convenio'] = convenio
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def solicitar_retentativa_cobr(self, txid: str, data: date) -> dict[str, Any]:
        """Solicitar retentativa de uma cobrança recorrente.

        Args:
            txid: Identificador da transação
            data: Data para a retentativa (formato date)

        Returns:
            dict contendo o resultado da solicitação

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        data_str = data.strftime('%Y-%m-%d')
        url = f'{self.get_base_url()}/cobr/{txid}/retentativa/{data_str}'
        resp = self.session.post(url, headers=headers)
        self._handle_error_response(resp, error_class=None)
        return resp.json()
