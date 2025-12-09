import numpy as np
import pandas as pd
import yaml
import os

# Import your custom modules
# (If these imports fail, make sure your __init__.py files exist!)
from src.reactor import HTGRCore
from src.brayton_cycle import BraytonCycle
from src.rankine_cycle import RankineCycle
from src.heat_rejection_system import HeatRejectionSystem

class PlantModel:
    """
    The Integrated Plant Model (IPM).
    Orchestrates the data flow between Physics, Cycles, and Cooling.
    """

    def __init__(self, config_path="config"):
        """
        Initialize all subsystems and load configuration.
        """
        print(f"Initializing Plant Model from: {config_path}")
        self.config_path = config_path
        self.results = [] # Storage for the simulation log

        # 1. Load Configurations
        self.sim_cfg = self._load_yaml("simulation.yaml")
        self.reactor_cfg = self._load_yaml("reactor.yaml")
        self.brayton_cfg = self._load_yaml("brayton.yaml")
        self.rankine_cfg = self._load_yaml("rankine.yaml")
        self.cooling_cfg = self._load_yaml("heat_rejection.yaml")

        # 2. Instantiate Subsystems (The "Machines")
        # We pass the config dictionaries into them so they know their limits
        self.core = HTGRCore(self.reactor_cfg)
        self.brayton = BraytonCycle(gas_type=self.reactor_cfg['thermodynamics']['coolant_gas'])
        self.rankine = RankineCycle()
        self.heat_rejection = HeatRejectionSystem()

        # 3. Initialize State
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
        # Load timing settings
        settings = self.sim_cfg.get('time_settings', {})
        duration = settings.get('duration', 86400) # Default 24 hours
        dt = settings.get('dt', 1.0)               # Default 1 second step

        print(f"--- Starting Transient Simulation ({duration}s) ---")

        # THE SIMULATION LOOP
        for t in range(int(duration)):
            self.current_time = t

            # --- STEP 1: REACTOR (Source) ---
            # Get heat output from the core
            # (Note: You need to implement get_thermal_stats in reactor.py next!)
            q_core_mw, t_outlet_c = self.core.get_thermal_stats(time=t)

            # --- STEP 2: BRAYTON CYCLE (Top Cycle) ---
            # Calculate efficiency based on pressure ratio (from config)
            p_ratio = self.brayton_cfg['design_point']['pressure_ratio']
            eta_gas = self.brayton.get_efficiency(p_ratio)
            
            # Calculate power
            p_gas_mw = self.brayton.get_power_output(q_core_mw, eta_gas)
            
            # Calculate Exhaust Heat (What's left over?)
            # Energy Out = Energy In - Work Done
            q_exhaust_mw = q_core_mw - p_gas_mw
            
            # Physics: Estimate Exhaust Temp (Simplified adiabatic drop)
            # T_exhaust = T_in * (1 - efficiency * losses)
            t_exhaust_c = t_outlet_c * (1 - eta_gas * 0.95) 

            # --- STEP 3: RANKINE CYCLE (Bottom Cycle) ---
            # Now returns only 2 values
            p_steam_mw, q_waste_mw = self.rankine.calculate_output(
                heat_input_mw=q_exhaust_mw,
                gas_exhaust_temp_c=t_exhaust_c
            )

            # --- STEP 4: HEAT REJECTION (Sink) ---
            # Just pass the heat. The class applies the 1% rule internally.
            p_fan_mw = self.heat_rejection.calculate_parasitic_load(
                waste_heat_mw=q_waste_mw
            )

            # --- STEP 5: TOTALS ---
            p_net_mw = p_gas_mw + p_steam_mw - p_fan_mw
            
            # Accumulate Total Energy (MWh = MW * hours)
            self.total_energy_produced_mwh += p_net_mw * (dt / 3600.0)

            # --- LOGGING ---
            # Save this second's data to memory
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
        
        # Ensure results directory exists
        output_dir = "results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = os.path.join(output_dir, "simulation_log.csv")
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")
        
        # Print a quick summary for the user
        print(f"Total Energy Generated: {self.total_energy_produced_mwh:.2f} MWh")
        print(f"Average Net Power: {df['Net_Power_MW'].mean():.2f} MW")

# Simple check to run it directly
if __name__ == "__main__":
    sim = PlantModel()
    sim.run()