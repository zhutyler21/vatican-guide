#!/usr/bin/env python3
"""Fetch reusable Wikimedia Commons thumbnails for the added guide cards."""
import json
import re
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
OUT = ROOT / 'images'
OUT.mkdir(exist_ok=True)
QUERIES = {
  'pompeii_forum': 'Pompeii forum Mount Vesuvius',
  'pompeii_apollo': 'Temple of Apollo Pompeii',
  'pompeii_basilica': 'Basilica Pompeii ruins',
  'pompeii_stabian_baths': 'Stabian Baths Pompeii',
  'pompeii_lupanar': 'Lupanar Pompeii',
  'pompeii_faun': 'House of the Faun Pompeii',
  'pompeii_mysteries': 'Villa of the Mysteries Pompeii fresco',
  'colosseum_facade': 'Colosseum Rome exterior',
  'colosseum_cavea': 'Colosseum cavea seating',
  'colosseum_arena': 'Colosseum arena Rome',
  'colosseum_hypogeum': 'Colosseum hypogeum underground',
  'colosseum_games': 'Colosseum gladiator mosaic',
  'colosseum_afterlife': 'Colosseum ruins Rome nineteenth century',
}
API = 'https://commons.wikimedia.org/w/api.php'
HEADERS = {'User-Agent': 'ItalyGuideResearch/1.0 (educational static guide)'}

def request_json(params):
    req = Request(API + '?' + urlencode(params), headers=HEADERS)
    with urlopen(req, timeout=30) as r:
        return json.load(r)

def download(url, target):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=60) as r:
        target.write_bytes(r.read())

for target, query in QUERIES.items():
    data = request_json({
        'action':'query','format':'json','generator':'search','gsrsearch':query,
        'gsrnamespace':6,'gsrlimit':10,'prop':'imageinfo','iiprop':'url','iiurlwidth':1400
    })
    pages = data.get('query', {}).get('pages', {})
    candidates = []
    for page in pages.values():
        info = (page.get('imageinfo') or [{}])[0]
        url = info.get('thumburl') or info.get('url')
        if url and re.search(r'\.(jpe?g|png)(?:\?|$)', url, re.I):
            candidates.append((page.get('title',''), url))
    if not candidates:
        print('MISS', target, query)
        continue
    title, url = candidates[0]
    destination = OUT / f'{target}.jpg'
    try:
        download(url, destination)
        print('OK', target, destination.stat().st_size, title)
    except Exception as exc:
        print('FAIL', target, type(exc).__name__, str(exc)[:120])
    time.sleep(.2)
