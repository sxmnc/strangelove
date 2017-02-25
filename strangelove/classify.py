from typing import List
import re

from strangelove.db import Torrent


def tokens(t):
    return re.split(r'[\.\s]', t.title.lower())


def crosscheck(tokens, filters):
    return any(any(f == t for f in filters) for t in tokens)


KINDS = (
    ('cam', ('cam', 'camrip', 'hdcam')),
    ('ts', ('hdts', 'hd-ts', 'hqhdts', 'ts', 'telesync', 'pdvd')),
    ('dvdscr', ('dvdscr', 'screener', 'scr', 'dvdscreener', 'bdscr', 'ddc')),
    ('hc', ('hc', 'korsub')),
    ('dvd', ('dvdrip',)),
    ('hd', ('bluray', 'brip', 'bdrip', 'brrip', 'bdr', 'hdrip', 'web-dl',
            'webdl', 'webrip', 'web-rip')),
    ('other', ()),
)


def is_valid_kind(kind: str):
    return any(kind == k for k, _ in KINDS)


def classify(torrents: List[Torrent]):
    kinds = {kind: set() for kind, _ in KINDS}
    for t in torrents:
        tk = tokens(t)
        for kind, filters in KINDS:
            if crosscheck(tk, filters):
                kinds[kind].add(t)
                break
        else:
            kinds['other'].add(t)
    return kinds


__all__ = ['classify']
