#!/usr/bin/env python3
"""
Demo de observabilidade da pypix-api.

Este script demonstra como usar o sistema completo de observabilidade
incluindo logging estruturado, metricas e tratamento avancado de erros.
"""

import time
import uuid
from typing import Any

# Imports da pypix-api com observabilidade
from pypix_api import (
    BBPixAPI,
    OAuth2Client,
    configure_observability,
    get_metrics_summary,
    get_observability_status,
)
from pypix_api.error_handling import (
    APIError,
    AuthenticationError,
    ErrorContext,
    ErrorRecovery,
    ValidationError,
)
from pypix_api.observability import ObservabilityMixin


class DemoBBAPI(BBPixAPI, ObservabilityMixin):
    """Exemplo de API do BB com observabilidade completa."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize with full observability."""
        super().__init__(*args, **kwargs)
        self.bank_name = 'BB'  # Para metricas

    def criar_cobranca_demo(self, txid: str, dados: dict):
        """Criar cobranca com observabilidade completa."""

        with self.observe_operation('criar_cobranca', txid=txid):
            # Simulacao de validacao
            with ErrorContext('validacao', {'txid': txid}):
                if not dados.get('valor'):
                    raise ValidationError('Valor obrigatorio', field='valor')

            # Simulacao de autenticacao
            with self.observe_operation('autenticacao'):
                self._simular_autenticacao()

            # Simulacao de chamada API
            with self.observe_api_call('POST', f'/cob/{txid}'):
                return self._simular_api_call(txid, dados)

    def _simular_autenticacao(self):
        """Simula processo de autenticacao."""
        import random

        # Simula latencia
        time.sleep(random.uniform(0.1, 0.5))

        # Simula falha ocasional
        if random.random() < 0.1:  # 10% chance de falha
            raise AuthenticationError('Token expirado')

        return 'jwt_token_123'

    def _simular_api_call(self, txid: str, dados: dict):
        """Simula chamada para API do banco."""
        import random

        # Simula latencia variavel
        time.sleep(random.uniform(0.2, 1.0))

        # Simula diferentes cenarios
        rand = random.random()

        if rand < 0.05:  # 5% - Erro de rede
            raise APIError('Timeout na conexao', status_code=500)
        elif rand < 0.1:  # 5% - Rate limit
            raise APIError('Rate limit excedido', status_code=429)
        elif rand < 0.15:  # 5% - Dados invalidos
            raise ValidationError('CPF invalido', field='devedor.cpf')

        # Sucesso
        return {
            'txid': txid,
            'status': 'ATIVA',
            'pixCopiaECola': f'00020126{len(txid):02d}{txid}5204000053039865802BR',
            'valor': dados.get('valor', {}),
            'devedor': dados.get('devedor', {}),
        }


def main():
    """Demonstracao completa de observabilidade."""

    print('🚀 Demonstracao de Observabilidade pypix-api')
    print('=' * 50)

    # 1. Configurar observabilidade
    print('\n1️⃣ Configurando observabilidade...')
    configure_observability(
        {
            'log_level': 'INFO',
            'log_format': 'text',  # Para demo, usar formato legivel
            'metrics_enabled': True,
            'error_reporting': True,
            'performance_threshold': 1.0,
        }
    )

    # 2. Verificar status do sistema
    print('\n2️⃣ Verificando status do sistema...')
    status = get_observability_status()
    print(
        f'Status geral: {status["status"]} ({"✅" if status["status"] == "healthy" else "❌"})'
    )

    for check, result in status['checks'].items():
        emoji = '✅' if result['healthy'] else '❌'
        print(f'  {emoji} {check}: {result.get("note", "OK")}')

    # 3. Criar instancia da API com observabilidade
    print('\n3️⃣ Inicializando API com observabilidade...')

    # Configuracao simulada (usar suas credenciais reais)
    oauth = OAuth2Client(
        client_id='demo_client_id',
        client_secret='demo_client_secret',
        cert_path='/fake/path/cert.p12',
        cert_password='fake_password',
        scope='cob.write cob.read',
    )

    api = DemoBBAPI(oauth=oauth, sandbox_mode=True)

    # 4. Executar operacoes com observabilidade
    print('\n4️⃣ Executando operacoes com observabilidade...')

    sucessos = 0
    erros = 0

    # Executar multiplas operacoes para gerar metricas
    for i in range(10):
        txid = f'DEMO-{uuid.uuid4().hex[:8].upper()}'

        dados_cobranca = {
            'calendario': {'expiracao': 3600},
            'devedor': {'cpf': '12345678901', 'nome': f'Cliente Demo {i + 1}'},
            'valor': {'original': f'{(i + 1) * 10}.50'},
            'chave': 'demo@empresa.com',
            'solicitacaoPagador': f'Demo cobranca #{i + 1}',
        }

        try:
            resultado = api.criar_cobranca_demo(txid, dados_cobranca)
            print(f'  ✅ Cobranca {i + 1}: {resultado["txid"]} - {resultado["status"]}')
            sucessos += 1

        except ValidationError as e:
            print(f'  ❌ Cobranca {i + 1}: Validacao - {e.message}')
            erros += 1

        except AuthenticationError as e:
            print(f'  🔐 Cobranca {i + 1}: Autenticacao - {e.message}')
            erros += 1

        except APIError as e:
            status_code = e.details.get('status_code', 'N/A')
            print(f'  🌐 Cobranca {i + 1}: API {status_code} - {e.message}')
            erros += 1

        except Exception as e:
            print(f'  💥 Cobranca {i + 1}: Erro inesperado - {e}')
            erros += 1

        # Pequena pausa entre operacoes
        time.sleep(0.1)

    print(f'\nResultados: {sucessos} sucessos, {erros} erros')

    # 5. Demonstrar retry automatico
    print('\n5️⃣ Demonstrando retry automatico...')

    def operacao_instavel():
        """Operacao que falha algumas vezes."""
        import random

        if random.random() < 0.7:  # 70% chance de falhar
            raise APIError('Servico temporariamente indisponivel', status_code=503)
        return {'status': 'sucesso'}

    try:
        resultado = ErrorRecovery.retry_with_backoff(
            operacao_instavel, max_retries=3, base_delay=0.5
        )
        print(f'✅ Operacao com retry bem-sucedida: {resultado}')
    except Exception as e:
        print(f'❌ Operacao falhou mesmo com retry: {e}')

    # 6. Exibir resumo de metricas
    print('\n6️⃣ Resumo de metricas coletadas...')
    metricas = get_metrics_summary()

    print(f'  📊 Total de metricas: {metricas["total_metrics"]}')
    print(f'  🌐 Chamadas de API: {metricas["total_api_calls"]}')
    print(f'  ✅ Chamadas bem-sucedidas: {metricas["successful_api_calls"]}')
    print(f'  ❌ Taxa de erro: {metricas["error_rate"]:.1%}')
    print(f'  ⚡ Tempo medio de resposta: {metricas["average_response_time"]:.3f}s')
    print(f'  💾 Uso de memoria: ~{metricas["memory_usage"]["total_estimated"]} bytes')

    # 7. Demonstrar exportacao de metricas
    print('\n7️⃣ Exportando metricas...')

    from pypix_api.metrics import export_metrics

    # Exportar para console
    print('Exportando para console:')
    export_metrics()

    # Exportar para arquivo (opcional)
    metrics_file = '/tmp/pypix_demo_metrics.json'
    if export_metrics(metrics_file):
        print(f'📁 Metricas exportadas para: {metrics_file}')

    # 8. Status final do sistema
    print('\n8️⃣ Status final do sistema...')
    status_final = get_observability_status()

    print(f'Status: {status_final["status"]}')
    print(f'Uptime: {status_final["health"]["uptime_seconds"]:.1f}s')

    if status_final['status'] != 'healthy':
        print('⚠️  Verificacoes que falharam:')
        for check, result in status_final['checks'].items():
            if not result.get('healthy', True):
                print(f'  - {check}: {result.get("error", "Unknown error")}')

    print('\n🎉 Demonstracao concluida!')
    print('\nPara producao, configure:')
    print('  - PYPIX_LOG_LEVEL=WARNING')
    print('  - PYPIX_LOG_FORMAT=json')
    print('  - PYPIX_METRICS_EXPORT_PATH=/var/log/pypix/metrics.jsonl')
    print('  - PYPIX_LOG_FILE=/var/log/pypix/app.log')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n👋 Demo interrompida pelo usuario')
    except Exception as e:
        print(f'\n💥 Erro durante demo: {e}')
        import traceback

        traceback.print_exc()
