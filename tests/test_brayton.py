import pytest
from src.brayton_cycle import BraytonCycle


def test_brayton_physics_conservation():
    """
    Verifies that Energy In = Work Out + Heat Out,
    proving the First Law of Thermodynamics.
    """

    config = {
        "design_point": {"pressure_ratio": 2.5},
        "physics": {
            "gamma": 1.66,
            "generator_efficiency": 1.0,
            "expansion_recovery_factor": 1.0,
        },
    }
    cycle = BraytonCycle(config)

    q_in = 100.0  # MW
    t_in = 750.0  # C

    work, heat_out, t_out = cycle.calculate_output(q_in, t_in)

    assert (work + heat_out) == pytest.approx(q_in, rel=1e-5)
