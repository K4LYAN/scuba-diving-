"""robots.txt and llms.txt for Dive Adda, built from the same data as the pages
(build_site.py passes itself in), so they never say anything the site does not.

Search engines and AI assistants are welcome: the business wants to be found
and quoted accurately. Only the build tooling is kept out of crawls.
"""
import html
import re

# Crawlers named explicitly, so a blanket rule elsewhere can never shut them out.
CRAWLERS = [
    'Googlebot', 'Bingbot', 'Applebot', 'DuckDuckBot', 'YandexBot',            # search engines
    'Google-Extended', 'Applebot-Extended',                                     # Gemini / Apple Intelligence
    'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',                                  # OpenAI
    'ClaudeBot', 'Claude-SearchBot', 'Claude-User',                             # Anthropic
    'PerplexityBot', 'Perplexity-User',                                         # Perplexity
    'meta-externalagent', 'Amazonbot', 'DuckAssistBot', 'MistralAI-User', 'CCBot',
]


def _txt(h):
    """Page copy (HTML entities, inline tags) as plain text."""
    return html.unescape(re.sub(r'<[^>]+>', '', h)).replace(' ', ' ').strip()


def robots_txt(site):
    D = site.DOMAIN
    out = ['# Dive Adda - %s' % D,
           '# Search engines and AI assistants may crawl and cite every public page.',
           '# Plain-text business summary for language models: %sllms.txt' % D, '']
    for bot in CRAWLERS:
        out += ['User-agent: %s' % bot, 'Allow: /', 'Disallow: /tools/', '']
    out += ['User-agent: *', 'Allow: /', 'Disallow: /tools/', '',
            'Sitemap: %ssitemap.xml' % D, '']
    return '\n'.join(out)


def llms_txt(site, pages):
    """llms.txt (llmstxt.org): what Dive Adda is, and which page answers what."""
    D = site.DOMAIN
    url = lambda f: D + ('' if f == 'index.html' else f)
    L = ['# Dive Adda', '',
         '> Dive Adda is an SSI certified scuba diving centre in Visakhapatnam (Vizag), Andhra Pradesh, India. '
         'It runs beginner Try Scuba dives, SSI scuba certification courses, snorkeling and sea water activities '
         'in Vizag, and river water sports on the Godavari in Rajahmundry.', '',
         '## Key facts', '',
         '- Business: Dive Adda (Dive Adda India), an SSI (Scuba Schools International) affiliated dive centre',
         '- Locations: Visakhapatnam, Andhra Pradesh (scuba centre and sea activities); '
         'Rajahmundry, Andhra Pradesh (Godavari river water sports)',
         '- Phone and WhatsApp: %s (https://wa.me/%s)' % (site.PHONE_TXT, site.WA),
         '- Website: %s' % D,
         '- Instagram: https://www.instagram.com/diveaddaindia/',
         '- Facebook: https://www.facebook.com/diveaddaindia/',
         '- How to book: WhatsApp, phone, or the enquiry form at %scontact.html. '
         'The team confirms availability, timings and the meeting point.' % D,
         '- Prices are not published on the website; ask the dive desk by phone or WhatsApp.', '',
         '## Try Scuba (beginners, no certification needed)', '']
    L += ['- %s: %s' % (_txt(label), _txt(value)) for value, label in site.TRY_FACTS]
    L += ['- Schedule: ' + '; '.join('%s: %s' % (_txt(t), _txt(n)) for t, n, _ in site.TRY_STEPS),
          '- Included: ' + ', '.join(_txt(x) for x in site.TRY_INCLUDED),
          '- Requirements: ' + '; '.join(_txt(x) for x in site.TRY_REQUIREMENTS),
          '- Full details: %sbeginner-level-scuba.html' % D, '',
          '## SSI courses', '']
    L += ['- [%s](%s): %s Level: %s. Who it is for: %s' % (_txt(c['full']), url(c['file']), _txt(c['short']),
                                                          _txt(c['level']), _txt(c['who']))
          for c in site.COURSES]
    L += ['', '## SSI specialty courses', '']
    L += ['- %s: %s' % (_txt(sp['name']), _txt(sp['text'])) for sp in site.SPECIALTIES]
    L += ['- Details: %scourses.html#specialties' % D]
    for d in site.DESTS:
        L += ['', '## %s' % _txt(d['name']), '', _txt(d['long']), '']
        L += ['- %s: %s' % (_txt(name), _txt(text)) for _, name, _, text, _ in d['acts']]
        L += ['- Page: %s' % url(d['file'])]
    L += ['', '## Pages', '']
    titles = {'index.html': 'Home', 'about.html': 'About Dive Adda',
              'beginner-level-scuba.html': 'Beginner level scuba (Try Scuba)', 'courses.html': 'All SSI courses',
              'blog.html': 'Blog', 'gallery.html': 'Photo gallery', 'events.html': 'Underwater events',
              'faq.html': 'Frequently asked questions', 'contact.html': 'Contact and booking'}
    titles.update({c['file']: _txt(c['full']) for c in site.COURSES})
    titles.update({d['file']: _txt(d['name']) for d in site.DESTS})
    titles.update({p['file']: _txt(p['title']) for p in site.POSTS})
    L += ['- [%s](%s)' % (titles[n], url(n)) for n, _ in pages if n in titles]
    L += ['', '## Optional', '']
    L += ['- [%s](%s)' % (_txt(lp['name']), url(lp['file'])) for lp in site.LEGAL]
    L += ['- [Sitemap](%ssitemap.xml)' % D, '']
    return '\n'.join(L)
