"""
pypix_api.banks.webhook_cobr_methods
---------------------------

Este módulo implementa a classe `WebHookCobrMethods`, que fornece métodos para operações de webhook de cobrança recorrente do PIX, conforme especificação do Banco Central do Brasil.

A classe `WebHookCobrMethods` é utilizada como base para integração com APIs bancárias que suportam o PIX, permitindo configurar webhooks para notificações de cobranças recorrentes. Os métodos abstraem detalhes de requisições HTTP, tratamento de erros e montagem de parâmetros, facilitando a integração de sistemas Python com provedores bancários.

Principais funcionalidades:
- Configuração de webhook para notificações de cobranças recorrentes
- Consulta de webhook configurado
- Cancelamento de webhook

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil, Sicoob).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    class MeuBanco(WebHookCobrMethods):
        ...

    banco = MeuBanco()
    resposta = banco.configurar_webhook_cobr(webhook_url="https://...")
"""

from typing import Any


class WebHookCobrMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de webhook de cobrança recorrente do PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def configurar_webhook_cobr(self, webhook_url: str) -> dict[str, Any]:
        """
        Configurar o Webhook de Cobrança Recorrente.

        Endpoint para configuração do serviço de notificações acerca de cobranças recorrentes.
        Somente cobranças associadas ao usuário recebedor serão notificadas.

        Args:
            webhook_url: URL do webhook para notificações (ex: "https://example.com/api/webhookcobr/")

        Returns:
            dict contendo os dados da configuração do webhook

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/webhookcobr'
        body = {'webhookUrl': webhook_url}
        resp = self.session.put(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_webhook_cobr(self) -> dict[str, Any]:
        """
        Consultar informações do Webhook de Cobrança Recorrente.

        Endpoint para recuperação de informações sobre o Webhook configurado.

        Returns:
            dict contendo as informações do webhook (incluindo URL e data de criação)

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/webhookcobr'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()

    def excluir_webhook_cobr(self) -> bool:
        """
        Cancelar o Webhook de Cobrança Recorrente.

        Endpoint para cancelamento do webhook. Não é a única forma pela qual um webhook pode ser removido.

        Returns:
            bool: True se o webhook foi excluído com sucesso (status 204), False caso contrário

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/webhookcobr'
        resp = self.session.delete(url, headers=headers)
        self._handle_error_response(resp)
        return resp.status_code == 204
