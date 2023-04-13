from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    age = Column(String(255), nullable=False)
    profession = Column(String(255), nullable=False)
    married = Column(String(255), nullable=False)
    gender = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    info_show = Column(Boolean, nullable=False)
    reset_code = Column(String(255), nullable=True)
    coins = Column(Integer, nullable=False, default=0)
    avatar = Column(String(255), nullable=True) # ссылки на файловое хранилище 
    status = Column(String(255), nullable=False, default="client")
    token = Column(String(255), nullable=True, unique=True)
    preferences = Column(JSON, nullable=True)#У Леши называется placeTags
    favourites = Column(String(255), nullable=True)
    anchors = Column(String(255), nullable=True)#json
    rewards = Column(String(255), nullable=True)#json 
    recommendations = Column(String(255), nullable=True)

class Place(Base):
    __tablename__ = 'places'

    place_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    city_name = Column(String(255), nullable=False)
    two_gis_url = Column(String(255), nullable=False)
    geometry_name = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=True)
    short_description = Column(String(255), nullable=True)
    long_description = Column(String(255), nullable=True)
    likes = Column(Integer, nullable=False, default=0)
    instagram_link = Column(String(255), nullable=True)
    category = Column(String(255), nullable=False)
    subcategory = Column(String(255), nullable=False)
    start_work_time = Column(String(255), nullable=True)
    end_work_time = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    marks = Column(JSON, nullable=True)



class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True)
    place_id = Column(Integer, ForeignKey('places.place_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    date = Column(DateTime(timezone=False), nullable=False)
    text = Column(String(255), nullable=False)
    mark = Column(Integer, nullable=False)
    image = Column(String(255), nullable=True)

    place = relationship("Place", backref="reviews")
    user = relationship("User", backref="reviews")
