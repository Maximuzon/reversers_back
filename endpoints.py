from io import BytesIO
import re
from typing import List
from fastapi import FastAPI, Depends,File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import Select, create_engine, MetaData, text, insert,update
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

bucket_name = 'reversers-images'


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
    file_contents = await file.read()
    file = BytesIO(file_contents)
    #filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    filename = place_id
    bucket_name = 'reversers-images'
    print(filename)
    object_key = f"base/{filename}"
    print("set object key")
    print(object_key)
    print(bucket_name)
    s3.upload_fileobj(file, bucket_name, object_key)
    print("file uploaded")
    # Update the existing record in the database with the new image URL
    
    url = "https://{0}.fra1.digitaloceanspaces.com/{1}".format(bucket_name, object_key)
    print(url)
    stmt = (update(Place).where(Place.place_id==place_id).values(images = url))
    db.execute(stmt)
    db.commit()
    print("query added")




#
@app.get("/getimage/{place_id}")
def get_image(place_id:int, db:Session = Depends(get_db)):
    place = db.query(Place).filter(Place.place_id == place_id).first() 
    url = place.images
    bucket_name = 'reversers-images'
    pattern = r'(?<=com\/).*'
    match = re.search(pattern, url)
    print(match)
    url_access = s3.generate_presigned_url(ClientMethod='get_object',
                                Params={'Bucket': bucket_name,
                                        'Key': match.group(0)},
                                ExpiresIn=3600)
    return url_access



@app.get("/users/raw/sql/{user_id}")
def get_raw_users(user_id:int, db: Session = Depends(get_db)):
    query = text(f"select user_id, login, phone from users where user_id = {user_id}")
    result = db.execute(query).fetchone()
    
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
    return db.query(Review).filter(Review.place_id == place_id ).all()

#add new REVIEW
@app.post("/reviews")
def create_review(place: CreateReview, db: Session = Depends(get_db)):
    db_review = schemas.Review(**place.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

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

if __name__ == "__main__":
    uvicorn.run(app,host='0.0.0.0', port = 8000)
