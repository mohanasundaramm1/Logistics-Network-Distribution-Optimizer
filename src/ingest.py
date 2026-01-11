import pandas as pd
import os
import logging
from src.database import init_db, engine
from src.models import DemandNodeSchema, TruckNodeSchema, RouteSchema, ConfigSchema

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

def validate_and_ingest(df, schema_cls, table_name):
    records = df.to_dict(orient="records")
    valid_records = []
    errors = 0
    
    print(f"Validating {len(records)} records for {table_name}...")
    
    for record in records:
        try:
            schema_cls(**record)
            valid_records.append(record)
        except Exception as e:
            errors += 1
            logging.error(f"Validation failed for {table_name}: {e} | Record: {record}")
            
    if errors > 0:
        print(f"WARNING: {errors} records failed validation for {table_name}. Check logs/ingestion.log.")
    
    if valid_records:
        df_valid = pd.DataFrame(valid_records)
        df_valid.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Successfully ingested {len(valid_records)} records into {table_name}.")
    else:
        print(f"No valid records to ingest for {table_name}.")

def ingest_data():
    print("--- Starting ETL Pipeline ---")
    init_db()
    
    # 1. Ingest Demand Nodes
    demand_file = os.path.join(DATA_DIR, "round1-day2_demand_node_data.csv")
    if os.path.exists(demand_file):
        df = pd.read_csv(demand_file).rename(columns={"index": "id"})
        validate_and_ingest(df, DemandNodeSchema, "demand_nodes")
    
    # 2. Ingest Truck Nodes
    truck_file = os.path.join(DATA_DIR, "truck_node_data.csv")
    if os.path.exists(truck_file):
        df = pd.read_csv(truck_file).rename(columns={"index": "id"})
        validate_and_ingest(df, TruckNodeSchema, "truck_nodes")
    
    # 3. Ingest Routes
    route_file = os.path.join(DATA_DIR, "round1-day2_demand_truck_data.csv")
    if os.path.exists(route_file):
        df = pd.read_csv(route_file).rename(columns={
            "demand_node_index": "demand_node_id",
            "truck_node_index": "truck_node_id"
        })
        validate_and_ingest(df, RouteSchema, "routes")
    
    # 4. Ingest Config
    config_file = os.path.join(DATA_DIR, "round1-day2_problem_data.csv")
    if os.path.exists(config_file):
        df = pd.read_csv(config_file).rename(columns={
            "burrito_price": "unit_price",
            "ingredient_cost": "unit_cost",
            "truck_cost": "vehicle_fixed_cost"
        })
        validate_and_ingest(df, ConfigSchema, "config")

    print("--- Pipeline Finished ---")

if __name__ == "__main__":
    ingest_data()
