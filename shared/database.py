from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Use SQLite for testing purposes
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Conexão com o banco de dados PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/db_PROJETO_deploy"

# Criar a SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()