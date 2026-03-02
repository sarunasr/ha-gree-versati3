"""Select platform for Gree Versati."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import GreeVersatiProtocolClient
from .constants import (
    CONF_DEVICE_ID,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DATA_ENTRIES,
    MODE_OPTIONS,
    PARAM_MOD,
)
from .coordinator import GreeVersatiCoordinator
from .entity import GreeVersatiEntity

_MODE_BY_LABEL = MODE_OPTIONS
_LABEL_BY_MODE = {value: key for key, value in MODE_OPTIONS.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    runtime_data = hass.data[entry.domain][DATA_ENTRIES][entry.entry_id]
    async_add_entities(
        [
            GreeVersatiModeSelect(
                runtime_data[DATA_COORDINATOR],
                entry.data[CONF_DEVICE_ID],
                runtime_data[DATA_CLIENT],
            )
        ]
    )


class GreeVersatiModeSelect(GreeVersatiEntity, SelectEntity):
    """Mode control select entity."""

    _attr_translation_key = "mode_control"
    _attr_options = list(_MODE_BY_LABEL)

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
    ) -> None:
        super().__init__(
            coordinator,
            device_id,
            PARAM_MOD,
            unique_id_key="mode_select",
        )
        self._client = client

    @property
    def current_option(self) -> str | None:
        """Return selected mode option."""
        raw_value = (self.coordinator.data or {}).get(PARAM_MOD)
        if raw_value is None:
            return None
        try:
            return _LABEL_BY_MODE.get(int(raw_value))
        except (TypeError, ValueError):
            return None

    async def async_select_option(self, option: str) -> None:
        """Change operation mode."""
        await self._client.async_set({PARAM_MOD: _MODE_BY_LABEL[option]})
        await self.coordinator.async_request_refresh()
