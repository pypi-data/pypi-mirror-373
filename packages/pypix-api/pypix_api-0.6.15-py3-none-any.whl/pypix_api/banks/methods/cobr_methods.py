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
        """Criar cobrança recorrente com txid específico."""
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr/{txid}'
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def revisar_cobr(self, txid: str, body: dict[str, Any]) -> dict[str, Any]:
        """Revisar cobrança recorrente."""
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr/{txid}'
        resp = self.session.patch(url, headers=headers, json=body)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def consultar_cobr(self, txid: str) -> dict[str, Any]:
        """Consultar cobrança recorrente através de um determinado txid."""
        headers = self._create_headers()
        url = f'{self.get_base_url()}/cobr/{txid}'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def criar_cobr(self, body: dict[str, Any]) -> dict[str, Any]:
        """Criar cobrança recorrente, onde o txid é definido pelo PSP."""
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
        """Consultar lista de cobranças recorrentes através de parâmetros."""
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
            params['paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp, error_class=None)
        return resp.json()

    def solicitar_retentativa_cobr(self, txid: str, data: date) -> dict[str, Any]:
        """Solicitar retentativa de uma cobrança recorrente."""
        headers = self._create_headers()
        data_str = data.strftime('%Y-%m-%d')
        url = f'{self.get_base_url()}/cobr/{txid}/retentativa/{data_str}'
        resp = self.session.post(url, headers=headers)
        self._handle_error_response(resp, error_class=None)
        return resp.json()
