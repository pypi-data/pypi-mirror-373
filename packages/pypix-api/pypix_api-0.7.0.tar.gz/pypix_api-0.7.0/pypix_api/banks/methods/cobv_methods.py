"""
Módulo cobv_methods.py

Este módulo define a classe CobVMethods, que implementa métodos para
  integração com cobranças Pix com vencimento (CobV) via API bancária.
Inclui operações para criar, revisar, consultar e listar cobranças com vencimento,
  utilizando autenticação OAuth2 e requisições HTTP.

Principais funcionalidades:
- Criação de cobrança com vencimento (CobV)
- Revisão de cobrança com vencimento
- Consulta de cobrança por txid
- Listagem de cobranças por período e filtros

Dependências:
- OAuth2 para autenticação (self.oauth)
- Cliente HTTP de sessão (self.session)
- Python 3.10+ (tipos nativos)

Autor: [Fabio Thomaz(fabio@ladder.dev.br)]
"""

from typing import Any


class CobVMethods:  # pylint: disable=E1101
    """
    Métodos para lidar com cobrança Pix com vencimento (CobV).
    """

    def criar_cobv(self, txid: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Cria uma cobrança com vencimento (CobV).
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobv/{txid}'
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def revisar_cobv(self, txid: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Revisa uma cobrança com vencimento (CobV).
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobv/{txid}'
        resp = self.session.patch(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_cobv(self, txid: str, revisao: int | None) -> dict[str, Any]:
        """
        Consulta uma cobrança com vencimento (CobV) por txid.
        """
        headers = self._create_headers()
        params = {}
        if revisao is not None:
            params['revisao'] = revisao
        url = f'{self.get_base_url()}/cobv/{txid}'
        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()

    def listar_cobv(
        self,
        inicio: str,
        fim: str,
        cpf: str | None = None,
        cnpj: str | None = None,
        location_presente: bool | None = None,
        status: str | None = None,
        lote_cob_v_id: int | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consulta lista de cobranças com vencimento (CobV).
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
        if lote_cob_v_id is not None:
            params['loteCobVId'] = str(lote_cob_v_id)
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        url = f'{self.get_base_url()}/cobv'
        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()
