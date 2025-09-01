import logging
from time import time

from zeus.device.cpu import get_current_cpu_index
from zeus.monitor import ZeusMonitor

from ms_utils.logging_lib import Logger

logger = Logger.setup_logger(__name__, level=logging.INFO)  # logging.DEBUG
logger.propagate = False


class PowerConsumption(ZeusMonitor):
    def __init__(self, cpu_indices=None, gpu_indices=None):
        if cpu_indices or gpu_indices:
            super().__init__(
                cpu_indices=cpu_indices if cpu_indices else [],
                gpu_indices=gpu_indices if gpu_indices else [],
            )
        else:
            current_cpu_index = get_current_cpu_index()
            super().__init__(cpu_indices=[current_cpu_index], gpu_indices=[])

    # start power consumption measure of the process and identify it by a key
    def start_measure(self, key: str) -> None:
        self.begin_window(key)

    # end measurement of power consumption of the process identified by the key
    def end_measure(self, key: str) -> float:
        power = self.end_window(key)
        return float(
            sum(power.gpu_energy.values())
            + sum(power.cpu_energy.values() if power.cpu_energy else 0)
            + sum(power.dram_energy.values() if power.dram_energy else 0)
        )

    # add methode for power consumption measurement that doesn't terminate the measure
    def get_power_consumption(self, key: str) -> float:
        # Retrieve the start time and energy consumption of this window.
        try:
            measurement_state = self.monitor.measurement_states.get(key)
        except KeyError:
            raise ValueError(
                f"Measurement window '{key}' does not exist"
            ) from None

        # Take instant power consumption measurements.
        # This, in theory, is introducing extra NVMLs call in the critical path
        # even if computation time is not so short. However, it is reasonable to
        # expect that computation time would be short if the user explicitly
        # turned on the `approx_instant_energy` option. Calling this function
        # as early as possible will lead to more accurate energy approximation.

        end_time: float = time()
        start_time = measurement_state.time
        gpu_start_energy = measurement_state.gpu_energy
        cpu_start_energy = measurement_state.cpu_energy
        dram_start_energy = measurement_state.dram_energy

        time_consumption: float = end_time - start_time
        gpu_energy_consumption: dict[int, float] = {}
        for gpu_index in self.monitor.gpu_indices:
            # Query energy directly if the GPU has newer architecture.
            if self.gpus.supportsGetTotalEnergyConsumption(gpu_index):
                end_energy = (
                    self.gpus.getTotalEnergyConsumption(gpu_index) / 1000.0
                )
                gpu_energy_consumption[gpu_index] = (
                    end_energy - gpu_start_energy[gpu_index]
                )

        power, power_measurement_time = (
            self.monitor._get_instant_power()
            if gpu_energy_consumption
            else ({}, 0.0)
        )

        cpu_energy_consumption: dict[int, float] = {}
        dram_energy_consumption: dict[int, float] = {}
        for cpu_index in self.monitor.cpu_indices:
            cpu_measurement = (
                self.monitor.cpus.getTotalEnergyConsumption(cpu_index) / 1000.0
            )
            if cpu_start_energy is not None:
                cpu_energy_consumption[cpu_index] = (
                    cpu_measurement.cpu_mj - cpu_start_energy[cpu_index]
                )
            if (
                dram_start_energy is not None
                and cpu_measurement.dram_mj is not None
            ):
                dram_energy_consumption[cpu_index] = (
                    cpu_measurement.dram_mj - dram_start_energy[cpu_index]
                )

        # If there are older GPU architectures, the PowerMonitor will take care of those.
        if self.monitor.power_monitor is not None:
            energy = self.monitor.power_monitor.get_energy(
                start_time, end_time
            )
            # Fallback to the instant power measurement if the PowerMonitor does not
            # have the power samples.
            if energy is None:
                energy = {
                    gpu: 0.0 for gpu in self.monitor.power_monitor.gpu_indices
                }
            gpu_energy_consumption |= energy

        # Approximate energy consumption if the measurement window is too short.
        c = 0
        for gpu_index in self.monitor.gpu_indices:
            if gpu_energy_consumption[gpu_index] == 0.0:
                gpu_energy_consumption[gpu_index] = power[gpu_index] * (
                    time_consumption - power_measurement_time
                )
                c = 1

        # Trigger a warning if energy consumption was measured as zero.
        if c > 0:
            logger.warn(
                "The energy consumption of one or more GPUs was measured as zero. This means that the time duration of the measurement window was shorter than the GPU's energy counter update period. In this case we approximate the energy consumption of a short time window as instant power draw x window duration.",
            )

        return float(
            sum(power.gpu_energy_consumption.values())
            + sum(
                cpu_energy_consumption.values()
                if cpu_energy_consumption
                else 0
            )
            + sum(
                dram_energy_consumption.values()
                if dram_energy_consumption
                else 0
            )
        )
