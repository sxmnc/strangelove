from irc3.plugins.cron import cron
import asyncio as aio
import irc3
import re

_RE_CMD = re.compile(r'^!movies\s+(\S+)\s*(.*)$')
_RE_CMD_ADD = re.compile(r'^\s*(.+?)\s*\((\d{4})\)\s*$')


@irc3.plugin
class StrangeLove:

    def __init__(self, bot):
        self._bot = bot
        self._core = bot.config.core
        self._dispatch = dict(add=self.cmd_add,
                              rm=self.cmd_rm,
                              list=self.cmd_list)

    @irc3.event(irc3.rfc.CONNECTED)
    def connected(self, *args, **kwargs):
        self._bot.join(self._bot.config.channel)

    @irc3.event(irc3.rfc.PRIVMSG)
    async def privmsg(self, mask, event, data, target):
        m = _RE_CMD.match(data)
        if m is not None:
            cmd = m.group(1)
            arg = m.group(2)
            func = self._dispatch.get(cmd)
            if func is not None:
                await func(arg)
            else:
                self._bot.privmsg(target, "Unknown subcommand.")

    async def cmd_add(self, movie):
        title = movie
        year = None

        m = _RE_CMD_ADD.match(movie)
        if m is not None:
            title = m.group(1)
            year = int(m.group(2))

        num, kinds = await self._core.add_movie(title, year)

        txt = ['{}:{}'.format(kind, len(torrents)) for kind, torrents
               in kinds.items()]
        self._bot.privmsg(self._bot.config.channel, 'Found {} torrents: '.format(num) + ', '.join(txt))

    async def cmd_rm(self, movie):
        self._core.rm_movie(movie)
        self._bot.privmsg(self._bot.config.channel, '{} removed.'.format(movie))

    async def cmd_list(self, _):
        movies = self._core.list_movies()
        txt = ['{} ({})'.format(m.title, m.year) if m.year is not None else m.title
               for m in movies]
        self._bot.privmsg(self._bot.config.channel, ', '.join(txt))


@cron('*/15 * * * *')
async def checker(bot):
    # core = bot.config.core
    # core.check_movies()
    pass


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
