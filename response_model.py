import json
from typing import List, Optional,Any
from typing import Dict
from MySQLdb import Timestamp
from pydantic import BaseModel, EmailStr, validator, Json
from sqlalchemy import DateTime
class UsersRead(BaseModel):
    user_id: int
    login: str
    phone: str
    email: str
    age: str
    profession: str
    married: str
    gender: str
    city: str
    info_show: bool
    coins: int
    avatar: Optional[str] = None # Set None as the default value for nullable fields
    status: str
    preferences: Optional[str]
    favourites: Optional[str] 
    anchors: Optional[str] #!!!!!!!!!!!!!!
    rewards: Optional[str]  #!!!!!!!!!!!!!!
    recommendations: Optional[str] 

    class Config:
        orm_mode = True
        
        
class CreateUser(BaseModel):
    user_id: int
    login: str
    password: str
    phone: str
    email: str
    age: Optional[str]
    profession: Optional[str]
    city: Optional[str]
    married: Optional[str]
    gender:Optional[str]
    info_show: bool
    coins: int
    avatar: Optional[str] = None
    status: Optional[str]
    preferences: Dict[str, str] 
    favourites: Optional[str] 
    anchors: Dict[str, Optional[str]]
    rewards: Dict[str, Optional[str]] 
    recommendations: Optional[str]

    class Config:
        orm_mode = True



class PlacesRead(BaseModel):
    place_id: int
    name: str
    city_name: str
    two_gis_url: str
    geometry_name: str
    phone: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    likes: int
    instagram_link: Optional[str]
    category: str
    subcategory: str
    start_work_time: Optional[str]
    end_work_time: Optional[str]
    tags: Dict[str, Optional[str]] = None
    images: Optional[str] = None
    marks: Dict[str, Optional[str]] = None
    class Config:
        orm_mode = True


class CreatePlace(BaseModel):
    place_id: int
    name: str
    city_name: Optional[str]
    two_gis_url: Optional[str]
    geometry_name: Optional[str]
    phone: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    likes: int
    instagram_link: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    start_work_time: Optional[str]
    end_work_time: Optional[str]
    tags: Dict[str, Optional[str]] = None
    images: Optional[List[str]] = None
    marks: Dict[str, Optional[str]] = None

    class Config:
        orm_mode = True

class createurl(BaseModel):
    place_id:int
    url: str

    class config:
        orm_mode = True

class ReviewRead(BaseModel):
    review_id: int
    place_id: int
    user_id: int
    date: Timestamp
    text: str
    mark: int
    image: Optional[str] = None

    class Config:
        orm_mode = True

class ReviewReadbyPlace(BaseModel):
    review_id: int
    place_id: int
    user_id: int
    date: Timestamp
    text: str
    mark: int
    image: Optional[str] = None
    login: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        orm_mode = True

class CreateReview(BaseModel):
    review_id: int  
    place_id: int
    user_id: int
    date: Timestamp
    text: str
    mark: int
    image: Optional[str]

    class Config:
        orm_mode = True

        
class Placestags(BaseModel):
    place_id: int
    tags :str
    @validator('tags')
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                pass
        raise ValueError('tags must be a JSON-encoded string')
        
    class Config:
        orm_mode = True
            
class GetAllPlaces(BaseModel):
    tags: List[str]
        
class UserBase(BaseModel):
    email: EmailStr


    
