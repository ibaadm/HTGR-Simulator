class BraytonCycle:
    """Model of a Closed-Cycle Gas Turbine (Brayton Cycle)."""

    def __init__(self, config_dict: dict) -> None:
        self.gamma = config_dict.get("physics", {}).get("gamma", 1.66)
        self.gen_eff = config_dict.get("physics", {}).get(
            "generator_efficiency", 0.98
        )

        p_ratio = config_dict.get("design_point", {}).get(
            "pressure_ratio", 2.5
        )
        exponent = (self.gamma - 1) / self.gamma
        self.thermal_eff = 1 - (1 / p_ratio**exponent)

    def calculate_performance(
        self, thermal_power_in: float
    ) -> tuple[float, float]:
        """
        Calculates both the power generated and the heat remaining.
        Follows the First Law: Q_in = Work + Q_exhaust
        """

        work_out = thermal_power_in * self.thermal_eff * self.gen_eff
        heat_exhaust = thermal_power_in - work_out

        return work_out, heat_exhaust
