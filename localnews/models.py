from sqlalchemy import *
from sqlalchemy import create_engine, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from itsdangerous import URLSafeTimedSerializer
from geoalchemy2 import types, Geometry
from datetime import datetime
import random

from . import app


def pid_generator():
    id = random.SystemRandom().randint(10**7, 10**8-1)
    if id in sess.query(Post.id).all():
        pid_generator()
    else:
        return id


login_serializer = URLSafeTimedSerializer(app.secret_key)
metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_engine(app.config['PostgresDB'], echo=True)
Sess = scoped_session(sessionmaker(bind=engine))
sess = Sess()

#Database

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, default=pid_generator)
    poster_id = Column(Integer)
    name = Column(String(255))
    locname = Column(String(255))
    loc_id = Column(Integer, ForeignKey('locations.id'))
    location = Column(Geometry('Point', srid=4326))
    title = Column(String(255))
    content = Column(JSON)
    link = Column(String(255))
    postedtime = Column(DateTime)
    editedtime = Column(DateTime)
    thumbnail = Column(String(1000))

    #actions = relationship("Action", back_populates="posts")
    locations = relationship("Location", back_populates="posts")

    @hybrid_property
    def timediff(self):
        diff = (datetime.now() - self.postedtime).total_seconds()
        return diff

    @timediff.expression
    def timediff(cls):
        return (func.DATE_PART(text("'day'"),  func.now() - cls.postedtime) * 24 +
               func.DATE_PART(text("'hour'"),  func.now() - cls.postedtime)) * 60 +\
               func.DATE_PART(text("'minute'"),  func.now() - cls.postedtime)


class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    location = Column(Geometry('Polygon', srid=4326))
    posts = relationship("Post", back_populates="locations")



class Locdict(Base):
    __tablename__ = 'locdicts'
    id = Column(Integer, primary_key=True)
    loc_id = Column(Integer)
    name = Column(String(255))
    location = Column(Geometry('Polygon', srid=4326))
