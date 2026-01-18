import pandas as pd
import yaml
import os

from src.reactor import HTGRCore
from src.brayton_cycle import BraytonCycle
from src.rankine_cycle import RankineCycle

class PlantModel:
    """
    The Integrated Plant Model (IPM).
    Orchestrates the data flow between Physics, Cycles, and Cooling.
    """

    def __init__(self, config_path="config"):
        """Initialize all subsystems and load configuration."""
        
        print(f"Initializing Plant Model from: {config_path}")
        self.config_path = config_path
        self.results = []

        self.sim_cfg = self._load_yaml("simulation.yaml")
        self.reactor_cfg = self._load_yaml("reactor.yaml")
        self.brayton_cfg = self._load_yaml("brayton.yaml")
        self.rankine_cfg = self._load_yaml("rankine.yaml")
        
        self.fan_penalty = self.sim_cfg.get('heat_rejection', {}).get('parasitic_fraction', 0.01)

        self.core = HTGRCore(self.reactor_cfg)
        self.brayton = BraytonCycle(self.brayton_cfg)
        self.rankine = RankineCycle()

        self.current_time = 0.0
        self.total_energy_produced_mwh = 0.0

    def _load_yaml(self, filename):
        """Helper to load yaml files safely."""
        filepath = os.path.join(self.config_path, filename)
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"WARNING: Config file {filename} not found. Using defaults.")
            return {}

    def run(self):
        """
        Main Time-Stepping Loop.
        Runs the simulation from T=0 to T=Duration.
        """

        settings = self.sim_cfg.get('time_settings', {})
        duration = settings.get('duration', 86400)
        dt = settings.get('dt', 1.0)

        print(f"--- Starting Transient Simulation ({duration}s) ---")

        for t in range(int(duration)):
            self.current_time = t

            q_core_mw, t_outlet_c = self.core.get_thermal_stats(time=t)

            p_ratio = self.brayton_cfg['design_point']['pressure_ratio']
            eta_gas = self.brayton.get_efficiency(p_ratio)
            p_gas_mw, q_exhaust_mw = self.brayton.calculate_performance(q_core_mw, eta_gas)
            t_exhaust_c = t_outlet_c * (1 - eta_gas * 0.90) 

            p_steam_mw, q_waste_mw = self.rankine.calculate_output(
                heat_input_mw=q_exhaust_mw,
                gas_exhaust_temp_c=t_exhaust_c
            )

            p_fan_mw = q_waste_mw * self.fan_penalty
            p_net_mw = p_gas_mw + p_steam_mw - p_fan_mw
            self.total_energy_produced_mwh += p_net_mw * (dt / 3600.0)

            self.results.append({
                "Time": t,
                "Reactor_Power_MW": q_core_mw,
                "Reactor_Temp_C": t_outlet_c,
                "Brayton_Power_MW": p_gas_mw,
                "Rankine_Power_MW": p_steam_mw,
                "Parasitic_Load_MW": p_fan_mw,
                "Net_Power_MW": p_net_mw,
                "System_Efficiency": p_net_mw / q_core_mw if q_core_mw > 0 else 0
            })

        print("--- Simulation Complete ---")
        self.save_results()

    def save_results(self):
        """Export the data to CSV for the dashboard."""
        df = pd.DataFrame(self.results)

        output_dir = "results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = os.path.join(output_dir, "simulation_log.csv")
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")

        print(f"Total Energy Generated: {self.total_energy_produced_mwh:.2f} MWh")
        print(f"Average Net Power: {df['Net_Power_MW'].mean():.2f} MW")