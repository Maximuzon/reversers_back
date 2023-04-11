import array
import json
import traceback
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData, func
from sqlalchemy.orm import sessionmaker
from schemas import User,Place, Review
from response_model import UsersRead, PlacesRead, CreateUser, GetAllPlaces
import schemas


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
@app.get("/places/id/{place_id}", response_model=PlacesRead)
def read_places(place_id: int, db: Session = Depends(get_db)):
    return db.query(Place).filter(Place.place_id == place_id ).first()

#Insert NEW USER to user table
@app.post("/users")
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    db_user = schemas.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# @app.get("/places/column/{column_name}", response_model=List[str])
# def get_unique_values(column_name: str, db: Session = Depends(get_db)):
#     query = db.query(getattr(schemas.Place, column_name)).distinct().all()
#     unique_values = [value[0] for value in query if value[0] is not None]
#     return unique_values

# @app.get("/places/column/{column_name}")
# def get_unique_values(column_name: str, db: Session = Depends(get_db)):
#     column = getattr(schemas.Place, column_name)  # Get the column object from the model class
#     query = db.query(func.jsonb_array_elements(column).cast(str).distinct())  # Use func to get unique values from the JSON column
#     results = [row[0] for row in query.all()]  # Extract the results from the query response
#     return results


# @app.get("/places/tags", response_model=list[GetAllPlaces]) 
# def read_places(db: Session = Depends(get_db)):
#     return db.query(Place).all()
# # @app.get("/places/tags", response_model=PlacesRead)
# # def read_places(db: Session = Depends(get_db)):
# #     return db.query(Place).all()


# # @app.get("/places/tags", response_model=PlacesRead)
# # def read_tags(db: Session = Depends(get_db)):
# #     tags_query = db.query(schemas.Place.tags).distinct().all()
# #     tags_list = [tag[0] for tag in tags_query if tag[0] is not None]
# #     return tags_list

# # @app.get("/places/tags", response_model=List[PlacesRead])
# # def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
# #     try:
# #         places =  db.query(Place.tags).offset(skip).limit(limit).all()
# #         return [PlacesRead.from_orm(place) for place in places]
# #     except Exception as e:
# #         traceback.print_exc()
# #         raise e

# # @app.get("/places/tags", response_model=List[str])
# # def read_tags(db: Session = Depends(get_db)):
# #     tags = db.query(Place.tags).distinct().all()
# #     return [tag[0] for tag in tags]