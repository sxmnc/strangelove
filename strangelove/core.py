import asyncio as aio
import aiohttp

from strangelove.classify import classify, compare
from strangelove.db import connect, Movie
from strangelove import thepiratebay


class Core:

    def __init__(self):
        self._db = connect()
        self._session = aiohttp.ClientSession()

    async def search(self, m):
        return await thepiratebay.search(m.format_search(),
                                         session=self._session)

    async def add_movie(self, title, year=None):
        m = Movie(title, year)
        try:
            torrents = await self.search(m)
        except:
            pass
        else:
            kls = classify(torrents)
            for cat in kls.values():
                for t in cat:
                    m.torrents.append(t)
            self._db.add(m)
            self._db.commit()
            return kls

    def rm_movie(self, title):
        m = self._db.query(Movie).filter(Movie.title.ilike(title)).first()
        self._db.delete(m)
        self._db.commit()

    def list_movies(self):
        return self._db.query(Movie).all()

    async def check_movie(self, m):
        torrents = await self.search(m)
        diff = compare(m.torrents, torrents)
        return (m, diff)

    async def check_movies(self):
        movies = self._db.query(Movie).all()
        if len(movies) > 0:
            coros = [self.check_movie(m) for m in movies]
            futs, _ = await aio.wait(coros)
            return [f.result() for f in futs]
        else:
            return []

    def __del__(self):
        self._session.close()
