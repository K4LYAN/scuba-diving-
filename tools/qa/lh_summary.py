"""Print scores, metrics and the main diagnostics from a Lighthouse JSON report."""
import json
import sys

d = json.load(open(sys.argv[1], encoding='utf-8'))
a = d['audits']
print({k: round(v['score'] * 100) for k, v in d['categories'].items()})
for k in ['first-contentful-paint', 'largest-contentful-paint', 'total-blocking-time', 'cumulative-layout-shift', 'speed-index']:
    print('  %-26s %s' % (k, a[k]['displayValue']))
if '-v' in sys.argv:
    for k, v in a.items():
        if v.get('score') is not None and v['score'] < 0.9 and v.get('scoreDisplayMode') in ('numeric', 'binary', 'metricSavings'):
            print('  -', k, v.get('displayValue', ''))
    print('LONG TASKS', [(i['url'][-50:], round(i['duration'])) for i in a['long-tasks']['details']['items'][:6]])
    print('MAIN', [(i['groupLabel'], round(i['duration'])) for i in a['mainthread-work-breakdown']['details']['items']])
