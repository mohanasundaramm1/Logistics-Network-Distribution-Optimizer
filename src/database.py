from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()

class DemandNode(Base):
    __tablename__ = 'demand_nodes'
    id = Column(String, primary_key=True)
    name = Column(String)
    x = Column(Float)
    y = Column(Float)
    demand = Column(Integer)

class TruckNode(Base):
    __tablename__ = 'truck_nodes'
    id = Column(String, primary_key=True)
    x = Column(Float)
    y = Column(Float)

class Route(Base):
    __tablename__ = 'routes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    demand_node_id = Column(String, ForeignKey('demand_nodes.id'))
    truck_node_id = Column(String, ForeignKey('truck_nodes.id'))
    distance = Column(Float)
    scaled_demand = Column(Float)

class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_price = Column(Float)
    unit_cost = Column(Float)
    vehicle_fixed_cost = Column(Float)

# Dynamic path resolution for the database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "supply_chain.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Ensure directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
