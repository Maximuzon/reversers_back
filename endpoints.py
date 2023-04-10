from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from schemas import User,Place, Review
from response_model import UsersRead, PlacesRead


app = FastAPI()

# @app.get("/")
# async def root():
#     return{"Hello":"Max"}
# Dependency to get the database session
def get_db():
    db_url = "mysql://doadmin:AVNS_ixs6LYwnPYYNRCz3SRl@db-reversers-do-user-13881334-0.b.db.ondigitalocean.com:25060/defaultdb?"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Endpoint to get all users


#Get all users
@app.get("/users", response_model=List[UsersRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

#Get specific USER based on id
@app.get("/users/{user_id}", response_model=UsersRead)
def read_users(user_id:int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.user_id == user_id ).first()

#Get all places
@app.get("/places", response_model=List[PlacesRead])
def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Place).offset(skip).limit(limit).all()

#Get specific PLACE based on id
@app.get("/places/{place_id}", response_model=PlacesRead)
def read_places(place_id: int, db: Session = Depends(get_db)):
    return db.query(Place).filter(Place.place_id == place_id ).first()

