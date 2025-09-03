"""pypix-api: Biblioteca Python para integracao com APIs bancarias do PIX.

Esta biblioteca facilita a integracao com APIs de bancos brasileiros,
fornecendo uma interface simples e consistente para operacoes PIX.
"""

__version__ = '0.6.2'
__author__ = 'Fabio Thomaz'
__email__ = 'fabio@ladder.dev.br'
__license__ = 'MIT'

# Exports principais
from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.bb import BBPixAPI
from pypix_api.banks.sicoob import SicoobPixAPI
from pypix_api.models.pix import PixCobranca

__all__ = [
    'BBPixAPI',
    'OAuth2Client',
    'PixCobranca',
    'SicoobPixAPI',
    '__author__',
    '__email__',
    '__license__',
    '__version__',
]

# Observabilidade (imports e exports opcionais)
import importlib.util

if importlib.util.find_spec('pypix_api.error_handling') is not None:
    from pypix_api.error_handling import (
        APIError as APIError,
    )
    from pypix_api.error_handling import (
        AuthenticationError as AuthenticationError,
    )
    from pypix_api.error_handling import (
        PIXError as PIXError,
    )
    from pypix_api.error_handling import (
        ValidationError as ValidationError,
    )
    from pypix_api.logging import PIXLogger as PIXLogger
    from pypix_api.logging import setup_logging as setup_logging
    from pypix_api.metrics import (
        MetricsCollector as MetricsCollector,
    )
    from pypix_api.metrics import (
        get_metrics_summary as get_metrics_summary,
    )
    from pypix_api.observability import (
        configure_observability as configure_observability,
    )
    from pypix_api.observability import (
        get_observability_status as get_observability_status,
    )

    # Adicionar exports de observabilidade
    __all__.extend(
        [
            'APIError',
            'AuthenticationError',
            'MetricsCollector',
            'PIXError',
            'PIXLogger',
            'ValidationError',
            'configure_observability',
            'get_metrics_summary',
            'get_observability_status',
            'setup_logging',
        ]
    )
