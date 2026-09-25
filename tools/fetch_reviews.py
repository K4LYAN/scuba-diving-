"""Fetch Dive Adda's live Google and Tripadvisor reviews into assets/data/reviews.json.

Uses the official APIs only (Tripadvisor blocks scraping, Google has no public
review feed):

  GOOGLE_PLACES_API_KEY   Google Places API (New) key            (required for Google)
  GOOGLE_PLACE_ID         Dive Adda's Place ID                   (optional; looked up by name if unset)
  TRIPADVISOR_API_KEY     Tripadvisor Content API key            (required for Tripadvisor)

Run:  python tools/fetch_reviews.py   then   python tools/build_site.py
A source whose key is missing or whose request fails keeps its last cached
data; build_site.py falls back to the sample reviews when nothing is cached.
Test offline:  python tools/fetch_reviews.py --mock tools/qa/mock-reviews
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'data', 'reviews.json')
TA_LOCATION_ID = '33033322'
GOOGLE_QUERY = 'Dive Adda Scuba Diving Center Visakhapatnam'
MOCK_DIR = None


def _get(url, headers=None, body=None, mock=None):
    if MOCK_DIR:
        with open(os.path.join(MOCK_DIR, mock), encoding='utf-8') as f:
            return json.load(f)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=dict(headers or {}, **({'Content-Type': 'application/json'} if data else {})))
    req.add_header('User-Agent', 'DiveAddaSiteBuild/1.0')
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def _month(iso):
    try:
        return datetime.fromisoformat(iso.replace('Z', '+00:00')).strftime('%b %Y')
    except (ValueError, AttributeError):
        return ''


def fetch_google(key):
    place_id = os.environ.get('GOOGLE_PLACE_ID', '').strip()
    if not place_id:
        found = _get('https://places.googleapis.com/v1/places:searchText',
                     {'X-Goog-Api-Key': key, 'X-Goog-FieldMask': 'places.id'},
                     {'textQuery': GOOGLE_QUERY}, mock='google-search.json')
        place_id = (found.get('places') or [{}])[0].get('id')
        if not place_id:
            raise RuntimeError('Place not found; set GOOGLE_PLACE_ID')
    d = _get('https://places.googleapis.com/v1/places/%s' % urllib.parse.quote(place_id),
             {'X-Goog-Api-Key': key, 'X-Goog-FieldMask': 'rating,userRatingCount,reviews,googleMapsUri'},
             mock='google-place.json')
    reviews = []
    for r in d.get('reviews', []):
        text = (r.get('originalText') or r.get('text') or {}).get('text', '').strip()
        if not text:
            continue
        reviews.append(dict(name=r.get('authorAttribution', {}).get('displayName', 'Google user'),
                            rating=int(r.get('rating', 0)), when=_month(r.get('publishTime', '')),
                            text=text, url=r.get('googleMapsUri') or d.get('googleMapsUri', '')))
    return dict(rating=d.get('rating'), count=d.get('userRatingCount'),
                url=d.get('googleMapsUri', ''), reviews=reviews)


def fetch_tripadvisor(key):
    base = 'https://api.content.tripadvisor.com/api/v1/location/%s/' % TA_LOCATION_ID
    d = _get(base + 'details?' + urllib.parse.urlencode({'key': key, 'language': 'en'}), mock='ta-details.json')
    rv = _get(base + 'reviews?' + urllib.parse.urlencode({'key': key, 'language': 'en'}), mock='ta-reviews.json')
    reviews = [dict(name=r.get('user', {}).get('username', 'Tripadvisor member'), rating=int(r.get('rating', 0)),
                    when=_month(r.get('published_date', '')), title=r.get('title', ''),
                    text=r.get('text', '').strip(), url=r.get('url', ''))
               for r in rv.get('data', []) if r.get('text')]
    return dict(rating=float(d['rating']) if d.get('rating') else None,
                count=int(d['num_reviews']) if d.get('num_reviews') else None,
                url=d.get('web_url', ''), reviews=reviews)


def main():
    global MOCK_DIR
    if '--mock' in sys.argv:
        MOCK_DIR = sys.argv[sys.argv.index('--mock') + 1]
    try:
        with open(OUT, encoding='utf-8') as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    jobs = [('google', 'GOOGLE_PLACES_API_KEY', fetch_google), ('tripadvisor', 'TRIPADVISOR_API_KEY', fetch_tripadvisor)]
    for sid, env, fn in jobs:
        key = 'mock' if MOCK_DIR else os.environ.get(env, '').strip()
        if not key:
            print('%s: %s not set, keeping cached data' % (sid, env))
            continue
        try:
            data = fn(key)
            data['fetched'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            cache[sid] = data
            print('%s: %s reviews, rating %s (%s total)' % (sid, len(data['reviews']), data['rating'], data['count']))
        except Exception as e:  # keep the last good data on any API failure
            print('%s: fetch failed (%s), keeping cached data' % (sid, e))
    out = OUT if not MOCK_DIR else os.path.join(MOCK_DIR, 'reviews.out.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    print('wrote', os.path.relpath(out, ROOT))


if __name__ == '__main__':
    main()
