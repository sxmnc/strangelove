import aiohttp
import math
import re
from bs4 import BeautifulSoup
from datetime import date
from urllib.parse import quote

from .db import Torrent

INFO_HASH_RE = re.compile(r'.*xt=urn:btih:([^&]+).*')

SIZE_TABLE = dict(
    b=1,
    kib=1 << 10,
    mib=1 << 20,
    gib=1 << 30,
    tib=1 << 40,
    pib=1 << 50,
)

NUM_RE = re.compile(r'\(approx (\d+) found\)')

SIZE_RE = re.compile(r'.*Size\s+([\d\.]+)\s+([^,]+).*')

DATE_RE = re.compile(r'^Uploaded\s+(\d\d)\-(\d\d)\s+(\d{4})?')


def parse_num(doc):
    h2 = ''.join(doc.find('h2').strings)
    m = NUM_RE.search(h2)
    return int(m.group(1))


def parse_info_hash(magnet):
    caps = INFO_HASH_RE.match(magnet)
    return bytes.fromhex(caps.group(1))


def parse_size(desc):
    caps = SIZE_RE.match(desc)
    frac = float(caps.group(1))
    unit = caps.group(2).lower()
    return int(frac * SIZE_TABLE[unit])


def parse_date(desc):
    caps = DATE_RE.match(desc)
    today = date.today()
    if caps:
        month = int(caps.group(1))
        day = int(caps.group(2))
        year = int(caps.group(3) or today.year)
        return date(year, month, day)
    else:
        return today


def parse_torrents(doc):
    div = doc.find('table', dict(id='searchResult'))
    for tr in div.find_all('tr')[1:]:
        td = tr.find_all('td')
        links = td[1].find_all('a')
        desc = ''.join(list(td[1].find('font').strings))

        yield Torrent(
            parse_info_hash(links[1]['href']),
            str(links[0].string),
            parse_size(desc),
            int(td[2].string),
            int(td[3].string),
            parse_date(desc),
            magnet=links[1]['href'],
        )


async def search(query, session, domain='thepiratebay.org'):
    query = quote(query)
    async def get(page):
        url = 'http://{}/search/{}/{}/7/{}'.format(domain, query, page, 200)
        with aiohttp.Timeout(10):
            async with session.get(url) as res:
                html = await res.text()
                return BeautifulSoup(html, 'html.parser')
    doc = await get(0)
    page = 1
    num = parse_num(doc)
    pages = math.ceil(num / 30)
    torrents = set(parse_torrents(doc))
    while page < pages:
        doc = await get(page)
        torrents.update(parse_torrents(doc))
        page += 1
    return torrents


__all__ = ['search']
