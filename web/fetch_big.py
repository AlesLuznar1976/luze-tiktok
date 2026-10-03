"""Download larger versions (long side up to ~2880 px) of the chosen Commons files, with full metadata."""
import json, os, re, urllib.parse, urllib.request, html, time
UA = {'User-Agent': 'luze-tiktok/1.0 (https://github.com/AlesLuznar1976/luze-tiktok; volunteer fire brigade stand ads)'}
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'big'); os.makedirs(OUT, exist_ok=True)
strip = lambda s: html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()
chosen = json.load(open(os.path.join(D, 'chosen.json'), encoding='utf8'))
meta = {}
for key, title in chosen.items():
    q = {'action': 'query', 'format': 'json', 'titles': title, 'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size'}
    d = json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q), headers=UA), timeout=60))
    pg = list(d['query']['pages'].values())[0]; ii = pg['imageinfo'][0]; md = ii.get('extmetadata', {})
    w, h = ii['width'], ii['height']
    tw = min(w, 2880 if w >= h else 1800)
    q2 = dict(q, iiurlwidth=tw)
    d2 = json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q2), headers=UA), timeout=60))
    ii2 = list(d2['query']['pages'].values())[0]['imageinfo'][0]
    url = ii2.get('thumburl') or ii2['url']
    open(os.path.join(OUT, key + '.jpg'), 'wb').write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())
    meta[key] = {'title': title, 'author': strip(md.get('Artist', {}).get('value'))[:200],
                 'license': strip(md.get('LicenseShortName', {}).get('value')),
                 'license_url': strip(md.get('LicenseUrl', {}).get('value')),
                 'source': ii.get('descriptionurl'), 'width': w, 'height': h}
    print(key, meta[key]['license'], meta[key]['author'][:40]); time.sleep(0.5)
json.dump(meta, open(os.path.join(D, 'big', 'credits.json'), 'w'), ensure_ascii=False, indent=1)
