import numpy as np

class HTGRCore:
    """
    High Temperature Gas Reactor (HTGR) Core Model.
    Currently uses a simplified thermal-hydraulic model for integration testing.
    """

    def __init__(self, config_dict):
        """
        Initialize the core with physics constants from reactor.yaml.
        """
        # SAFETY CHECK: If config is None (empty file), make it an empty dict
        if config_dict is None:
            config_dict = {}

        # 1. Load Constants
        self.nominal_power = config_dict.get('design_specs', {}).get('nominal_thermal_power_mw', 30.0)
        
        thermo = config_dict.get('thermodynamics', {})
        self.target_temp = thermo.get('target_outlet_temp_c', 850.0)
        self.inlet_temp = thermo.get('inlet_temperature_c', 395.0)
        
        # 2. State Variables
        self.current_power = 0.0
        self.current_temp = self.inlet_temp

    def get_thermal_stats(self, time):
        """
        Calculates the Core State for the current time step.
        
        Args:
            time (int): Simulation time in seconds.
            
        Returns:
            tuple: (Current_Thermal_Power_MW, Outlet_Temperature_C)
        """
        
        # --- DUMMY PHYSICS: STARTUP RAMP ---
        # Real Physics: dP/dt = (rho - beta)/Lambda * P ... (Neutron Kinetics)
        # Dummy Physics: "It takes 1 hour (3600s) to reach full power."
        
        ramp_up_duration = 3600.0 # 1 hour
        
        if time < ramp_up_duration:
            # We are starting up!
            # Fraction of completion (0.0 to 1.0)
            progress = time / ramp_up_duration
            
            # Linear Ramp
            self.current_power = self.nominal_power * progress
            
            # Temperature lags slightly behind power (Thermal Inertia)
            # Temp = Inlet + (Delta_T * progress)
            delta_t = self.target_temp - self.inlet_temp
            self.current_temp = self.inlet_temp + (delta_t * progress)
            
        else:
            # We are at steady state (Full Power)
            self.current_power = self.nominal_power
            self.current_temp = self.target_temp
            
            # --- ADD NOISE (OPTIONAL) ---
            # Make the graph look realistic by adding tiny fluctuations
            # Random fluctuation +/- 0.5 degrees
            noise = np.random.uniform(-0.5, 0.5)
            self.current_temp += noise

        return self.current_power, self.current_temp