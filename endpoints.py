# coding: utf-8
from io import BytesIO
import json
import re
from typing import List, Dict, Optional
from fastapi import FastAPI, Depends,File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import sqlalchemy
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import Select, create_engine, MetaData, func, text, insert,update
from sqlalchemy.orm import sessionmaker
import uvicorn
from schemas import User,Place, Review
from response_model import ReviewRead, UsersRead, PlacesRead, CreateUser, CreatePlace,CreateReview, ReviewReadbyPlace
import schemas
from fastapi.middleware.cors import CORSMiddleware
from boto3 import session
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
#uvicorn endpoints:app --reload
#c:/Users/Max/virtualENV/Scripts/Activate.ps1

#личная страница добавить эндпоинты для аватарки. загрузка в базу(апдэйт всего юзера ), вернуть изображение на фронт. 
#эндпоинты по возвращению нескольких изображений в виде словаря. Изменить поле images в Place_id done
#эндпоинты. по нажатию на сердечко, добавить пользователю в favourites атрибту place_id.  в таблице place этому же place_id прибавить +1 в likes. done

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # здесь можно указать список разрешенных origin
    allow_credentials=True,
    allow_methods=["*"], # здесь можно указать список разрешенных HTTP методов
    allow_headers=["*"], # здесь можно указать список разрешенных заголовков
)


ACCESS_ID = 'DO00EJLHPYCCTDA4TWBF'
SECRET_KEY = 'ILuVkUqKIyaBjJkXrfBNUFCwWbsxIgGiskahP3WY7f4'

# Initiate session
session = session.Session()
s3 = session.client('s3',
                        region_name='fra1',
                        endpoint_url='https://reversers-api-spaces.fra1.digitaloceanspaces.com',
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY)

bucket_name = 'reversers-api-spaces'
@app.get("/")
async def root():
    return {"message": "Не кроши на меня хлебушек."}

# Dependency to get the database session
def get_db():
    db_url = "mysql://doadmin:AVNS_nmPqJUMf-G0O503ByqG@db-mysql-fra1-14046-do-user-14174856-0.b.db.ondigitalocean.com:25060/defaultdb?"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#image generative function 
def generate_image_url(url: str):
    if url is not None:
        bucket_name = 'reversers-api-spaces'
        pattern = r'(?<=com\/).*'
        match = re.search(pattern, url)
        url_access = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': match.group(0)},
            ExpiresIn=3600
        )
        return url_access
    return None




# Endpoint to get all users

@app.put("/uploadfile/{place_id}")
async def upload_image(place_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

    # Save the image to DigitalOcean Spaces
    file_contents = await file.read()
    file = BytesIO(file_contents)
    timestamp = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    filename = f"{place_id}_{timestamp}"
    bucket_name = 'reversers-api-spaces'
    print(filename)
    object_key = f"base/{filename}"
    print("set object key")
    print(object_key)
    print(bucket_name)
    s3.upload_fileobj(file, bucket_name, object_key)
    print("file uploaded")
    # Update the existing record in the database with the new image URL

    existing_place = db.query(Place).filter(Place.place_id == place_id).first()
    if existing_place:
        image_urls = json.loads(existing_place.images) if existing_place.images else []
        image_urls.append("https://{0}.fra1.digitaloceanspaces.com/{1}".format(bucket_name, object_key))
        new_images = json.dumps(image_urls)
        stmt = update(Place).where(Place.place_id == place_id).values(images=new_images)
        db.execute(stmt)
        db.commit()
        return {"message": "Image uploaded and database updated successfully"}
    else:
        return {"message": "Place not found"}
    
    # url = "https://{0}.fra1.digitaloceanspaces.com/{1}".format(bucket_name, object_key)
    # print(url)
    # stmt = (update(Place).where(Place.place_id==place_id).values(images = url))
    # db.execute(stmt)
    # db.commit()
    # print("query added")




@app.get("/getimage/{place_id}")
def get_images(place_id: int, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.place_id == place_id).first() 
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    images_json = place.images
    images_list = json.loads(images_json)
    pre_signed_urls = []
    for url in images_list:
        pattern = r'(?<=com\/).*'
        match = re.search(pattern, url)
        url_access = s3.generate_presigned_url(ClientMethod='get_object',
                                Params={'Bucket': bucket_name,
                                        'Key': match.group(0)},
                                ExpiresIn=3600)
        pre_signed_urls.append(url_access)
    return pre_signed_urls



#Get all users

@app.get("/users", response_model=List[UsersRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

#Get specific USER based on id
@app.get("/users/{user_id}")
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

#check the user
@app.post("/users/check")
async def check_user(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    user = db.query(User).filter_by(email=email, password=password).first()
    print(user)
    if user:
        return {"user_id": user.user_id}
    else:
        return {"message": "User does not exist"}
    
#return amount of reviews of the user
@app.get("/user/reviews/{user_id}")
def get_reviews(user_id:int, db: Session = Depends(get_db)):
     reviews = db.query(Review).filter(Review.user_id == user_id).all()
     user = db.query(User).filter(User.user_id ==user_id).first()
     review_list = []
     for review in reviews:
         review_dict = {
             "review_id": review.review_id,
             "login": user.login,
             "place_id": review.place_id,
             "user_id": review.user_id,
             "date": review.date,
             "text": review.text,
             "mark": review.mark,
             "review_likes": review.likes,
             'review_dislikes':review.dislikes,
             'avatar': generate_image_url(review.image),
             'review_image': generate_image_url(review.image)
         }
         review_list.append(review_dict)
     return review_list

@app.get("/user/reviews/count/{user_id}")
def get_reviews(user_id:int, db: Session = Depends(get_db)):
    reviews_count = db.query(func.count(Review.review_id)).filter(Review.user_id == user_id).scalar()
    return reviews_count

# #add favorite
# @app.put("/user/addfavorite/{user_id}/{place_id}")
# def add_favorite(user_id: int, place_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.user_id == user_id).first()
#     user.favourites += f"{place_id},"
#     place = db.query(Place).filter(Place.place_id == place_id).first()
#     place.likes += 1
#     db.add(user)
#     db.commit()
    # leshagei = user.favourites
    # leshagei.update({f"{len(leshagei)+1}":place_id})


@app.put("/user/addfavorite/{user_id}/{place_id}")
def add_favorite(user_id: int, place_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    favourites = json.loads(user.favourites) if user.favourites else {}
    place = db.query(Place).filter(Place.place_id == place_id).first()

    # Check if the place is already in the user's favorites
    if str(place_id) in favourites:
        # Remove the place from the user's favorites
        favourites.pop(str(place_id))
        # Decrease the like count for the place
        place.likes -= 1
    else:
        # Add the place to the user's favorites
        favourites[str(place_id)] = place_id
        # Increase the like count for the place
        place.likes += 1

    user.favourites = json.dumps(favourites)
    db.add(user)
    db.add(place)
    db.commit()


    


#update the user
@app.put("/user/{user_id}")
def update_user(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    return {"message": f"User {user_id} updated successfully"}

#upload image for the user
@app.put("/uploadavatar/{user_id}")
async def upload_image(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

    # Save the image to DigitalOcean Spaces
    file_contents = await file.read()
    file = BytesIO(file_contents)
    #filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    filename = user_id
    bucket_name = 'reversers-api-spaces'
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
    stmt = (update(User).where(User.user_id==user_id).values(avatar = url))
    db.execute(stmt)
    db.commit()
    print("query added")

@app.get("/user/avatar/{user_id}")
def get_image(user_id:int, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first() 
    if user is None or user.avatar is None:
        # Return a default "image not found" URL or message
        return {"message": "Image not found"}
    else:
        url = user.avatar
        bucket_name = 'reversers-api-spaces'
        pattern = r'(?<=com\/).*'
        match = re.search(pattern, url)
        print(match)
        url_access = s3.generate_presigned_url(ClientMethod='get_object',
                                               Params={'Bucket': bucket_name,
                                                       'Key': match.group(0)},
                                               ExpiresIn=3600)
        return url_access

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

@app.get("/review/{place_id}", response_model=List[ReviewReadbyPlace])
def read_places(place_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(Review.place_id == place_id)
        .options(joinedload(Review.user))  # Include user relationship
        .all()
    )

    result = []
    for review in reviews:
        url = review.image
        if url is not None:
            review.image = generate_image_url(url)

        user_id = review.user_id
        user = db.query(User).filter(User.user_id == user_id).first()
        login = user.login if user else None
        avatar = generate_image_url(user.avatar) if user else None
    

        review_read = ReviewReadbyPlace.from_orm(review)
        review_read.login = login
        review_read.avatar = avatar

        result.append(review_read)

    return result
    



#add new REVIEW
@app.post("/reviews")
def create_review(place: CreateReview, db: Session = Depends(get_db)):
    db_review = schemas.Review(**place.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.post("/review/imageupload/{review_id}")
async def upload_image(review_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

    # Save the image to DigitalOcean Spaces
    file_contents = await file.read()
    file = BytesIO(file_contents)
    #filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    filename = review_id
    bucket_name = 'reversers-api-spaces'
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
    stmt = (update(Review).where(Review.review_id==review_id).values(image = url))
    db.execute(stmt)
    db.commit()
    print("query added")



@app.get("/review/getimage/{review_id}")
def get_image(review_id:int, db:Session = Depends(get_db)):
    place = db.query(Review).filter(Review.review_id == review_id).first() 
    url = place.image
    bucket_name = 'reversers-api-spaces'
    pattern = r'(?<=com\/).*'
    match = re.search(pattern, url)
    print(match)
    url_access = s3.generate_presigned_url(ClientMethod='get_object',
                                Params={'Bucket': bucket_name,
                                        'Key': match.group(0)},
                                ExpiresIn=3600)
    return url_access


@app.get("/review/images/getall/{place_id}")
def get_images(place_id:int,db:Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.place_id==place_id).all()
    
    url_dict = {}
    bucket_name = 'reversers-api-spaces'
    pattern = r'(?<=com\/).*'

    for review in reviews:
        url = str(review.image)
        match = re.search(pattern, url)
        print(match)
        if match:
            url_access = s3.generate_presigned_url(ClientMethod='get_object',
                                    Params={'Bucket': bucket_name,
                                            'Key': match.group(0)},
                                    ExpiresIn=3600)
            url_dict[review.review_id] = str(url_access)
        else:
            url_dict[review.review_id] = None

    return url_dict

# receive place_id, return dict["review_id":image]

@app.put("/reviews/{user_id}/{review_id}/like")
def like_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found. Please login or create a new user.")
    
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    
    reviews_liked = json.loads(user.reviews_liked) if user.reviews_liked else {}
    reviews_disliked = json.loads(user.reviews_disliked) if user.reviews_disliked else {}

    str_review_id = str(review_id)
    if str_review_id not in reviews_disliked:
        if str_review_id not in reviews_liked:
            review.likes += 1
            reviews_liked[str_review_id] = review_id
            user.reviews_liked = json.dumps(reviews_liked)

            db.commit()
            return {"message": "Review liked successfully"}
        else:
            review.likes -= 1
            del reviews_liked[str_review_id]
            user.reviews_liked = json.dumps(reviews_liked)

            db.commit()
            return {"message": "Review like removed"}

    return {"message": "Review cannot be liked by the user. Already exists in opposite array"}


@app.put("/reviews/{user_id}/{review_id}/dislike")
def dislike_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found. Please login or create a new user.")
    
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    
    reviews_liked = json.loads(user.reviews_liked) if user.reviews_liked else {}
    reviews_disliked = json.loads(user.reviews_disliked) if user.reviews_disliked else {}

    str_review_id = str(review_id)
    if str_review_id not in reviews_liked:
        if str_review_id not in reviews_disliked:
            review = db.query(Review).filter(Review.review_id == review_id).first()
            review.dislikes += 1
            reviews_disliked[str_review_id] = review_id
            user.reviews_disliked = json.dumps(reviews_disliked)

            db.commit()
            return {"message": "Review disliked successfully"}
        else:
            review = db.query(Review).filter(Review.review_id == review_id).first()
            review.dislikes -= 1
            del reviews_disliked[str_review_id]
            user.reviews_disliked = json.dumps(reviews_disliked)

            db.commit()
            return {"message": "Review dislike removed"}

    return {"message": "Review cannot be disliked by the user. Already exists in opposite array"}

@app.get("/user/{user_id}/like")#дописать эндпоинты
def return_likes(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    return {user.reviews_liked}

@app.get("/user/{user_id}/dislike")#дописать эндпоинты
def return_likes(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    return {user.reviews_disliked}


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

@app.get("/test/cycle")#дописать эндпоинты
def return_likes(db: Session = Depends(get_db)):
    places = db.query(Place).all()
    for place in places:
        reviews = db.query(Review).filter_by(place_id=place.place_id).all()
        if reviews:
            total_mark = sum(review.mark for review in reviews)
            average_mark = total_mark / len(reviews)
            place.rating = average_mark

def get_db_sch():
    db_url = "mysql://doadmin:AVNS_nmPqJUMf-G0O503ByqG@db-mysql-fra1-14046-do-user-14174856-0.b.db.ondigitalocean.com:25060/defaultdb?"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        return db  # Return the database session directly
    finally:
        db.close()



def calculate_ratings():
    db = get_db_sch()  # Call get_db to retrieve the database session
    places = db.query(Place).all()
    logging.info("Opened connection, starting cycle")
    for place in places:
        reviews = db.query(Review).filter_by(place_id=place.place_id).all()
        logging.info("got reviews, working")
        if reviews:
            total_mark = sum(review.mark for review in reviews)
            average_mark = total_mark / len(reviews)
            place.rating = average_mark
        else:
            place.rating = None
    db.commit() 

    logging.info("Rating calculation job completed successfully.")

# Configure logging
logging.basicConfig(level=logging.INFO)
scheduler = BackgroundScheduler()
scheduler.add_job(calculate_ratings, 'interval', minutes=10)  
scheduler.start()


if __name__ == "__main__":
    uvicorn.run(app,host='0.0.0.0', port = 8000)
