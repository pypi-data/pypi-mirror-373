"""
pypix_api.banks.lotecobv_methods
-------------------------------

Este módulo implementa a classe `LoteCobVMethods`, que fornece métodos para operações
de lotes de cobrança com vencimento (LoteCobV) do PIX, conforme especificação do
Banco Central do Brasil.

A classe `LoteCobVMethods` é utilizada como base para integração com APIs bancárias
que suportam o PIX, permitindo criar, alterar, consultar e listar lotes de cobranças
com vencimento. Os métodos abstraem detalhes de requisições HTTP, tratamento de erros
e montagem de parâmetros, facilitando a integração de sistemas Python com provedores
bancários.

Principais funcionalidades:
- Criação de lote de cobrança com vencimento
- Alteração de lote de cobrança com vencimento
- Consulta de lote por ID
- Consulta de múltiplos lotes por período e filtros

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil, Sicoob).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    class MeuBanco(LoteCobVMethods):
        ...

    banco = MeuBanco()
    lote = banco.criar_lote_cobv("lote123", {...})
    consulta = banco.consultar_lote_cobv("lote123")

"""

from typing import Any


class LoteCobVMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de lote de cobrança com vencimento (LoteCobV) do PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def criar_lote_cobv(self, id_lote: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Criar lote de cobranças com vencimento.

        Endpoint para criar um lote de cobranças com vencimento com um ID específico.

        Args:
            id_lote: Identificador do lote de cobranças com vencimento
            body: Dados do lote contendo:
                - descricao (str): Descrição do lote de cobranças
                - cobsv (list): Array de cobranças com vencimento

        Returns:
            dict contendo os dados do lote criado com status HTTP 202 (Accepted)

        Raises:
            HTTPError: Para erros 400, 403, 404, 503

        Note:
            Este endpoint retorna status 202 (Accepted) pois a criação do lote
            é processada de forma assíncrona.
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/lotecobv/{id_lote}'
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def alterar_lote_cobv(self, id_lote: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Alterar lote de cobranças com vencimento.

        Endpoint para alterar um lote de cobranças com vencimento existente.
        O array a ser atribuído na requisição deve ser composto pelas exatas
        requisições de criação de cobranças que constaram no array atribuído
        na requisição originária.

        Args:
            id_lote: Identificador do lote de cobranças com vencimento
            body: Dados do lote revisado contendo:
                - descricao (str): Descrição do lote de cobranças
                - cobsv (list): Array de cobranças com vencimento

        Returns:
            dict contendo os dados do lote alterado com status HTTP 202 (Accepted)

        Raises:
            HTTPError: Para erros 400, 403, 404, 503

        Note:
            Uma vez criado um lote, não se pode remover ou adicionar cobranças
            a este lote. Apenas alterações nas cobranças existentes são permitidas.
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/lotecobv/{id_lote}'
        resp = self.session.patch(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_lote_cobv(self, id_lote: str) -> dict[str, Any]:
        """
        Consultar lote de cobranças com vencimento.

        Endpoint para consultar um lote de cobranças com vencimento através de um ID específico.

        Args:
            id_lote: Identificador do lote de cobranças com vencimento

        Returns:
            dict contendo os dados do lote de cobranças com vencimento

        Raises:
            HTTPError: Para erros 403, 404, 503

        Note:
            Para cada elemento do array `cobsv` retornado, caso a requisição de
            criação de cobrança esteja em status "NEGADA", o atributo `problema`
            será preenchido com detalhes do erro.
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/lotecobv/{id_lote}'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()

    def listar_lotes_cobv(
        self,
        inicio: str,
        fim: str,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar lista de lotes de cobranças com vencimento.

        Endpoint para consultar lotes de cobranças com vencimento através de parâmetros
        como início e fim de período.

        Args:
            inicio: Data de início da consulta (formato ISO)
            fim: Data de fim da consulta (formato ISO)
            pagina_atual: Página atual para paginação (padrão: 0)
            itens_por_pagina: Quantidade de itens por página (padrão: 100)

        Returns:
            dict contendo a lista de lotes de cobranças com vencimento

        Raises:
            HTTPError: Para erros 403, 503
            ValueError: Se a data fim for anterior à data início

        Note:
            Os parâmetros de paginação são opcionais. Se não informados,
            serão utilizados os valores padrão do PSP.
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/lotecobv'
        params = {'inicio': inicio, 'fim': fim}

        # Adiciona parâmetros opcionais se fornecidos
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()
