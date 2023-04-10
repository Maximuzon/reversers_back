from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from schemas import User, Place, Review,Base

# engine = create_engine('mysql://doadmin:AVNS_ixs6LYwnPYYNRCz3SRl@db-reversers-do-user-13881334-0.b.db.ondigitalocean.com:25060/defaultdb?')
# metadata = MetaData(bind = engine)
# Base = declarative_base()
# Base.metadata.create_all(engine)




# create engine
engine = create_engine('mysql://doadmin:AVNS_ixs6LYwnPYYNRCz3SRl@db-reversers-do-user-13881334-0.b.db.ondigitalocean.com:25060/defaultdb?')
Base.metadata.create_all(engine)

# Base.metadata.create_all(engine)

# # create session
Session = sessionmaker(bind=engine)
session = Session()

# # create Base
Base = declarative_base()
# print('starting migrating schema')

# Base.metadata.create_all(engine)
# print('schema is used, tables created')

# session.commit()

session.close()