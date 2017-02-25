import aiohttp

from strangelove.core import Core
from strangelove.irc import start_bot


def main():
    session = aiohttp.ClientSession()
    core = Core(session)
    try:
        start_bot(core)
    finally:
        session.close()
