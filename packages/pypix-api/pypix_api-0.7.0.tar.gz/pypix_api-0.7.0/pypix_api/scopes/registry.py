"""Registry para gerenciar escopos de diferentes bancos."""

from pypix_api.scopes.base import BankScopesBase, ScopeGroup


class ScopeRegistry:
    """Registry centralizado para escopos de bancos."""

    _banks: dict[str, type[BankScopesBase]] = {}

    @classmethod
    def register(cls, bank_code: str, scope_class: type[BankScopesBase]) -> None:
        """Registra uma classe de escopos para um código de banco.

        Args:
            bank_code: Código do banco (ex: '001', '756', 'bb', 'sicoob')
            scope_class: Classe que define os escopos do banco
        """
        cls._banks[bank_code.lower()] = scope_class

    @classmethod
    def get_scopes(cls, bank_code: str) -> type[BankScopesBase]:
        """Obtém a classe de escopos para um código de banco.

        Args:
            bank_code: Código do banco

        Returns:
            Type[BankScopesBase]: Classe de escopos do banco

        Raises:
            ValueError: Se o banco não estiver registrado
        """
        bank_code = bank_code.lower()
        if bank_code not in cls._banks:
            available = ', '.join(cls._banks.keys())
            raise ValueError(
                f"Banco '{bank_code}' não encontrado. Bancos disponíveis: {available}"
            )
        return cls._banks[bank_code]

    @classmethod
    def get_pix_scopes(cls, bank_code: str) -> ScopeGroup:
        """Obtém os escopos PIX para um código de banco.

        Args:
            bank_code: Código do banco

        Returns:
            ScopeGroup: Escopos PIX do banco
        """
        scope_class = cls.get_scopes(bank_code)
        return scope_class.get_pix_scopes()

    @classmethod
    def get_scope_group(cls, bank_code: str, group_name: str) -> ScopeGroup:
        """Obtém um grupo específico de escopos para um banco.

        Args:
            bank_code: Código do banco
            group_name: Nome do grupo de escopos

        Returns:
            ScopeGroup: Grupo de escopos solicitado
        """
        scope_class = cls.get_scopes(bank_code)
        return scope_class.get_scope_group(group_name)

    @classmethod
    def list_banks(cls) -> list[str]:
        """Lista todos os bancos registrados."""
        return list(cls._banks.keys())

    @classmethod
    def list_scope_groups(cls, bank_code: str) -> list[str]:
        """Lista todos os grupos de escopos disponíveis para um banco.

        Args:
            bank_code: Código do banco

        Returns:
            List[str]: Lista de nomes dos grupos de escopos
        """
        scope_class = cls.get_scopes(bank_code)
        return scope_class.list_available_groups()

    @classmethod
    def combine_scopes(cls, bank_code: str, *group_names: str) -> str:
        """Combina múltiplos grupos de escopos de um banco.

        Args:
            bank_code: Código do banco
            *group_names: Nomes dos grupos a serem combinados

        Returns:
            str: Escopos combinados separados por espaço
        """
        scope_class = cls.get_scopes(bank_code)
        groups = [scope_class.get_scope_group(name) for name in group_names]
        return scope_class.combine_scopes(*groups)


# Função de conveniência para obter escopos
def get_bank_scopes(bank_code: str) -> type[BankScopesBase]:
    """Função de conveniência para obter escopos de um banco."""
    return ScopeRegistry.get_scopes(bank_code)


def get_pix_scopes(bank_code: str) -> str:
    """Função de conveniência para obter escopos PIX como string."""
    return ScopeRegistry.get_pix_scopes(bank_code).as_string()
