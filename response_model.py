from typing import List, Optional
from pydantic import BaseModel

class UserRead(BaseModel):
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
    anchors: Optional[str] = None
    rewards: Optional[str] = None
    recommendations: Optional[str] = None

    class Config:
        orm_mode = True


