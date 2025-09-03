"""Módulo de escopos bancários."""

from pypix_api.scopes.bb import BBScopes
from pypix_api.scopes.registry import ScopeRegistry, get_bank_scopes, get_pix_scopes
from pypix_api.scopes.sicoob import SicoobScopes

# Registrar todos os bancos
ScopeRegistry.register('756', SicoobScopes)
ScopeRegistry.register('sicoob', SicoobScopes)

ScopeRegistry.register('001', BBScopes)
ScopeRegistry.register('bb', BBScopes)
ScopeRegistry.register('banco_do_brasil', BBScopes)

# Exportar funções principais
__all__ = [
    'BBScopes',
    'ScopeRegistry',
    'SicoobScopes',
    'get_bank_scopes',
    'get_pix_scopes',
]
