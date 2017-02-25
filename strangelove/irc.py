from irc3.plugins.cron import cron
from typing import List

import asyncio as aio
import irc3
import re

from strangelove.classify import classify, KINDS
from strangelove.db import Movie
from strangelove.thepiratebay import TooBeaucoupError

_RE_CMD = re.compile(r'^!movies\s+(\S+)\s*(.*)$')
_RE_CMD_ADD = re.compile(r'^\s*(.+?)\s*\((\d{4})\)\s*$')


def fmt_status(m: Movie) -> str:
    kinds = classify(m.torrents)
    return '{}: has {} torrents ({})'.format(m.title,
                                             len(m.torrents),
                                             fmt_kinds(kinds))


def fmt_new(m: Movie, new: int, kinds) -> str:
    return '{}: found {} new torrents ({})'.format(m.title, new,
                                                   fmt_kinds(kinds))


def fmt_kinds(kinds) -> str:
    return ', '.join('{}:{}'.format(kind, len(torrents)) for kind, torrents
                     in kinds.items())


def fmt_list(movies: List[Movie]) -> str:
    return ', '.join('{} ({})'.format(m.title, m.year)
                     if m.year is not None
                     else m.title
                     for m in movies)


def wrap(line: str, size: int=400) -> List[str]:
    lines = []
    words = line.split(' ')
    count = 0
    curr = []
    for word in words:
        if len(word) > size:
            raise ValueError('word too big')
        elif count + len(word) + 1 > size:
            lines.append(' '.join(curr))
            count = len(word)
            curr = [word]
        else:
            count += len(word) + 1
            curr.append(word)
    if len(curr) > 0:
        lines.append(' '.join(curr))
    return lines


def reply(bot, fmt: str, *args, **kwargs):
    for line in wrap(fmt.format(*args, **kwargs)):
        bot.privmsg(bot.config.channel, line)


@irc3.plugin
class StrangeLove:

    def __init__(self, bot):
        self._bot = bot
        self._core = bot.config.core
        self._dispatch = dict(add=self.cmd_add,
                              rm=self.cmd_rm,
                              list=self.cmd_list,
                              status=self.cmd_status,
                              links=self.cmd_links)

    @irc3.event(irc3.rfc.CONNECTED)
    def on_connected(self, *args, **kwargs):
        self._bot.join(self._bot.config.channel)

    @irc3.event(irc3.rfc.PRIVMSG)
    async def on_privmsg(self, mask, event, data, target):
        m = _RE_CMD.match(data)
        if m is not None:
            cmd = m.group(1)
            arg = m.group(2)
            func = self._dispatch.get(cmd)
            if func is not None:
                await func(arg)
            else:
                self._bot.privmsg(target, "Unknown subcommand.")

    async def cmd_add(self, title: str):
        year = None

        m = _RE_CMD_ADD.match(title)
        if m is not None:
            title = m.group(1)
            year = int(m.group(2))

        try:
            m = await self._core.add_movie(title, year)
            self.reply(fmt_status(m))
        except TooBeaucoupError:
            self.reply('The name you entered is too broad. Narrow you search' +
                       ' using the year for example.')

    async def cmd_rm(self, title: str):
        m = self._core.rm_movie(title)
        if m is None:
            self.reply('Movie not found.')
            return

        self.reply('{} removed.'.format(m.title))

    async def cmd_list(self, _):
        movies = self._core.list_movies()
        self.reply(fmt_list(movies))

    async def cmd_status(self, title: str):
        m = self._core.find_movie(title)
        if m is None:
            self.reply('Movie not found.')
            return

        self.reply(fmt_status(m))

    async def cmd_links(self, query: str):
        pos = query.index(' ')
        kind = query[:pos].lower()
        title = query[pos+1:]

        if kind not in KINDS:
            self.reply('Unknown kind.')
            return

        m = self._core.find_movie(title)
        if m is None:
            self.reply('Movie not found.')
            return

        kinds = classify(m.torrents)
        self.reply(' '.join(t.url for t in kinds[kind]))

    def reply(self, fmt: str, *args, **kwargs):
        reply(self._bot, fmt, *args, **kwargs)


@cron('*/5 * * * *')
async def checker(bot):
    reply(bot, 'Checking...')
    core = bot.config.core
    info = await core.check_movies()
    for movie, new, kinds in info:
        if new > 0:
            reply(bot, fmt_new(movie, new, kinds))
    reply(bot, 'Done.')


def start_bot(core):
    config = {
        'core': core,
        'loop': aio.get_event_loop(),
        'nick': 'strangelove',
        'channel': '#strangelove',
        'host': 'irc.freenode.net',
        'verbose': True,
        'includes': ['irc3.plugins.core', 'strangelove.irc'],
    }
    bot = irc3.IrcBot.from_config(config)
    bot.run()
