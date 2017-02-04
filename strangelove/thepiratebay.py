import aiohttp
import re
from bs4 import BeautifulSoup
from datetime import date
from urllib.parse import quote

from .db import Torrent

INFO_HASH_RE = re.compile(r'.*xt=urn:btih:([^&]+).*')

CATEGORIES = dict(
    all=0,
    music=101,
    video=200,
    tv=205,
)

SIZE_TABLE = dict(
    b=1,
    kib=1 << 10,
    mib=1 << 20,
    gib=1 << 30,
    tib=1 << 40,
    pib=1 << 50,
)

SIZE_RE = re.compile(r'.*Size\s+([\d\.]+)\s+([^,]+).*')

DATE_RE = re.compile(r'^Uploaded\s+(\d\d)\-(\d\d)\s+(\d{4})?')


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


def parse_html(html):
    doc = BeautifulSoup(html, 'html.parser')
    div = doc.find('table', dict(id='searchResult'))
    for tr in div.find_all('tr')[1:]:
        td = tr.find_all('td')
        links = td[1].find_all('a')
        desc = ''.join((list(td[1].find('font').strings)))

        yield Torrent(
            parse_info_hash(links[1]['href']),
            str(links[0].string),
            parse_size(desc),
            int(td[2].string),
            int(td[3].string),
            parse_date(desc),
            magnet=links[1]['href'],
        )


async def search(query, session, category='video', domain='thepiratebay.org'):
    url = 'http://{}/search/{}/0/7/{}'.format(domain, quote(query),
                                              CATEGORIES[category])
    with aiohttp.Timeout(10):
        async with session.get(url) as res:
            if res.status == 200:
                return parse_html(await res.text())
