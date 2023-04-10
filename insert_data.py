
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from schemas import User, Place, Review,Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
import datetime

# Get the current date and time
now = datetime.datetime.now()

engine = create_engine('mysql://doadmin:AVNS_ixs6LYwnPYYNRCz3SRl@db-reversers-do-user-13881334-0.b.db.ondigitalocean.com:25060/defaultdb?')
Session = sessionmaker(bind=engine)
session = Session()

#----------------------------------------------------------
#Users
#----------------------------------------------------------
#DIC FOR USERS
# user_data = [
#     {
#         'login': 'user1',
#         'password': 'password1',
#         'phone': '+1234567890',
#         'email': 'user1@example.com',
#         'age': 25,
#         'profession': 'Engineer',
#         'married': 'No',
#         'info_show': True,
#         'reset_code': None,
#         'coins': 100,
#         'avatar': None,
#         'status': 'active',
#         'token': None,
#         'preferences': None,
#         'favourites': None,
#         'anchors': None,
#         'rewards': None,
#         'recommendations': None
#     },
#     {
#         'login': 'user2',
#         'password': 'password2',
#         'phone': '+2345678901',
#         'email': 'user2@example.com',
#         'age': 30,
#         'profession': 'Teacher',
#         'married': 'Yes',
#         'info_show': False,
#         'reset_code': 'abcd1234',
#         'coins': 200,
#         'avatar': 'user2.jpg',
#         'status': 'inactive',
#         'token': 'xyz789',
#         'preferences': 'Sports',
#         'favourites': 'Music',
#         'anchors': 'Beaches',
#         'rewards': 'Coupons',
#         'recommendations': 'Movies'
#     }
# ]

# # Loop through the user_data list and insert each dictionary as a new User object
# for data in user_data:
#     user = User(**data)
#     session.add(user)

# Commit the changes to the database
#session.commit()






# Insert 10 rows into the places table
#----------------------------------------------------------
#Places
#----------------------------------------------------------
for i in range(10):
    place = Place(
        name=f'Place {i}',
        city_name='New York',
        two_gis_url=f'https://2gis.com/{i}',
        geometry_name='Point',
        phone='555-555-5555',
        short_description='A cool place',
        long_description='This place is really cool',
        likes=2*i,
        instagram_link='https://instagram.com',
        category='Entertainment',
        subcategory='Cinema',
        start_work_time='9:00',
        end_work_time='22:00',
        tags=['tag1', 'tag2', 'tag3'],
        images=['https://placeimg.com/640/480/any'] * 3,
        marks=[3, 4, 5]
    )
    session.add(place)




#----------------------------------------------------------
#Reviews
#----------------------------------------------------------



new_review = Review(
    place_id=3,
    user_id=2,
    date=now,
    text='WAASSSSSSSSSSSSSSSSSSS!',
    mark=4
)

# Add the review to the session
session.add(new_review)

# Commit the transaction to the database
session.commit()

# Close the session
session.close()