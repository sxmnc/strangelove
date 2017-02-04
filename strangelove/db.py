import functools
from functools import total_ordering

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import (BigInteger, Boolean, Date, ForeignKey, Integer, String)
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

Column = functools.partial(sqlalchemy.Column, nullable=False)


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    year = Column(String(100))
    # Movie cam was notified.
    cam = Column(Boolean, default=False)
    # Movie screener was notified.
    screener = Column(Boolean, default=False)
    # Movie in high definition was notified.
    release = Column(Boolean, default=False)

    def __init__(self, title, year):
        self.title = title
        self.year = year
        self.torrents = []

    def format_search(self):
        return '{} {}'.format(self.title, self.year)

    def __repr__(self):
        return self.title


@total_ordering
class Torrent(Base):
    __tablename__ = 'torrents'

    info_hash = Column(String(20), primary_key=True)
    title = Column(String(250))
    size = Column(BigInteger)
    seeds = Column(Integer)
    leechs = Column(Integer)
    date = Column(Date)
    magnet = Column(String)

    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie = relationship('Movie', backref=backref('torrents',
                                                  cascade='all,delete-orphan'))

    def __init__(self, info_hash, title, size, seeds, leechs, date, *,
                 magnet=None, url=None):
        self.info_hash = info_hash
        self.title = title
        self.size = size
        self.seeds = seeds
        self.leechs = leechs
        self.date = date
        self.magnet = magnet

    def __eq__(self, other):
        if isinstance(other, Torrent):
            return self.info_hash == other.info_hash
        return False

    def __hash__(self):
        return self.info_hash.__hash__()

    def __lt__(self, other):
        return self.seeds < other.seeds

    def __repr__(self):
        return self.title


def connect():
    import os
    os.unlink('movies.db')
    engine = create_engine('sqlite:///movies.db')
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine)
    return maker()
