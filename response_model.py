
from typing import List, Optional
<<<<<<< HEAD
from pydantic import BaseModel, EmailStr
=======
from pydantic import BaseModel

>>>>>>> 5f9e5ac59c08639c2159d5ae35ed87180547fa58
class UsersRead(BaseModel):
    user_id: int
    login: str
    phone: str
    email: str
    age: int
    profession: str
    married: str
    info_show: bool
    coins: int
    avatar: Optional[str] = None # Set None as the default value for nullable fields
    status: str
    preferences: Optional[str] = None
    favourites: Optional[str] = None
    anchors: Optional[str] = None #!!!!!!!!!!!!!!
    rewards: Optional[str] = None #!!!!!!!!!!!!!!
<<<<<<< HEAD
    recommendations: Optional[str] = None

    class Config:
        orm_mode = True
        
        
class CreateUser(BaseModel):
    user_id: int
    login: str
    password: str
    phone: str
    email: str
    age: int
    profession: str
    married: str
    info_show: bool
    coins: int
    avatar: Optional[str] = None # Set None as the default value for nullable fields
    status: str
    preferences: Optional[str] = None
    favourites: Optional[str] = None
    anchors: Optional[str] = None #!!!!!!!!!!!!!!
    rewards: Optional[str] = None #!!!!!!!!!!!!!!
=======
>>>>>>> 5f9e5ac59c08639c2159d5ae35ed87180547fa58
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
    tags: Optional[List[str]]
    images: Optional[List[str]]
    marks: Optional[List[str]]

    class Config:
<<<<<<< HEAD
        orm_mode = True
        
class GetAllPlaces(BaseModel):
    tags: str
        
class UserBase(BaseModel):
    email: EmailStr


    
=======
        orm_mode = True
>>>>>>> 5f9e5ac59c08639c2159d5ae35ed87180547fa58
