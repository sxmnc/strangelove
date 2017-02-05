import asyncio as aio

from strangelove.irc import start_bot


def main():
    start_bot(aio.get_event_loop())

if __name__ == '__main__':
    main()
