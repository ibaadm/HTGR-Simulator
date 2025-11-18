import numpy as np

class BraytonCycle:
    """Model of a Closed-Cycle Gas Turbine (Brayton Cycle)."""
    
    def __init__(self, gas_type: str = 'helium'):
        if gas_type == 'helium':
            self.gamma = 1.66
        elif gas_type == 'nitrogen':
            self.gamma = 1.4
        else:
            raise ValueError("Unknown gas type. Use 'helium' or 'nitrogen'.")

    def get_efficiency(self, pressure_ratio: float | np.ndarray) -> float | np.ndarray:
        """
        Calculate ideal thermal efficiency.
        Formula: 1 - (1 / r_p ^ ((gamma-1)/gamma))
        """
        
        exponent = (self.gamma - 1) / self.gamma
        efficiency = 1 - (1 / (pressure_ratio ** exponent))
        
        return efficiency

    def get_power_output(self, thermal_power_in: float | np.ndarray, efficiency: float | np.ndarray) -> float | np.ndarray:
        """Calculate electric power output (MW) from thermal input."""
        return thermal_power_in * efficiency