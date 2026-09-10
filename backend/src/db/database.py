from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings

engine = create_engine(
    settings.DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def create_table():
    Base.metadata.create_all(engine)
    if not any(column["name"] == "title" for column in inspect(engine).get_columns("stories")):
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE stories ADD COLUMN title VARCHAR NOT NULL DEFAULT 'Untitled'")
            )
    