# -*- coding: utf-8 -*-
"""
Dive Adda — static site generator.

Every page shares one chrome (ambient water, dive gate, navigation, footer,
assistant) so the underwater design system stays identical across the site.
The shared CSS/JS live in assets/; this script only composes the markup.

    python tools/build_site.py

Source of truth for copy: the Dive Adda brochure (Scuba Diving Brochure.pdf)
and the details supplied by the owner. Nothing here states a price, a rating,
a street address or a dive site, because none of those are verified.
"""
import hashlib
import html
import json
import os
import shutil
import subprocess
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, 'tools', 'index.original.html')
PARTIALS = os.path.join(ROOT, 'tools', 'partials')

DOMAIN = 'https://www.diveaddaindia.com/'
PHONE_TXT = '+91 89777 62155'
PHONE_TEL = '+918977762155'
WA = '918977762155'
IG = 'https://www.instagram.com/diveaddaindia/'
FB = 'https://www.facebook.com/diveaddaindia/'
ORG_ID = DOMAIN + '#organization'
CENTRE_ID = DOMAIN + '#divecentre'
E = html.escape


# ---------------------------------------------------------------- partials
def _orig(a, b):
    lines = open(ORIG, encoding='utf-8').read().split('\n')
    return '\n'.join(lines[a - 1:b])


FIREBASE = _orig(195, 250)
TWCONFIG = _orig(253, 284)
# The demo config's hero-pattern pointed at a stock photo; keep the utility,
# point it at our own cover image so no page references a stock URL.
TWCONFIG = TWCONFIG.replace(
    "https://images.unsplash.com/photo-1530053969600-caed2596d242?q=80&w=2070&auto=format&fit=crop",
    "assets/img/brochure/cover-divers.jpg")
NOSCRIPT = _orig(1915, 1927)
AMBIENT = open(os.path.join(PARTIALS, 'ambient.html'), encoding='utf-8').read()
GATE = open(os.path.join(PARTIALS, 'gate.html'), encoding='utf-8').read()


# ---------------------------------------------------------------- helpers
def U(pid, w=1200):
    return 'https://images.unsplash.com/photo-%s?q=80&w=%d&auto=format&fit=crop' % (pid, w)


def uset(pid):
    return ', '.join('%s %dw' % (U(pid, w), w) for w in (480, 768, 1200, 1600))


def B(name):
    return 'assets/img/brochure/%s.jpg' % name


PHOTO_DIRS = ('assets/img/brochure/', 'assets/img/activities/')
_MANIFESTS = {}


def _img_meta(src):
    """(folder, stem, meta) for a photo that tools/optimize_images.py has processed."""
    folder = next((d for d in PHOTO_DIRS if src.startswith(d)), None)
    if not folder:
        return None, None, None
    if folder not in _MANIFESTS:
        path = os.path.join(ROOT, folder, 'manifest.json')
        _MANIFESTS[folder] = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    stem = src.rsplit('/', 1)[1].rsplit('.', 1)[0]
    return folder, stem, _MANIFESTS[folder].get(stem)


def webp_srcset(src):
    folder, stem, m = _img_meta(src)
    if not m:
        return ''
    return ', '.join('%s%s-%d.webp %dw' % (folder, stem, w, w) for w in m['widths'])


def full_src(src):
    """Largest rendition, for the lightbox."""
    folder, stem, m = _img_meta(src)
    return '%s%s-%d.webp' % (folder, stem, m['widths'][-1]) if m else src


def photo(src, alt, cls='', sizes='100vw', lazy=True, extra=''):
    """A responsive image: Unsplash srcset, or WebP renditions with the JPEG as fallback."""
    load = 'loading="lazy"' if lazy else 'fetchpriority="high"'
    alt = html.unescape(alt)
    if src.startswith('uns:'):
        pid = src[4:]
        return ('<img src="%s" srcset="%s" sizes="%s" alt="%s" class="%s" %s %s decoding="async">'
                % (U(pid), uset(pid), sizes, E(alt), cls, load, extra))
    _, _, m = _img_meta(src)
    dims = 'width="%d" height="%d"' % (m['w'], m['h']) if m else ''
    img = ('<img src="%s" alt="%s" class="%s" %s %s %s decoding="async">'
           % (src, E(alt), cls, dims, load, extra))
    srcset = webp_srcset(src)
    if not srcset:
        return img
    return '<picture><source type="image/webp" srcset="%s" sizes="%s">%s</picture>' % (srcset, sizes, img)


def src_of(src):
    return U(src[4:], 1600) if src.startswith('uns:') else src


ICON = {
    'shield': 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
    'people': 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
    'heart': 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
    'cap': 'M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z',
    'spark': 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z',
    'globe': 'M21 12a9 9 0 11-18 0 9 9 0 0118 0zM3.6 9h16.8M3.6 15h16.8M12 3a15 15 0 010 18 15 15 0 010-18z',
    'pin': 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM15 11a3 3 0 11-6 0 3 3 0 016 0z',
    'eye': 'M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
    'bolt': 'M13 10V3L4 14h7v7l9-11h-7z',
    'phone': 'M3 5a2 2 0 012-2h3.28a1 1 0 01.95.68l1.5 4.5a1 1 0 01-.5 1.21l-2.26 1.13a11 11 0 005.52 5.52l1.13-2.26a1 1 0 011.2-.5l4.5 1.5a1 1 0 01.68.95V19a2 2 0 01-2 2h-1A16 16 0 013 6V5z',
    'chat': 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z',
    'camera': 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9zm12 4a3 3 0 11-6 0 3 3 0 016 0z',
    'gift': 'M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zM5 12h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7',
    'boat': 'M3 17l2.5-7h13L21 17M5 21h14a2 2 0 001.9-1.37L22 16H2l1.1 3.63A2 2 0 005 21zM12 10V4m0 0L9 6m3-2l3 2',
    'wave': 'M2 12c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2M2 17c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2M2 7c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2',
    'clock': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    'arrow': 'M17 8l4 4m0 0l-4 4m4-4H3',
    'check': 'M5 13l4 4L19 7',
    'plus': 'M12 4v16m8-8H4',
}


def svg(name, cls='w-5 h-5', sw='2'):
    return ('<svg class="%s" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="%s" d="%s"></path></svg>'
            % (cls, sw, ICON[name]))


def wa_link(text):
    return 'https://wa.me/%s?text=%s' % (WA, quote(text))


# ---------------------------------------------------------------- site data
DESTS = [
    dict(id='visakhapatnam', name='Visakhapatnam', short='Vizag', file='visakhapatnam.html',
         sub='Vizag &middot; Andhra Pradesh', img=B('cover-divers'), hero=B('cover-divers'), depth=12,
         blurb='Home of our SSI certified scuba centre on the Bay of Bengal &mdash; try scuba, snorkel and ride the waves.',
         long='Visakhapatnam (Vizag) is the coastal home of Dive Adda. Our SSI certified scuba centre runs Try Scuba, SSI courses and guided dives here, alongside snorkeling and water activities on the Bay of Bengal.',
         acts=[
             ('scuba-diving', 'Scuba Diving', 'wave', 'Breathe underwater with an SSI instructor beside you. New to diving? Start at beginner level.', 'beginner-level-scuba.html'),
             ('snorkeling', 'Snorkeling', 'eye', 'Explore underwater life effortlessly, floating with a mask, snorkel and fins. No certification needed.', None),
             ('jet-ski', 'Jet Ski', 'bolt', 'A fast, thrilling ride across the water on a jet ski.', None),
             ('leisure-boat', 'Leisure Boat', 'boat', 'A relaxed boat ride out on the water.', None),
             ('atv-rides', 'ATV Rides', 'spark', 'Off-road fun on an all-terrain vehicle.', None),
         ]),
    dict(id='rajahmundry', name='Rajahmundry', short='Rajahmundry', file='rajahmundry.html',
         sub='On the Godavari &middot; Andhra Pradesh', img='assets/img/activities/godavari-bridge.jpg',
         hero='assets/img/activities/godavari-bridge.jpg', depth=3,
         blurb='Water rides and adventures on the Godavari river with the Dive Adda team.',
         long='Rajahmundry sits on the banks of the Godavari in Andhra Pradesh. Dive Adda runs speed boat rides, jet ski rides and kayaking here, plus towed rides for groups.',
         acts=[
             ('speed-boat-ride', 'Speed Boat Ride', 'boat', 'A high-speed boat ride across the Godavari.', None),
             ('jet-ski-ride', 'Jet Ski Ride', 'bolt', 'Skim across the river on a jet ski.', None),
             ('kayaking', 'Kayaking', 'wave', 'Paddle at your own pace in a kayak.', None),
             ('dragon-ride', 'Dragon Ride', 'spark', 'A towed inflatable ride for groups &mdash; hold on tight.', None),
             ('disco-ride', 'Disco Ride', 'spark', 'A spinning towed ride that is all about the laughs.', None),
             ('bumper-ride', 'Bumper Ride', 'people', 'A towed bumper ride that bounces across the water.', None),
         ]),
]

COURSES = [
    dict(id='open-water', file='open-water-diver.html', name='Open Water Diver', full='SSI Open Water Diver', level='Beginner', step='01', depth=18,
         img=B('ssi-pool-training'),
         short='The entry-level SSI certification &mdash; your first step from confined water practice to diving in open water.',
         long='Open Water Diver is where most divers begin. You learn the essential skills in confined water with an instructor beside you, then put them to use in open water. It is an internationally recognised SSI certification.',
         who='Anyone who wants a scuba certification of their own. No previous diving experience is needed.',
         learn=['Essential diving skills', 'How your equipment works', 'Safe diving practices', 'An internationally recognised SSI certification']),
    dict(id='advanced-adventurer', file='advanced-adventurer.html', name='Advanced Adventurer', full='SSI Advanced Adventurer', level='Certified divers', step='02', depth=30,
         img='uns:1582967788606-a171c1080cb0',
         short='Build on your training and try different types of diving with an instructor alongside you.',
         long='Advanced Adventurer is the natural next step after Open Water. You dive with an instructor across different kinds of diving, adding experience and confidence to the skills you already have.',
         who='Certified Open Water divers ready to try different types of diving.',
         learn=['Experience across different types of diving', 'More confidence in the water', 'Guided dives with an instructor', 'A foundation for further SSI training']),
    dict(id='react-right', file='react-right.html', name='React Right', full='SSI React Right', level='First aid &middot; all levels', step='03', depth=5,
         img=B('confined-diving'),
         short='SSI&rsquo;s first aid and emergency response training, for divers and non-divers.',
         long='React Right is SSI&rsquo;s first aid and emergency response programme. It teaches you to recognise an emergency and respond to it calmly &mdash; skills that matter on a dive boat and on dry land.',
         who='Divers and non-divers who want first aid and emergency response skills.',
         learn=['Recognising an emergency', 'First aid and emergency response', 'Staying calm under pressure', 'A core part of the rescue pathway']),
    dict(id='diver-stress-rescue', file='diver-stress-rescue.html', name='Diver Stress &amp; Rescue', full='SSI Diver Stress &amp; Rescue', level='Continuing education', step='04', depth=20,
         img='uns:1530053969600-caed2596d242',
         short='Learn to spot stress early, prevent problems, and help another diver when something goes wrong.',
         long='Stress is behind most diving incidents. This programme teaches you to recognise it in yourself and your buddy, prevent problems before they escalate, and manage a rescue if one is needed.',
         who='Certified divers who want to recognise and manage problems underwater.',
         learn=['Recognising stress in yourself and others', 'Preventing problems before they grow', 'Rescue skills and techniques', 'Diving with greater awareness']),
    dict(id='dive-master', file='dive-master.html', name='Dive Master', full='SSI Divemaster', level='Professional', step='05', depth=40,
         img=B('guided-fun-dive'),
         short='The first professional level &mdash; for divers who want to guide, assist and build a career in diving.',
         long='Dive Master is the first professional rating in the SSI pathway. It is for experienced divers who want to guide certified divers, assist instructors, and take diving from a hobby to a career.',
         who='Experienced divers who want to guide others and take diving from a hobby to a career.',
         learn=['Guiding certified divers', 'Assisting instructors', 'Dive leadership and planning', 'The start of a career in diving']),
]

# ---- First Time Scuba (Try Scuba), from the Dive Adda program
TRY_FACTS = [('6:30 AM &ndash; 12:30 PM', 'Morning experience'), ('&asymp; 40 min', 'Dive time per person'),
             ('6&ndash;8 m', 'Maximum depth'), ('8 years', 'Minimum age')]

TRY_STEPS = [
    ('6:30 AM &ndash; 6:45 AM', 'Report at Centre',
     'Report at the Dive Adda centre to complete the necessary formalities before starting your scuba diving experience.'),
    ('6:45 AM &ndash; 7:15 AM', 'Equipment &amp; Dive Briefing',
     'Join our classroom briefing to learn about your scuba diving equipment, safety procedures and dive plan. Our team will help you understand your gear and the important instructions you need to follow for a safe and enjoyable underwater experience.'),
    ('7:30 AM &ndash; 8:30 AM', 'Travel to the Dive Site',
     'Travel to the beach, where the boat will be loaded before heading to the dive site. After a short 10&ndash;15 minute boat ride, you&rsquo;ll reach the dive site and begin your underwater experience accompanied by a professional diving instructor.'),
    ('About 40 minutes per person', 'Your Dive',
     'Each scuba diving session lasts approximately 40 minutes per person, reaching a maximum depth of 6&ndash;8 metres.'),
    ('12:00 PM &ndash; 12:30 PM', 'Return to Beach &amp; Centre',
     'After returning, your scuba diving pictures and video will be transferred to you at the centre. If the transfer is not possible at the centre, they will be shared online.'),
]

TRY_INCLUDED = ['Boat', 'Scuba diving equipment', 'Experienced instructors', 'Snacks, fruits and water', 'Pictures and video of your experience']

TRY_REQUIREMENTS = ['Minimum age: 8 years',
                    'Guests with major medical conditions require prior written approval from a physician',
                    'It is recommended that you do not fly within 18&ndash;24 hours after diving']

TRY_KNOW = [
    ('camera', 'Bring Your Essentials', 'Please bring a cap, change of clothes and towel.'),
    ('heart', 'Eat Light Before Diving', 'We recommend eating light before arriving to avoid feeling uncomfortable during the boat journey.'),
    ('wave', 'Weather &amp; Sea Conditions', 'The itinerary may change depending on sea and local weather conditions.'),
    ('pin', 'Transport &amp; Accommodation', 'Guests need to arrange their own transportation and accommodation.'),
]

TRY_FAQS = [
    ('What is Try Scuba?', 'Try Scuba is an introduction to scuba diving that allows beginners to experience the underwater world with equipment training, safety briefing and guidance from an experienced diving instructor.'),
    ('Do I need previous scuba diving experience?', 'No. Try Scuba is an introductory scuba diving experience designed for people who are trying scuba diving.'),
    ('What is the minimum age for Try Scuba?', 'The minimum age for Try Scuba is 8 years.'),
    ('How long is the scuba diving session?', 'Each scuba diving session lasts approximately 40 minutes per person.'),
    ('How deep will I go during Try Scuba?', 'The maximum depth is 6&ndash;8 metres.'),
    ('Is scuba diving equipment provided?', 'Yes. The boat and scuba diving equipment are included in the Try Scuba experience.'),
    ('Will an instructor accompany me during the dive?', 'Yes. Your dive is accompanied by an experienced, professional diving instructor.'),
    ('Will I get photos and videos of my dive?', 'Yes. Pictures and a video are included in the experience.'),
    ('What should I bring for scuba diving?', 'Bring a cap, change of clothes and towel. It is also recommended to eat light before arriving.'),
    ('Can I fly after scuba diving?', 'We recommend that you do not fly within 18&ndash;24 hours after diving.'),
    ('Can I scuba dive if I have a medical condition?', 'Guests with major medical conditions require prior written approval from a physician.'),
    ('What happens if the weather is bad?', 'If weather conditions are unsuitable, the dive may be postponed according to guest availability. If postponement is not possible, the amount will be refunded after deducting the cost of activities already undertaken.'),
    ('What is the cancellation policy?', 'Cancellation 72 hours before the activity: 50% refund. Cancellation 24&ndash;48 hours before the activity: no refund. See our <a href="refund-policy.html" class="link-glow font-semibold">Refund Policy</a> for details.'),
]

# Everything a guest can ask for by name: forms, the booking assistant and Book buttons share it
EXPERIENCE_OPTIONS = ['Try Scuba (first dive)', 'SSI Course']
for _d in DESTS:
    for _a in _d['acts']:
        if _a[1] not in EXPERIENCE_OPTIONS:
            EXPERIENCE_OPTIONS.append(_a[1])
EXPERIENCE_OPTIONS += ['Underwater Event', 'Something else']

# ---- SSI specialty programmes
SPECIALTIES = [
    dict(id='deep-diving', name='Deep Diving', icon='eye',
         text='Plan and make deeper dives with the training, gas awareness and safety skills that depth asks for.'),
    dict(id='enriched-air-nitrox', name='Enriched Air Nitrox', icon='bolt',
         text='Dive with a higher-oxygen mix to extend your no-decompression limits on repetitive dives.'),
    dict(id='perfect-buoyancy', name='Perfect Buoyancy', icon='wave',
         text='Hover effortlessly, use less air and keep your fins clear of the reef.'),
    dict(id='night-limited-visibility', name='Night &amp; Limited Visibility', icon='spark',
         text='Dive after dark or in low visibility using lights, signals and careful navigation.'),
]

# ---- Reviews. Paste real quotes here (name, date, rating, text); the section
# links to the review sites until it has any.
TRIPADVISOR_URL = 'https://www.tripadvisor.in/Attraction_Review-g12421929-d33033322-Reviews-Dive_Adda_Scuba_Diving_Center-Visakhapatnam_District_Andhra_Pradesh.html'
GOOGLE_REVIEWS_URL = 'https://www.google.com/search?q=Dive+Adda+Scuba+Diving+Center+Visakhapatnam+reviews'

# Homepage testimonials. The entries below are copied exactly from the review
# screenshot supplied for the design (excerpts end where the screenshot cut
# them off). They are marked demo=True because they could not be checked
# against Dive Adda's live Google and TripAdvisor pages; while any source is a
# demo, the section says so. Once confirmed, set demo=False. Counts and relative
# dates are as shown in the screenshot and will not update on their own.
REVIEW_SOURCES = [
    dict(id='google', name='Google', url=GOOGLE_REVIEWS_URL, label='Excellent', rating=5, count=568, demo=True,
         reviews=[
             dict(name='MarvelouSiddharth', when='7 months ago', rating=5,
                  text='Best scuba school in goa highly recommended! My wife and I had an amazing&hellip;', more=True),
             dict(name='Mahesh g.warrier', when='7 months ago', rating=5, text='Had a great experience.'),
             dict(name='Manna Singh', when='7 months ago', rating=5,
                  text='It was priceless movement&hellip;i must recommend this as they are very professional&hellip;.i was scared before start but dinesh the instructor he&hellip;', more=True),
         ]),
    dict(id='tripadvisor', name='Tripadvisor', url=TRIPADVISOR_URL, label='Excellent', rating=5, count=381, demo=True,
         reviews=[
             dict(name='Freedom58686498324', when='5 months ago', rating=5, title='Scuba',
                  text='Very good experience to much friendly staff members they help you'),
             dict(name='Travel25055630721', when='5 months ago', rating=5, title='40+40 scuba diving',
                  text='It&rsquo;s spell bounding experience, I can&rsquo;t express my happiness. I took 40+40 min long scuba diving . That&hellip;', more=True),
             dict(name='Dwarkesh', when='5 months ago', rating=5, title='Scuba Nitrox',
                  text='Great experience with Ashish &amp; Dinesh! Will come back here next time as well!'),
         ]),
]


def _live_reviews(path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'data', 'reviews.json')):
    """Replace a sample source with live API data (tools/fetch_reviews.py) when cached."""
    try:
        with open(path, encoding='utf-8') as f:
            live = json.load(f)
    except (OSError, ValueError):
        return
    for src in REVIEW_SOURCES:
        d = live.get(src['id'])
        if not d or not d.get('reviews'):
            continue
        reviews = []
        for r in d['reviews'][:8]:
            text = r['text']
            cut = len(text) > 180
            if cut:
                text = text[:170].rsplit(' ', 1)[0] + '…'
            reviews.append(dict(name=r['name'], when=E(r.get('when', '')), rating=r.get('rating') or 5,
                                title=E(r['title']) if r.get('title') else '', text=E(text), more=cut))
        rating = d.get('rating') or 0
        src.update(demo=False, reviews=reviews, url=d.get('url') or src['url'], rating=round(rating),
                   count=d.get('count'), label='Excellent' if rating >= 4.5 else 'Very good' if rating >= 4 else 'Rated %.1f' % rating)


# ---- Blog
BLOG_LINKS = [
    ('SSI Blog', 'https://www.divessi.com/blog/', 'Training, marine life and travel stories from Scuba Schools International.'),
    ('SSI Education', 'https://www.divessi.com/en/education', 'How the SSI training path works, from your first dive to professional level.'),
    ('Divers Alert Network', 'https://dan.org/', 'Dive safety, health and medical guidance for divers.'),
]

POSTS = [
    dict(slug='first-dive-what-to-expect',
         file='blog-first-dive-what-to-expect.html',
         title='What to expect on your first scuba dive in Vizag',
         date='2026-09-21', date_label='21 September 2026', read='4 min read',
         tag='Beginner',
         img=B('guided-fun-dive'),
         excerpt='Never breathed underwater before? Here is exactly how a beginner dive morning with Dive Adda runs, from the briefing at our centre to the boat ride out.',
         intro='If you have never breathed underwater before, the first question is usually the same: what actually happens on the day? Here is the whole morning, start to finish.'),
]


def opt_img(*candidates):
    # First local file that exists; drop a file in and the build picks it up.
    for rel in candidates:
        if rel and os.path.exists(os.path.join(ROOT, rel.replace('/', os.sep))):
            return rel
    return ''


ACTIVITY_FALLBACK = {
    'scuba-diving': 'assets/img/brochure/guided-fun-dive.jpg',
    'snorkeling': 'assets/img/brochure/snorkelling.jpg',
    'leisure-boat': 'assets/img/brochure/boat-diving.jpg',
    'speed-boat-ride': 'assets/img/brochure/boat-diving.jpg',
}


def activity_photo(aid):
    # The fallback may be a stock-photo id rather than a file, so it is not
    # existence-checked: a dropped-in photo wins, otherwise the fallback stands.
    return (opt_img('assets/img/activities/%s.jpg' % aid, 'assets/img/activities/%s.webp' % aid,
                    'assets/img/activities/%s.png' % aid) or ACTIVITY_FALLBACK.get(aid, ''))


def course_photo(cid, fallback=''):
    return (opt_img('assets/img/courses/%s.jpg' % cid, 'assets/img/courses/%s.webp' % cid,
                    'assets/img/courses/%s.png' % cid) or fallback)

EVENTS = [
    dict(id='birthday-parties', name='Birthday Parties', img=B('event-birthday'), icon='gift',
         text='Mark the day underwater. We plan the dive, the group and the moment with you, so the celebration happens beneath the surface.'),
    dict(id='marriage-proposals', name='Marriage Proposals', img=B('event-proposal'), icon='heart',
         text='Ask the question where nobody expects it. Our team helps you plan the descent, the timing and the surprise.'),
    dict(id='pre-wedding-shoots', name='Pre-Wedding Shoots', img=B('event-prewedding'), icon='camera',
         text='An underwater pre-wedding shoot, guided by divers who know how to keep you comfortable and photogenic below the surface.'),
    dict(id='conservation-diving', name='Conservation Diving', img=B('event-conservation'), icon='globe',
         text='Divers witness the effects of pollution firsthand. Join a conservation dive &mdash; cleaning up waste, protecting reefs and building ocean awareness.'),
]

SCUBA_CARDS = [
    ('01', 'bolt', 'What is Scuba?',
     'An underwater adventure that lets you explore the marine world using a Self-Contained Underwater Breathing Apparatus.',
     '<p>Scuba enables divers to breathe underwater and move freely while exploring coral reefs, shipwrecks and marine life. '
     'It is both a recreational and a professional activity, with applications in marine research, underwater photography, '
     'rescue operations and even archaeology.</p>'),
    ('02', 'heart', 'Why Scuba Diving?',
     'More than a sport &mdash; it is a gateway to a whole new world beneath the ocean.',
     '<ul class="space-y-3">'
     '<li><b class="text-brand-glow">Exploration &amp; Adventure:</b> the wonders of the ocean, from vibrant coral reefs to fascinating sea creatures.</li>'
     '<li><b class="text-brand-glow">Thrilling Experience:</b> weightlessness and free movement, similar to floating in space.</li>'
     '<li><b class="text-brand-glow">Escape from Routine:</b> a peaceful, quiet world away from the hustle of daily life.</li>'
     '<li><b class="text-brand-glow">Close to Nature:</b> marine life in its natural habitat, and a deeper appreciation for the ocean.</li>'
     '</ul>'),
    ('03', 'cap', 'Benefits of a Course',
     'What taking a scuba diving course actually gives you.',
     '<ul class="grid sm:grid-cols-2 gap-2.5">'
     + ''.join('<li class="flex items-start gap-2.5"><span class="bp-dot mt-1.5"></span><span>%s</span></li>' % b for b in [
         'Learn essential diving skills', 'Enhanced safety', 'Global certification',
         'Career &amp; volunteering opportunities', 'Physical &amp; mental health benefits',
         'Meet a community of divers', 'Underwater photography &amp; videography'])
     + '</ul>'),
    ('04', 'globe', 'Diving Protects the Ocean',
     'Divers play a big role in protecting the ocean &mdash; and awareness starts underwater.',
     '<p>By exploring underwater, divers witness firsthand the effects of pollution and climate change. Many take part in '
     'conservation efforts like cleaning up plastic waste, protecting coral reefs and educating others about ocean health. '
     'Some become marine biologists or volunteers in reef restoration projects. The more people who learn to dive responsibly, '
     'the more awareness we create about keeping our oceans clean and safe for future generations.</p>'),
]

GALLERY = [
    (B('cover-divers'), 'diving', 'Divers over the reef', 'Dive, Discover, Repeat', 'g-wide g-tall'),
    (B('ssi-pool-training'), 'courses', 'SSI training session', 'Skills in confined water', 'g-tall'),
    (B('guided-fun-dive'), 'diving', 'Guided fun dive', 'With a Dive Adda instructor', ''),
    (B('snorkelling'), 'snorkelling', 'Snorkelling', 'Mask, snorkel and fins', ''),
    (B('dive-centre-storefront'), 'destinations', 'The Dive Adda centre', 'Scuba dive centre', 'g-tall'),
    (B('boat-diving'), 'boat', 'Boat diving', 'Entry from the boat', 'g-wide'),
    (B('confined-diving'), 'courses', 'Confined water training', 'Controlled environment', ''),
    (B('outbound-trip'), 'destinations', 'Outbound trip', 'Diving together', 'g-wide'),
    (B('event-birthday'), 'events', 'Underwater birthday', 'Celebrating below the surface', ''),
    (B('event-proposal'), 'events', 'Underwater proposal', 'The question, underwater', ''),
    (B('event-prewedding'), 'events', 'Pre-wedding shoot', 'Underwater portraits', ''),
    (B('event-conservation'), 'events', 'Conservation dive', 'Waste recovered from the water', ''),
]

GALLERY_FILTERS = [('all', 'All'), ('diving', 'Diving'), ('courses', 'Courses'), ('snorkelling', 'Snorkelling'),
                   ('boat', 'Boat Diving'), ('events', 'Underwater Events'), ('destinations', 'Locations')]

TEAM = [
    dict(mono='DA', name='Our Founder', role='Founder, Dive Adda',
         cert='Founded Dive Adda as an SSI affiliated dive centre',
         exp='15 years of service in the Indian Navy, over a decade of experience in submarines, and 10 years in the oil &amp; gas industry',
         spec='Underwater marine operations',
         bio='Dive Adda was founded by a seasoned professional whose journey is deeply rooted in the world beneath the waves. Years of hands-on experience in underwater marine operations led to a scuba diving company built on safe, exciting and unforgettable diving experiences.'),
    dict(mono='SSI', name='Our Instructor Team', role='Professional dive instructors',
         cert='SSI training programmes',
         exp='Over 15 years of industry experience',
         spec='Training for every level, from a first dive to professional',
         bio='Our team of expert instructors provides professional dive training for all levels &mdash; from beginners taking their first dive to advanced divers and professionals looking to enhance their skills.'),
]

GENERAL_FAQS = [
    ('Is Dive Adda SSI certified?',
     'Yes. Dive Adda is an internationally certified dive centre, proudly affiliated with SSI (Scuba Schools International), which means our training programmes meet the highest global standards.'),
    ('What courses are available?',
     'SSI courses from beginner to professional level: Open Water Diver, Advanced Adventurer, React Right, Diver Stress &amp; Rescue and Dive Master. Each course has its own page with details.'),
    ('Where does Dive Adda operate?',
     'Our SSI certified scuba centre is in Visakhapatnam (Vizag). We also run water activities in Rajahmundry.'),
    ('What activities are available in Visakhapatnam?',
     'Scuba diving, snorkeling, jet ski, leisure boat rides and ATV rides.'),
    ('What activities are available in Rajahmundry?',
     'Speed boat rides, jet ski rides, kayaking, dragon rides, disco rides and bumper rides.'),
    ('How do I book?',
     'Use the booking assistant on this site, send an enquiry through the contact form, message us on WhatsApp, or call us on %s. We confirm availability for your date and take it from there.' % PHONE_TXT),
]


NAV = [
    ('home', 'Home', 'index.html', None),
    ('about', 'About Us', 'about.html', None),
    ('beginner-level-scuba', 'Beginner Level Scuba', 'beginner-level-scuba.html', None),
    ('courses', 'Courses', 'courses.html',
     [('Beginner Level Scuba', 'beginner-level-scuba.html')] + [(c['name'], c['file']) for c in COURSES]
     + [('Specialties', 'courses.html#specialties'), ('View all courses', 'courses.html')]),
    ('locations', 'Locations', None, 'locations'),
    ('more', 'More', None, [('Blog', 'blog.html'), ('Gallery', 'gallery.html'), ('Events', 'events.html'), ('FAQ&rsquo;s', 'faq.html')]),
    ('contact', 'Contact Us', 'contact.html', None),
]

CARET = ('<svg class="caret" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
         '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7"></path></svg>')
M_CARET = ('<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
           '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7"></path></svg>')


# ---------------------------------------------------------------- chrome
def locations_drop():
    # Desktop flyout: pick a location, its activities show alongside
    tabs = ''.join(
        '<button type="button" class="loc-tab" role="tab" id="loct-%s" aria-selected="%s" aria-controls="locp-%s">'
        '<span>%s</span><span class="loc-count">%d</span></button>'
        % (d['id'], 'true' if i == 0 else 'false', d['id'], d['name'], len(d['acts']))
        for i, d in enumerate(DESTS))
    panels = ''.join(
        '<div class="loc-panel" id="locp-%s" role="tabpanel" aria-labelledby="loct-%s"%s>'
        '<span class="drop-title">Activities</span>%s'
        '<a class="loc-all" href="%s">Explore %s &rarr;</a></div>'
        % (d['id'], d['id'], '' if i == 0 else ' hidden',
           ''.join('<a href="%s#%s"><span class="dot"></span>%s</a>' % (d['file'], a[0], a[1]) for a in d['acts']),
           d['file'], d['name'])
        for i, d in enumerate(DESTS))
    return ('<div class="nav-drop loc-drop glass-deep theme-scope">'
            '<div class="loc-tabs" role="tablist" aria-label="Locations">' + tabs + '</div>'
            '<div class="loc-panels">' + panels + '</div></div>')


def locations_mobile():
    subs = ''.join(
        '<details class="m-sub"><summary>%s%s</summary><div class="m-sub-links">%s'
        '<a class="m-sub-all" href="%s">Explore %s &rarr;</a></div></details>'
        % (d['name'], M_CARET,
           ''.join('<a href="%s#%s">%s</a>' % (d['file'], a[0], a[1]) for a in d['acts']),
           d['file'], d['name'])
        for d in DESTS)
    return '<details class="m-group"><summary>Locations' + M_CARET + '</summary><div class="m-links">' + subs + '</div></details>'


def nav(page, section):
    desktop = []
    mobile = []
    for key, label, href, children in NAV:
        active = ' is-active' if section == key else ''
        aria = ' aria-current="page"' if section == key else ''
        if children == 'locations':
            desktop.append('<div class="nav-item nav-loc"><button type="button" class="nav-link%s" aria-expanded="false" aria-haspopup="true">Locations%s</button>%s</div>'
                           % (active, CARET, locations_drop()))
            mobile.append(locations_mobile())
        elif children:
            drop = ''.join('<a href="%s"%s><span class="dot"></span>%s</a>'
                           % (h, ' class="drop-all"' if l.startswith('View all') else '', l) for l, h in children)
            desktop.append(
                '<div class="nav-item"><button type="button" class="nav-link%s" aria-expanded="false" aria-haspopup="true">%s%s</button>'
                '<div class="nav-drop glass-deep theme-scope"><span class="drop-title">%s</span>%s</div></div>'
                % (active, label, CARET, label, drop))
            mobile.append('<details class="m-group"><summary>%s%s</summary><div class="m-links">%s</div></details>'
                          % (label, M_CARET, ''.join('<a href="%s">%s</a>' % (h, l) for l, h in children)))
        else:
            desktop.append('<a href="%s" class="nav-link%s"%s>%s</a>' % (href, active, aria, label))
            mobile.append('<a href="%s" class="m-link">%s</a>' % (href, label))

    return '''    <nav id="navbar" class="pre-dive post-dive-in fixed inset-x-0 top-0 z-50" aria-label="Main">
      <div id="navPill" class="glass-deep theme-scope relative max-w-7xl mx-auto flex justify-between items-center gap-3 rounded-2xl">

        <a href="index.html" class="nav-brand flex items-center group min-w-0" aria-label="Dive Adda — home">
          <img src="assets/img/logo-mark-light-2x.png" alt="" class="brand-mark logo-light" width="69" height="38">
          <img src="assets/img/logo-mark-2x.png" alt="" class="brand-mark logo-dark" width="69" height="38">
          <span class="brand-text leading-none min-w-0">
            <span class="brand-word block text-white">DIVE ADDA</span>
            <span class="brand-tag block mt-1">Discover &mdash; The Deep</span>
          </span>
        </a>

        <div class="nav-links hidden xl:flex items-center gap-5 font-medium text-[13px]">
          ''' + '\n          '.join(desktop) + '''
          <button type="button" data-book class="btn-bio liquid ripple-host px-5 py-2.5 rounded-full font-semibold text-[13px] whitespace-nowrap">Book your dive</button>
        </div>

        <div class="nav-actions flex items-center gap-2 sm:gap-3 shrink-0 xl:ml-4">
          <button id="themeToggle" class="theme-toggle" type="button" role="switch" aria-checked="false" aria-label="Switch between dark and light theme" title="Switch theme">
            <span class="knob">
              <svg class="ic ic-moon" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
              <svg class="ic ic-sun" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17a5 5 0 100-10 5 5 0 000 10zm0 2.5a1 1 0 011 1V22a1 1 0 11-2 0v-1.5a1 1 0 011-1zm0-19a1 1 0 011 1V3a1 1 0 11-2 0V1.5a1 1 0 011-1zM3.5 11h1.5a1 1 0 110 2H3.5a1 1 0 110-2zm15.5 0h1.5a1 1 0 110 2H19a1 1 0 110-2zM5.6 4.2l1.1 1.1a1 1 0 11-1.4 1.4L4.2 5.6a1 1 0 011.4-1.4zm11.7 11.7l1.1 1.1a1 1 0 11-1.4 1.4l-1.1-1.1a1 1 0 011.4-1.4zM18.4 4.2a1 1 0 011.4 1.4l-1.1 1.1a1 1 0 11-1.4-1.4zM6.7 15.9a1 1 0 011.4 1.4l-1.1 1.1a1 1 0 11-1.4-1.4z"/></svg>
            </span>
          </button>
          <button id="mobileMenuBtn" type="button" class="nav-burger xl:hidden text-brand-glow" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu">
            <svg class="ic ic-open w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            <svg class="ic ic-close w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div id="mobileMenu" class="glass-deep theme-scope absolute top-full mt-3 left-0 right-0 flex-col p-5 sm:p-6 rounded-2xl">
          <div class="m-contact">
            <a href="tel:''' + PHONE_TEL + '''" class="m-call">''' + svg('phone', 'w-4 h-4') + '''<span>''' + PHONE_TXT + '''</span></a>
            <a href="''' + wa_link('Hi Dive Adda!') + '''" target="_blank" rel="noopener" class="m-wa" aria-label="Chat on WhatsApp">''' + svg('chat', 'w-4 h-4') + '''<span>WhatsApp</span></a>
          </div>
          ''' + '\n          '.join(mobile) + '''
          <button type="button" data-book class="btn-bio liquid ripple-host w-full mt-4 px-6 py-3 rounded-full font-bold">Book your dive</button>
        </div>
      </div>
    </nav>
'''


def float_widgets():
    return '''    <a href="''' + wa_link("Hi Dive Adda! I'd like to ask about diving with you.") + '''"
       target="_blank" rel="noopener"
       class="float-widget fixed bottom-6 left-6 z-[90] w-14 h-14 rounded-full text-white flex items-center justify-center group liquid ripple-host animate-float bg-[#128C4A]/90 border border-[#4ade80]/35 shadow-[0_14px_36px_-10px_rgba(37,211,102,0.55)] hover:shadow-[0_18px_46px_-8px_rgba(37,211,102,0.85)] backdrop-blur-md"
       aria-label="Chat with Dive Adda on WhatsApp">
        <span class="absolute inset-0 rounded-full bg-[#25D366]/30 blur-lg bio-pulse" style="--dur:5s" aria-hidden="true"></span>
        <svg class="relative w-7 h-7 drop-shadow-md" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
        </svg>
        <span class="absolute left-[68px] glass-deep text-brand-ink px-3 py-1.5 rounded-xl text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap pointer-events-none">Chat on WhatsApp</span>
    </a>

    <div id="callRail" class="theme-scope" role="complementary" aria-label="Quick contact">
        <a href="tel:''' + PHONE_TEL + '''" class="call-pill call-fab glass-deep" aria-label="Call Dive Adda on ''' + PHONE_TXT + '''" title="Call ''' + PHONE_TXT + '''">
            <span class="call-ic">''' + svg('phone', 'w-4 h-4') + '''</span>
            <span class="call-text">
                <span class="block text-[9px] uppercase tracking-[0.22em] text-brand-glow">Dive desk</span>
                <span class="block text-sm font-bold text-white leading-tight">''' + PHONE_TXT + '''</span>
            </span>
        </a>
        <button type="button" data-book class="rail-book group ripple-host glass-deep border-r-0 rounded-l-2xl py-6 px-2 md:px-3 flex flex-col items-center gap-3 text-brand-ink transition-all duration-500 hover:pr-4 hover:shadow-[-10px_0_40px_-8px_rgba(34,211,238,0.55)]">
            <span class="absolute inset-y-0 left-0 w-[2px] bg-gradient-to-b from-brand-accent via-brand-violet to-transparent shadow-[0_0_14px_#22D3EE]" aria-hidden="true"></span>
            <svg class="w-5 h-5 text-brand-glow group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            <span style="writing-mode: vertical-rl; transform: rotate(180deg);" class="font-display font-bold tracking-[0.22em] text-[11px] uppercase text-brand-ink/90 group-hover:text-white transition-colors">Booking Open</span>
        </button>
    </div>

    <div id="depthMeter" aria-hidden="true">
        <span class="dm-label">Depth</span>
        <span class="dm-track"><span class="dm-fill"></span></span>
        <span class="dm-read">0m</span>
    </div>
'''


def footer():
    explore = [('About Us', 'about.html'), ('Beginner Level Scuba', 'beginner-level-scuba.html'), ('SSI Courses', 'courses.html'),
               ('Events', 'events.html'), ('Gallery', 'gallery.html'), ('Blog', 'blog.html'), ('FAQ&rsquo;s', 'faq.html'),
               ('Contact Us', 'contact.html')]
    legal = [('Privacy Policy', 'privacy-policy.html'), ('Terms &amp; Conditions', 'terms-and-conditions.html'),
             ('Refund Policy', 'refund-policy.html'), ('FAQ&rsquo;s', 'faq.html')]
    links = lambda items: ''.join('<li><a href="%s" class="hover:text-brand-glow transition-colors">%s</a></li>' % (h, l) for l, h in items)
    return '''    <footer class="site-footer theme-scope relative py-14 site-gutter border-t border-white/[0.06] bg-brand-abyss/80 backdrop-blur-xl overflow-hidden">
        <div class="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-brand-accent/45 to-transparent" aria-hidden="true"></div>
        <div class="absolute inset-0 pointer-events-none" aria-hidden="true" style="background: radial-gradient(70% 80% at 50% 120%, rgba(34,211,238,0.08), transparent 65%);"></div>

        <div class="relative max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 lg:gap-12 mb-10">
            <div class="sm:col-span-2 lg:col-span-1">
                <a href="index.html" class="inline-block mb-5" aria-label="Dive Adda — home">
                    <img src="assets/img/logo-full-light-2x.png" alt="Dive Adda — Discover the Deep" class="logo-light w-[168px] h-auto" width="168" height="138" loading="lazy">
                    <img src="assets/img/logo-full-2x.png" alt="Dive Adda — Discover the Deep" class="logo-dark w-[168px] h-auto" width="168" height="138" loading="lazy">
                </a>
                <p class="text-sm text-brand-dim/80 mb-5 leading-relaxed">An internationally certified dive centre, proudly affiliated with SSI. Try Scuba, SSI courses and water adventures in Visakhapatnam and Rajahmundry.</p>
                <div class="flex items-center gap-4 mb-5">
                    <img src="assets/img/ssi-dive-center-2x.png" alt="SSI Official Partner Dive Center" class="w-16 h-16 object-contain" loading="lazy" width="64" height="52">
                    <span class="text-[11px] uppercase tracking-[0.2em] text-brand-glow/80 font-bold leading-relaxed">SSI Certified<br>Dive Centre</span>
                </div>
                <div class="flex gap-3">
                    <a href="''' + IG + '''" target="_blank" rel="noopener" aria-label="Dive Adda on Instagram" class="w-9 h-9 rounded-xl flex items-center justify-center text-brand-dim bg-white/[0.04] border border-white/[0.08] hover:text-brand-violet hover:border-brand-violet/45 transition-colors duration-300">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                    </a>
                    <a href="''' + FB + '''" target="_blank" rel="noopener" aria-label="Dive Adda on Facebook" class="w-9 h-9 rounded-xl flex items-center justify-center text-brand-dim bg-white/[0.04] border border-white/[0.08] hover:text-brand-glow hover:border-brand-accent/45 transition-colors duration-300">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M22 12a10 10 0 10-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0022 12z"/></svg>
                    </a>
                </div>
            </div>

            <div>
                <h4 class="font-bold text-white mb-4 text-sm uppercase tracking-[0.16em]">Explore</h4>
                <ul class="space-y-2.5 text-sm text-brand-dim/80">''' + links(explore) + '''</ul>
            </div>

            <div>
                <h4 class="font-bold text-white mb-4 text-sm uppercase tracking-[0.16em]">Locations</h4>
                <ul class="space-y-2.5 text-sm text-brand-dim/80">''' + links([(d['name'], d['file']) for d in DESTS]) + '''</ul>
                <h4 class="font-bold text-white mb-3 mt-7 text-sm uppercase tracking-[0.16em]">Courses</h4>
                <ul class="space-y-2.5 text-sm text-brand-dim/80">''' + links([(c['name'], c['file']) for c in COURSES]) + '''</ul>
            </div>

            <div>
                <h4 class="font-bold text-white mb-4 text-sm uppercase tracking-[0.16em]">Contact</h4>
                <ul class="space-y-3 text-sm text-brand-dim/80">
                    <li><a href="tel:''' + PHONE_TEL + '''" class="inline-flex items-center gap-2 hover:text-brand-glow transition-colors">''' + svg('phone', 'w-4 h-4') + PHONE_TXT + '''</a></li>
                    <li><a href="''' + wa_link('Hi Dive Adda!') + '''" target="_blank" rel="noopener" class="inline-flex items-center gap-2 hover:text-brand-glow transition-colors">''' + svg('chat', 'w-4 h-4') + '''WhatsApp</a></li>
                    <li><a href="''' + IG + '''" target="_blank" rel="noopener" class="hover:text-brand-glow transition-colors">@diveaddaindia</a></li>
                    <li class="break-words">www.diveaddaindia.com</li>
                </ul>
                <button type="button" data-book class="btn-bio liquid ripple-host mt-6 px-6 py-3 rounded-full font-display font-bold text-sm w-full">Book your dive</button>
            </div>
        </div>

        <div class="relative max-w-7xl mx-auto pt-6 border-t border-white/[0.06] flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-brand-dim/60">
            <p>&copy; <span data-year>2026</span> Dive Adda &mdash; Discover the Deep. All rights reserved.</p>
            <nav class="footer-legal" aria-label="Legal">''' + ''.join('<a href="%s" class="hover:text-brand-glow transition-colors">%s</a>' % (h, l) for l, h in legal) + '''</nav>
        </div>
    </footer>
'''


CHATBOT = '''    <div id="chatbotWidget" class="glass-deep theme-scope fixed bottom-24 left-6 md:left-auto md:right-6 md:bottom-6 z-[100] hidden flex-col w-[350px] max-w-[calc(100vw-3rem)] rounded-2xl overflow-hidden transition-all duration-500 transform translate-y-4 opacity-0">
        <div class="relative p-4 flex justify-between items-center z-10 border-b border-white/[0.07]" style="background: linear-gradient(120deg, rgba(6,24,43,0.9), rgba(11,58,67,0.85));">
            <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-brand-accent/50 to-transparent" aria-hidden="true"></span>
            <div class="flex items-center gap-3">
                <div class="chat-avatar w-10 h-10 rounded-full flex items-center justify-center relative">
                    ''' + svg('chat', 'w-5 h-5 text-[#02131B]', '2.2') + '''
                    <span class="absolute bottom-0 right-0 w-3 h-3 bg-[#34D399] border-2 border-[#06182b] rounded-full shadow-[0_0_10px_#34D399]"></span>
                </div>
                <div>
                    <h3 class="font-bold text-sm tracking-wide text-white">Dive Adda Assistant</h3>
                    <p class="text-[10px] text-brand-glow/80 font-medium tracking-wide">Booking &middot; replies instantly</p>
                </div>
            </div>
            <button onclick="closeChat()" aria-label="Close chat" class="text-brand-dim hover:text-white transition-colors bg-white/[0.06] hover:bg-white/[0.14] border border-white/10 p-1.5 rounded-full">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div id="chatBody" class="p-4 h-[350px] overflow-y-auto flex flex-col gap-3 scroll-smooth"></div>
        <div id="chatInputArea" class="p-3 border-t border-white/[0.07] flex gap-2" style="background: rgba(4,18,31,0.75);">
            <input type="text" id="chatInput" class="chat-input flex-1 rounded-full px-4 py-2.5 text-sm transition-all" placeholder="Type your message..." aria-label="Your answer">
            <button id="chatSendBtn" aria-label="Send message" class="btn-bio ripple-host w-10 h-10 rounded-full flex items-center justify-center shrink-0 active:scale-95 transition-transform">
                <svg class="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
            </button>
        </div>
    </div>
'''

LIGHTBOX = '''    <div id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
        <div class="lb-backdrop"></div>
        <span class="lb-count" id="lbCount"></span>
        <button type="button" class="lb-btn lb-close" aria-label="Close photo viewer"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
        <button type="button" class="lb-btn lb-prev" aria-label="Previous photo"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg></button>
        <button type="button" class="lb-btn lb-next" aria-label="Next photo"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></button>
        <figure>
            <img id="lbImg" src="" alt="">
            <figcaption id="lbCap" class="font-display font-semibold"></figcaption>
        </figure>
    </div>
'''

PROFILE_MODAL = '''    <div id="profileModal" class="da-modal" role="dialog" aria-modal="true" aria-labelledby="pmName">
        <div class="modal-backdrop" data-modal-close></div>
        <div class="modal-card glass-deep theme-scope">
            <div class="modal-band"></div>
            <button type="button" class="pm-close absolute top-4 right-4 z-10 w-9 h-9 rounded-full grid place-items-center text-white bg-white/[0.14] border border-white/20 hover:bg-white/25 transition-colors" data-modal-close aria-label="Close profile">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
            <div class="p-7 md:p-9 -mt-14 relative">
                <div class="team-avatar" data-p="avatar"></div>
                <h2 id="pmName" data-p="name" class="font-display text-2xl font-bold text-white text-center"></h2>
                <p data-p="role" class="text-[11px] uppercase tracking-[0.2em] text-brand-glow mt-2 text-center"></p>
                <div class="divider-bio my-6"></div>
                <dl class="space-y-4 text-sm">
                    <div><dt class="field-label">Certification</dt><dd data-p="cert" class="text-brand-ink"></dd></div>
                    <div><dt class="field-label">Experience</dt><dd data-p="exp" class="text-brand-ink"></dd></div>
                    <div><dt class="field-label">Speciality</dt><dd data-p="spec" class="text-brand-ink"></dd></div>
                </dl>
                <p data-p="bio" class="text-brand-dim leading-relaxed mt-6"></p>
                <button type="button" data-book class="btn-bio liquid ripple-host w-full mt-7 px-6 py-3.5 rounded-full font-display font-bold">Book a dive with our team</button>
            </div>
        </div>
    </div>
'''

BOOK_MODAL = '''    <div id="bookNowModal" role="dialog" aria-modal="true" aria-labelledby="bookModalTitle" aria-describedby="bookModalCopy">
        <div class="modal-backdrop" data-modal-close></div>
        <div class="modal-card glass-deep theme-scope">
            <div class="modal-band">
                <span class="absolute left-6 bottom-4 chip-cyan px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.14em]">SSI Certified Dive Centre</span>
            </div>
            <button type="button" id="bookModalClose" data-modal-close aria-label="Close"
                    class="absolute top-4 right-4 z-10 w-9 h-9 rounded-full grid place-items-center text-white bg-white/[0.14] border border-white/20 hover:bg-white/25 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
            <div class="p-7 md:p-9">
                <h2 id="bookModalTitle" class="font-display text-2xl md:text-3xl font-bold text-white leading-tight mb-3">
                    Ready to <span class="text-gradient-bio">discover the deep?</span>
                </h2>
                <p id="bookModalCopy" class="text-brand-dim leading-relaxed mb-6">
                    Tell our assistant your destination, the experience you want and your dates &mdash; we will check availability with the dive desk and confirm on WhatsApp.
                </p>
                <ul class="space-y-2.5 mb-7 text-sm">
                    <li class="flex items-center gap-3 text-brand-ink"><span class="w-1.5 h-1.5 rounded-full bg-brand-accent shadow-[0_0_10px_#22D3EE]"></span>SSI certified instructors</li>
                    <li class="flex items-center gap-3 text-brand-ink"><span class="w-1.5 h-1.5 rounded-full bg-brand-accent shadow-[0_0_10px_#22D3EE]"></span>Beginners welcome &mdash; no experience needed</li>
                    <li class="flex items-center gap-3 text-brand-ink"><span class="w-1.5 h-1.5 rounded-full bg-brand-accent shadow-[0_0_10px_#22D3EE]"></span>Visakhapatnam and Rajahmundry</li>
                </ul>
                <div class="flex flex-col sm:flex-row gap-3">
                    <button type="button" id="bookModalGo" class="btn-bio liquid ripple-host flex-1 px-6 py-3.5 rounded-full font-display font-bold tracking-wide">Book your dive</button>
                    <button type="button" data-modal-close class="btn-ghost liquid ripple-host px-6 py-3.5 rounded-full font-semibold text-sm">Maybe later</button>
                </div>
            </div>
        </div>
    </div>
'''


# ---------------------------------------------------------------- structured data
def ld_org():
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": "Dive Adda",
        "alternateName": "Dive Adda India",
        "slogan": "Discover — The Deep",
        "url": DOMAIN,
        "description": "Dive Adda is an internationally certified scuba diving centre affiliated with SSI, running Try Scuba, SSI courses and water activities in Visakhapatnam and Rajahmundry.",
        "telephone": PHONE_TEL,
        "logo": {"@type": "ImageObject", "url": DOMAIN + "assets/img/logo-full.png"},
        "sameAs": [IG, FB],
    }


def ld_centre():
    offers = ['Try Scuba', 'SSI Courses'] + [html.unescape(a[1]) for d in DESTS for a in d['acts']]
    return {
        "@type": ["LocalBusiness", "SportsActivityLocation"],
        "@id": CENTRE_ID,
        "name": "Dive Adda — SSI Certified Scuba Centre",
        "url": DOMAIN,
        "description": "SSI certified scuba diving centre in Visakhapatnam offering Try Scuba, SSI courses, snorkeling and water activities, with water rides in Rajahmundry.",
        "telephone": PHONE_TEL,
        "address": {"@type": "PostalAddress", "addressLocality": "Visakhapatnam", "addressRegion": "Andhra Pradesh", "addressCountry": "IN"},
        "areaServed": [{"@type": "City", "name": n} for n in ("Visakhapatnam", "Rajahmundry")],
        "image": [DOMAIN + B('cover-divers'), DOMAIN + B('ssi-pool-training'), DOMAIN + B('guided-fun-dive')],
        "parentOrganization": {"@id": ORG_ID},
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for n in dict.fromkeys(offers)],
    }


def ld_breadcrumb(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + h}
        for i, (n, h) in enumerate(trail)]}


def ld_faq(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": html.unescape(q),
         "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a)}} for q, a in items]}


def ld_service(name, desc, path):
    return {"@type": "Service", "name": name, "description": desc, "serviceType": name,
            "provider": {"@id": ORG_ID}, "url": DOMAIN + path,
            "areaServed": [{"@type": "City", "name": n} for n in ("Visakhapatnam", "Rajahmundry")]}


def ld_course(c):
    return {"@type": "Course", "name": html.unescape(c['full']),
            "description": html.unescape(c['long']),
            "provider": {"@id": ORG_ID},
            "educationalCredentialAwarded": "SSI certification",
            "url": DOMAIN + c['file'],
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "onsite",
                                  "location": {"@id": CENTRE_ID}}}


# ---------------------------------------------------------------- shell
def shell(page, section, depth, title, desc, path, body, ld, hero_img=None,
          use_map=False, book_modal=False, lightbox=False, profile=False, span=40, noindex=False):
    depth = max(0, min(MAX_DEPTH, depth))
    graph = [ld_org(), ld_centre()] + ld
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    preload = ''
    if hero_img:
        ss = webp_srcset(hero_img)
        preload = ('    <link rel="preload" as="image" type="image/webp" fetchpriority="high" imagesrcset="%s" imagesizes="100vw">\n' % ss
                   if ss else '    <link rel="preload" as="image" fetchpriority="high" href="%s">\n' % src_of(hero_img))
    leaflet_css = '    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>\n' if use_map else ''
    leaflet_js = '    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>\n' if use_map else ''
    og_img = DOMAIN + B('cover-divers')

    return '''<!DOCTYPE html>
<html lang="en" class="scroll-smooth gate-open">
<head>
    <meta charset="UTF-8">

    <script>
        /* Applied before the first paint so the page never flashes the wrong
           theme: a saved choice wins, otherwise the device's preference. */
        (function () {
            var t = null;
            try { t = localStorage.getItem('db-theme'); } catch (e) {}
            if (t !== 'light' && t !== 'dark') {
                t = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
            }
            document.documentElement.setAttribute('data-theme', t);
        })();
    </script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark light">
    <title>''' + title + '''</title>

    <meta name="description" content="''' + E(desc) + '''">
    <meta name="robots" content="''' + ('noindex, follow' if noindex else 'index, follow, max-image-preview:large') + '''">
    <meta name="author" content="Dive Adda">
    <meta name="theme-color" content="#04121F" media="(prefers-color-scheme: dark)">
    <meta name="theme-color" content="#F3FAFC" media="(prefers-color-scheme: light)">
    <link rel="canonical" href="''' + DOMAIN + path + '''">
    <link rel="icon" href="assets/img/favicon-64.png" type="image/png" sizes="64x64">
    <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">

    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Dive Adda">
    <meta property="og:locale" content="en_IN">
    <meta property="og:url" content="''' + DOMAIN + path + '''">
    <meta property="og:title" content="''' + title + '''">
    <meta property="og:description" content="''' + E(desc) + '''">
    <meta property="og:image" content="''' + og_img + '''">
    <meta property="og:image:alt" content="Divers exploring a reef with Dive Adda">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="''' + title + '''">
    <meta name="twitter:description" content="''' + E(desc) + '''">
    <meta name="twitter:image" content="''' + og_img + '''">

    <!-- Structured data mirrors the page exactly: no invented prices, ratings,
         reviews, street address or dive sites. -->
    <script type="application/ld+json">
''' + jsonld + '''
    </script>

''' + preload + '''
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">

''' + leaflet_css + '''    <link rel="stylesheet" href="''' + asset('assets/css/dive-adda.css') + '''">
    <link rel="stylesheet" href="''' + asset('assets/css/dive-adda-pages.css') + '''">
    <link rel="stylesheet" href="''' + asset('assets/css/tailwind.css') + '''">
    <link rel="stylesheet" href="''' + asset('assets/css/dive-adda-responsive.css') + '''">

''' + FIREBASE + '''

''' + NOSCRIPT + '''
</head>
<body class="antialiased font-sans flex flex-col min-h-screen text-brand-dim selection:bg-brand-accent/30 selection:text-white overflow-x-hidden gate-open" data-page="''' + page + '''" data-section="''' + section + '''" data-depth="''' + str(depth) + '''" data-depth-span="''' + str(span) + '''">

''' + AMBIENT + '''

''' + GATE + '''

''' + float_widgets() + '''
''' + nav(page, section) + '''
<div id="siteRoot" class="relative z-[1] flex flex-col flex-grow">

''' + body + '''

''' + footer() + '''
</div><!-- /#siteRoot -->

''' + (BOOK_MODAL if book_modal else '') + (PROFILE_MODAL if profile else '') + (LIGHTBOX if lightbox else '') + CHATBOT + '''
''' + leaflet_js + '''    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
    <script src="''' + asset('assets/js/dive-adda.js') + '''"></script>
    <script src="''' + asset('assets/js/dive-adda-pages.js') + '''"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- components
def sec_head(num, eyebrow, title, desc='', link=None, center=False):
    l = ''
    if link:
        l = ('<div class="mt-6 md:mt-0"><a href="%s" class="link-glow font-semibold flex items-center gap-2 group">%s'
             '<svg class="w-4 h-4 group-hover:translate-x-1.5 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
             '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg></a></div>'
             % (link[1], link[0]))
    wrap = 'text-center max-w-3xl mx-auto' if center else 'md:flex justify-between items-end'
    return ('<div class="sec-head %s reveal"><div>'
            '<p class="eyebrow mb-4">%s &mdash; %s</p>'
            '<h2 class="font-display text-4xl md:text-5xl font-bold text-white mb-4 heading-glow">%s</h2>'
            '%s</div>%s</div>'
            % (wrap, num, eyebrow, title,
               '<p class="text-brand-dim max-w-2xl text-lg leading-relaxed%s">%s</p>' % (' mx-auto' if center else '', desc) if desc else '',
               l))


MAX_DEPTH = 40  # the site's depth scale: 0 m at the surface, 40 m at the deepest


def page_hero(eyebrow, title, desc, img, depth, crumbs, ghost=None, ctas='', extra='', compact=False):
    depth = max(0, min(MAX_DEPTH, depth))
    crumb = ' <span class="opacity-40">/</span> '.join(
        ['<a href="%s">%s</a>' % (h, n) if h else '<span class="text-white/80">%s</span>' % n for n, h in crumbs])
    return '''    <header class="page-hero''' + (' is-compact' if compact else '') + '''">
        ''' + photo(img, '', 'ph-img', '100vw', lazy=False) + '''
        <div class="ph-shade"></div>
        <div class="ph-glow"></div>
        ''' + ('<span class="city-ghost" aria-hidden="true">%s</span>' % ghost if ghost else '') + '''
        <div class="ph-inner reveal active">
            <nav class="crumbs mb-7" aria-label="Breadcrumb">''' + crumb + '''</nav>
            <div class="flex flex-wrap items-center gap-3 mb-5">
                <span class="chip-cyan rounded-full px-4 py-1.5 font-bold tracking-[0.22em] uppercase text-[10px]">''' + eyebrow + '''</span>
                <span class="chip depth-chip rounded-full px-3.5 py-1.5 text-[10px] font-bold tracking-[0.18em] uppercase">''' + str(depth) + ''' m</span>
            </div>
            <h1 class="ph-title font-display font-bold text-white heading-glow mb-6">''' + title + '''</h1>
            <p class="text-lg md:text-xl text-brand-ink/85 max-w-2xl leading-relaxed">''' + desc + '''</p>
            ''' + ctas + extra + '''
        </div>
    </header>
'''


def hero_ctas(primary='Book your dive', experience='', destination=''):
    return ('<div class="flex flex-col sm:flex-row gap-4 mt-9 w-full sm:w-auto">'
            '<button type="button" data-book data-experience="%s" data-destination="%s" class="btn-bio liquid liquid-strong ripple-host px-8 py-4 rounded-full font-display font-bold text-lg">%s</button>'
            '<a href="contact.html#enquire" class="btn-ghost liquid ripple-host px-8 py-4 rounded-full font-bold text-lg flex items-center justify-center gap-2.5">Send an enquiry %s</a>'
            '</div>' % (experience, destination, primary, svg('arrow', 'w-4 h-4 text-brand-glow')))


def story_section():
    return '''<section id="story" class="mb-32">
        ''' + sec_head('01', 'Our Story', 'Rooted in the world beneath the waves',
                       'At Dive Adda, we bring the depths of the ocean closer to you.') + '''
        <div class="grid lg:grid-cols-2 gap-10 items-center">
            <div class="reveal">
                <div class="frame-photo glass-panel p-2 h-[420px] md:h-[520px]">
                    ''' + photo(B('dive-centre-storefront'), 'The Dive Adda scuba dive centre at night', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw') + '''
                </div>
            </div>
            <div class="reveal delay-100">
                <p class="text-brand-dim text-lg leading-relaxed mb-5">Dive Adda was founded by a seasoned professional with <b class="text-brand-ink">15 years of service in the Indian Navy</b>, over a decade of experience in submarines, and 10 years in the oil &amp; gas industry.</p>
                <p class="text-brand-dim leading-relaxed mb-5">With years of hands-on experience in underwater marine operations, our passion for the ocean led us to create a scuba diving company that offers safe, exciting and unforgettable diving experiences. Whether you are a beginner eager to take your first breath underwater or an experienced diver looking to explore new depths, we ensure top-notch safety, expert guidance, and an adventure like no other.</p>
                <div class="glass-panel rounded-2xl p-5 flex items-center gap-5 mb-7">
                    <img src="assets/img/ssi-dive-center-2x.png" alt="SSI Official Partner Dive Center" class="ssi-badge w-20 h-20 object-contain" loading="lazy" width="80" height="65">
                    <div>
                        <h4 class="font-display font-bold text-white text-lg">Internationally certified</h4>
                        <p class="text-sm text-brand-dim leading-relaxed">We are proudly affiliated with SSI, ensuring our training programmes meet the highest global standards.</p>
                    </div>
                </div>
                <div class="grid sm:grid-cols-3 gap-4 mb-8">
                    ''' + ''.join(
        '<div class="stat-tile rounded-2xl p-5"><p class="fact-num text-gradient-bio">%s</p><p class="text-xs text-brand-dim mt-2 leading-relaxed">%s</p></div>' % (n, l)
        for n, l in [('15', 'years of service in the Indian Navy'), ('10+', 'years of experience in submarines'), ('15+', 'years of industry experience as a team')]) + '''
                </div>
            </div>
        </div>
    </section>'''


def scuba_cards_section(num='04'):
    cards = ''.join(
        '<button type="button" class="info-card glass-panel bio-edge text-left reveal %s" aria-expanded="%s">'
        '<span class="ic-num" aria-hidden="true">%s</span>'
        '<span class="ic-icon mb-5">%s</span>'
        '<h3 class="font-display text-xl font-bold text-white mb-2">%s</h3>'
        '<p class="text-brand-dim text-sm leading-relaxed">%s</p>'
        '<span class="ic-more"><div><div class="text-brand-dim text-sm leading-relaxed pt-4 border-t border-white/[0.08]">%s</div></div></span>'
        '<span class="mt-5 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.2em] text-brand-glow">'
        '<span class="ic-toggle">%s</span> Read more</span>'
        '</button>'
        % (['', 'delay-100', 'delay-200', 'delay-300'][i], 'true' if i == 0 else 'false',
           n, svg(ic, 'w-6 h-6'), t, teaser, more, svg('plus', 'w-3.5 h-3.5'))
        for i, (n, ic, t, teaser, more) in enumerate(SCUBA_CARDS))
    return ('<section id="what-is-scuba" class="mb-32">'
            + sec_head(num, 'What is Scuba?', 'Breathe underwater, properly explained',
                       'Tap any card to go deeper.', center=True)
            + '<div class="grid sm:grid-cols-2 gap-6">' + cards + '</div></section>')


def course_card(c, i):
    return ('<article class="course-card bento-card bio-edge glow-hover liquid reveal %s group">'
            '<div class="cc-media on-media">%s'
            '<span class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/35 to-transparent"></span>'
            '<span class="cc-step font-display" aria-hidden="true">%s</span>'
            '<span class="cc-level chip-cyan px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.14em]">%s</span>'
            '</div>'
            '<div class="p-6 flex flex-col flex-grow">'
            '<h3 class="font-display text-xl font-bold text-white mb-2">%s</h3>'
            '<p class="text-brand-dim text-sm leading-relaxed flex-grow">%s</p>'
            '<a href="%s" class="mt-5 btn-ghost liquid ripple-host px-5 py-2.5 rounded-full text-sm font-semibold inline-flex items-center justify-center gap-2">View course %s</a>'
            '</div></article>'
            % (['', 'delay-100', 'delay-200'][i % 3],
               photo(course_photo(c['id'], c['img']), c['full'], 'bento-image', '(max-width: 767px) 100vw, 33vw'),
               c['step'], c['level'], c['name'], c['short'], c['file'],
               svg('arrow', 'w-3.5 h-3.5 text-brand-glow')))


def courses_section(num='02', exclude=None, title='Certified, beginner to professional',
                    desc='SSI certified courses from beginners to professional level, taught by our instructor team.',
                    link=('All courses', 'courses.html'), overview=False):
    items = [c for c in COURSES if c is not exclude]
    tail = ''
    if overview:
        tail = ('<div class="courses-cta reveal">'
                '<div class="flex items-center gap-4">'
                '<img src="assets/img/ssi-dive-center-2x.png" alt="SSI Official Partner Dive Center" class="w-16 object-contain" width="64" height="52" loading="lazy">'
                '<p class="text-sm text-brand-dim leading-relaxed max-w-sm">An SSI certified dive centre: the certification you earn with us is recognised worldwide.</p></div>'
                '<a href="courses.html" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold inline-flex items-center justify-center gap-2.5">Explore All SSI Courses %s</a>'
                '</div>' % svg('arrow', 'w-4 h-4'))
    return ('<section id="courses" class="mb-32">'
            + sec_head(num, 'SSI Courses', title, desc, link)
            + '<div class="course-grid grid sm:grid-cols-2 xl:grid-cols-3 gap-5 lg:gap-6 orphan-sm-xl">'
            + ''.join(course_card(c, i) for i, c in enumerate(items)) + '</div>' + tail + '</section>')


def events_section(num='07'):
    cards = ''.join(
        '<a href="events.html#%s" class="group relative rounded-3xl overflow-hidden bento-card on-media liquid glow-hover bio-edge isolate reveal %s block %s">'
        '%s'
        '<div class="absolute inset-0 duotone"></div>'
        '<div class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/55 to-transparent"></div>'
        '<div class="absolute inset-0 p-6 flex flex-col justify-end z-[4] transform transition-transform duration-700 group-hover:translate-y-[-8px]">'
        '<span class="ic-icon mb-4 w-11 h-11">%s</span>'
        '<h3 class="font-display text-xl md:text-2xl font-bold text-white mb-2">%s</h3>'
        '<p class="text-brand-ink/75 text-sm">%s</p></div></a>'
        % (e['id'], ['', 'delay-100', 'delay-200', 'delay-300'][i], 'lg:col-span-2' if i in (0, len(EVENTS) - 1) else '',
           photo(e['img'], e['name'], 'absolute inset-0 w-full h-full object-cover bento-image', '(max-width: 767px) 100vw, 50vw'),
           svg(e['icon'], 'w-5 h-5'), e['name'], e['text'])
        for i, e in enumerate(EVENTS))
    return ('<section id="underwater-events" class="mb-32">'
            + sec_head(num, 'Underwater Events', 'Celebrate below the surface',
                       'The moments people remember, moved underwater and planned with our team.',
                       ('All underwater events', 'events.html'))
            + '<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6 auto-rows-[260px]">' + cards + '</div></section>')


def fact_tiles(items):
    return ('<div class="grid grid-cols-2 gap-3">' + ''.join(
        '<div class="stat-tile rounded-2xl p-4"><p class="font-display font-bold text-white text-lg leading-tight">%s</p>'
        '<p class="text-xs text-brand-dim mt-1 leading-relaxed">%s</p></div>' % (v, l) for v, l in items) + '</div>')


def pill_list(items, cols='sm:grid-cols-2'):
    return ('<ul class="grid %s gap-3">' % cols + ''.join(
        '<li class="benefit-pill glass-panel"><span class="bp-dot"></span><span class="text-brand-ink text-sm">%s</span></li>' % x
        for x in items) + '</ul>')


def itinerary_timeline():
    steps = ''.join(
        '<div class="j-step"><span class="j-node">%02d</span>'
        '<div class="j-card glass-panel"><p class="text-[11px] font-bold uppercase tracking-[0.18em] text-brand-glow mb-1.5">%s</p>'
        '<h3 class="font-display font-bold text-white text-lg mb-1.5">%s</h3>'
        '<p class="text-sm text-brand-dim leading-relaxed">%s</p></div></div>' % (i + 1, t, h, d)
        for i, (t, h, d) in enumerate(TRY_STEPS))
    return '<div class="journey journey-vertical reveal"><span class="journey-line" aria-hidden="true"><span></span></span>' + steps + '</div>'


def location_card(d, i):
    chips = ''.join('<a href="%s#%s" class="chip loc-chip px-3 py-1.5 rounded-full text-xs font-semibold">%s</a>'
                    % (d['file'], a[0], a[1]) for a in d['acts'])
    return ('<article class="loc-card glass-panel rounded-3xl overflow-hidden flex flex-col reveal %s">'
            '<div class="relative h-[220px] md:h-[260px] overflow-hidden on-media">%s'
            '<span class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/40 to-transparent"></span>'
            '<div class="absolute left-5 right-5 bottom-4"><span class="chip-cyan px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.16em]">%s</span>'
            '<h3 class="font-display font-bold text-white text-3xl md:text-4xl mt-3">%s</h3></div></div>'
            '<div class="p-6 md:p-7 flex flex-col gap-5 flex-grow">'
            '<p class="text-brand-dim leading-relaxed">%s</p>'
            '<div><p class="field-label mb-2">Activities</p><div class="flex flex-wrap gap-2">%s</div></div>'
            '<div class="flex flex-wrap gap-3 mt-auto">'
            '<a href="%s" class="btn-bio liquid ripple-host px-6 py-3 rounded-full font-bold text-sm">Explore %s</a>'
            '<button type="button" data-book data-destination="%s" class="btn-ghost liquid ripple-host px-6 py-3 rounded-full font-semibold text-sm">Book here</button>'
            '</div></div></article>'
            % ('' if i == 0 else 'delay-100',
               photo(d['img'], d['name'], 'bento-image absolute inset-0 w-full h-full object-cover', '(max-width: 767px) 100vw, 50vw'),
               d['sub'], d['name'], d['blurb'], chips, d['file'], d['name'], d['name']))


def about_home_section(num='01'):
    return ('<section id="about" class="mb-32">'
            + sec_head(num, 'About Us', 'About Dive Adda',
                       'An internationally certified dive centre, proudly affiliated with SSI, born out of a life spent working under water.',
                       ('Our full story', 'about.html'))
            + '<div class="grid lg:grid-cols-2 gap-10 items-center">'
            + '<div class="reveal"><div class="frame-photo glass-panel p-2 h-[300px] lg:h-[440px]">'
            + photo(B('dive-centre-storefront'), 'The Dive Adda scuba dive centre', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw')
            + '</div></div>'
            + '<div class="reveal delay-100">'
            + '<p class="text-brand-dim text-lg leading-relaxed mb-5">Dive Adda was founded by a professional with <b class="text-brand-ink">15 years of service in the Indian Navy</b>, over a decade in submarines and 10 years in the oil &amp; gas industry. That experience under water is what the centre is built on.</p>'
            + '<p class="text-brand-dim leading-relaxed mb-7">Today our SSI certified instructors take complete beginners on their first breath underwater, train divers up to professional level, and run snorkeling and water activities in Visakhapatnam and Rajahmundry.</p>'
            + '<div class="grid sm:grid-cols-3 gap-4 mb-8">'
            + ''.join('<div class="stat-tile rounded-2xl p-5"><p class="fact-num text-gradient-bio">%s</p><p class="text-xs text-brand-dim mt-2 leading-relaxed">%s</p></div>' % (n, l)
                      for n, l in [('15', 'years in the Indian Navy'), ('10+', 'years in submarines'), ('15+', 'years of team experience')])
            + '</div>'
            + '<div class="flex flex-wrap gap-3">'
            + '<a href="about.html" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold text-sm">About Dive Adda</a>'
            + '<a href="courses.html" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold text-sm">See the courses</a>'
            + '</div></div></div></section>')


def xp_head(num, eyebrow, title, city, place, tone=''):
    """Section heading with the city set beneath it, inside the same h2."""
    return ('<div class="xp-head reveal %s">'
            '<p class="eyebrow mb-4">%s &mdash; %s</p>'
            '<h2 class="xp-title font-display font-bold text-white heading-glow">'
            '<span class="block">%s</span>'
            '<span class="xp-city">%s<span class="xp-place">%s %s</span></span></h2>'
            '</div>' % (tone, num, eyebrow, title, city, svg('pin', 'w-4 h-4'), place))


def scuba_vizag_section(num='03'):
    highlights = [('clock', '&asymp; 40 min', 'underwater per person'),
                  ('wave', '6&ndash;8 m', 'maximum depth for first-timers'),
                  ('people', 'Age 8+', 'no experience needed'),
                  ('camera', 'Photos &amp; video', 'of your dive, included')]
    tiles = ''.join(
        '<li class="xp-stat"><span class="xp-stat-ic">%s</span><span><b>%s</b><span>%s</span></span></li>'
        % (svg(ic, 'w-5 h-5'), v, l) for ic, v, l in highlights)
    return ('<section id="scuba-diving" class="xp xp-sea mb-32" aria-labelledby="scuba-diving-title">'
            + xp_head(num, 'Scuba Diving', 'Scuba Diving', 'Vizag', 'Visakhapatnam, Andhra Pradesh').replace('<h2 ', '<h2 id="scuba-diving-title" ', 1)
            + '<div class="xp-grid">'
            + '<div class="xp-media reveal">'
            + '<figure class="xp-feature on-media">'
            + photo(B('cover-divers'), 'Divers exploring the reef with a Dive Adda instructor', 'xp-img', '(max-width: 1023px) 100vw, 58vw')
            + '<figcaption class="xp-badge">SSI certified dive centre &middot; Vizag</figcaption></figure>'
            + '<div class="xp-thumbs">'
            + '<figure class="xp-thumb on-media">' + photo(B('ssi-pool-training'), 'A beginner practising skills with an SSI instructor', 'xp-img', '(max-width: 1023px) 50vw, 29vw') + '</figure>'
            + '<figure class="xp-thumb on-media">' + photo(B('boat-diving'), 'A diver rolling back off the boat into the sea', 'xp-img', '(max-width: 1023px) 50vw, 29vw') + '</figure>'
            + '</div></div>'
            + '<div class="xp-copy reveal delay-100">'
            + '<p class="xp-lead">Breathe underwater for the first time off the coast of Vizag.</p>'
            + '<p class="text-brand-dim leading-relaxed mb-4">Your morning starts with a classroom briefing at our SSI certified centre: how your equipment works, the signals you will use and the plan for your dive. Then it is a short 10&ndash;15 minute boat ride out to the dive site, where an experienced instructor takes you down and stays beside you the whole way.</p>'
            + '<p class="text-brand-dim leading-relaxed mb-7">No experience is needed to start. Already certified? Guided dives and SSI courses take you further.</p>'
            + '<ul class="xp-stats">' + tiles + '</ul>'
            + '<div class="flex flex-col sm:flex-row gap-3 mt-8">'
            + '<button type="button" data-book data-experience="Try Scuba (first dive)" data-destination="Visakhapatnam" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Book your dive</button>'
            + '<a href="beginner-level-scuba.html" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold text-center">Explore scuba diving</a>'
            + '</div></div></div></section>')


def water_sports_section(num='04'):
    d = next(x for x in DESTS if x['id'] == 'rajahmundry')
    tiles = ''.join(
        '<li><a class="ws-tile on-media group" href="%s#%s">%s'
        '<span class="ws-shade"></span><span class="ws-name">%s</span></a></li>'
        % (d['file'], aid, photo(activity_photo(aid), name, 'xp-img', '(max-width: 639px) 50vw, (max-width: 1023px) 33vw, 16vw'), name)
        for aid, name, icon, desc, link in d['acts'] if activity_photo(aid))
    return ('<section id="water-sports" class="xp xp-river mb-32" aria-labelledby="water-sports-title">'
            + xp_head(num, 'Water Sports', 'Water Sports', 'Rajahmundry', 'On the Godavari, Andhra Pradesh', 'xp-head-river').replace('<h2 ', '<h2 id="water-sports-title" ', 1)
            + '<div class="xp-grid xp-grid-flip">'
            + '<div class="xp-media reveal">'
            + '<figure class="xp-feature on-media">'
            + photo('assets/img/activities/godavari-bridge.jpg', 'The Godavari arch bridge across the river at Rajahmundry', 'xp-img', '(max-width: 1023px) 100vw, 58vw')
            + '<figcaption class="xp-badge xp-badge-river">The Godavari &middot; Rajahmundry</figcaption></figure></div>'
            + '<div class="xp-copy reveal delay-100">'
            + '<p class="xp-lead">Swap the sea for the Godavari.</p>'
            + '<p class="text-brand-dim leading-relaxed mb-4">At Rajahmundry the Godavari runs wide beneath its landmark bridges, and it is where the Dive Adda team runs an afternoon&rsquo;s worth of river adventure: speed boat rides, jet skis and kayaks for anyone who wants the thrill of the water without going under it.</p>'
            + '<p class="text-brand-dim leading-relaxed mb-7">Bringing friends or family? The dragon, disco and bumper rides are towed rides made for groups and plenty of laughs. Every ride is run by our team, and timings are confirmed when you book.</p>'
            + '<div class="flex flex-col sm:flex-row gap-3">'
            + '<button type="button" data-book data-destination="Rajahmundry" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Book water sports</button>'
            + '<a href="rajahmundry.html" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold text-center">Explore water sports</a>'
            + '</div></div></div>'
            + '<ul class="ws-grid reveal" aria-label="Water sports in Rajahmundry">' + tiles + '</ul>'
            + '</section>')


GOOGLE_G = ('<svg class="rv-logo-g" viewBox="0 0 48 48" aria-hidden="true">'
            '<path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.6-.4-3.9z"/>'
            '<path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>'
            '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/>'
            '<path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C36.9 39.2 44 34 44 24c0-1.3-.1-2.6-.4-3.9z"/></svg>')
TA_OWL = ('<svg class="rv-logo-ta" viewBox="0 0 48 48" aria-hidden="true">'
          '<circle cx="24" cy="24" r="22" fill="#34E0A1"/>'
          '<circle cx="15.5" cy="25" r="6.5" fill="#fff"/><circle cx="32.5" cy="25" r="6.5" fill="#fff"/>'
          '<circle cx="15.5" cy="25" r="3" fill="#000"/><circle cx="32.5" cy="25" r="3" fill="#000"/>'
          '<path d="M24 31l-3-4h6z" fill="#000"/><path d="M9 17c4-3 9-4.5 15-4.5S35 14 39 17" stroke="#000" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg>')


def rating_marks(source, n):
    if source == 'google':
        mark = ('<svg class="rv-star" viewBox="0 0 20 20" aria-hidden="true"><path fill="currentColor" '
                'd="M10 1.6l2.47 5.2 5.53.77-4 4.02.95 5.81L10 14.7l-4.95 2.7.95-5.81-4-4.02 5.53-.77z"/></svg>')
    else:
        mark = '<span class="rv-bubble" aria-hidden="true"></span>'
    return '<span class="rv-marks rv-marks-%s" role="img" aria-label="Rated %d out of 5">%s</span>' % (source, n, mark * n)


def avatar_hue(name):
    return sum(ord(c) for c in name) * 47 % 360


def review_card(src, r, i):
    more = ('<a class="rv-more" href="%s" target="_blank" rel="noopener">Read more<span class="sr-only"> of %s&rsquo;s review on %s</span></a>'
            % (src['url'], E(r['name']), src['name'])) if r.get('more') and src.get('url') else ''
    title = ('<h3 class="rv-title">%s</h3>' % r['title']) if r.get('title') else ''
    return ('<article class="rv-card" aria-label="%s review by %s" data-index="%d">'
            '<header class="rv-card-head">'
            '<span class="rv-avatar" style="--av:%d" aria-hidden="true">%s</span>'
            '<span class="min-w-0"><span class="rv-name">%s</span><span class="rv-when">%s</span></span>'
            '<span class="rv-src" title="%s review">%s</span></header>'
            '%s%s<p class="rv-text">%s</p>%s</article>'
            % (src['name'], E(r['name']), i, avatar_hue(r['name']), E(r['name'][:1].upper()),
               E(r['name']), r.get('when', ''), src['name'], GOOGLE_G if src['id'] == 'google' else TA_OWL,
               rating_marks(src['id'], r.get('rating', 5)), title, r['text'], more))


def review_row(src):
    logo = ('<span class="rv-wordmark rv-wordmark-g" aria-label="Google">'
            '<b style="color:#4285F4">G</b><b style="color:#EA4335">o</b><b style="color:#FBBC05">o</b>'
            '<b style="color:#4285F4">g</b><b style="color:#34A853">l</b><b style="color:#EA4335">e</b></span>'
            if src['id'] == 'google' else
            '<span class="rv-wordmark rv-wordmark-ta">%s<span>Tripadvisor</span></span>' % TA_OWL)
    count = ('<p class="rv-count">Based on <b>%d reviews</b></p>' % src['count']) if src.get('count') else ''
    summary = ('<aside class="rv-summary" aria-label="%s rating summary">'
               '<p class="rv-label">%s</p>%s%s'
               '<a class="rv-brand" href="%s" target="_blank" rel="noopener" aria-label="See all reviews on %s">%s</a>'
               '</aside>' % (src['name'], src['label'], rating_marks(src['id'], src['rating']), count,
                              src['url'], src['name'], logo))
    tid = 'rv-track-%s' % src['id']
    cards = ''.join(review_card(src, r, i) for i, r in enumerate(src['reviews']))
    carousel = ('<div class="rv-carousel" data-rv role="region" aria-roledescription="carousel" aria-label="%s reviews">'
                '<button type="button" class="rv-nav rv-prev" data-rv-prev aria-controls="%s" aria-label="Previous %s review">'
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg></button>'
                '<div class="rv-track" id="%s" tabindex="0" aria-label="%s reviews, use arrow keys to scroll">%s</div>'
                '<button type="button" class="rv-nav rv-next" data-rv-next aria-controls="%s" aria-label="Next %s review">'
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg></button>'
                '</div>' % (src['name'], tid, src['name'], tid, src['name'], cards, tid, src['name']))
    return '<div class="rv-row reveal">' + summary + carousel + '</div>'


def testimonials_section(num='05'):
    head = sec_head(num, 'Testimonials', 'What our guests say',
                    'Here&rsquo;s what guests say about their dives on Google and Tripadvisor.', center=True)
    demo = any(src.get('demo') for src in REVIEW_SOURCES)
    note = ('<p class="rv-demo-note" role="note">Sample reviews shown from the design reference &mdash; '
            'replace them with Dive Adda&rsquo;s verified reviews before launch.</p>') if demo else ''
    rows = ''.join(review_row(src) for src in REVIEW_SOURCES if src['reviews'])
    return '<section id="testimonials" class="mb-32">' + head + note + '<div class="rv-rows">' + rows + '</div></section>'


def book_section(num='06'):
    return ('<section id="book" class="mb-16"><div class="cta-band glass-deep bio-edge reveal">'
            '<div class="relative grid lg:grid-cols-[1.4fr_1fr] gap-8 items-center">'
            '<div><p class="eyebrow mb-4">%s &mdash; Book</p>'
            '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-3 heading-glow">Ready to discover the deep?</h2>'
            '<p class="text-brand-dim text-lg leading-relaxed max-w-xl mb-6">Tell us the experience, location and date. The Dive Adda team confirms availability and gets you ready.</p>'
            '<div class="flex items-center gap-3 text-sm text-brand-dim"><img src="assets/img/ssi-dive-center-2x.png" alt="SSI Official Partner Dive Center" class="w-12 h-12 object-contain" width="48" height="39" loading="lazy">'
            '<span>SSI certified dive centre &middot; Visakhapatnam</span></div></div>'
            '<div class="flex flex-col gap-3">'
            '<button type="button" data-book class="btn-bio liquid liquid-strong ripple-host px-7 py-4 rounded-full font-display font-bold">Book your dive</button>'
            '<a href="%s" target="_blank" rel="noopener" class="liquid ripple-host px-7 py-4 rounded-full font-semibold text-center text-white bg-[#128C4A]/90 border border-[#4ade80]/35">Chat on WhatsApp</a>'
            '<a href="tel:%s" class="btn-ghost liquid ripple-host px-7 py-4 rounded-full font-semibold text-center">Call %s</a>'
            '<a href="blog.html" class="btn-ghost liquid ripple-host px-7 py-4 rounded-full font-semibold text-center inline-flex items-center justify-center gap-2">%s Blog</a>'
            '</div></div></div></section>' % (num, wa_link("Hi Dive Adda! I'd like to book."), PHONE_TEL, PHONE_TXT, svg('chat', 'w-4 h-4 text-brand-glow')))


def gallery_grid(gid, items, filters=True):
    bar = ''
    if filters:
        # Only offer a filter that actually has photos behind it, so no chip
        # can ever empty the grid.
        present = {c for _, cat, _, _, _ in items for c in cat.split(' ')}
        shown = [(f, l) for f, l in GALLERY_FILTERS if f == 'all' or f in present]
        bar = ('<div class="filter-bar mb-8 reveal" data-filter-for="%s" role="group" aria-label="Filter photos">%s</div>'
               % (gid, ''.join('<button type="button" class="filter-btn" data-filter="%s" aria-pressed="%s">%s</button>'
                               % (f, 'true' if f == 'all' else 'false', l) for f, l in shown)))
    tiles = ''.join(
        '<figure class="gallery-tile on-media %s reveal %s" data-cat="%s" data-caption="%s">'
        '%s<span class="tile-scrim"></span>'
        '<figcaption class="gallery-cap"><p class="font-display font-bold text-white text-sm leading-tight">%s</p>'
        '<p class="text-[11px] text-brand-dim mt-0.5">%s</p></figcaption>'
        '<button type="button" class="g-open" aria-label="Open photo: %s"></button>'
        '</figure>'
        % (span, ['', 'delay-100', 'delay-200', 'delay-300'][i % 4], cat, E(cap),
           photo(img, cap, '', '(max-width: 767px) 50vw, 25vw', extra='data-full="%s"' % full_src(img)),
           cap, sub, E(cap))
        for i, (img, cat, cap, sub, span) in enumerate(items))
    return bar + '<div class="gallery-grid" id="%s" data-gallery>%s</div>' % (gid, tiles)


def gallery_section(num='10'):
    return ('<section id="gallery" class="mb-32">'
            + sec_head(num, 'Gallery', 'Our gallery',
                       'Training sessions, fun dives, snorkelling and underwater events &mdash; photographed with our own divers.',
                       ('Open full gallery', 'gallery.html'))
            + gallery_grid('galleryHome', GALLERY[:9]) + '</section>')


def team_section(num='11'):
    cards = ''.join(
        '<article class="team-card glass-panel reveal %s cursor-pointer" tabindex="0" role="button" data-profile '
        'data-name="%s" data-role="%s" data-cert="%s" data-exp="%s" data-spec="%s" data-bio="%s">'
        '<div class="team-avatar"><span class="team-mono">%s</span></div>'
        '<h3 class="font-display text-lg font-bold text-white">%s</h3>'
        '<p class="text-[11px] uppercase tracking-[0.2em] text-brand-glow mt-1.5">%s</p>'
        '<span class="chip-cyan inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.12em] mt-4">%s</span>'
        '<p class="text-sm text-brand-dim leading-relaxed mt-4">%s</p>'
        '<span class="mt-5 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.2em] text-brand-glow">View profile</span>'
        '</article>'
        % (['', 'delay-100'][i % 2], E(html.unescape(t['name'])), E(html.unescape(t['role'])),
           E(html.unescape(t['cert'])), E(html.unescape(t['exp'])), E(html.unescape(t['spec'])),
           E(html.unescape(t['bio'])), t['mono'], t['name'], t['role'], t['spec'], t['bio'])
        for i, t in enumerate(TEAM))
    return ('<section id="team" class="mb-32">'
            + sec_head(num, 'Team', 'Meet the Dive Adda team',
                       'Our team of expert instructors provides professional dive training for all levels.', center=True)
            + '<div class="grid sm:grid-cols-2 gap-6 max-w-4xl mx-auto">' + cards + '</div>'
            + '<!-- Add a team member: copy one <article data-profile> and fill in the real name, role, '
              'certification, experience and speciality. Drop a headshot in with '
              '<img class="team-photo" src="assets/img/team/name.jpg" alt="Name"> inside .team-avatar. -->'
            + '</section>')


def conservation_section(num='12'):
    words = [('Dive', 'Learn to dive responsibly with instructors who treat the ocean as the point, not the backdrop.', 'bolt'),
             ('Discover', 'Divers witness firsthand the effects of pollution and climate change on the marine world.', 'eye'),
             ('Protect', 'Join conservation efforts &mdash; cleaning up plastic waste, protecting coral reefs and educating others about ocean health.', 'globe')]
    cards = ''.join(
        '<div class="ddp-card glass-panel bio-edge reveal %s"><span class="ddp-ring" aria-hidden="true"></span>'
        '<span class="ic-icon mb-6">%s</span>'
        '<h3 class="ddp-word text-gradient-bio mb-3">%s</h3>'
        '<p class="text-brand-dim leading-relaxed">%s</p></div>'
        % (['', 'delay-100', 'delay-200'][i], svg(ic, 'w-6 h-6'), w, d)
        for i, (w, d, ic) in enumerate(words))
    return ('<section id="conservation" class="mb-32">'
            + sec_head(num, 'Ocean Conservation', 'Dive. Discover. Protect.',
                       'The more people who learn to dive responsibly, the more awareness we create about keeping our oceans clean and safe for future generations.', center=True)
            + '<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6 orphan-sm-lg">' + cards + '</div>'
            + '<div class="text-center mt-10 reveal"><a href="events.html#conservation-diving" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold inline-flex items-center gap-2.5">Join a conservation dive %s</a></div>'
            % svg('arrow', 'w-4 h-4 text-brand-glow')
            + '</section>')


def faq_block(num, eyebrow, title, desc, items, sid='faq', footer=True):
    acc = ''.join(
        '<details class="faq-item glass-panel reveal"%s><summary>%s<span class="fq-icon">%s</span></summary>'
        '<div class="fq-body">%s</div></details>' % (' open' if i == 0 else '', q, svg('plus', 'w-4 h-4'), a)
        for i, (q, a) in enumerate(items))
    tail = ('<p class="text-center text-brand-dim mt-10 reveal">Still unsure? <a href="contact.html#enquire" class="link-glow font-semibold">Send us your question</a> or call <a href="tel:%s" class="link-glow font-semibold">%s</a>.</p>'
            % (PHONE_TEL, PHONE_TXT)) if footer else ''
    return ('<section id="%s" class="mb-28">' % sid + sec_head(num, eyebrow, title, desc, center=True)
            + '<div class="max-w-3xl mx-auto grid gap-4" data-faq-group>' + acc + '</div>' + tail + '</section>')


def enquiry_section(num='14'):
    dest_opts = ''.join('<option value="%s">%s</option>' % (d['name'], d['name']) for d in DESTS)
    exp_opts = ''.join('<option value="%s">%s</option>' % (html.unescape(n), n) for n in EXPERIENCE_OPTIONS)
    course_opts = ''.join('<option value="%s">%s</option>' % (html.unescape(c['name']), c['name']) for c in COURSES)
    return '''<section id="enquire" class="mb-10 pt-6">
        <div class="grid lg:grid-cols-5 gap-10 items-start">
            <div class="lg:col-span-2 reveal">
                <p class="eyebrow mb-4">''' + num + ''' &mdash; Contact</p>
                <h2 class="font-display text-4xl font-bold text-white mb-5 heading-glow">Ask us anything</h2>
                <p class="text-brand-dim text-lg leading-relaxed mb-8">Not sure which course fits, travelling with non-divers, or chasing a specific date? Send it over and our team will get back to you.</p>
                <ul class="space-y-3">
                    <li><a href="tel:''' + PHONE_TEL + '''" class="glass-panel liquid rounded-2xl p-4 flex items-center gap-4">
                        <span class="shrink-0 p-2.5 rounded-xl bg-brand-accent/12 border border-brand-accent/30 text-brand-glow">''' + svg('phone') + '''</span>
                        <span><span class="block text-white font-bold text-sm">Call the dive desk</span><span class="block text-xs text-brand-dim">''' + PHONE_TXT + '''</span></span></a></li>
                    <li><a href="''' + wa_link('Hi Dive Adda! I have an enquiry.') + '''" target="_blank" rel="noopener" class="glass-panel liquid rounded-2xl p-4 flex items-center gap-4">
                        <span class="shrink-0 p-2.5 rounded-xl bg-[#25D366]/12 border border-[#4ade80]/30 text-[#4ade80]">''' + svg('chat') + '''</span>
                        <span><span class="block text-white font-bold text-sm">Chat on WhatsApp</span><span class="block text-xs text-brand-dim">Fastest way to reach the team</span></span></a></li>
                    <li><a href="''' + IG + '''" target="_blank" rel="noopener" class="glass-panel liquid rounded-2xl p-4 flex items-center gap-4">
                        <span class="shrink-0 p-2.5 rounded-xl bg-brand-violet/12 border border-brand-violet/30 text-brand-violet">''' + svg('camera') + '''</span>
                        <span><span class="block text-white font-bold text-sm">@diveaddaindia</span><span class="block text-xs text-brand-dim">See what we have been diving lately</span></span></a></li>
                </ul>
            </div>

            <div class="lg:col-span-3 glass-panel rounded-3xl p-7 md:p-9 reveal delay-100">
                <form id="inquiryForm" novalidate>
                    <div class="grid sm:grid-cols-2 gap-5">
                        <div class="field">
                            <label class="field-label" for="inqName">Name</label>
                            <input class="field-input" id="inqName" name="name" type="text" autocomplete="name" placeholder="Your name" required>
                            <p class="field-error">Please tell us your name.</p>
                        </div>
                        <div class="field">
                            <label class="field-label" for="inqPhone">Phone</label>
                            <input class="field-input" id="inqPhone" name="phone" type="tel" autocomplete="tel" placeholder="''' + PHONE_TXT + '''" required aria-required="true">
                            <p class="field-error">Please add a number we can reach you on.</p>
                        </div>
                        <div class="field">
                            <label class="field-label" for="inqEmail">Email <span class="normal-case tracking-normal opacity-60">(optional)</span></label>
                            <input class="field-input" id="inqEmail" name="email" type="email" autocomplete="email" placeholder="you@example.com">
                            <p class="field-error">That email does not look right.</p>
                        </div>
                        <div class="field">
                            <label class="field-label" for="inqDestination">Destination</label>
                            <select class="field-input" id="inqDestination" name="destination">
                                ''' + dest_opts + '''
                                <option value="Not sure yet">Not sure yet</option>
                            </select>
                        </div>
                        <div class="field">
                            <label class="field-label" for="inqExperience">Experience</label>
                            <select class="field-input" id="inqExperience" name="experience">
                                ''' + exp_opts + '''
                            </select>
                        </div>
                        <div class="field">
                            <label class="field-label" for="inqCourse">Course <span class="normal-case tracking-normal opacity-60">(if any)</span></label>
                            <select class="field-input" id="inqCourse" name="course">
                                <option value="">Not applicable</option>
                                ''' + course_opts + '''
                            </select>
                        </div>
                        <div class="field">
                            <label class="field-label" for="inqDate">Preferred date</label>
                            <input class="field-input" id="inqDate" name="date" type="date" required>
                            <p class="field-error">Choose a date, today or later.</p>
                        </div>
                        <div class="field">
                            <label class="field-label" for="inqGuests">Guests</label>
                            <input class="field-input" id="inqGuests" name="guests" type="number" min="1" max="24" value="2" required>
                            <p class="field-error">Between 1 and 24 guests.</p>
                        </div>
                    </div>

                    <div class="field mt-5">
                        <label class="field-label" for="inqMessage">Message</label>
                        <textarea class="field-input" id="inqMessage" name="message" placeholder="Tell us what you have in mind - first dive, a course, a group, or an underwater event."></textarea>
                    </div>

                    <div class="flex flex-col sm:flex-row items-center gap-3 mt-7">
                        <button type="submit" id="inqSubmit" class="btn-bio liquid ripple-host w-full sm:w-auto px-8 py-4 rounded-full font-display font-bold tracking-wide flex items-center justify-center gap-2.5">
                            <span class="inq-label">Send enquiry</span>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                        </button>
                        <button type="button" id="inqWaDirect" class="liquid ripple-host w-full sm:w-auto px-7 py-4 rounded-full font-semibold text-sm text-white bg-[#128C4A]/90 border border-[#4ade80]/35 shadow-[0_10px_30px_-10px_rgba(37,211,102,0.6)] flex items-center justify-center gap-2.5">
                            ''' + svg('chat', 'w-4 h-4') + '''Chat on WhatsApp
                        </button>
                    </div>
                    <p class="text-xs text-brand-dim/80 mt-4">No deposit to enquire &mdash; just an answer from the Dive Adda team.</p>
                    <p id="inqFormError" class="text-xs mt-4 hidden" style="color:#FCA5A5;" role="alert"></p>
                </form>

                <div id="inquirySuccess" role="status">
                    <div class="text-center py-6">
                        <span class="inline-grid place-items-center w-16 h-16 rounded-full mb-6 bg-brand-accent/15 border border-brand-accent/40 text-brand-glow shadow-[0_0_34px_-8px_rgba(34,211,238,0.8)]">
                            ''' + svg('check', 'w-8 h-8') + '''
                        </span>
                        <h3 class="font-display text-2xl font-bold text-white mb-3">Enquiry received</h3>
                        <p class="text-brand-dim leading-relaxed max-w-md mx-auto mb-2" id="inqSuccessCopy">Thanks &mdash; we have your details and the Dive Adda team will get back to you shortly.</p>
                        <p class="text-xs text-brand-dim/70 mb-8">Want an answer sooner? Send the same details straight to our WhatsApp.</p>
                        <div class="flex flex-col sm:flex-row gap-3 justify-center">
                            <button type="button" id="inqWhatsapp" class="liquid ripple-host px-6 py-3 rounded-full font-semibold text-sm text-white bg-[#128C4A]/90 border border-[#4ade80]/35 shadow-[0_10px_30px_-10px_rgba(37,211,102,0.6)]">Continue on WhatsApp</button>
                            <button type="button" id="inqReset" class="btn-ghost liquid ripple-host px-6 py-3 rounded-full font-semibold text-sm">Send another</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>'''


def cta_band(title, copy, experience='', destination=''):
    return ('<section class="mb-24"><div class="cta-band glass-deep bio-edge reveal">'
            '<div class="relative grid lg:grid-cols-[2fr_1fr] gap-8 items-center">'
            '<div><h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-3 heading-glow">%s</h2>'
            '<p class="text-brand-dim text-lg leading-relaxed max-w-2xl">%s</p></div>'
            '<div class="flex flex-col gap-3">'
            '<button type="button" data-book data-experience="%s" data-destination="%s" class="btn-bio liquid liquid-strong ripple-host px-7 py-4 rounded-full font-display font-bold">Book your dive</button>'
            '<a href="tel:%s" class="btn-ghost liquid ripple-host px-7 py-4 rounded-full font-semibold text-center">Call %s</a>'
            '</div></div></div></section>' % (title, copy, experience, destination, PHONE_TEL, PHONE_TXT))


def main_open():
    return '<main class="theme-scope site-main flex-grow max-w-7xl mx-auto w-full">'


# ---------------------------------------------------------------- pages
def page_home():
    hero = '''    <header class="home-hero relative w-full overflow-hidden">
        ''' + photo(B('cover-divers'), '', 'hero-media absolute inset-0 w-full h-full object-cover z-0 saturate-[.85]', '100vw', lazy=False, extra='id="heroVideo"') + '''
        <div class="absolute inset-0 bg-gradient-to-b from-brand-abyss/90 via-brand-deep/65 to-brand-deep z-[5]"></div>
        <div class="absolute inset-0 z-[6] pointer-events-none" style="background: radial-gradient(80% 55% at 50% 45%, rgba(34,211,238,0.08), transparent 65%);"></div>
        <div id="heroFish" class="absolute inset-0 z-[7] overflow-hidden pointer-events-none" aria-hidden="true"></div>

        <div class="hero-inner relative z-10 text-center max-w-4xl mx-auto w-full flex flex-col items-center reveal active">
            <span class="float-organic inline-flex items-center gap-2.5 chip-cyan rounded-full px-4 py-1.5 font-semibold tracking-[0.22em] uppercase text-[10px] mb-8">
                <span class="w-1.5 h-1.5 rounded-full bg-brand-glow shadow-[0_0_10px_#67E8F9]"></span>
                SSI Certified Scuba Centre &middot; Visakhapatnam
            </span>
            <h1 class="hero-title font-display font-bold text-white leading-[0.95] mb-5 heading-glow tracking-tight">DIVE <span class="text-gradient-bio">ADDA</span></h1>
            <p class="hero-tagline font-bold uppercase text-brand-glow/80 mb-7">Discover &mdash; The Deep</p>
            <p class="hero-lead text-brand-ink/80 mb-9 max-w-2xl font-medium leading-relaxed">Scuba diving in Vizag, SSI certification courses, and water sports on the Godavari in Rajahmundry.</p>
            <div class="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                <button type="button" data-book data-experience="Try Scuba (first dive)" data-destination="Visakhapatnam" class="btn-bio liquid liquid-strong ripple-host px-8 py-4 rounded-full font-display font-bold text-lg">Book your dive</button>
                <a href="#about" class="btn-ghost liquid ripple-host px-8 py-4 rounded-full font-bold text-lg flex items-center justify-center gap-2.5">Explore
                    <svg class="w-5 h-5 text-brand-glow cue-dot" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                </a>
            </div>
            <div class="hero-cue mt-12 flex flex-col items-center gap-2 text-[10px] uppercase tracking-[0.3em] text-brand-dim/50" aria-hidden="true">
                <span>Descend</span>
                <span class="relative w-[1px] h-10 bg-gradient-to-b from-brand-accent/60 to-transparent"></span>
            </div>
        </div>
    </header>
'''
    body = (hero + main_open()
            + about_home_section('01')
            + courses_section('02', title='SSI Courses', desc='Learn to dive. Build confidence. Become certified.', link=None, overview=True)
            + scuba_vizag_section('03') + water_sports_section('04')
            + testimonials_section('05') + book_section('06')
            + '</main>')
    ld = [
        {"@type": "WebSite", "@id": DOMAIN + "#website", "url": DOMAIN, "name": "Dive Adda", "inLanguage": "en", "publisher": {"@id": ORG_ID}},
        {"@type": "WebPage", "@id": DOMAIN + "#webpage", "url": DOMAIN,
         "name": "Scuba Diving in Vizag & Water Sports in Rajahmundry | Dive Adda",
         "isPartOf": {"@id": DOMAIN + "#website"}, "about": {"@id": CENTRE_ID}},
        {"@type": "Service", "name": "Scuba diving in Vizag", "serviceType": "Scuba diving",
         "description": "Beginner scuba dives and guided dives off Visakhapatnam with SSI certified instructors. About 40 minutes underwater, maximum depth 6-8 metres for first-timers, minimum age 8.",
         "provider": {"@id": ORG_ID}, "areaServed": {"@type": "City", "name": "Visakhapatnam"}, "url": DOMAIN + "visakhapatnam.html"},
        {"@type": "Service", "name": "Water sports in Rajahmundry", "serviceType": "Water sports",
         "description": "River water sports on the Godavari at Rajahmundry: speed boat rides, jet ski rides, kayaking, and dragon, disco and bumper rides.",
         "provider": {"@id": ORG_ID}, "areaServed": {"@type": "City", "name": "Rajahmundry"}, "url": DOMAIN + "rajahmundry.html"},
    ] + [ld_course(c) for c in COURSES]
    return shell('home', 'home', 18,
                 'Scuba Diving in Vizag &amp; Water Sports in Rajahmundry | Dive Adda',
                 'SSI certified scuba diving in Vizag: beginner dives and SSI scuba courses, plus Godavari river water sports in Rajahmundry. Book your dive with Dive Adda.',
                 '', body, ld, hero_img=B('cover-divers'), book_modal=True)


def page_first_time_scuba():
    overview = ('<section class="mb-28"><div class="grid lg:grid-cols-2 gap-10 items-center">'
                '<div class="reveal"><div class="frame-photo glass-panel p-2 h-[320px] md:h-[460px]">'
                + photo(B('ssi-pool-training'), 'A Try Scuba guest learning with a Dive Adda instructor', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw')
                + '</div></div><div class="reveal delay-100">'
                '<p class="eyebrow mb-4">01 &mdash; Try Scuba</p>'
                '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-5 heading-glow">Try Scuba Diving with Dive Adda</h2>'
                '<p class="text-brand-dim text-lg leading-relaxed mb-4">Try Scuba is your introduction to the amazing world of scuba diving and an opportunity to explore the underwater world of Vizag.</p>'
                '<p class="text-brand-dim leading-relaxed mb-4">Never tried scuba diving before? No problem. Our Try Scuba experience is designed to introduce you to scuba diving with proper equipment training, safety briefing, and guidance from an experienced diving instructor.</p>'
                '<p class="text-brand-dim leading-relaxed mb-7">Your experience takes you from the initial briefing at our centre to the dive site, where you can explore the underwater landscape and marine life.</p>'
                + fact_tiles(TRY_FACTS) + '</div></div></section>')

    day = ('<section id="itinerary" class="mb-28">'
           + sec_head('02', 'Try Scuba Experience Details', 'Your first scuba diving experience',
                      'Duration: 6:30 AM &ndash; 12:30 PM', center=True)
           + '<div class="max-w-3xl mx-auto">' + itinerary_timeline() + '</div></section>')

    included = ('<section class="mb-28"><div class="grid lg:grid-cols-2 gap-6">'
                '<div class="glass-panel rounded-3xl p-6 md:p-8 reveal">'
                '<p class="eyebrow mb-3">03 &mdash; Included</p>'
                '<h2 class="font-display text-2xl md:text-3xl font-bold text-white mb-5">What&rsquo;s included?</h2>'
                '<p class="text-brand-dim mb-5">Your Try Scuba experience includes:</p>'
                + pill_list(TRY_INCLUDED, cols='') + '</div>'
                '<div class="glass-panel rounded-3xl p-6 md:p-8 reveal delay-100">'
                '<p class="eyebrow mb-3">04 &mdash; Requirements</p>'
                '<h2 class="font-display text-2xl md:text-3xl font-bold text-white mb-5">Requirements for Try Scuba</h2>'
                '<p class="text-brand-dim mb-5">Before booking your first scuba diving experience, please note:</p>'
                + pill_list(TRY_REQUIREMENTS, cols='') + '</div>'
                '</div></section>')

    know = ('<section class="mb-28">'
            + sec_head('05', 'Before You Come', 'Important things to know', '', center=True)
            + '<div class="grid sm:grid-cols-2 gap-5">'
            + ''.join('<div class="trust-card glass-panel bio-edge reveal %s"><span class="ic-icon mb-4">%s</span>'
                      '<h3 class="font-display text-lg font-bold text-white mb-2">%s</h3>'
                      '<p class="text-brand-dim text-sm leading-relaxed">%s</p></div>'
                      % (['', 'delay-100'][i % 2], svg(ic, 'w-5 h-5'), t, d) for i, (ic, t, d) in enumerate(TRY_KNOW))
            + '</div></section>')

    body = (page_hero('Beginner Level Scuba', 'Beginner Level Scuba in <span class="text-gradient-bio">Vizag</span>',
                      'Never tried scuba diving before? No problem. Equipment training, a safety briefing and an experienced instructor beside you.',
                      B('guided-fun-dive'), 8, [('Home', 'index.html'), ('Beginner Level Scuba', None)], ghost='TRY',
                      ctas=hero_ctas('Book your dive', experience='Try Scuba (first dive)', destination='Visakhapatnam'))
            + main_open() + overview + day + included + know
            + faq_block('06', 'Try Scuba FAQs', 'Questions before your first dive', '', TRY_FAQS)
            + cta_band('Ready for your first breath underwater?',
                       'Tell us your preferred date and group size. We confirm availability and send you everything you need to know.',
                       experience='Try Scuba (first dive)', destination='Visakhapatnam')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Beginner Level Scuba', 'beginner-level-scuba.html')]),
          ld_service('Beginner Level Scuba (Try Scuba)', 'An introduction to scuba diving in Visakhapatnam with equipment training, a safety briefing and an experienced diving instructor. About 40 minutes underwater to a maximum depth of 6-8 metres. Minimum age 8.', 'beginner-level-scuba.html'),
          ld_faq(TRY_FAQS)]
    return shell('beginner-level-scuba', 'beginner-level-scuba', 8,
                 'Beginner Level Scuba in Vizag | Try Scuba with Dive Adda',
                 'Beginner level scuba diving in Visakhapatnam with Dive Adda: equipment training, safety briefing and an experienced instructor. About 40 minutes underwater, 6-8 m max depth, minimum age 8.',
                 'beginner-level-scuba.html', body, ld, hero_img=B('guided-fun-dive'))


def specialties_section(num='03'):
    cards = ''.join(
        '<article id="%s" class="spec-card glass-panel bio-edge reveal %s">%s'
        '<div class="spec-body">'
        '<h3 class="font-display text-xl font-bold text-white mb-2">%s</h3>'
        '<p class="text-brand-dim text-sm leading-relaxed mb-5">%s</p>'
        '<button type="button" data-book data-experience="SSI Course" class="btn-ghost liquid ripple-host px-5 py-2.5 rounded-full font-semibold text-sm">Enquire</button>'
        '</div></article>'
        % (sp['id'], ['', 'delay-100', 'delay-200', 'delay-300'][i % 4],
           ('<div class="spec-media on-media">%s<span class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/30 to-transparent"></span></div>'
            % photo(course_photo(sp['id']), sp['name'], 'bento-image absolute inset-0 w-full h-full object-cover', '(max-width: 767px) 100vw, 25vw'))
           if course_photo(sp['id']) else
           ('<div class="spec-icon">%s</div>' % svg(sp['icon'], 'w-6 h-6')),
           sp['name'], sp['text'])
        for i, sp in enumerate(SPECIALTIES))
    return ('<section id="specialties" class="mb-28">'
            + sec_head(num, 'Specialties', 'Go further with SSI specialties',
                       'Short programmes that add a specific skill to the diving you already do.')
            + '<div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 lg:gap-6">' + cards + '</div></section>')


def page_courses():
    ssi_intro = ('<section class="mb-24"><div class="cta-band glass-deep bio-edge reveal">'
                 '<div class="relative grid lg:grid-cols-[auto_1fr] gap-8 items-center">'
                 '<img src="assets/img/ssi-dive-center-2x.png" alt="SSI Official Partner Dive Center" class="ssi-badge mx-auto object-contain" width="132" height="107" loading="lazy">'
                 '<div><h2 class="font-display text-3xl font-bold text-white mb-3">An internationally certified SSI dive centre</h2>'
                 '<p class="text-brand-dim text-lg leading-relaxed">We are proudly affiliated with SSI (Scuba Schools International), ensuring our training programmes meet the highest global standards. '
                 'Our team provides professional dive training for all levels &mdash; from beginners taking their first dive to professionals looking to enhance their skills.</p>'
                 '</div></div></div></section>')
    benefits = ('<section class="mb-28">'
                + sec_head('02', 'Benefits', 'Why take a scuba course', 'What a course gives you, beyond the certification card.', center=True)
                + '<div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">'
                + ''.join('<div class="trust-card glass-panel bio-edge reveal"><span class="ic-icon mb-4">%s</span>'
                          '<h3 class="font-display font-bold text-white text-lg leading-tight">%s</h3></div>' % (svg(ic, 'w-5 h-5'), b)
                          for ic, b in [('cap', 'Learn essential diving skills'), ('shield', 'Enhanced safety'),
                                        ('globe', 'Global certification'), ('people', 'Career &amp; volunteering opportunities'),
                                        ('heart', 'Physical &amp; mental health benefits'), ('chat', 'Meet a community of divers'),
                                        ('camera', 'Underwater photography &amp; videography'), ('spark', 'A reason to keep diving')])
                + '</div></section>')
    body = (page_hero('SSI Courses', 'Get <span class="text-gradient-bio">certified</span>',
                      'SSI certified courses from beginner to professional level, taught by instructors with over 15 years of industry experience.',
                      B('ssi-pool-training'), 12, [('Home', 'index.html'), ('Courses', None)],
                      ghost='SSI', ctas=hero_ctas('Start a course', experience='SSI Course'))
            + main_open() + ssi_intro
            + courses_section('01', title='Choose your course', desc='Every course has its own page with what you will learn and who it is for.', link=None)
            + benefits
            + specialties_section('03')
            + faq_block('04', 'FAQ', 'Course questions', '', GENERAL_FAQS[:2])
            + cta_band('Not sure which course fits?',
                       'Tell us where you are starting from and our instructors will point you to the right programme.',
                       experience='SSI Course')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Courses', 'courses.html')])] + [ld_course(c) for c in COURSES] + [ld_faq(GENERAL_FAQS[:2])]
    return shell('courses', 'courses', 12,
                 'SSI Scuba Diving Courses | Open Water Diver to Dive Master | Dive Adda',
                 'SSI certified scuba courses with Dive Adda in Visakhapatnam: Open Water Diver, Advanced Adventurer, React Right, Diver Stress & Rescue and Dive Master.',
                 'courses.html', body, ld, hero_img=B('ssi-pool-training'))


def page_course(c):
    idx = COURSES.index(c)
    steps = ''.join(
        '<a href="%s" class="%s"%s><span class="cs-n">%s</span>%s</a>'
        % (x['file'], 'chip-cyan' if x is c else 'chip', ' aria-current="page"' if x is c else '', x['step'], x['name'])
        for x in COURSES)
    prev_c = COURSES[idx - 1] if idx > 0 else None
    next_c = COURSES[idx + 1] if idx < len(COURSES) - 1 else None
    nav_links = ''
    if prev_c:
        nav_links += '<a href="%s" class="btn-ghost liquid ripple-host px-6 py-3 rounded-full font-semibold text-sm">&larr; %s</a>' % (prev_c['file'], prev_c['name'])
    if next_c:
        nav_links += '<a href="%s" class="btn-ghost liquid ripple-host px-6 py-3 rounded-full font-semibold text-sm">Next: %s &rarr;</a>' % (next_c['file'], next_c['name'])

    overview = ('<section class="mb-28"><div class="grid lg:grid-cols-2 gap-10 items-center">'
                '<div class="reveal"><div class="frame-photo glass-panel p-2 h-[300px] md:h-[440px]">'
                + photo(c['img'], c['full'], 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw')
                + '</div></div><div class="reveal delay-100">'
                '<div class="flex flex-wrap items-center gap-3 mb-4"><span class="chip-cyan px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.14em]">%s</span>'
                '<span class="eyebrow">Step %s of %d</span></div>'
                '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-5 heading-glow">About the course</h2>'
                '<p class="text-brand-dim text-lg leading-relaxed mb-6">%s</p>'
                '<div class="glass-panel rounded-2xl p-5"><p class="field-label mb-1">Who it&rsquo;s for</p><p class="text-brand-ink leading-relaxed">%s</p></div>'
                '</div></div></section>') % (c['level'], c['step'], len(COURSES), c['long'], c['who'])

    learn = ('<section class="mb-28">' + sec_head('02', 'What You&rsquo;ll Learn', 'Skills this course gives you', '')
             + '<div class="reveal">' + pill_list(c['learn']) + '</div></section>')

    pathway = ('<section class="mb-24">' + sec_head('03', 'Course Pathway', 'Where this course fits',
                                                     'SSI training builds from your first certification to professional level.')
               + '<div class="course-steps reveal">' + steps + '</div>'
               + ('<div class="flex flex-wrap gap-3 mt-8 reveal">' + nav_links + '</div>' if nav_links else '')
               + '</section>')

    plain = html.unescape(c['name'])
    body = (page_hero('SSI Course', c['full'], c['short'], c['img'], c['depth'],
                      [('Home', 'index.html'), ('Courses', 'courses.html'), (c['name'], None)], ghost='SSI',
                      ctas=hero_ctas('Enquire about this course', experience='SSI Course'))
            + main_open() + overview + learn + pathway
            + cta_band('Start %s' % c['name'],
                       'Tell us when you would like to start and our instructors will confirm dates and what you need to begin.',
                       experience='SSI Course', destination='Visakhapatnam')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Courses', 'courses.html'), (plain, c['file'])]), ld_course(c)]
    return shell(c['id'], 'courses', c['depth'],
                 '%s Course in Visakhapatnam | Dive Adda' % html.unescape(c['full']).replace('&', '&amp;'),
                 '%s with Dive Adda, an SSI certified dive centre in Visakhapatnam. %s' % (html.unescape(c['full']), html.unescape(c['short'])),
                 c['file'], body, ld, hero_img=c['img'])


def page_destination(d):
    other = [x for x in DESTS if x is not d][0]
    acts = ''.join(
        '<article id="%s" class="act-card glass-panel bio-edge reveal %s">%s'
        '<div class="act-body">'
        '<h3 class="font-display text-xl font-bold text-white mb-2">%s</h3>'
        '<p class="text-brand-dim text-sm leading-relaxed mb-6 flex-grow">%s</p>'
        '<div class="flex flex-wrap gap-3">'
        '<button type="button" data-book data-destination="%s" data-experience="%s" class="btn-bio liquid ripple-host px-5 py-2.5 rounded-full font-bold text-sm">Book</button>'
        '%s</div></div></article>'
        % (aid, ['', 'delay-100', 'delay-200'][i % 3],
           ('<div class="act-media on-media group">%s'
            '<span class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/25 to-transparent"></span>'
            '<span class="act-badge">%s</span></div>'
            % (photo(activity_photo(aid), name, 'bento-image absolute inset-0 w-full h-full object-cover', '(max-width: 639px) 100vw, (max-width: 1023px) 50vw, 33vw'),
               svg(icon, 'w-5 h-5')))
           if activity_photo(aid) else ('<div class="act-media act-media-empty"><span class="ic-icon">%s</span></div>' % svg(icon, 'w-6 h-6')),
           name, desc, d['name'], html.unescape(name),
           ('<a href="%s" class="btn-ghost liquid ripple-host px-5 py-2.5 rounded-full font-semibold text-sm">Learn more</a>' % link) if link else '')
        for i, (aid, name, icon, desc, link) in enumerate(d['acts']))

    centre = ''
    if d['id'] == 'visakhapatnam':
        centre = ('<section class="mb-28"><div class="grid lg:grid-cols-2 gap-10 items-center">'
                  '<div class="reveal"><div class="frame-photo glass-panel p-2 h-[380px] md:h-[500px]">'
                  + photo(B('dive-centre-storefront'), 'The Dive Adda scuba dive centre', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw')
                  + '</div></div><div class="reveal delay-100">'
                  '<p class="eyebrow mb-4">02 &mdash; The Centre</p>'
                  '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-4 heading-glow">Our SSI certified scuba centre</h2>'
                  '<p class="text-brand-dim text-lg leading-relaxed mb-6">Dive Adda is an internationally certified dive centre, proudly affiliated with SSI. '
                  'Try Scuba, SSI courses and guided dives all start here, for complete beginners and certified divers alike.</p>'
                  '<div class="glass-panel rounded-2xl p-5 flex items-center gap-5 mb-7">'
                  '<img src="assets/img/ssi-dive-center-2x.png" alt="SSI Official Partner Dive Center" class="w-16 h-16 object-contain" loading="lazy" width="64" height="52">'
                  '<p class="text-sm text-brand-dim leading-relaxed">Our training programmes meet the highest global standards.</p></div>'
                  '<a href="beginner-level-scuba.html" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold inline-flex items-center gap-2.5">New to diving? Start here ' + svg('arrow', 'w-4 h-4 text-brand-glow') + '</a>'
                  '</div></div></section>')
    map_num = '03' if centre else '02'
    other_num = '04' if centre else '03'

    body = (page_hero('Location', 'Dive Adda <span class="text-gradient-bio">%s</span>' % d['name'], d['long'], d['hero'], d['depth'],
                      [('Home', 'index.html'), (d['name'], None)],
                      ghost=d['short'].upper(), ctas=hero_ctas('Book in ' + d['name'], destination=d['name']))
            + main_open()
            + '<section id="activities" class="mb-28">'
            + sec_head('01', 'Activities', 'What you can do in %s' % d['name'],
                       'Timings and availability are confirmed when you book.')
            + '<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6 orphan-sm-lg">' + acts + '</div></section>'
            + centre
            + '<section class="mb-24">' + sec_head(map_num, 'On the map', 'Find us in %s' % d['name'], '')
            + '<div class="h-[420px] relative rounded-3xl overflow-hidden glass-panel p-2 reveal">'
            + '<div id="diveMap" data-focus="%s"></div></div></section>' % d['id']
            + '<section class="mb-24">' + sec_head(other_num, 'Also with Dive Adda', other['name'], '')
            + '<div class="grid md:grid-cols-2 gap-6"><div class="md:col-span-2 lg:col-span-1">' + location_card(other, 0) + '</div></div></section>'
            + cta_band('Planning a day in %s?' % d['name'],
                       'Tell us the activity, your date and group size &mdash; we confirm availability with the team.',
                       destination=d['name'])
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), (d['name'], d['file'])]),
          ld_service('Water activities in ' + d['name'], html.unescape(d['long']), d['file'])]
    return shell(d['id'], 'locations', d['depth'],
                 '%s: %s | Dive Adda' % (d['name'], ', '.join(html.unescape(a[1]) for a in d['acts'][:3])),
                 html.unescape(d['long'])[:180],
                 d['file'], body, ld, hero_img=d['hero'], use_map=True)


def page_events():
    details = ''
    for i, e in enumerate(EVENTS):
        flip = (i % 2 == 1)
        details += ('<section id="%s" class="mb-24">'
                    '<div class="grid lg:grid-cols-2 gap-10 items-center">'
                    '<div class="reveal %s"><div class="frame-photo glass-panel p-2 h-[320px] md:h-[420px]">%s</div></div>'
                    '<div class="reveal delay-100 %s">'
                    '<span class="ic-icon mb-5">%s</span>'
                    '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-4 heading-glow">%s</h2>'
                    '<p class="text-brand-dim text-lg leading-relaxed mb-7">%s</p>'
                    '<button type="button" data-book data-experience="Underwater Event" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Plan this event</button>'
                    '</div></div></section>'
                    % (e['id'], 'lg:order-2' if flip else '',
                       photo(e['img'], e['name'], 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'),
                       'lg:order-1' if flip else '', svg(e['icon'], 'w-6 h-6'), e['name'], e['text']))

    how = ('<section class="mb-28">'
           + sec_head('02', 'How it works', 'From idea to underwater',
                      'Every underwater event is planned with you, and run by SSI certified instructors.', center=True)
           + '<div class="journey reveal"><span class="journey-line" aria-hidden="true"><span></span></span>'
           + ''.join('<div class="j-step"><span class="j-node">%s</span>'
                     '<div class="j-card glass-panel"><h3 class="font-display font-bold text-white mb-1.5">%s</h3>'
                     '<p class="text-sm text-brand-dim leading-relaxed">%s</p></div></div>' % (n, t, d)
                     for n, t, d in [
                         ('01', 'Tell us the occasion', 'Birthday, proposal, shoot or a conservation dive &mdash; and how many people are coming.'),
                         ('02', 'Plan it with our team', 'We work out the location, the timing and what everyone needs to be comfortable underwater.'),
                         ('03', 'Safety briefing', 'Everyone taking part gets a full briefing and practice, whether or not they have dived before.'),
                         ('04', 'The moment', 'You get the memory. Our instructors handle everything else.')])
           + '</div></section>')

    body = (page_hero('Underwater Events', 'Celebrate <span class="text-gradient-bio">below the surface</span>',
                      'Birthday parties, marriage proposals, pre-wedding shoots and conservation dives &mdash; planned with the Dive Adda team.',
                      B('event-prewedding'), 15,
                      [('Home', 'index.html'), ('Underwater Events', None)],
                      ghost='EVENTS', ctas=hero_ctas('Plan an event', experience='Underwater Event'))
            + main_open() + events_section('01') + details + how
            + cta_band('Have an occasion in mind?',
                       'Tell us what you are planning and our team will work out how to do it underwater.',
                       experience='Underwater Event')
            + '</main>')

    ld = [ld_breadcrumb([('Home', ''), ('Underwater Events', 'events.html')]),
          ld_service('Underwater Events', 'Underwater birthday parties, marriage proposals, pre-wedding shoots and conservation dives with Dive Adda.', 'events.html')]
    return shell('events', 'more', 15,
                 'Underwater Events: Birthdays, Proposals &amp; Pre-Wedding Shoots | Dive Adda',
                 'Underwater birthday parties, marriage proposals, pre-wedding shoots and conservation diving with Dive Adda, planned and run by SSI certified instructors.',
                 'events.html', body, ld, hero_img=B('event-prewedding'))


def page_gallery():
    body = (page_hero('Gallery', 'Our <span class="text-gradient-bio">gallery</span>',
                      'Training sessions, fun dives, snorkelling, boat diving and underwater events &mdash; photographed on our own dives.',
                      B('cover-divers'), 20,
                      [('Home', 'index.html'), ('Gallery', None)], ghost='PHOTO')
            + main_open()
            + '<section class="mb-24">'
            + '<p class="text-brand-dim text-lg leading-relaxed max-w-2xl mb-8 reveal">Filter by what you want to see, then tap any photo to open it full screen.</p>'
            + gallery_grid('galleryAll', GALLERY)
            + '<!-- Add photos: copy a <figure class="gallery-tile">, set data-cat to one of '
              'diving / courses / snorkelling / boat / events / destinations, and point the img at your file. -->'
            + '</section>'
            + cta_band('Want to be in the next one?',
                       'Book a dive and bring a camera &mdash; or let our team shoot it for you.')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Gallery', 'gallery.html')]),
          {"@type": "ImageGallery", "name": "Dive Adda Gallery", "url": DOMAIN + "gallery.html",
           "about": {"@id": CENTRE_ID}}]
    return shell('gallery', 'more', 20,
                 'Gallery | Dive Adda Scuba Diving Photos',
                 'Photos from Dive Adda: SSI training sessions, guided fun dives, snorkelling, boat diving and underwater events.',
                 'gallery.html', body, ld, hero_img=B('cover-divers'), lightbox=True)


def page_about():
    who = ('<section class="mb-28"><div class="grid lg:grid-cols-2 gap-10 items-center">'
           '<div class="reveal delay-100 lg:order-2"><div class="frame-photo glass-panel p-2 h-[360px] md:h-[460px]">%s</div></div>'
           '<div class="reveal lg:order-1">'
           '<p class="eyebrow mb-4">02 &mdash; Who We Are</p>'
           '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-5 heading-glow">Passionate about the underwater world</h2>'
           '<p class="text-brand-dim text-lg leading-relaxed mb-5">We are passionate about exploring the underwater world and sharing that experience with others. '
           'As an internationally certified dive center, we are proudly affiliated with SSI, ensuring that our training programs meet the highest global standards.</p>'
           '<p class="text-brand-dim leading-relaxed mb-5">With over 15 years of industry experience, our team of expert instructors provides professional dive training for all levels '
           '&mdash; from beginners taking their first dive to advanced divers and professionals looking to enhance their skills. '
           'Whether you want to experience the thrill of diving for the first time or pursue a career in scuba diving, we offer comprehensive courses, '
           'personalized instruction, and safe, unforgettable diving adventures.</p>'
           '<p class="font-display text-xl font-bold text-gradient-bio">Join us and dive into a whole new world!</p>'
           '</div></div></section>'
           % photo(B('outbound-trip'), 'The Dive Adda community on an outbound trip', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'))

    passion = ('<section class="mb-28"><div class="cta-band glass-deep bio-edge reveal">'
               '<div class="relative text-center max-w-3xl mx-auto">'
               '<p class="eyebrow mb-4">04 &mdash; Our Passion for the Ocean</p>'
               '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-5 heading-glow">Trust, expertise and passion at the core</h2>'
               '<p class="text-brand-dim text-lg leading-relaxed">Join us and discover the wonders of the underwater world with trust, expertise, and passion '
               'at the core of everything we do.</p></div></div></section>')

    body = (page_hero('About Us', 'Our <span class="text-gradient-bio">story</span>',
                      'At Dive Adda, we bring the depths of the ocean closer to you.',
                      B('outbound-trip'), 6,
                      [('Home', 'index.html'), ('About Us', None)], ghost='STORY',
                      ctas=hero_ctas('Dive with us'))
            + main_open() + story_section() + who
            + scuba_cards_section('03') + passion + team_section('05') + conservation_section('06')
            + cta_band('Come and see for yourself',
                       'Book a beginner dive, an SSI course or a day on the water with the team behind the story.')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('About Us', 'about.html')]),
          {"@type": "AboutPage", "url": DOMAIN + "about.html", "about": {"@id": ORG_ID}, "name": "About Dive Adda"}]
    return shell('about', 'about', 6,
                 'About Us | Dive Adda SSI Certified Dive Centre',
                 'Dive Adda was founded by a professional with 15 years in the Indian Navy, over a decade in submarines and 10 years in oil & gas. An SSI affiliated dive centre with over 15 years of team experience.',
                 'about.html', body, ld, hero_img=B('outbound-trip'), profile=True)


def page_faq():
    body = (page_hero('FAQ&rsquo;s', 'Before you <span class="text-gradient-bio">dive in</span>',
                      'The questions we are asked most, answered by the Dive Adda team.',
                      B('confined-diving'), 22, [('Home', 'index.html'), ('FAQ&rsquo;s', None)], ghost='FAQ', compact=True)
            + main_open()
            + faq_block('01', 'Try Scuba', 'First-time scuba questions', '', TRY_FAQS, sid='try-scuba-faq', footer=False)
            + faq_block('02', 'General', 'About Dive Adda', '', GENERAL_FAQS, sid='general-faq')
            + cta_band('Question not answered here?',
                       'Send it over &mdash; our team answers personally, and there is no deposit to enquire.')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ("FAQ's", 'faq.html')]), ld_faq(TRY_FAQS + GENERAL_FAQS)]
    return shell('faq', 'more', 22,
                 'FAQ&rsquo;s | Try Scuba &amp; Diving Questions | Dive Adda',
                 'Try Scuba minimum age, dive time, depth, what to bring, weather and cancellation policy, plus SSI courses and locations. Answers from Dive Adda.',
                 'faq.html', body, ld, hero_img=B('confined-diving'))


def post_card(p, featured=False):
    return ('<article class="post-card glass-panel reveal%s">'
            '<a class="post-media on-media group" href="%s" aria-label="%s">%s'
            '<span class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/30 to-transparent"></span></a>'
            '<div class="post-body">'
            '<div class="flex flex-wrap items-center gap-3 mb-3 text-[11px] uppercase tracking-[0.18em]">'
            '<span class="chip-cyan px-3 py-1 rounded-full font-bold">%s</span>'
            '<span class="text-brand-dim">%s</span><span class="text-brand-dim/60">%s</span></div>'
            '<h3 class="font-display font-bold text-white mb-3 %s"><a href="%s">%s</a></h3>'
            '<p class="text-brand-dim leading-relaxed mb-5">%s</p>'
            '<a href="%s" class="link-glow font-semibold text-sm inline-flex items-center gap-2">Read the post %s</a>'
            '</div></article>'
            % (' post-featured' if featured else '', p['file'], E(p['title']),
               photo(p['img'], p['title'], 'bento-image absolute inset-0 w-full h-full object-cover',
                     '(max-width: 767px) 100vw, 50vw'),
               p['tag'], p['date_label'], p['read'],
               'text-2xl md:text-3xl' if featured else 'text-xl', p['file'], p['title'], p['excerpt'],
               p['file'], svg('arrow', 'w-3.5 h-3.5')))


def page_blog():
    posts = ''.join(post_card(p, featured=(i == 0)) for i, p in enumerate(POSTS))
    reads = ''.join(
        '<a class="read-link glass-panel reveal" href="%s" target="_blank" rel="noopener">'
        '<span class="read-ic">%s</span>'
        '<span class="min-w-0"><span class="block text-white font-semibold">%s</span>'
        '<span class="block text-sm text-brand-dim">%s</span></span>'
        '<span class="read-host">%s</span></a>'
        % (url, svg('arrow', 'w-4 h-4'), name, note, url.split('/')[2].replace('www.', ''))
        for name, url, note in BLOG_LINKS)
    body = (page_hero('Blog', 'The <span class="text-gradient-bio">dive log</span>',
                      'Guides and stories from the Dive Adda team, plus reading from the wider diving world.',
                      B('guided-fun-dive'), 10, [('Home', 'index.html'), ('Blog', None)], ghost='BLOG', compact=True)
            + main_open()
            + '<section class="mb-28"><div class="post-grid">' + posts + '</div></section>'
            + '<section class="mb-24">'
            + sec_head('02', 'Elsewhere', 'More reads from the dive world',
                       'Articles and resources we send guests to, published by SSI and Divers Alert Network.')
            + '<div class="grid gap-4 max-w-3xl">' + reads + '</div></section>'
            + cta_band('Ready to try it yourself?',
                       'Reading about diving is one thing. Breathing underwater for the first time is another.',
                       experience='Try Scuba (first dive)', destination='Visakhapatnam')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Blog', 'blog.html')]),
          {"@type": "Blog", "@id": DOMAIN + "blog.html#blog", "name": "Dive Adda Blog", "url": DOMAIN + "blog.html",
           "publisher": {"@id": ORG_ID},
           "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "datePublished": p['date'],
                         "url": DOMAIN + p['file'], "image": DOMAIN + p['img'], "author": {"@id": ORG_ID}} for p in POSTS]}]
    return shell('blog', 'more', 10, 'Blog | Dive Adda',
                 'Dive guides and stories from Dive Adda in Visakhapatnam and Rajahmundry, plus reading from SSI and Divers Alert Network.',
                 'blog.html', body, ld, hero_img=B('guided-fun-dive'))


def page_post(p):
    steps = ''.join(
        '<li><b class="text-brand-ink">%s &mdash; %s.</b> %s</li>' % (t, h, d) for t, h, d in TRY_STEPS)
    article = ('<article class="legal post-article glass-panel rounded-3xl p-6 md:p-10 max-w-3xl mx-auto reveal">'
               '<div class="flex flex-wrap items-center gap-3 mb-6 text-[11px] uppercase tracking-[0.18em]">'
               '<span class="chip-cyan px-3 py-1 rounded-full font-bold">%s</span>'
               '<span class="text-brand-dim">%s</span><span class="text-brand-dim/60">%s</span>'
               '<span class="text-brand-dim/60">Dive Adda</span></div>'
               '<p class="text-brand-ink text-lg leading-relaxed mb-8">%s</p>'
               % (p['tag'], p['date_label'], p['read'], p['intro'])
               + '<section class="legal-block"><h2 class="font-display text-xl md:text-2xl font-bold text-white mb-3">You do not need any experience</h2>'
                 '<p>Our beginner level dive is built for people trying scuba for the first time. You get equipment training, a safety briefing, and an experienced instructor with you in the water. The minimum age is 8 years, and you do not need a certification of any kind.</p></section>'
               + '<section class="legal-block"><h2 class="font-display text-xl md:text-2xl font-bold text-white mb-3">The morning, hour by hour</h2>'
                 '<ul>' + steps + '</ul></section>'
               + '<section class="legal-block"><h2 class="font-display text-xl md:text-2xl font-bold text-white mb-3">What is included</h2><ul>'
               + ''.join('<li>%s</li>' % x for x in TRY_INCLUDED) + '</ul></section>'
               + '<section class="legal-block"><h2 class="font-display text-xl md:text-2xl font-bold text-white mb-3">What to bring</h2>'
                 '<p>Bring a cap, a change of clothes and a towel. Eat light before you arrive &mdash; it keeps the boat ride comfortable. Guests arrange their own transport and accommodation.</p></section>'
               + '<section class="legal-block"><h2 class="font-display text-xl md:text-2xl font-bold text-white mb-3">Before you book</h2><ul>'
               + ''.join('<li>%s</li>' % x for x in TRY_REQUIREMENTS)
               + '<li>Sea and weather conditions can change the plan; we will tell you as early as we can.</li></ul></section>'
               + '<section class="legal-block"><h2 class="font-display text-xl md:text-2xl font-bold text-white mb-3">Ready to go?</h2>'
                 '<p>Full details of the day are on the <a href="beginner-level-scuba.html">Beginner Level Scuba</a> page, '
                 'and the <a href="faq.html">FAQ</a> answers the questions we hear most. When you are ready, '
                 '<a href="contact.html#enquire">send us your dates</a>.</p></section>'
               + '<div class="flex flex-wrap gap-3 mt-10">'
                 '<button type="button" data-book data-experience="Try Scuba (first dive)" data-destination="Visakhapatnam" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Book your dive</button>'
                 '<a href="blog.html" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold">All posts</a>'
                 '</div></article>')
    body = (page_hero('Blog', p['title'], p['excerpt'], p['img'], 10,
                      [('Home', 'index.html'), ('Blog', 'blog.html'), (p['tag'], None)], compact=True)
            + main_open() + article + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Blog', 'blog.html'), (p['title'], p['file'])]),
          {"@type": "BlogPosting", "headline": p['title'], "description": p['excerpt'],
           "datePublished": p['date'], "dateModified": p['date'], "url": DOMAIN + p['file'],
           "image": DOMAIN + p['img'], "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID},
           "mainEntityOfPage": DOMAIN + p['file']}]
    return shell('blog', 'more', 10, '%s | Dive Adda' % p['title'], p['excerpt'][:180], p['file'], body, ld, hero_img=p['img'])


def page_contact():
    body = (page_hero('Contact Us', 'Talk to the <span class="text-gradient-bio">dive desk</span>',
                      'Call, message on WhatsApp, or send an enquiry. We will confirm availability for your dates.',
                      B('boat-diving'), 24, [('Home', 'index.html'), ('Contact Us', None)], ghost='HELLO')
            + main_open()
            + enquiry_section('01')
            + '<section class="mb-24 mt-24">' + sec_head('02', 'Locations', 'Where to find us',
                                                          'Our SSI certified scuba centre is in Visakhapatnam, and we run water activities in Rajahmundry.')
            + '<div class="grid lg:grid-cols-3 gap-8 items-stretch">'
            + '<div class="lg:col-span-1 reveal"><ul class="space-y-3">'
            + ''.join('<li><a href="%s" class="glass-panel liquid rounded-2xl p-4 flex items-start gap-4">'
                      '<span class="shrink-0 p-2.5 rounded-xl bg-brand-accent/12 border border-brand-accent/30 text-brand-glow">%s</span>'
                      '<span><span class="block text-white font-bold">%s</span>'
                      '<span class="block text-sm text-brand-dim/85">%s</span></span></a></li>'
                      % (d['file'], svg('pin'), d['name'], d['sub']) for d in DESTS)
            + '</ul>'
            + '<div class="glass-panel rounded-2xl p-5 mt-4"><p class="text-sm text-brand-dim leading-relaxed">'
              'Meeting points and timings are confirmed by the team when you book.</p></div></div>'
            + '<div class="lg:col-span-2 h-[460px] relative rounded-3xl overflow-hidden glass-panel p-2 reveal delay-200">'
            + '<div id="diveMap"></div></div></div></section>'
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Contact Us', 'contact.html')]),
          {"@type": "ContactPage", "url": DOMAIN + "contact.html", "about": {"@id": CENTRE_ID}}]
    return shell('contact', 'contact', 24,
                 'Contact Us | Book with Dive Adda in Visakhapatnam or Rajahmundry',
                 'Contact Dive Adda to book Try Scuba, SSI courses or water activities in Visakhapatnam and Rajahmundry. Call +91 89777 62155 or message us on WhatsApp.',
                 'contact.html', body, ld, hero_img=B('boat-diving'), use_map=True)


LEGAL_UPDATED = '17 September 2026'
CONTACT_LINE = ('Call or WhatsApp <a href="tel:%s">%s</a>, or message <a href="%s" target="_blank" rel="noopener">@diveaddaindia</a> on Instagram.'
                % (PHONE_TEL, PHONE_TXT, IG))

LEGAL = [
    dict(file='privacy-policy.html', slug='privacy-policy', name='Privacy Policy',
         title='Privacy <span class="text-gradient-bio">Policy</span>',
         intro='How Dive Adda collects, uses and protects your information.',
         desc='How Dive Adda collects, uses and protects the personal information you share through our website, booking assistant and bookings.',
         sections=[
             ('Who we are', '<p>Dive Adda (&ldquo;we&rdquo;, &ldquo;us&rdquo;) operates this website and runs scuba diving, SSI training and water activities in Visakhapatnam and Rajahmundry, Andhra Pradesh, India.</p>'),
             ('Information we collect',
              '<ul>'
              '<li><b>Enquiries and bookings:</b> when you use our enquiry form or booking assistant we collect your name, phone or WhatsApp number, email address (optional), preferred location, experience or course, preferred date, number of guests and any message you write.</li>'
              '<li><b>When you contact us directly</b> by phone, WhatsApp or Instagram, we receive the information you choose to share.</li>'
              '<li><b>For your activity:</b> details needed to complete formalities before diving, which may include health information relevant to your safety (for example, a physician&rsquo;s approval for a medical condition).</li>'
              '<li><b>Photos and videos</b> taken during your experience.</li>'
              '<li><b>On your device:</b> this site remembers your light or dark theme choice and whether you have already seen the intro animation, using your browser&rsquo;s storage. This stays on your device.</li>'
              '</ul>'),
             ('How we use your information',
              '<ul><li>To respond to enquiries and confirm, manage or change bookings</li>'
              '<li>To keep you safe before, during and after your activity</li>'
              '<li>To share the photos and video from your experience with you</li>'
              '<li>To improve our services</li></ul>'
              '<p>We do not sell your personal information.</p>'),
             ('Where it is stored and who we share it with',
              '<p>Enquiries submitted through this website are stored using Google Firebase. If you choose to continue on WhatsApp, your message is handled by WhatsApp.</p>'
              '<p>This website loads fonts, maps, script libraries and some images from third-party services (such as Google Fonts, Esri map tiles and public content networks). As with any website, these services receive your IP address when your browser requests their files.</p>'
              '<p>We may disclose information where required by law.</p>'),
             ('How long we keep it', '<p>We keep personal information only for as long as it is needed for the purposes above, or as required by law.</p>'),
             ('Your choices', '<p>You can ask us to access, correct or delete the personal information we hold about you by contacting us using the details below.</p>'),
             ('Children', '<p>Some of our activities are available from 8 years of age. Bookings for guests under 18 should be made by a parent or guardian.</p>'),
             ('Changes to this policy', '<p>We may update this policy from time to time. The date at the top of this page shows when it was last updated.</p>'),
             ('Contact us', '<p>' + CONTACT_LINE + '</p>'),
         ]),
    dict(file='terms-and-conditions.html', slug='terms-and-conditions', name='Terms &amp; Conditions',
         title='Terms &amp; <span class="text-gradient-bio">Conditions</span>',
         intro='The terms that apply when you use this website or book an experience with Dive Adda.',
         desc='Terms and conditions for using the Dive Adda website and booking Try Scuba, SSI courses and water activities in Visakhapatnam and Rajahmundry.',
         sections=[
             ('About these terms', '<p>These terms apply to your use of this website and to bookings for Dive Adda experiences, including Try Scuba, SSI courses, water activities and underwater events in Visakhapatnam and Rajahmundry.</p>'),
             ('Bookings', '<p>An enquiry through this website, our booking assistant, WhatsApp or phone is a request. Your booking is confirmed only when Dive Adda confirms availability. Timings and meeting points are shared when you book.</p>'),
             ('Eligibility and health',
              '<ul><li>The minimum age for Try Scuba is 8 years.</li>'
              '<li>Guests with major medical conditions require prior written approval from a physician.</li>'
              '<li>Please share any health information relevant to your safety honestly before your activity.</li>'
              '<li>For safety reasons, our instructors may decide not to start, or to stop, an activity.</li></ul>'),
             ('Safety',
              '<ul><li>Follow the briefing and your instructor&rsquo;s instructions at all times.</li>'
              '<li>It is recommended that you do not fly within 18&ndash;24 hours after diving.</li>'
              '<li>Do not take part in any activity under the influence of alcohol or drugs.</li></ul>'),
             ('Weather and sea conditions', '<p>The itinerary may change depending on sea and local weather conditions. If conditions are unsuitable, your activity may be postponed according to your availability. If postponement is not possible, the amount will be refunded after deducting the cost of activities already undertaken.</p>'),
             ('Cancellations and refunds', '<p>Cancellations and refunds are covered by our <a href="refund-policy.html">Refund Policy</a>.</p>'),
             ('Transport and accommodation', '<p>Guests need to arrange their own transportation and accommodation.</p>'),
             ('What to bring', '<p>Please bring a cap, change of clothes and towel. We recommend eating light before arriving.</p>'),
             ('Photos and videos', '<p>Where included in your experience, your photos and video are transferred to you at the centre, or shared online if that is not possible.</p>'),
             ('Participation', '<p>Scuba diving and water activities involve inherent risks. Taking part is your choice, and following the instructions of the Dive Adda team is a condition of taking part.</p>'),
             ('Website content', '<p>Information on this website is provided for general guidance. Availability and details are confirmed at the time of booking.</p>'),
             ('Governing law', '<p>These terms are governed by the laws of India.</p>'),
             ('Contact us', '<p>' + CONTACT_LINE + '</p>'),
         ]),
    dict(file='refund-policy.html', slug='refund-policy', name='Refund Policy',
         title='Refund <span class="text-gradient-bio">Policy</span>',
         intro='What happens if you cancel, or if the weather stops your activity going ahead.',
         desc='Dive Adda refund and cancellation policy: weather postponements, and refunds for cancellations made before your activity.',
         sections=[
             ('Weather and sea conditions', '<p>If weather conditions are unsuitable, your activity may be postponed according to your availability. If postponement is not possible, the amount will be refunded after deducting the cost of activities already undertaken.</p>'),
             ('If you cancel',
              '<ul><li><b>Cancellation 72 hours before the activity:</b> 50% refund.</li>'
              '<li><b>Cancellation 24&ndash;48 hours before the activity:</b> no refund.</li></ul>'
              '<p>For any other situation, please contact us before cancelling.</p>'),
             ('How to cancel', '<p>Contact us with your name, booking date and activity so we can process your cancellation.</p>'),
             ('Contact us', '<p>' + CONTACT_LINE + '</p>'),
         ]),
]


def page_legal(lp):
    blocks = ''.join('<section class="legal-block"><h2 class="font-display text-xl md:text-2xl font-bold text-white mb-3">%s</h2>%s</section>' % (h, b)
                     for h, b in lp['sections'])
    body = (page_hero('Legal', lp['title'], lp['intro'], B('cover-divers'), 2,
                      [('Home', 'index.html'), (lp['name'], None)], compact=True)
            + main_open()
            + '<article class="legal glass-panel rounded-3xl p-6 md:p-10 max-w-3xl mx-auto reveal">'
            + '<p class="text-xs uppercase tracking-[0.2em] text-brand-glow mb-8">Last updated: ' + LEGAL_UPDATED + '</p>'
            + blocks + '</article></main>')
    ld = [ld_breadcrumb([('Home', ''), (html.unescape(lp['name']), lp['file'])])]
    return shell(lp['slug'], 'legal', 2, '%s | Dive Adda' % lp['name'], lp['desc'], lp['file'], body, ld, hero_img=B('cover-divers'))


# ---------------------------------------------------------------- write
def write(name, content):
    path = os.path.join(ROOT, name)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  %-22s %7.1f KB' % (name, len(content) / 1024.0))


_VERSIONS = {}


def asset(path):
    """Asset URL with a content hash, so a deploy never serves stale CSS/JS."""
    v = _VERSIONS.get(path)
    return '%s?v=%s' % (path, v) if v else path


def hash_assets():
    for rel in ['assets/css/dive-adda.css', 'assets/css/dive-adda-pages.css', 'assets/css/tailwind.css',
                'assets/css/dive-adda-responsive.css', 'assets/js/dive-adda.js', 'assets/js/dive-adda-pages.js']:
        full = os.path.join(ROOT, rel)
        if os.path.exists(full):
            _VERSIONS[rel] = hashlib.sha1(open(full, 'rb').read()).hexdigest()[:10]


def build_tailwind():
    """Compile only the utilities the pages use (replaces the in-browser Play CDN)."""
    npx = shutil.which('npx') or shutil.which('npx.cmd')
    if not npx:
        print('  !! npx not found: assets/css/tailwind.css was NOT rebuilt')
        return
    cmd = [npx, '--yes', 'tailwindcss@3.4.17', '-c', 'tools/tailwind/tailwind.config.js',
           '-i', 'tools/tailwind/input.css', '-o', 'assets/css/tailwind.css', '--minify']
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('Tailwind build failed:\n' + r.stderr)
    print('  %-22s %7.1f KB' % ('assets/css/tailwind.css', os.path.getsize(os.path.join(ROOT, 'assets/css/tailwind.css')) / 1024.0))


def main():
    print('Building Dive Adda...')
    _live_reviews()
    # Pass 1 writes the pages Tailwind scans; pass 2 rewrites them with final asset hashes.
    write_pages()
    build_tailwind()
    hash_assets()
    write_pages()
    print('Done.')


OBSOLETE = ['diving.html', 'water-sports.html', 'vizag.html', 'goa.html', 'first-time-scuba.html']


def write_pages():
    pages = [('index.html', page_home), ('about.html', page_about),
             ('beginner-level-scuba.html', page_first_time_scuba), ('courses.html', page_courses)]
    pages += [(c['file'], (lambda c=c: page_course(c))) for c in COURSES]
    pages += [(d['file'], (lambda d=d: page_destination(d))) for d in DESTS]
    pages += [('blog.html', page_blog)]
    pages += [(p['file'], (lambda p=p: page_post(p))) for p in POSTS]
    pages += [('gallery.html', page_gallery), ('events.html', page_events),
              ('faq.html', page_faq), ('contact.html', page_contact)]
    pages += [(lp['file'], (lambda lp=lp: page_legal(lp))) for lp in LEGAL]
    for name, fn in pages:
        write(name, fn())

    # Pages the site no longer has
    for old in OBSOLETE:
        path = os.path.join(ROOT, old)
        if os.path.exists(path):
            os.remove(path)
            print('  removed %s' % old)

    today = '2026-09-17'
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name, _ in pages:
        loc = '' if name == 'index.html' else name
        sm.append('  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n  </url>' % (DOMAIN, loc, today))
    sm.append('</urlset>')
    write('sitemap.xml', '\n'.join(sm) + '\n')
    write('robots.txt', 'User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: %ssitemap.xml\n' % DOMAIN)


if __name__ == '__main__':
    main()
