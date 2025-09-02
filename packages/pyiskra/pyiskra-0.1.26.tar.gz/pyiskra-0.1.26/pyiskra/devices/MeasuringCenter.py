import logging
import time
import asyncio
import struct

from pyiskra.exceptions import InvalidResponseCode, MeasurementTypeNotSupported
from .BaseDevice import Device
from ..adapters import RestAPI, Modbus
from ..helper import (
    MeasurementType,
    ModbusMapper,
    Measurements,
    Measurement,
    Phase_Measurements,
    Total_Measurements,
    Counter,
    Counters,
    counter_units,
    get_counter_direction,
    get_counter_type,
)

log = logging.getLogger(__name__)


class MeasuringCentre(Device):
    """
    Represents an Impact device.

    Attributes:
        supports_measurements (bool): Indicates whether the device supports measurements.
        supports_counters (bool): Indicates whether the device supports counters.
        fw_version (float): The firmware version of the device.
    """

    DEVICE_PARAMETERS = {
        "MT": {"phases": 3, "resettable_counters": 4, "non_resettable_counters": 0},
        "iMT": {"phases": 3, "resettable_counters": 4, "non_resettable_counters": 0},
        "MC": {"phases": 3, "resettable_counters": 4, "non_resettable_counters": 0},
        "iMC": {"phases": 3, "resettable_counters": 4, "non_resettable_counters": 0},
        # Add more models as needed
    }

    supports_measurements = True
    supports_counters = True
    supports_interval_measurements = False

    async def init(self):
        """
        Initializes the Impact device.

        This method retrieves basic information, updates the status, and logs a success message.
        """
        await self.get_basic_info()
        await self.update_status()
        log.debug(f"Successfully initialized {self.model} {self.serial}")

    async def get_measurements(
        self, measurement_type: MeasurementType = MeasurementType.ACTUAL_MEASUREMENTS
    ):
        """
        Retrieves measurements from the device.

        Returns:
            dict: A dictionary containing the measurements.
        """
        if (
            measurement_type != MeasurementType.ACTUAL_MEASUREMENTS
            and self.supports_interval_measurements == False
        ):
            raise MeasurementTypeNotSupported(
                f"{measurement_type} is not supported by {self.model}"
            )

        if isinstance(self.adapter, RestAPI):
            log.debug(
                f"Getting measurements from Rest API for {self.model} {self.serial}"
            )
            return await self.adapter.get_measurements()
        elif isinstance(self.adapter, Modbus):
            log.debug(
                f"Getting measurements from Modbus for {self.model} {self.serial}"
            )
            data = await self.adapter.read_input_registers(2500, 106)
            mapper = ModbusMapper(data, 2500)

            data_temperature = await self.adapter.read_input_registers(2658, 2)
            temperature_mapper = ModbusMapper(data_temperature, 2658)

            phases = []
            for phase in range(self.phases):

                voltage = Measurement(
                    mapper.get_float(2500 + 2 * phase),
                    "V",
                )
                current = Measurement(
                    mapper.get_float(2516 + 2 * phase),
                    "A",
                )
                active_power = Measurement(
                    mapper.get_float(2530 + 2 * phase),
                    "W",
                )
                reactive_power = Measurement(
                    mapper.get_float(2538 + 2 * phase),
                    "var",
                )
                apparent_power = Measurement(
                    mapper.get_float(2546 + 2 * phase),
                    "VA",
                )
                power_factor = Measurement(
                    mapper.get_float(2554 + 2 * phase),
                    "",
                )
                power_angle = Measurement(
                    mapper.get_float(2570 + 2 * phase),
                    "°",
                )
                thd_current = Measurement(
                    mapper.get_float(2588 + 2 * phase),
                    "%",
                )
                thd_voltage = Measurement(
                    mapper.get_float(2594 + 2 * phase),
                    "%",
                )
                phases.append(
                    Phase_Measurements(
                        voltage,
                        current,
                        active_power,
                        reactive_power,
                        apparent_power,
                        power_factor,
                        power_angle,
                        thd_voltage,
                        thd_current,
                    )
                )

            active_power_total = Measurement(
                mapper.get_float(2536),
                "W",
            )
            reactive_power_total = Measurement(
                mapper.get_float(2544),
                "var",
            )
            apparent_power_total = Measurement(
                mapper.get_float(2552),
                "VA",
            )
            power_factor_total = Measurement(
                mapper.get_float(2560),
                "",
            )
            power_angle_total = Measurement(
                mapper.get_float(2576),
                "°",
            )
            frequency = Measurement(
                mapper.get_float(2584),
                "Hz",
            )
            temperature = Measurement(
                temperature_mapper.get_float(2658),
                "°C",
            )
            total = Total_Measurements(
                active_power_total,
                reactive_power_total,
                apparent_power_total,
                power_factor_total,
                power_angle_total,
            )

            return Measurements(phases, total, frequency, temperature)

    async def get_counters(self):
        """
        Retrieves counters from the device.

        Returns:
            dict: A dictionary containing the counters.
        """
        if isinstance(self.adapter, RestAPI):
            log.debug(f"Getting counters from Rest API for {self.model} {self.serial}")
            return await self.adapter.get_counters()
        elif isinstance(self.adapter, Modbus):
            log.debug(
                f"Getting measurements from Modbus for {self.model} {self.serial}"
            )

            # Open the connection
            handle_connection = not self.adapter.connected
            if handle_connection:
                await self.adapter.open_connection()

            data = await self.adapter.read_input_registers(400, 94)
            data_mapper = ModbusMapper(data, 400)
            direction_settings = await self.adapter.read_holding_registers(151, 1)
            counter_settings = await self.adapter.read_holding_registers(421, 94)
            counter_settings_mapper = ModbusMapper(counter_settings, 421)

            # Close the connection
            if handle_connection:
                await self.adapter.close_connection()

            non_resettable = []
            resettable = []
            reverse_connection = False
            if direction_settings[0] & 2:
                reverse_connection = True

            for counter in range(self.resettable_counters):
                units = counter_units[
                    counter_settings_mapper.get_uint16(421 + 10 * counter) & 0x3
                ]
                direction = get_counter_direction(
                    counter_settings_mapper.get_uint16(422 + 10 * counter),
                    reverse_connection,
                )
                counter_type = get_counter_type(direction, units)
                value = data_mapper.get_int32(406 + 2 * counter)
                exponent = data_mapper.get_int16(401 + counter)
                resettable.append(
                    Counter(
                        value * (10**exponent),
                        units,
                        direction,
                        counter_type,
                    )
                )

            for counter in range(self.non_resettable_counters):
                units = counter_units[
                    counter_settings_mapper.get_uint16(
                        421 + 10 * (counter + self.resettable_counters)
                    )
                    & 0x3
                ]
                direction = get_counter_direction(
                    counter_settings_mapper.get_uint16(
                        422 + 10 * (counter + self.resettable_counters)
                    ),
                    reverse_connection,
                )
                counter_type = get_counter_type(direction, units)
                value = data_mapper.get_int32(
                    406 + 2 * (counter + self.resettable_counters)
                )
                exponent = data_mapper.get_int16(
                    401 + (counter + self.resettable_counters)
                )
                non_resettable.append(
                    Counter(
                        value * (10**exponent),
                        units,
                        direction,
                        counter_type,
                    )
                )

            return Counters(non_resettable, resettable)

    async def update_status(self):
        """
        Updates the status of the device.

        This method acquires a lock to ensure that only one update is running at a time.
        It retrieves measurements and counters, updates the corresponding attributes,
        and sets the update timestamp.
        """
        # If update is already running, wait for it to finish and then return
        if self.update_lock.locked():
            log.debug("Update already running for %s %s" % (self.model, self.serial))
            while self.update_lock.locked():
                await asyncio.sleep(0.1)
            return

        # If update is not running, acquire the lock and update
        async with self.update_lock:
            log.debug("Updating status for %s %s" % (self.model, self.serial))

            # if the adapter is Modbus, open the connection
            if isinstance(self.adapter, Modbus):
                await self.adapter.open_connection()

            self.measurements = await self.get_measurements()
            self.counters = await self.get_counters()

            # if the adapter is Modbus, close the connection
            if isinstance(self.adapter, Modbus):
                await self.adapter.close_connection()

            self.update_timestamp = time.time()
