import asyncio as aio

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

    async def add_movie(self, title: str, year: int=None) -> Movie:
        m = Movie(title, year)
        m.torrents = list(await self.search(m))
        self._db.add(m)
        self._db.commit()
        return m

    def find_movie(self, title: str) -> Movie:
        return (self._db.query(Movie)
                        .filter(Movie.title.ilike('%{}%'.format(title)))
                        .first())

    def rm_movie(self, title: str) -> Movie:
        m = self.find_movie(title)
        if m is not None:
            self._db.delete(m)
            self._db.commit()
        return m

    def list_movies(self):
        return self._db.query(Movie).all()

    async def check_movie(self, m: Movie):
        torrents = await self.search(m)
        cache = set(m.torrents)

        # purge removed torrents from database
        removed = cache - torrents
        for t in removed:
            self._db.delete(t)
        self._db.commit()

        # add new torrents to the database
        added = torrents - cache
        if len(added) > 0:
            m.torrents.extend(added)
            self._db.commit()

        return m, added, removed

    async def check_movies(self):
        movies = self._db.query(Movie).all()
        if len(movies) > 0:
            coros = [self.check_movie(m) for m in movies]
            futs, _ = await aio.wait(coros)
            return [f.result() for f in futs]
        else:
            return []
