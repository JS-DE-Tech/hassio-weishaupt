"""Tests for Weishaupt number entities."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import types
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "custom_components" / "weishaupt_wtc"


def load_module(module_name: str, file_path: Path):
    """Load a module from file while preserving package-relative imports."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


homeassistant_pkg = types.ModuleType("homeassistant")
homeassistant_pkg.__path__ = []
sys.modules.setdefault("homeassistant", homeassistant_pkg)

components_pkg = types.ModuleType("homeassistant.components")
components_pkg.__path__ = []
sys.modules.setdefault("homeassistant.components", components_pkg)

sensor_component = types.ModuleType("homeassistant.components.sensor")


class SensorEntity:
    """Minimal sensor entity stub."""


class SensorDeviceClass:
    """Return the requested enum member name as a string."""

    def __getattr__(self, name: str) -> str:
        return name


class SensorStateClass:
    """Return the requested enum member name as a string."""

    def __getattr__(self, name: str) -> str:
        return name


sensor_component.SensorEntity = SensorEntity
sensor_component.SensorDeviceClass = SensorDeviceClass()
sensor_component.SensorStateClass = SensorStateClass()
sys.modules["homeassistant.components.sensor"] = sensor_component

number_component = types.ModuleType("homeassistant.components.number")
number_component.NumberEntity = object
number_component.NumberMode = SimpleNamespace(SLIDER="slider")
sys.modules.setdefault("homeassistant.components.number", number_component)

config_entries = types.ModuleType("homeassistant.config_entries")
config_entries.ConfigEntry = object
sys.modules.setdefault("homeassistant.config_entries", config_entries)

core = types.ModuleType("homeassistant.core")
core.HomeAssistant = object
core.callback = lambda func: func
sys.modules.setdefault("homeassistant.core", core)

const = types.ModuleType("homeassistant.const")
const.PERCENTAGE = "%"
const.UnitOfEnergy = SimpleNamespace(KILO_WATT_HOUR="kWh")
const.UnitOfPower = SimpleNamespace(KILO_WATT="kW")
const.UnitOfPressure = SimpleNamespace(BAR="bar")
const.UnitOfTemperature = SimpleNamespace(CELSIUS="°C")
const.UnitOfTime = SimpleNamespace(HOURS="h")
sys.modules.setdefault("homeassistant.const", const)

helpers_pkg = types.ModuleType("homeassistant.helpers")
helpers_pkg.__path__ = []
sys.modules.setdefault("homeassistant.helpers", helpers_pkg)

device_registry_module = types.ModuleType("homeassistant.helpers.device_registry")
device_registry_module.DeviceInfo = dict
sys.modules["homeassistant.helpers.device_registry"] = device_registry_module

entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
entity_platform.AddEntitiesCallback = object
sys.modules.setdefault("homeassistant.helpers.entity_platform", entity_platform)

update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")


class CoordinatorEntity:
    """Minimal coordinator entity stub."""

    def __class_getitem__(cls, item):
        return cls

    def __init__(self, coordinator) -> None:
        self.coordinator = coordinator

    @property
    def available(self) -> bool:
        return True


update_coordinator.CoordinatorEntity = CoordinatorEntity
sys.modules.setdefault("homeassistant.helpers.update_coordinator", update_coordinator)

custom_components_pkg = types.ModuleType("custom_components")
custom_components_pkg.__path__ = [str(REPO_ROOT / "custom_components")]
sys.modules.setdefault("custom_components", custom_components_pkg)

integration_pkg = types.ModuleType("custom_components.weishaupt_wtc")
integration_pkg.__path__ = [str(PACKAGE_ROOT)]
sys.modules.setdefault("custom_components.weishaupt_wtc", integration_pkg)

load_module("custom_components.weishaupt_wtc.const", PACKAGE_ROOT / "const.py")
load_module("custom_components.weishaupt_wtc.parsing", PACKAGE_ROOT / "parsing.py")
sensors = load_module(
    "custom_components.weishaupt_wtc.sensors", PACKAGE_ROOT / "sensors.py"
)
load_module(
    "custom_components.weishaupt_wtc.heating_circuits",
    PACKAGE_ROOT / "heating_circuits.py",
)
coordinator_module = types.ModuleType("custom_components.weishaupt_wtc.coordinator")
coordinator_module.WeishauptDataUpdateCoordinator = object
sys.modules["custom_components.weishaupt_wtc.coordinator"] = coordinator_module
load_module("custom_components.weishaupt_wtc.sensor", PACKAGE_ROOT / "sensor.py")
number = load_module("custom_components.weishaupt_wtc.number", PACKAGE_ROOT / "number.py")


def sensor_by_key(key: str):
    """Return a sensor definition by key."""
    return next(sensor_def for sensor_def in sensors.ALL_SENSORS if sensor_def.key == key)


class WriteClient:
    """Capture writes and return a configured success value."""

    def __init__(self, success: bool = True) -> None:
        self.success = success
        self.calls: list[dict] = []

    async def write_parameter(self, **kwargs) -> bool:
        """Capture a write call."""
        self.calls.append(kwargs)
        return self.success


class NumberCoordinator:
    """Minimal coordinator for number tests."""

    def __init__(self, data: dict, client: WriteClient) -> None:
        self.data = data
        self.client = client
        self.refreshes = 0

    async def async_request_refresh(self) -> None:
        """Capture refresh requests."""
        self.refreshes += 1


class NumberTests(unittest.IsolatedAsyncioTestCase):
    """Test warm-water number entities."""

    def _entity(self, key: str, raw_value: int = 550):
        sensor_def = sensor_by_key(key)
        client = WriteClient()
        coordinator = NumberCoordinator(
            {key: {"value_int": raw_value, "value_hex": f"{raw_value:04x}"}},
            client,
        )
        return (
            number.WeishauptNumberEntity(
                coordinator=coordinator,
                sensor_def=sensor_def,
                entry=SimpleNamespace(entry_id="entry-123"),
                settings=number.NUMBER_SETTINGS[key],
            ),
            client,
            coordinator,
        )

    async def test_normal_setpoint_bounds_and_write_scaling(self) -> None:
        """Normal setpoint should read/write with the requested constraints."""
        entity, client, coordinator = self._entity("sg_wwsolltemperatur_normal", 550)

        self.assertEqual(entity.native_value, 55.0)
        self.assertEqual(entity._attr_native_min_value, 50.0)
        self.assertEqual(entity._attr_native_max_value, 60.0)
        self.assertEqual(entity._attr_native_step, 1.0)

        await entity.async_set_native_value(50.0)

        self.assertEqual(client.calls[0]["value_int"], 500)
        self.assertEqual(coordinator.refreshes, 1)
        with self.assertRaises(ValueError):
            await entity.async_set_native_value(49.0)

    async def test_absenk_setpoint_bounds_and_write_scaling(self) -> None:
        """Absenk setpoint should read/write with the requested constraints."""
        entity, client, coordinator = self._entity("sg_wwsolltemperatur_absenk", 80)

        self.assertEqual(entity.native_value, 8.0)
        self.assertEqual(entity._attr_native_min_value, 8.0)
        self.assertEqual(entity._attr_native_max_value, 60.0)
        self.assertEqual(entity._attr_native_step, 1.0)

        await entity.async_set_native_value(60.0)

        self.assertEqual(client.calls[0]["value_int"], 600)
        self.assertEqual(coordinator.refreshes, 1)
        with self.assertRaises(ValueError):
            await entity.async_set_native_value(61.0)


if __name__ == "__main__":
    unittest.main()
