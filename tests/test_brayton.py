import pytest
from src.brayton_cycle import BraytonCycle


def test_conservation_of_energy():
    """
    VERIFICATION 1: Conservation of Energy
    Ensures that (Work Out + Heat Exhaust) is exactly equal to (Heat Input).
    """
    config = {
        "design_point": {"pressure_ratio": 2.5},
        "physics": {"gamma": 1.66},
    }
    brayton = BraytonCycle(config)

    input_power = 30.0
    input_temp = 850.0

    work_out, heat_exhaust, t_exhaust = brayton.calculate_output(
        input_power, input_temp
    )

    assert abs((work_out + heat_exhaust) - input_power) < 0.0001


def test_mathematical_consistency():
    """
    VERIFICATION 2: Mathematical Consistency
    Verifies that the class calculates thermal efficiency according
    to the standard Brayton formula: n = 1 - (1 / rp^((g-1)/g))
    """
    p_ratio = 2.0
    gamma = 1.666
    config = {
        "design_point": {"pressure_ratio": p_ratio},
        "physics": {"gamma": gamma},
    }
    brayton = BraytonCycle(config)

    exponent = (gamma - 1) / gamma
    expected_efficiency = 1 - (1 / (p_ratio**exponent))

    assert brayton.thermal_eff == pytest.approx(expected_efficiency, abs=1e-5)


def test_edge_cases_and_stability():
    """
    VERIFICATION 3: Edge Case Handling
    Ensures the simulation does not crash with zero inputs or missing config.
    """
    brayton_default = BraytonCycle({})
    assert brayton_default.gamma == 1.66

    power, heat, temp = brayton_default.calculate_output(0.0, 395.0)
    assert power == 0.0
    assert heat == 0.0
    assert temp < 395.0

    power_neg, _, _ = brayton_default.calculate_output(-10.0, 395.0)
    assert power_neg < 0
