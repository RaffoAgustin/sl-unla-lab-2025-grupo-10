from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Nombre del archivo SQLite
DATABASE_URL = "sqlite:///./database.db"

# Crear motor (engine)
engine = create_engine( DATABASE_URL, connect_args={"check_same_thread": False})

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para el uso de session de la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Crear tablas
Base.metadata.create_all(bind=engine)