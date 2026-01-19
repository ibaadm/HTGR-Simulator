import numpy as np


class HTGRCore:
    """
    High Temperature Gas Reactor (HTGR) Core Model.
    Simulates HTGR core transients using a flow-driven startup strategy
    """

    def __init__(self, config_dict: dict) -> None:
        """Initialize the core with physics constants from reactor.yaml."""
        if config_dict is None:
            config_dict = {}

        self.nominal_power = config_dict.get("design_specs", {}).get(
            "nominal_thermal_power_mw", 30.0
        )

        thermo = config_dict.get("thermodynamics", {})
        self.target_temp = thermo.get("target_outlet_temp_c", 850.0)
        self.inlet_temp = thermo.get("inlet_temperature_c", 395.0)
        self.helium_cp = thermo.get("specific_heat_helium_j_kg_k", 5195.0)

        self.time_constant = thermo.get(
            "thermal_time_constant_seconds", 1200.0
        )
        self.pump_time_constant = thermo.get(
            "pump_time_constant_seconds", 300.0
        )
        self.startup_delay = thermo.get("startup_delay_seconds", 600.0)

        delta_t_design = self.target_temp - self.inlet_temp
        power_watts = self.nominal_power * 1_000_000
        self.nominal_mass_flow = power_watts / (
            self.helium_cp * delta_t_design
        )

        self.current_power = 0.0
        self.current_temp = self.inlet_temp
        self.current_mass_flow = 0.0

    def get_thermal_stats(self, time: float) -> tuple[float, float, float]:
        flow_factor = 1 - np.exp(-time / self.pump_time_constant)
        self.current_mass_flow = self.nominal_mass_flow * flow_factor

        if time < self.startup_delay:
            self.current_power = 0.0
        else:
            reactor_time = time - self.startup_delay
            power_factor = 1 - np.exp(-reactor_time / self.time_constant)
            self.current_power = self.nominal_power * power_factor

        if self.current_mass_flow < 0.1:
            self.current_temp = self.inlet_temp
        else:
            current_power_watts = self.current_power * 1_000_000
            delta_t = current_power_watts / (
                self.current_mass_flow * self.helium_cp
            )
            self.current_temp = self.inlet_temp + delta_t

        if time > (3 * self.time_constant):
            self.current_temp += np.random.uniform(-0.5, 0.5)

        return self.current_power, self.current_temp, self.current_mass_flow
