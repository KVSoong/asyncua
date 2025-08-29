"""Platform for switch integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import STATE_OFF, STATE_UNAVAILABLE, STATE_OK
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AsyncuaCoordinator
from .const import (
    CONF_NODE_HUB,
    CONF_NODE_ID,
    CONF_NODE_NAME,
    CONF_NODE_SWITCH_DI,
    CONF_NODE_UNIQUE_ID,
    CONF_NODES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

NODE_SCHEMA = {
    CONF_NODES: [
        {
            vol.Required(CONF_NODE_HUB): cv.string,
            vol.Required(CONF_NODE_NAME): cv.string,
            vol.Required(CONF_NODE_ID): cv.string,
            vol.Optional(CONF_NODE_SWITCH_DI): cv.string,
            vol.Optional(CONF_NODE_UNIQUE_ID): cv.string,
        }
    ]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    schema=NODE_SCHEMA,
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up asyncua_switch coordinator_nodes."""

    coordinator_nodes: dict[str, list[dict[str, str]]] = {}
    coordinators: dict[str, AsyncuaCoordinator] = {}
    asyncua_switches: list = []

    for _idx_node, val_node in enumerate(config[CONF_NODES]):
        if val_node[CONF_NODE_HUB] not in coordinator_nodes:
            coordinator_nodes[val_node[CONF_NODE_HUB]] = []
        coordinator_nodes[val_node[CONF_NODE_HUB]].append(val_node)

    for key_coordinator, val_coordinator in coordinator_nodes.items():
        # Get the respective asyncua coordinator
        if key_coordinator not in hass.data[DOMAIN]:
            raise ConfigEntryError(
                f"Asyncua hub {key_coordinator} not found. Specify a valid asyncua hub in the configuration."
            )
        coordinators[key_coordinator] = hass.data[DOMAIN][key_coordinator]
        coordinators[key_coordinator].add_sensors(sensors=val_coordinator)

        for _idx_sensor, val_sensor in enumerate(val_coordinator):
            asyncua_switches.append(
                AsyncuaSwitch(
                    coordinator=coordinators[key_coordinator],
                    name=val_sensor[CONF_NODE_NAME],
                    hub=val_sensor[CONF_NODE_HUB],
                    node_id=val_sensor[CONF_NODE_ID],
                    addr_di=val_sensor.get(CONF_NODE_SWITCH_DI),
                    unique_id=val_sensor.get(CONF_NODE_UNIQUE_ID),
                )
            )
    async_add_entities(asyncua_switches)
    for idx_switch, val_switch in enumerate(asyncua_switches):
        await val_switch.async_init()
        _LOGGER.debug("Initialized switch %s - %s", idx_switch, val_switch.attr_name)


class AsyncuaSwitch(SwitchEntity, CoordinatorEntity[AsyncuaCoordinator]):
    """A switch implementation for Asyncua OPCUA nodes."""

    def __init__(
        self,
        coordinator: AsyncuaCoordinator,
        name: str,
        hub: str,
        node_id: str,
        addr_di: str | None = None,
        unique_id: str | None = None,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator=coordinator)
        self._attr_name = name
        self._attr_unique_id = (
            unique_id if unique_id is not None else f"{DOMAIN}.{hub}.{node_id}"
        )
        self._attr_available = STATE_UNAVAILABLE
        self._available = STATE_UNAVAILABLE
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_is_on: bool | None
        self._hub = hub
        self._coordinator = coordinator
        self._node_id = node_id
        self._addr_di = addr_di if addr_di is not None else node_id

    @property
    def attr_name(self):
        """Return __attr_name variable."""
        return self._attr_name

    @property
    def is_on(self) -> bool | None:
        """Check if OPCUA connection is available, set availability state to unavailable on connection error."""
        if not self.coordinator.hub.connected:
            self._attr_is_on = None
            self._attr_available = STATE_UNAVAILABLE
            self._available = STATE_UNAVAILABLE
            return self._attr_is_on
        # Return node state and set availability to OK
        self._attr_is_on = self.coordinator.hub.cache_val.get(
            self._attr_unique_id, None
        )
        self._attr_available = STATE_OK
        self._available = STATE_OK
        return self._attr_is_on

    async def async_init(self) -> None:
        """Initialize switch to get latest value."""
        await self._async_set_value()

    async def _async_set_value(self, val: bool = None, **kwargs) -> None:
        """Set boolean value to node then execute refresh to get updated DI value."""
        if val is not None:
            await self.coordinator.hub.set_value(
                nodeid=self._node_id,
                value=val,
                **kwargs,
            )
        new_val = await self.coordinator.hub.get_value(nodeid=self._addr_di)
        self._attr_is_on = new_val
        self._attr_available = True
        await self.coordinator.async_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self._async_set_value(val=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._async_set_value(val=False)
