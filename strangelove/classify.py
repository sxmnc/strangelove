import re


def tokens(t):
    return re.split(r'[\.\s]', t.title.lower())


def crosscheck(tokens, filters):
    return any(any(f == t for f in filters) for t in tokens)


KINDS = {
    'cam': ('cam', 'camrip', 'hdcam'),
    'dvdscr': ('dvdscr', 'screener', 'scr', 'dvdscreener', 'bdscr', 'ddc'),
    'hc': ('hc', 'korsub'),
    'dvd': ('dvdrip',),
    'hd': ('bluray', 'brip', 'bdrip', 'brrip', 'bdr', 'hdrip', 'web-dl',
           'webdl', 'webrip', 'web-rip')
}


def classify(torrents):
    kinds = {cat: set() for cat in KINDS.keys()}
    for t in torrents:
        tk = tokens(t)
        for kind, filters in KINDS.items():
            if crosscheck(tk, filters):
                kinds[kind].add(t)
                break
    return kinds


__all__ = ['classify']
