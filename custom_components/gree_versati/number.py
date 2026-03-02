"""Number platform for Gree Versati."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import GreeVersatiProtocolClient
from .constants import (
    CONF_DEVICE_ID,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DATA_ENTRIES,
    HE_WAT_OUT_TEMP_SET_STEP,
    MAX_HE_WAT_OUT_TEMP_SET,
    MAX_WAT_BOX_TEMP_SET,
    MIN_HE_WAT_OUT_TEMP_SET,
    MIN_WAT_BOX_TEMP_SET,
    PARAM_HE_WAT_OUT_TEM_SET,
    PARAM_WAT_BOX_TEM_SET,
    WAT_BOX_TEMP_SET_STEP,
)
from .coordinator import GreeVersatiCoordinator
from .entity import GreeVersatiEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    runtime_data = hass.data[entry.domain][DATA_ENTRIES][entry.entry_id]
    async_add_entities(
        [
            GreeVersatiOutletSetpointNumber(
                runtime_data[DATA_COORDINATOR],
                entry.data[CONF_DEVICE_ID],
                runtime_data[DATA_CLIENT],
            ),
            GreeVersatiWatBoxSetpointNumber(
                runtime_data[DATA_COORDINATOR],
                entry.data[CONF_DEVICE_ID],
                runtime_data[DATA_CLIENT],
            ),
        ]
    )


class GreeVersatiSetpointNumber(GreeVersatiEntity, NumberEntity):
    """Base writable setpoint number entity."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = "box"

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
        param_key: str,
    ) -> None:
        super().__init__(coordinator, device_id, param_key)
        self._client = client

    @property
    def native_value(self) -> float | None:
        """Return current setpoint value."""
        value = (self.coordinator.data or {}).get(self._param_key)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set setpoint value."""
        await self._client.async_set({self._param_key: int(round(value))})
        await self.coordinator.async_request_refresh()


class GreeVersatiOutletSetpointNumber(GreeVersatiSetpointNumber):
    """Number entity for heating water outlet setpoint."""

    _attr_translation_key = "he_wat_out_tem_set"
    _attr_native_min_value = MIN_HE_WAT_OUT_TEMP_SET
    _attr_native_max_value = MAX_HE_WAT_OUT_TEMP_SET
    _attr_native_step = HE_WAT_OUT_TEMP_SET_STEP

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
    ) -> None:
        super().__init__(coordinator, device_id, client, PARAM_HE_WAT_OUT_TEM_SET)


class GreeVersatiWatBoxSetpointNumber(GreeVersatiSetpointNumber):
    """Number entity for water box temperature setpoint."""

    _attr_translation_key = "wat_box_tem_set"
    _attr_native_min_value = MIN_WAT_BOX_TEMP_SET
    _attr_native_max_value = MAX_WAT_BOX_TEMP_SET
    _attr_native_step = WAT_BOX_TEMP_SET_STEP

    def __init__(
        self,
        coordinator: GreeVersatiCoordinator,
        device_id: str,
        client: GreeVersatiProtocolClient,
    ) -> None:
        super().__init__(coordinator, device_id, client, PARAM_WAT_BOX_TEM_SET)
