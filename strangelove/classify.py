import re


def tokens(t):
    return re.split(r'[\.\s]', t.title.lower())


def crosscheck(tokens, filters):
    return any(any(f == t for f in filters) for t in tokens)


CATEGORIES = {
    'cam': ('cam', 'camrip', 'hdcam'),
    'dvdscr': ('dvdscr', 'screener', 'scr', 'dvdscreener', 'bdscr', 'ddc'),
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


def compare(oldts, newts):
    old_classes = classify(oldts)
    new_classes = classify(newts)

    diff = {name: new - old for name, old, new in zip(old_classes.keys(),
                                                      old_classes.values(),
                                                      new_classes.values())}

    return diff
