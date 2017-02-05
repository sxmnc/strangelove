import irc3


@irc3.plugin
class StrangeLove:

    def __init__(self, context):
        self.context = context

    @irc3.event(irc3.rfc.CONNECTED)
    def connected(self, *args, **kwargs):
        print(args, kwargs)
        self.context.join(self.context.config.channel)

    @irc3.event(irc3.rfc.PRIVMSG)
    def privmsg(self, *args, **kwargs):
        print(args, kwargs)


def start_bot(loop):
    config = {
        'loop': loop,
        'nick': 'strangelove',
        'channel': '#sexmaniac',
        'host': 'irc.freenode.net',
        'verbose': True,
        'includes': ['strangelove.irc'],
    }
    bot = irc3.IrcBot.from_config(config)
    bot.run()
