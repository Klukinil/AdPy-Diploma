import sqlalchemy as sa
import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

login = 'postgres'
kod = '6022'
engine = sa.create_engine(f'postgresql+psycopg2://{login}:{kod}@localhost:5432/VK_Finder')
connection = engine.connect()
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'user_vk'

    id = sa.Column(sa.Integer, primary_key=True)
    vk_id = sa.Column(sa.Integer, nullable=False, unique=True)
    first_name = sa.Column(sa.String(50), nullable=False)
    second_name = sa.Column(sa.String(50), nullable=False)
    city = sa.Column(sa.String(50), nullable=False)
    datinguser = relationship('Partners', uselist=False, back_populates='user_vk')

    def __init__(self, vk_id, first_name, second_name, city):
        self.vk_id = vk_id
        self.first_name = first_name
        self.second_name = second_name
        self.city = city



class Partners(Base):
    __tablename__ = 'datinguser'

    id = sa.Column(sa.Integer, primary_key=True)
    pair_vk_id = sa.Column(sa.Integer, nullable=False, unique=True)
    first_name = sa.Column(sa.String(50), nullable=False)
    second_name = sa.Column(sa.String(50), nullable=False)
    birth_year = sa.Column(sa.String(50))
    id_User_VK = sa.Column(sa.Integer, sa.ForeignKey('user_vk.vk_id'))
    user_vk = relationship('User', back_populates='datinguser')
    photo = relationship('Photo', uselist=False, back_populates='datinguser')


    def __init__(self, pair_vk_id, first_name, second_name, birth_year, id_User_VK):
        self.pair_vk_id = pair_vk_id
        self.first_name = first_name
        self.second_name = second_name
        self.birth_year = birth_year
        self.id_User_VK = id_User_VK



class Photo(Base):
    __tablename__ = 'photo'

    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    id_DatingUser = sa.Column(sa.Integer, sa.ForeignKey('datinguser.pair_vk_id'))
    datinguser = relationship('Partners', back_populates='photo')
    count_likes = sa.Column(sa.Integer, nullable=False)
    link_photo = sa.Column(sa.String, nullable=False)

    def __init__(self, id_DatingUser, count_likes, link_photo):
        self.id_DatingUser = id_DatingUser
        self.count_likes = count_likes
        self.link_photo = link_photo


Base.metadata.create_all(engine)