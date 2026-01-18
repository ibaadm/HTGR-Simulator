from iapws import IAPWS97

class RankineCycle:
    def __init__(self):
        self.boiler_pressure_mpa = 10.0      
        self.turbine_efficiency = 0.85       
        self.pinch_point_delta_t = 30.0      

        self.condenser_temp_c = 50.0 

    def calculate_output(self, heat_input_mw: float, gas_exhaust_temp_c: float):
        if gas_exhaust_temp_c < (self.condenser_temp_c + 20):
            return 0.0, heat_input_mw

        target_steam_temp_c = gas_exhaust_temp_c - self.pinch_point_delta_t
        if target_steam_temp_c > 600.0: target_steam_temp_c = 600.0
        t_steam_k = target_steam_temp_c + 273.15

        try:
            steam_in = IAPWS97(P=self.boiler_pressure_mpa, T=t_steam_k)
            h1 = steam_in.h
            s1 = steam_in.s

            t_condenser_k = self.condenser_temp_c + 273.15

            condenser_state = IAPWS97(T=t_condenser_k, x=0) 
            p_condenser = condenser_state.P
            h_liquid = condenser_state.h

            steam_out_ideal = IAPWS97(P=p_condenser, s=s1)
            h2_ideal = steam_out_ideal.h

            delta_h_real = (h1 - h2_ideal) * self.turbine_efficiency

            energy_added_per_kg = h1 - h_liquid
            mass_flow_kg_s = heat_input_mw * 1000 / energy_added_per_kg

            electric_power_mw = (mass_flow_kg_s * delta_h_real) / 1000.0
            waste_heat_mw = heat_input_mw - electric_power_mw

            return electric_power_mw, waste_heat_mw

        except Exception as e:
            print(f"Rankine Error: {e}")
            return 0.0, heat_input_mw