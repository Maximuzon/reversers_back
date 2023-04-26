from io import BytesIO
import json
from typing import List
from fastapi import FastAPI, Depends,File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import Select, create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
import uvicorn
from schemas import User,Place, Review
from response_model import ReviewRead, UsersRead, PlacesRead, CreateUser, GetAllPlaces, Placestags, CreatePlace,CreateReview
import schemas
from fastapi.middleware.cors import CORSMiddleware
from boto3 import session
from datetime import datetime
#uvicorn endpoints:app --reload

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # здесь можно указать список разрешенных origin
    allow_credentials=True,
    allow_methods=["*"], # здесь можно указать список разрешенных HTTP методов
    allow_headers=["*"], # здесь можно указать список разрешенных заголовков
)


ACCESS_ID = 'DO00TEVUBHKB6D7XRJXY'
SECRET_KEY = 'iGVqWV85WDk+7RU9svSJOHrFQ4VGsrnYAXp3ILKeDaU'

# Initiate session
session = session.Session()
s3 = session.client('s3',
                        region_name='fra1',
                        endpoint_url='https://reversers-images.fra1.digitaloceanspaces.com',
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY)




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

@app.post("/uploadfile/{place_id}")
async def upload_image(place_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

    # Save the image to DigitalOcean Spaces
    bucket_name = 'reversers-images'
    print("got bucket name")
    file_contents = await file.read()
    print("received file_contents")
    file = BytesIO(file_contents)
    print("decoded file")
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    print("set filename")
    print(filename)
    object_key = f"base/{filename}"
    print("set object key")
    print(object_key)
    s3.upload_fileo(file, bucket_name, object_key)
    print("file uploaded")

    
    # Update the existing record in the database with the new image URL
    query = text(f"UPDATE places SET image='https://{bucket_name}.fra1.digitaloceanspaces.com/{object_key}' WHERE place_id={place_id}")
    print("query added")
    db.execute(query)
    db.commit()

    return {"filename": filename}


@app.get("/getimage/{place_id}")
async def get_image(place_id: int, db: Session = Depends(get_db)):
    query = text(f"SELECT image FROM places WHERE id = {place_id}")
    result = db.execute(query).fetchone()
    if result:
        return result
    else:
        return None


# @app.get("/users/raw/sql/{user_id}")
# def get_raw_users(user_id:int, db: Session = Depends(get_db)):
#     query = text(f"select * from users where user_id = {user_id}")
#     result = db.execute(query).fetchone()
#     print(result)
#     return {"data": result}

@app.get("/users/raw/sql/{user_id}")
def get_raw_users(user_id:int, db: Session = Depends(get_db)):
    query = text(f"select user_id, login, phone from users where user_id = {user_id}")
    
    result = db.execute(query).fetchmany()
    
    if result is not None:
        print(result)
        return {"data": result}
    else:
        return {"data": None}

#Get all users
@app.get("/users", response_model=List[UsersRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

#Get specific USER based on id
@app.get("/users/{user_id}", response_model=UsersRead)
def read_users(user_id:int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.user_id == user_id ).first()

#Insert NEW USER to user table
@app.post("/users")
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    db_user = schemas.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


#Get all places
@app.get("/places", response_model=List[PlacesRead])
def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Place).offset(skip).limit(limit).all()

#Get specific PLACE based on id
@app.get("/places/{place_id}", response_model=PlacesRead)
def read_places(place_id: int, db: Session = Depends(get_db)):
    return db.query(Place).filter(Place.place_id == place_id ).first()

#add NEW PLACE
@app.post("/places")
def create_place(place: CreatePlace, db: Session = Depends(get_db)):
    db_place = schemas.Place(**place.dict())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

#Get all REVIEW
@app.get("/places", response_model=List[ReviewRead])
def read_review(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Review).offset(skip).limit(limit).all()

#Get specific REVIEW based on id
@app.get("/review/{place_id}", response_model=ReviewRead)
def read_places(place_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Place.place_id == place_id ).first()

#add new REVIEW
@app.post("/reviews")
def create_review(place: CreateReview, db: Session = Depends(get_db)):
    db_review = schemas.Review(**place.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


# #RETRIEVE ALL TAGS
# @app.get("/tags")
# async def get_all_tags(db: Session = Depends(get_db)):
#     tags = {}
#     try:
#         # retrieve all rows from the places table
#         query = Select(Place.tags)
#         result = db.execute(query)
#         # extract tags from each row and add to the tags dictionary
#         for row in result:
#             row_tags = row[0]
#             for key, value in row_tags.items():
#                 tags.setdefault(key, []).append(value)
#         return {"tags": tags}
#     finally:
#         db.close()       

#Get user_id





#Get all places
# @app.get("/tags/new")
# def get_all_tags(db: Session = Depends(get_db)):
#     tags = {}
#     places = db.query(Place).all()
#     for place in places:
#         tags.update(place.tags)
#     return tags.items()


#GET TAGS WITHOUT REPETITIONS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.get("/tags")
async def get_all_tags(db: Session = Depends(get_db)):
    tags = {}
    try:
        # retrieve all rows from the places table
        query = Select(Place.tags)
        result = db.execute(query)
        # extract tags from each row and add to the tags dictionary
        for row in result:
            row_tags = row[0]
            for key, value in row_tags.items():
                tags.setdefault(key, []).append(value)
        # convert sets to lists
        for key in tags:
            tags[key] = list(set(tags[key]))
        return {"tags": tags}
    finally:
        db.close()

#return user


# #Get all REVIEWS
# @app.get("/reviews", response_model=List[Revi])
# def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return db.query(Place).offset(skip).limit(limit).all()


# @app.get("/places/column/{column_name}", response_model=List[str])
# def get_unique_values(column_name: str, db: Session = Depends(get_db)):
#     query = db.query(getattr(schemas.Place, column_name)).distinct().all()
#     unique_values = [value[0] for value in query if value[0] is not None]
#     return unique_values
#
# @app.get("/places/column/{column_name}")
# def get_unique_values(column_name: str, db: Session = Depends(get_db)):
#     column = getattr(schemas.Place, column_name)  # Get the column object from the model class
#     query = db.query(func.jsonb_array_elements(column).cast(str).distinct())  # Use func to get unique values from the JSON column
#     results = [row[0] for row in query.all()]  # Extract the results from the query response
#     return results


# @app.get("/places/tags", response_model=list[GetAllPlaces]) 
# def read_places(db: Session = Depends(get_db)):
#     return db.query(Place).all()

# @app.get("/places/tags/{place_id}", response_model=Placestags)
# def read_places(place_id: int, db: Session = Depends(get_db)):
#     return db.query(Place.tags).filter(Place.place_id == place_id )
#______-----------
# @app.get("/places/tags/{place_id}", response_model=Placestags)
# def read_places(place_id: int, db: Session = Depends(get_db)):
#     place = db.query(Place).filter(Place.place_id == place_id).first()
#     tags = Place.tags  # Assuming Place object has a `tags` field
#     return {"place_id": place.place_id,"tags": tags}

# @app.get("/places/tags")
# def get_places():
#     with Session(get_db) as session:
#         places = session.query(Place.place_id, Place.tags).all()
#         return places

if __name__ == "__main__":
    uvicorn.run(app,host='0.0.0.0', port = 8000)
