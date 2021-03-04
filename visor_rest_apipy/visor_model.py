# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
metadata = Base.metadata


def create_db_session(db_url):
    visor_engine = create_engine(db_url)
    Session = sessionmaker(bind = visor_engine)
    result = Session()
    return result


class VisorSession(Base):
    __tablename__ = 'visor_session'

    session_id = Column(UUID, primary_key=True, index=True)
    client_string = Column(String(2048), index=True)
    user_token = Column(String(256), nullable=False, unique=True)
    start_time = Column(TIMESTAMP(precision=0), nullable=False)
    end_time = Column(TIMESTAMP(precision=0))


class VisorImage(Base):
    __tablename__ = 'visor_image'

    image_id = Column(UUID, primary_key=True, index=True)
    session_id = Column(ForeignKey('visor_session.session_id'), nullable=False, unique=True)
    s3_key = Column(String(2048))
    crc = Column(String(256))
    image_path = Column(String(2048))
    upload_time = Column(TIMESTAMP(precision=0), nullable=False)

    session = relationship('VisorSession', uselist=False)


class VisorSessionRecord(Base):
    __tablename__ = 'visor_session_record'

    record_id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(ForeignKey('visor_session.session_id'), nullable=False, index=True)
    image_id = Column(ForeignKey('visor_image.image_id'), index=True)
    upload_state = Column(String(50))
    image_path = Column(String(2048))

    image = relationship('VisorImage')
    session = relationship('VisorSession')
