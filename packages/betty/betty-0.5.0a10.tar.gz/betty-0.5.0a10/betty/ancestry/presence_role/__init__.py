"""
Provide presence roles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from betty.locale.localizable import Localizable, _
from betty.mutability import Mutable
from betty.plugin import Plugin, PluginRepository
from betty.plugin.entry_point import EntryPointPluginRepository

if TYPE_CHECKING:
    from betty.machine_name import MachineName


class PresenceRole(Mutable, Plugin):
    """
    A person's role at an event.

    Read more about :doc:`/development/plugin/presence-role`.
    """

    @final
    @override
    @classmethod
    def plugin_type_cls(cls) -> type[Plugin]:
        return PresenceRole

    @final
    @override
    @classmethod
    def plugin_type_id(cls) -> MachineName:
        return "presence-role"

    @final
    @override
    @classmethod
    def plugin_type_label(cls) -> Localizable:
        return _("Presence role")


PRESENCE_ROLE_REPOSITORY: PluginRepository[PresenceRole] = EntryPointPluginRepository(
    PresenceRole, "betty.presence_role"
)
"""
The presence role plugin repository.

Read more about :doc:`/development/plugin/presence-role`.
"""
