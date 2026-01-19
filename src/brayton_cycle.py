class BraytonCycle:
    """Model of a Closed-Cycle Gas Turbine (Brayton Cycle)."""

    def __init__(self, config_dict: dict) -> None:
        self.gamma = config_dict.get("physics", {}).get("gamma", 1.66)
        self.gen_eff = config_dict.get("physics", {}).get(
            "generator_efficiency", 0.98
        )

    def get_efficiency(self, pressure_ratio: float) -> float:
        """Calculate ideal thermal efficiency."""

        exponent = (self.gamma - 1) / self.gamma
        efficiency = 1 - (1 / (pressure_ratio**exponent))

        return efficiency

    def calculate_performance(
        self, thermal_power_in: float, efficiency: float
    ) -> tuple[float, float]:
        """
        Calculates both the power generated and the heat remaining.
        Follows the First Law: Q_in = Work + Q_exhaust
        """

        work_out = thermal_power_in * efficiency * self.gen_eff
        heat_exhaust = thermal_power_in - work_out

        return work_out, heat_exhaust
