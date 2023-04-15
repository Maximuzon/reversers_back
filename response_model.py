import json
from typing import List, Optional
from typing import Dict
from pydantic import BaseModel, EmailStr, validator, Json
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
    preferences: Dict[str, str] = None
    favourites: Optional[str] = None
    anchors: Optional[str] = None #!!!!!!!!!!!!!!
    rewards: Optional[str] = None #!!!!!!!!!!!!!!
    recommendations: Optional[str] = None

    class Config:
        orm_mode = True
        
        
class CreateUser(BaseModel):
    user_id: int
    login: str
    password: str
    phone: str
    email: str
    age: str
    profession: str
    city: str
    married: str
    gender:str
    info_show: bool
    coins: int
    avatar: Optional[str] = None # Set None as the default value for nullable fields
    status: str
    preferences: Dict[str, str] = None
    favourites: Optional[str] = None
    anchors: Optional[str] = None #!!!!!!!!!!!!!!
    rewards: Optional[str] = None #!!!!!!!!!!!!!!
    recommendations: Optional[str] = None

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
    tags: Dict[str, str] = None
    images: Optional[List[str]] = None
    marks: Optional[List[str]]

class CreatePlace(BaseModel):
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
    tags: Dict[str, str] = None
    images: Optional[List[str]] = None
    marks: Optional[List[str]]

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


    
