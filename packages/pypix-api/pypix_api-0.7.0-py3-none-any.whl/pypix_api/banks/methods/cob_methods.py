"""
pypix_api.banks.cob_methods
---------------------------

Este módulo implementa a classe `CobMethods`, que fornece métodos para operações de cobrança imediata (COB) do PIX, conforme especificação do Banco Central do Brasil.

A classe `CobMethods` é utilizada como base para integração com APIs bancárias que suportam o PIX, permitindo criar, revisar, consultar e listar cobranças imediatas. Os métodos abstraem detalhes de requisições HTTP, tratamento de erros e montagem de parâmetros, facilitando a integração de sistemas Python com provedores bancários.

Principais funcionalidades:
- Criação de cobrança imediata (com txid definido ou automático)
- Revisão de cobrança existente
- Consulta de cobrança por txid
- Consulta de múltiplas cobranças por período e filtros

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil, Sicoob).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    class MeuBanco(CobMethods):
        ...

    banco = MeuBanco()
    resposta = banco.criar_cob(txid="meu-txid", body={...})

"""

from typing import Any


class CobMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de cobrança imediata (COB) do PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def criar_cob(self, txid: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Criar cobrança imediata com txid específico.

        Endpoint para criar uma cobrança imediata com um txid definido.

        Args:
            txid: Identificador da transação
            body: Dados da cobrança imediata

        Returns:
            dict contendo os dados da cobrança criada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cob/{txid}'
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def criar_cob_auto_txid(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Criar cobrança imediata com txid automático.

        Endpoint para criar uma cobrança imediata onde o txid é definido pelo PSP.

        Args:
            body: Dados da cobrança imediata

        Returns:
            dict contendo os dados da cobrança criada

        Raises:
            HTTPError: Para erros 400, 403, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cob'
        resp = self.session.post(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def revisar_cob(self, txid: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Revisar cobrança imediata.

        Endpoint para revisar uma cobrança imediata existente.
        A revisão deve ser incrementada em 1.

        Args:
            txid: Identificador da transação
            body: Dados da cobrança revisada

        Returns:
            dict contendo os dados da cobrança revisada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cob/{txid}'
        resp = self.session.patch(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_cob(self, txid: str, revisao: int | None = None) -> dict[str, Any]:
        """
        Consultar cobrança imediata.

        Endpoint para consultar uma cobrança através de um determinado txid.

        Args:
            txid: Identificador da transação
            revisao: Número da revisão (opcional)

        Returns:
            dict contendo os dados da cobrança

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cob/{txid}'
        params = {}

        if revisao is not None:
            params['revisao'] = revisao

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_cobs(
        self,
        inicio: str,
        fim: str,
        cpf: str | None = None,
        cnpj: str | None = None,
        location_presente: bool | None = None,
        status: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar lista de cobranças imediatas.

        Endpoint para consultar cobranças imediatas através de parâmetros como
        início, fim, cpf, cnpj e status.

        Args:
            inicio: Data de início da consulta (formato ISO)
            fim: Data de fim da consulta (formato ISO)
            cpf: CPF do devedor (11 dígitos). Não pode ser usado com CNPJ
            cnpj: CNPJ do devedor (14 dígitos). Não pode ser usado com CPF
            location_presente: Filtro por presença de location
            status: Status da cobrança para filtro
            pagina_atual: Página atual para paginação
            itens_por_pagina: Quantidade de itens por página

        Returns:
            dict contendo a lista de cobranças

        Raises:
            HTTPError: Para erros 403, 503
            ValueError: Se CPF e CNPJ forem informados simultaneamente
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        headers = self._create_headers()
        url = f'{self.get_base_url()}/cob'
        params = {'inicio': inicio, 'fim': fim}

        # Adiciona parâmetros opcionais se fornecidos
        if cpf:
            params['cpf'] = cpf
        if cnpj:
            params['cnpj'] = cnpj
        if location_presente is not None:
            params['locationPresente'] = str(location_presente).lower()
        if status:
            params['status'] = status
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()
