import gurobipy as gp
from gurobipy import GRB, quicksum
import pandas as pd
from src.database import engine

class LogisticsOptimizer:
    def __init__(self, output_flag=0):
        self.output_flag = output_flag

    def _fetch_data(self):
        df_demand = pd.read_sql("demand_nodes", engine)
        df_truck = pd.read_sql("truck_nodes", engine)
        df_routes = pd.read_sql("routes", engine)
        df_config = pd.read_sql("config", engine)
        return df_demand, df_truck, df_routes, df_config

    def solve(self):
        df_demand, df_truck, df_routes, df_config = self._fetch_data()

        if df_config.empty:
            return {"status": "ERROR", "message": "Configuration data missing."}

        # Parameters
        unit_price = df_config.iloc[0]['unit_price']
        unit_cost = df_config.iloc[0]['unit_cost']
        vehicle_cost_value = df_config.iloc[0]['vehicle_fixed_cost']
        profit_per_unit = unit_price - unit_cost

        # Data Structures
        vehicle_locations = df_truck['id'].tolist()
        demand_nodes = df_demand['id'].tolist()
        
        scaled_demand = {}
        valid_pairs = []
        
        for _, row in df_routes.iterrows():
            i = row['truck_node_id']
            j = row['demand_node_id']
            sd = row['scaled_demand']
            if sd > 0:
                scaled_demand[(i, j)] = sd
                valid_pairs.append((i, j))
                
        vehicle_fixed_cost = {t: vehicle_cost_value for t in vehicle_locations}

        # Gurobi Model
        m = gp.Model("Logistics_Network_Optimization")
        m.setParam('OutputFlag', self.output_flag)

        # Variables
        z = m.addVars(vehicle_locations, vtype=GRB.BINARY, name="OpenVehicle")
        x = m.addVars(valid_pairs, vtype=GRB.BINARY, name="Assign")

        # Constraints
        for j in demand_nodes:
            vehicles_that_can_serve_j = [(i, jj) for (i, jj) in valid_pairs if jj == j]
            if vehicles_that_can_serve_j:
                m.addConstr(
                    quicksum(x[(i, jj)] for (i, jj) in vehicles_that_can_serve_j) == 1,
                    name=f"OneVehicle_{j}"
                )
        
        for (i, j) in valid_pairs:
            m.addConstr(x[(i, j)] <= z[i], name=f"Activation_{i}_{j}")

        # Objective
        m.setObjective(
            quicksum(profit_per_unit * scaled_demand[(i, j)] * x[(i, j)] for (i, j) in valid_pairs)
            - quicksum(vehicle_fixed_cost[i] * z[i] for i in vehicle_locations),
            GRB.MAXIMIZE
        )

        m.optimize()

        # Result Formatting
        if m.status == GRB.OPTIMAL:
            chosen_vehicles = [i for i in vehicle_locations if z[i].X > 0.5]
            assignments = {}
            for i in chosen_vehicles:
                assigned_nodes = []
                for j in demand_nodes:
                    if (i, j) in valid_pairs and x[(i, j)].X > 0.5:
                        assigned_nodes.append(j)
                if assigned_nodes:
                    assignments[i] = assigned_nodes
            
            return {
                "status": "OPTIMAL",
                "optimal_profit": m.objVal,
                "chosen_trucks": chosen_vehicles,
                "assignments": assignments
            }
        
        return {"status": "INFEASIBLE_OR_UNBOUNDED", "optimal_profit": 0.0, "chosen_trucks": [], "assignments": {}}
