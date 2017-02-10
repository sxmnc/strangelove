import asyncio as aio

from strangelove.classify import classify
from strangelove.db import connect, Movie
from strangelove import thepiratebay


class Core:

    def __init__(self, session):
        self._db = connect()
        print(self._db)
        self._session = session

    async def search(self, m):
        return await thepiratebay.search(m.format_search(),
                                         session=self._session)

    async def add_movie(self, title, year=None):
        m = Movie(title, year)
        torrents = await self.search(m)
        m.torrents = list(torrents)
        self._db.add(m)
        self._db.commit()
        return len(torrents), classify(torrents)

    def rm_movie(self, title):
        m = self._db.query(Movie).filter(Movie.title.ilike(title)).first()
        if m is not None:
            self._db.delete(m)
            self._db.commit()
        else:
            raise ValueError

    def list_movies(self):
        return self._db.query(Movie).all()

    async def check_movie(self, m):
        torrents = await self.search(m)
        cache = set(m.torrents)
        diff = torrents - cache
        if len(diff) > 0:
            classify(diff)
            # TODO more

    async def check_movies(self):
        movies = self._db.query(Movie).all()
        if len(movies) > 0:
            coros = [self.check_movie(m) for m in movies]
            futs, _ = await aio.wait(coros)
            return [f.result() for f in futs]
        else:
            return []
