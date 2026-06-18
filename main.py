from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Create the ENGINE instance (not the function!)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_match"
engine = create_engine(DATABASE_URL)

# 2. Base and session
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Your model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    description = Column(String)

# 4. Create tables — pass engine INSTANCE, not the function
Base.metadata.create_all(bind=engine)

# 5. App
app = FastAPI()

from pydantic import BaseModel


# Request body schema
class UserCreate(BaseModel):
    name: str


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST API
@app.post("/users")
def create_user(user: UserCreate):
    db = SessionLocal()

    new_user = User(name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.close()

    return {"msg": "User created", "data": {"id": new_user.id, "name": new_user.name}}

@app.get("/users")
def get_users():
    db = SessionLocal()

    users = db.query(User).all()

    db.close()

    return {"data": users}