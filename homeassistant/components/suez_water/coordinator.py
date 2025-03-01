"""Suez water update coordinator."""

from pysuez import AggregatedData, PySuezError, SuezClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import _LOGGER, HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_COUNTER_ID, DATA_REFRESH_INTERVAL, DOMAIN


class SuezWaterCoordinator(DataUpdateCoordinator[AggregatedData]):
    """Suez water coordinator."""

    _suez_client: SuezClient
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize suez water coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DATA_REFRESH_INTERVAL,
            always_update=True,
            config_entry=config_entry,
        )

    async def _async_setup(self) -> None:
        self._suez_client = SuezClient(
            username=self.config_entry.data[CONF_USERNAME],
            password=self.config_entry.data[CONF_PASSWORD],
            counter_id=self.config_entry.data[CONF_COUNTER_ID],
        )
        if not await self._suez_client.check_credentials():
            raise ConfigEntryError("Invalid credentials for suez water")

    async def _async_update_data(self) -> AggregatedData:
        """Fetch data from API endpoint."""
        try:
            data = await self._suez_client.fetch_aggregated_data()
        except PySuezError as err:
            _LOGGER.exception(err)
            raise UpdateFailed(
                f"Suez coordinator error communicating with API: {err}"
            ) from err
        _LOGGER.debug("Successfully fetched suez data")
        return data
