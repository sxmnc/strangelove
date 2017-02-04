import asyncio as aio
import aiohttp

from strangelove import thepiratebay
from strangelove.classify import classify, compare
from strangelove.db import connect, Movie


class Core:

    def __init__(self):
        self._db = connect()
        self._session = aiohttp.ClientSession()

    async def search(self, m):
        return await thepiratebay.search(m.format_search(),
                                         session=self._session)

    async def add_movie(self, title, year):
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


async def main_task():
    core = Core()
    # await core.add_movie('arrival', 2016)
    # core.rm_movie('arrival')
    print(await core.check_movies())


def main():
    aio.get_event_loop().run_until_complete(main_task())


if __name__ == '__main__':
    main()
