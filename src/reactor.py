import numpy as np

class HTGRCore:
    """
    High Temperature Gas Reactor (HTGR) Core Model.
    Includes First-Order Thermal Inertia and Mass Flow Calculation.
    """

    def __init__(self, config_dict):
        """Initialize the core with physics constants from reactor.yaml."""
        if config_dict is None:
            config_dict = {}

        self.nominal_power = config_dict.get('design_specs', {}).get('nominal_thermal_power_mw', 30.0)
        
        thermo = config_dict.get('thermodynamics', {})
        self.target_temp = thermo.get('target_outlet_temp_c', 850.0)
        self.inlet_temp = thermo.get('inlet_temperature_c', 395.0)
        self.helium_cp = thermo.get('specific_heat_helium_j_kg_k', 5195.0)
        self.time_constant = thermo.get('thermal_time_constant_seconds', 1200.0)

        self.current_power = 0.0
        self.current_temp = self.inlet_temp

    def get_thermal_stats(self, time):
        """Calculates Power, Temp, and Mass Flow using Thermal Inertia."""
        
        inertia_factor = 1 - np.exp(-time / self.time_constant)
        
        self.current_power = self.nominal_power * inertia_factor

        delta_t_total = self.target_temp - self.inlet_temp
        self.current_temp = self.inlet_temp + (delta_t_total * inertia_factor)

        if time > (3 * self.time_constant):
             self.current_temp += np.random.uniform(-0.5, 0.5)
        
        delta_t_current = self.current_temp - self.inlet_temp

        if delta_t_current <= 0.1:
            mass_flow_kg_s = 0.0
        else:
            power_watts = self.current_power * 1_000_000
            mass_flow_kg_s = power_watts / (self.helium_cp * delta_t_current)

        return self.current_power, self.current_temp, mass_flow_kg_s