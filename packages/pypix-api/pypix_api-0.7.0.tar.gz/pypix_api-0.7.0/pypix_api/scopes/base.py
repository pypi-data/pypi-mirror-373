"""Classe base para definição de escopos bancários."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScopeGroup:
    """Grupo de escopos para uma funcionalidade específica."""

    name: str
    scopes: list[str]
    description: str

    def as_string(self) -> str:
        """Retorna os escopos como string separada por espaços."""
        return ' '.join(self.scopes)

    def __contains__(self, scope: str) -> bool:
        """Verifica se um escopo específico está no grupo."""
        return scope in self.scopes

    def __add__(self, other: 'ScopeGroup') -> 'ScopeGroup':
        """Combina dois grupos de escopos."""
        combined_scopes = list(dict.fromkeys(self.scopes + other.scopes))
        return ScopeGroup(
            name=f'{self.name}_{other.name}',
            scopes=combined_scopes,
            description=f'{self.description} + {other.description}',
        )


class BankScopesBase(ABC):
    """Classe base para definição de escopos bancários."""

    # Informações do banco (devem ser definidas pelas subclasses)
    BANK_NAME: str = ''
    BANK_CODE: str = ''
    BANK_CODES: list[str] = []  # Códigos alternativos (ex: ['001', 'bb'])

    @classmethod
    @abstractmethod
    def get_pix_scopes(cls) -> ScopeGroup:
        """Retorna os escopos PIX do banco."""

    @classmethod
    def get_scope_group(cls, name: str) -> ScopeGroup:
        """Obtém um grupo de escopos pelo nome."""
        return getattr(cls, name.upper())

    @classmethod
    def list_available_groups(cls) -> list[str]:
        """Lista todos os grupos de escopos disponíveis."""
        return [
            attr
            for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), ScopeGroup)
        ]

    @classmethod
    def combine_scopes(cls, *groups: ScopeGroup) -> str:
        """Combina múltiplos grupos de escopos em uma string."""
        all_scopes = []
        for group in groups:
            all_scopes.extend(group.scopes)
        unique_scopes = list(dict.fromkeys(all_scopes))
        return ' '.join(unique_scopes)

    @classmethod
    def get_bank_info(cls) -> dict[str, Any]:
        """Retorna informações do banco."""
        return {
            'name': cls.BANK_NAME,
            'code': cls.BANK_CODE,
            'alternative_codes': cls.BANK_CODES,
            'available_groups': cls.list_available_groups(),
        }
