class HeatRejectionSystem:
    """
    Models the Water Independent Heat Rejection System.
    
    CONSTRAINT UPDATE:
    Per competition rules for teams without a Cooling sub-team:
    1. Fix bottom cycle temp to 50C (Handled in Rankine Cycle).
    2. Parasitic load is 1% of rejected heat.
    """

    def __init__(self, config_dict=None):
        # We accept config_dict to keep architecture consistent,
        # even if we don't use it for this simplified rule.
        pass

    def calculate_parasitic_load(self, waste_heat_mw: float) -> float:
        """
        Calculates the electricity required to run pumps/fans.
        Rule: 1% of the heat being rejected.

        Args:
            waste_heat_mw (float): The heat leaving the condenser.

        Returns:
            float: Electricity consumed (MW).
        """
        parasitic_ratio = 0.01 # 1% Rule
        return waste_heat_mw * parasitic_ratio