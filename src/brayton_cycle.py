import numpy as np

class BraytonCycle:
    """Model of a Closed-Cycle Gas Turbine (Brayton Cycle)."""
    
    def __init__(self, config_dict):
        self.gamma = config_dict.get('physics', {}).get('gamma', 1.66)

    def get_efficiency(self, pressure_ratio: float | np.ndarray) -> float | np.ndarray:
        """Calculate ideal thermal efficiency."""
        
        exponent = (self.gamma - 1) / self.gamma
        efficiency = 1 - (1 / (pressure_ratio ** exponent))
        
        return efficiency
    
    def calculate_performance(self, thermal_power_in, efficiency):
        """
        Calculates both the power generated and the heat remaining.
        Follows the First Law: Q_in = Work + Q_exhaust
        """
        # Mechanical/Electrical losses (e.g., 98% generator efficiency)
        loss_factor = 0.98 
        
        work_out = thermal_power_in * efficiency * loss_factor
        heat_exhaust = thermal_power_in - work_out
        
        return work_out, heat_exhaust