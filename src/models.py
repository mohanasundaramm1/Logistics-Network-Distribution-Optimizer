from pydantic import BaseModel, Field, field_validator
import logging
import os

# Configure Logging to logs/ directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'ingestion.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DemandNodeSchema(BaseModel):
    id: str
    name: str | None = None
    x: float
    y: float
    demand: int = Field(..., ge=0)

    @field_validator('id')
    def id_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('ID cannot be empty')
        return v

class TruckNodeSchema(BaseModel):
    id: str
    x: float
    y: float

class RouteSchema(BaseModel):
    demand_node_id: str
    truck_node_id: str
    distance: float = Field(..., ge=0)
    scaled_demand: float = Field(..., ge=0)

class ConfigSchema(BaseModel):
    unit_price: float = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)
    vehicle_fixed_cost: float = Field(..., gt=0)
