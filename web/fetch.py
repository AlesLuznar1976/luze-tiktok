"""Find freely licensed photos on Wikimedia Commons for the given queries and download 1440 px versions."""
import json, os, re, time, urllib.parse, urllib.request, html

UA = {'User-Agent': 'luze-tiktok/1.0 (https://github.com/AlesLuznar1976/luze-tiktok; volunteer fire brigade stand ads)'}
OK = re.compile(r'^(CC0|Public domain|PD.*|CC BY(-SA)? (2\.0|2\.5|3\.0|4\.0)( .*)?)$', re.I)
API = 'https://commons.wikimedia.org/w/api.php'
OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def get(params):
    url = API + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


index = {}
p = os.path.join(os.path.dirname(__file__), 'index.json')
if os.path.exists(p):
    index = json.load(open(p))
queries = [q.strip() for q in open(os.path.join(os.path.dirname(__file__), 'queries.txt'), encoding='utf8') if q.strip()]
for q in queries:
    try:
        d = get({'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': q + ' filetype:bitmap',
                 'gsrnamespace': 6, 'gsrlimit': 25, 'prop': 'imageinfo',
                 'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': 1440})
    except Exception as e:
        print('query failed', q, e); continue
    pages = sorted((d.get('query') or {}).get('pages', {}).values(), key=lambda x: x.get('index', 99))
    n = 0
    for pg in pages:
        ii = (pg.get('imageinfo') or [{}])[0]
        md = ii.get('extmetadata', {})
        lic = strip(md.get('LicenseShortName', {}).get('value'))
        if not OK.match(lic) or ii.get('mime') not in ('image/jpeg', 'image/png'):
            continue
        if ii.get('width', 0) < 1200 and ii.get('height', 0) < 1200:
            continue
        title = pg['title']
        key = re.sub(r'[^a-z0-9]+', '_', title.lower().replace('file:', ''))[:60].strip('_')
        if key in index:
            n += 1; continue
        fn = key + ('.png' if ii['mime'] == 'image/png' else '.jpg')
        try:
            with urllib.request.urlopen(urllib.request.Request(ii['thumburl'], headers=UA), timeout=60) as r:
                open(os.path.join(OUT, fn), 'wb').write(r.read())
        except Exception as e:
            print('dl failed', title, e); continue
        index[key] = {'file': 'img/' + fn, 'title': title, 'query': q, 'license': lic,
                      'license_url': strip(md.get('LicenseUrl', {}).get('value')),
                      'author': strip(md.get('Artist', {}).get('value'))[:200],
                      'credit': strip(md.get('Credit', {}).get('value'))[:200],
                      'description': strip(md.get('ImageDescription', {}).get('value'))[:300],
                      'source': ii.get('descriptionurl'), 'width': ii.get('width'), 'height': ii.get('height')}
        n += 1
        time.sleep(0.5)
        if n >= 8:
            break
    print(q, '->', n)
json.dump(index, open(p, 'w'), ensure_ascii=False, indent=1)
