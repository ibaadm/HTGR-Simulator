import numpy as np

class HTGRCore:
    """
    High Temperature Gas Reactor (HTGR) Core Model.
    Currently uses a simplified thermal-hydraulic model.
    """

    def __init__(self, config_dict):
        """Initialize the core with physics constants from reactor.yaml."""
        if config_dict is None:
            config_dict = {}

        self.nominal_power = config_dict.get('design_specs', {}).get('nominal_thermal_power_mw', 30.0)
        
        thermo = config_dict.get('thermodynamics', {})
        self.target_temp = thermo.get('target_outlet_temp_c', 850.0)
        self.inlet_temp = thermo.get('inlet_temperature_c', 395.0)

        self.current_power = 0.0
        self.current_temp = self.inlet_temp

    def get_thermal_stats(self, time):
        """Calculates the Core State for the current time step."""
        
        ramp_up_duration = 3600.0
        
        if time < ramp_up_duration:
            progress = time / ramp_up_duration

            self.current_power = self.nominal_power * progress

            delta_t = self.target_temp - self.inlet_temp
            self.current_temp = self.inlet_temp + (delta_t * progress)
            
        else:
            self.current_power = self.nominal_power
            self.current_temp = self.target_temp

            noise = np.random.uniform(-0.5, 0.5)
            self.current_temp += noise

        return self.current_power, self.current_temp