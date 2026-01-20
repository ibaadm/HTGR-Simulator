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

        self.recovery_factor = config_dict.get("physics", {}).get(
            "expansion_recovery_factor", 0.90
        )

    def calculate_output(
        self, thermal_power_in: float, t_inlet_c: float
    ) -> tuple[float, float, float]:
        """
        Calculates power generated, heat remaining, and exhaust temperature.
        Follows the First Law (Q_in = Work + Q_exhaust) and expansion physics.
        """

        work_out = thermal_power_in * self.thermal_eff * self.gen_eff
        heat_exhaust = thermal_power_in - work_out

        t_exhaust = t_inlet_c * (1 - self.thermal_eff * self.recovery_factor)

        return work_out, heat_exhaust, t_exhaust
