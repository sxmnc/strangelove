import irc3
import re

from strangelove.core import Core

_RE_CMD = re.compile(r'^!movies\s+(\S+)\s*(.*)$')
_RE_CMD_ADD = re.compile(r'^\s*(.+)\s*\((\d{4})\)\s*$')


@irc3.plugin
class StrangeLove:

    def __init__(self, bot):
        self._core = None
        self.bot = bot
        self.dispatch = dict(add=self.cmd_add,
                             rm=self.cmd_rm,
                             list=self.cmd_list)

    @property
    def core(self):
        if self._core is None:
            self._core = Core()
        return self._core

    @irc3.event(irc3.rfc.CONNECTED)
    def connected(self, *args, **kwargs):
        self.bot.join(self.bot.config.channel)

    @irc3.event(irc3.rfc.PRIVMSG)
    async def privmsg(self, mask, event, data, target):
        m = _RE_CMD.match(data)
        if m is not None:
            cmd = m.group(1)
            arg = m.group(2)
            func = self.dispatch.get(cmd)
            if func is not None:
                await func(arg)
            else:
                self.bot.privmsg(target, "Unknown subcommand.")

    async def cmd_add(self, movie):
        title = movie
        year = None

        m = _RE_CMD_ADD.match(movie)
        if m is not None:
            title = m.group(1)
            year = int(m.group(2))

        print('adding', title, year)
        klss = await self.core.add_movie(title, year)

        txt = ['{}:{}'.format(kls, len(torrents)) for kls, torrents
               in klss.items()]
        self.bot.privmsg(self.bot.config.channel, ', '.join(txt))

    async def cmd_rm(self, movie):
        self.core.rm_movie(movie)
        self.bot.privmsg(self.bot.config.channel, '{} removed.'.format(movie))

    async def cmd_list(self, _):
        movies = self.core.list_movies()
        txt = ['{} ({})'.format(m.title, m.year) if m.year is not None else m.title
               for m in movies]
        self.bot.privmsg(self.bot.config.channel, ', '.join(txt))


def start_bot(loop):
    config = {
        'loop': loop,
        'nick': 'strangelove',
        'channel': '#strangelove',
        'host': 'irc.freenode.net',
        'verbose': True,
        'includes': ['irc3.plugins.core', 'strangelove.irc'],
    }
    bot = irc3.IrcBot.from_config(config)
    bot.run()
