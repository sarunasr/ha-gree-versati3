"""Switch platform for Gree Versati."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import GreeVersatiProtocolClient
from .constants import (
    CONF_DEVICE_ID,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DATA_ENTRIES,
    PARAM_POW,
)
from .coordinator import GreeVersatiCoordinator
from .entity import GreeVersatiEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    runtime_data = hass.data[entry.domain][DATA_ENTRIES][entry.entry_id]
    async_add_entities(
        [
            GreeVersatiPowerSwitch(
                runtime_data[DATA_COORDINATOR],
                entry.data[CONF_DEVICE_ID],
                runtime_data[DATA_CLIENT],
            )
        ]
    )


class GreeVersatiPowerSwitch(GreeVersatiEntity, SwitchEntity):
    """Power control switch."""

    _attr_translation_key = "power_control"

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
    ) -> None:
        super().__init__(
            coordinator,
            device_id,
            PARAM_POW,
            unique_id_key="power_switch",
        )
        self._client = client

    @property
    def is_on(self) -> bool | None:
        """Return switch state."""
        value = (self.coordinator.data or {}).get(PARAM_POW)
        if value is None:
            return None
        try:
            return bool(int(value))
        except (TypeError, ValueError):
            return bool(value)

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn on power."""
        await self._client.async_set({PARAM_POW: 1})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn off power."""
        await self._client.async_set({PARAM_POW: 0})
        await self.coordinator.async_request_refresh()
