import re


def tokens(t):
    return re.split(r'[\.\s]', t.title.lower())


def crosscheck(tokens, filters):
    return any(any(f == t for f in filters) for t in tokens)


CATEGORIES = {
    'cam': ('cam', 'camrip', 'hdcam'),
    'dvdscr': ('dvdscr', 'screener', 'scr', 'dvdscreener', 'bdscr', 'ddc'),
    'hc': ('hc'),
    'dvd': ('dvdrip',),
    'hd': ('bluray', 'brip', 'bdrip', 'brrip', 'bdr', 'hdrip', 'web-dl',
           'webdl', 'webrip', 'web-rip')
}


def classify(torrents):
    classes = {cat: set() for cat in CATEGORIES.keys()}
    for t in torrents:
        tk = tokens(t)
        for cat, filters in CATEGORIES.items():
            if crosscheck(tk, filters):
                classes[cat].add(t)
                break
    return classes

__all__ = ['classify']
