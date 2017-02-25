from irc3.plugins.cron import cron
from typing import List

import asyncio as aio
import irc3
import re

from strangelove.classify import classify
from strangelove.db import Movie

_RE_CMD = re.compile(r'^!movies\s+(\S+)\s*(.*)$')
_RE_CMD_ADD = re.compile(r'^\s*(.+?)\s*\((\d{4})\)\s*$')


def msg_status(m: Movie, kinds=None):
    if kinds is None:
        kinds = classify(m.torrents)
    stats = ['{}:{}'.format(kind, len(torrents)) for kind, torrents
             in kinds.items()]
    return '{}: found {} torrents ({})'.format(m.title,
                                               len(m.torrents),
                                               ', '.join(stats))


def msg_list(movies: List[Movie]):
    return ', '.join(['{} ({})'.format(m.title, m.year)
                      if m.year is not None
                      else m.title
                      for m in movies])


@irc3.plugin
class StrangeLove:

    def __init__(self, bot):
        self._bot = bot
        self._core = bot.config.core
        self._dispatch = dict(add=self.cmd_add,
                              rm=self.cmd_rm,
                              list=self.cmd_list,
                              status=self.cmd_status)

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

        m = await self._core.add_movie(title, year)
        self.reply(msg_status(m))

    async def cmd_rm(self, title: str):
        try:
            m = self._core.rm_movie(title)
            self.reply('{} removed.'.format(m.title))
        except ValueError:
            self.reply('Not found.')

    async def cmd_list(self, _):
        movies = self._core.list_movies()
        self.reply(msg_list(movies))

    async def cmd_status(self, title: str):
        m = self._core.find_movie(title)
        self.reply(msg_status(m))

    def reply(self, fmt: str, *args, **kwargs):
        self._bot.privmsg(self._bot.config.channel,
                          fmt.format(*args, **kwargs))


@cron('*/5 * * * *')
async def checker(bot):
    bot.privmsg(bot.config.channel, "Checking...")
    core = bot.config.core
    info = await core.check_movies()
    for movie, new, kinds in info:
        if new > 0:
            bot.privmsg(bot.config.channel, msg_status(movie, kinds))
    bot.privmsg(bot.config.channel, "Done.")


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
