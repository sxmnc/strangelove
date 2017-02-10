import asyncio as aio
import aiohttp

from strangelove.core import Core
from strangelove.irc import start_bot


def run():
    session = aiohttp.ClientSession()
    core = Core(session)
    try:
        start_bot(core)
    finally:
        session.close()


def main():
    run()

if __name__ == '__main__':
    main()
