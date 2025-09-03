"""
pypix_api.banks.pix_methods
---------------------------

Este módulo implementa a classe `PixMethods`, que fornece métodos para operações de PIX, conforme especificação do Banco Central do Brasil.

A classe `PixMethods` é utilizada como base para integração com APIs bancárias que suportam o PIX, permitindo consultar PIX recebidos e outras operações relacionadas. Os métodos abstraem detalhes de requisições HTTP, tratamento de erros e montagem de parâmetros, facilitando a integração de sistemas Python com provedores bancários.

Principais funcionalidades:
- Consulta de PIX recebidos por período e filtros
- Consulta de PIX individual por e2eid
- Solicitação de devolução de PIX
- Consulta de devolução de PIX

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil, Sicoob).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    class MeuBanco(PixMethods):
        ...

    banco = MeuBanco()
    resposta = banco.consultar_pix(inicio="2023-01-01T00:00:00Z", fim="2023-01-31T23:59:59Z")
    pix_individual = banco.consultar_pix_por_e2eid("E12345678202301011200abcdef123456")
    devolucao = banco.solicitar_devolucao_pix("E12345678202301011200abcdef123456", "devolucao123", {"valor": "100.00"})
    consulta_devolucao = banco.consultar_devolucao_pix("E12345678202301011200abcdef123456", "devolucao123")

"""

from typing import Any


class PixMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def consultar_pix(
        self,
        inicio: str,
        fim: str,
        txid: str | None = None,
        txid_presente: bool | None = None,
        devolucao_presente: bool | None = None,
        cpf: str | None = None,
        cnpj: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar PIX recebidos.

        Endpoint para consultar PIX recebidos através de parâmetros como
        início, fim, txid, cpf, cnpj e outros filtros.

        Args:
            inicio: Data de início da consulta (formato ISO)
            fim: Data de fim da consulta (formato ISO)
            txid: Identificador da transação (opcional)
            txid_presente: Filtro por presença de txid (opcional)
            devolucao_presente: Filtro por presença de devolução (opcional)
            cpf: CPF do devedor (11 dígitos). Não pode ser usado com CNPJ
            cnpj: CNPJ do devedor (14 dígitos). Não pode ser usado com CPF
            pagina_atual: Página atual para paginação (padrão: 0)
            itens_por_pagina: Quantidade de itens por página (padrão: 100)

        Returns:
            dict contendo a lista de PIX recebidos

        Raises:
            HTTPError: Para erros 403, 503
            ValueError: Se CPF e CNPJ forem informados simultaneamente
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        headers = self._create_headers()
        url = f'{self.get_base_url()}/pix'
        params = {'inicio': inicio, 'fim': fim}

        # Adiciona parâmetros opcionais se fornecidos
        if txid:
            params['txid'] = txid
        if txid_presente is not None:
            params['txIdPresente'] = str(txid_presente).lower()
        if devolucao_presente is not None:
            params['devolucaoPresente'] = str(devolucao_presente).lower()
        if cpf:
            params['cpf'] = cpf
        if cnpj:
            params['cnpj'] = cnpj
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_pix_por_e2eid(self, e2eid: str) -> dict[str, Any]:
        """
        Consultar PIX individual.

        Endpoint para consultar um PIX através de um e2eid específico.

        Args:
            e2eid: Identificador end-to-end da transação PIX

        Returns:
            dict contendo os dados do PIX

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/pix/{e2eid}'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()

    def solicitar_devolucao_pix(
        self, e2eid: str, id_devolucao: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Solicitar devolução de PIX.

        Endpoint para solicitar uma devolução através de um e2eid do PIX e do ID da devolução.
        O motivo que será atribuído à PACS.004 será "MD06" ou "SL02" de acordo com a natureza
        da devolução.

        Args:
            e2eid: Identificador end-to-end da transação PIX
            id_devolucao: Identificador único da devolução
            body: Dados para pedido de devolução contendo:
                - valor (str): Valor solicitado para devolução (formato: \\d{1,10}\\.\\d{2})
                - natureza (str, opcional): Natureza da devolução ("ORIGINAL" ou "RETIRADA")
                - descricao (str, opcional): Mensagem ao pagador (máx. 140 caracteres)

        Returns:
            dict contendo os dados da devolução solicitada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503

        Note:
            Naturezas da devolução:
            - ORIGINAL: devolução de PIX comum ou valor da compra em PIX Troco (MD06)
            - RETIRADA: devolução de PIX Saque ou valor do troco em PIX Troco (SL02)

            A soma dos valores de todas as devoluções não pode ultrapassar o valor total do PIX.
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/pix/{e2eid}/devolucao/{id_devolucao}'
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_devolucao_pix(self, e2eid: str, id_devolucao: str) -> dict[str, Any]:
        """
        Consultar devolução de PIX.

        Endpoint para consultar uma devolução através de um End To End ID do PIX
        e do ID da devolução.

        Args:
            e2eid: Identificador end-to-end da transação PIX
            id_devolucao: Identificador único da devolução

        Returns:
            dict contendo os dados da devolução

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/pix/{e2eid}/devolucao/{id_devolucao}'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()
