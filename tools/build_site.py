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
import html
import json
import os
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


def photo(src, alt, cls='', sizes='100vw', lazy=True, extra=''):
    """An <img>, with a responsive srcset when the source is an Unsplash id."""
    if src.startswith('uns:'):
        pid = src[4:]
        return ('<img src="%s" srcset="%s" sizes="%s" alt="%s" class="%s" %s %s decoding="async">'
                % (U(pid), uset(pid), sizes, E(alt), cls, 'loading="lazy"' if lazy else 'fetchpriority="high"', extra))
    return ('<img src="%s" alt="%s" class="%s" %s %s decoding="async">'
            % (src, E(alt), cls, 'loading="lazy"' if lazy else 'fetchpriority="high"', extra))


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
    dict(id='vizag', name='Vizag', file='vizag.html', sub='Visakhapatnam &middot; Andhra Pradesh',
         img='assets/img/brochure/dive-centre-storefront.jpg',
         hero=B('cover-divers'),
         blurb='Our SSI certified scuba centre, on the Bay of Bengal coast. This is where first dives, SSI courses and guided fun dives begin.',
         long='Vizag &mdash; Visakhapatnam &mdash; is the coastal home of Dive Adda. Our SSI certified scuba centre runs training from confined water through to guided open water dives, for complete beginners and certified divers alike.',
         acts=['Scuba Diving', 'SSI Courses', 'Guided Fun Dives', 'Snorkelling', 'Boat Diving', 'Shore Diving', 'Confined Diving', 'Underwater Events']),
    dict(id='rajahmundry', name='Rajahmundry', file='rajahmundry.html', sub='Andhra Pradesh',
         img='uns:1583212292454-1fe6229603b7',
         hero='uns:1583212292454-1fe6229603b7',
         blurb='Scuba diving and water sports with the Dive Adda team, on the banks of the Godavari.',
         long='Rajahmundry sits on the Godavari in Andhra Pradesh. Dive Adda brings scuba diving and water sport experiences here, guided by the same instructors who teach at our centre.',
         acts=['Scuba Diving', 'Water Sports']),
    dict(id='goa', name='Goa', file='goa.html', sub='West coast of India',
         img='uns:1546026423-cc4642628d2b',
         hero='uns:1546026423-cc4642628d2b',
         blurb='Scuba diving and water sports on India&rsquo;s west coast, along the Arabian Sea.',
         long='Goa faces the Arabian Sea on India&rsquo;s west coast. Dive Adda runs scuba diving and water sport experiences here for first-timers and certified divers.',
         acts=['Scuba Diving', 'Water Sports']),
]

COURSES = [
    dict(id='open-water', name='Open Water', full='SSI Open Water Diver', level='Beginner', step='01',
         img=B('ssi-pool-training'),
         short='The entry-level SSI certification &mdash; your first step from confined water practice to diving in open water.',
         long='Open Water Diver is where most divers begin. You learn the essential skills in confined water with an instructor beside you, then put them to use in open water. It is an internationally recognised SSI certification.',
         learn=['Essential diving skills', 'How your equipment works', 'Safe diving practices', 'An internationally recognised SSI certification']),
    dict(id='advanced-adventurer', name='Advanced Adventurer', full='SSI Advanced Adventurer', level='Certified divers', step='02',
         img='uns:1582967788606-a171c1080cb0',
         short='Build on your training and try different types of diving with an instructor alongside you.',
         long='Advanced Adventurer is the natural next step after Open Water. You dive with an instructor across different kinds of diving, adding experience and confidence to the skills you already have.',
         learn=['Experience across different types of diving', 'More confidence in the water', 'Guided dives with an instructor', 'A foundation for further SSI training']),
    dict(id='react-right', name='React Right', full='SSI React Right', level='First aid &middot; all levels', step='03',
         img=B('confined-diving'),
         short='SSI&rsquo;s first aid and emergency response training, for divers and non-divers.',
         long='React Right is SSI&rsquo;s first aid and emergency response programme. It teaches you to recognise an emergency and respond to it calmly &mdash; skills that matter on a dive boat and on dry land.',
         learn=['Recognising an emergency', 'First aid and emergency response', 'Staying calm under pressure', 'A core part of the rescue pathway']),
    dict(id='diver-stress-rescue', name='Diver Stress &amp; Rescue', full='SSI Diver Stress &amp; Rescue', level='Continuing education', step='04',
         img='uns:1530053969600-caed2596d242',
         short='Learn to spot stress early, prevent problems, and help another diver when something goes wrong.',
         long='Stress is behind most diving incidents. This programme teaches you to recognise it in yourself and your buddy, prevent problems before they escalate, and manage a rescue if one is needed.',
         learn=['Recognising stress in yourself and others', 'Preventing problems before they grow', 'Rescue skills and techniques', 'Diving with greater awareness']),
    dict(id='dive-master', name='Dive Master', full='SSI Divemaster', level='Professional', step='05',
         img=B('guided-fun-dive'),
         short='The first professional level &mdash; for divers who want to guide, assist and build a career in diving.',
         long='Dive Master is the first professional rating in the SSI pathway. It is for experienced divers who want to guide certified divers, assist instructors, and take diving from a hobby to a career.',
         learn=['Guiding certified divers', 'Assisting instructors', 'Dive leadership and planning', 'The start of a career in diving']),
]

ACTIVITIES = [
    dict(id='boat-diving', name='Boat Diving', n='01', img=B('boat-diving'),
         text='Boat diving offers easy access to deeper dive sites, stunning marine life, and unforgettable underwater adventures.'),
    dict(id='shore-diving', name='Shore Diving', n='02', img=B('shore-diving'),
         text='Shore diving is an easy, accessible dive from the beach, offering stunning underwater exploration.'),
    dict(id='confined-diving', name='Confined Diving', n='03', img=B('confined-diving'),
         text='Confined diving is training in a controlled water environment, like a pool, ensuring safety and skill development.'),
]

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

EXPERIENCES = [
    dict(name='Scuba Diving', href='diving.html#scuba-diving', img='uns:1544551763-46a013bb70d5',
         desc='Breathe underwater and explore the marine world with a Dive Adda instructor beside you.',
         chip='For everyone', chipcls='chip-coral', big=True, exp='Scuba Diving (first dive)'),
    dict(name='SSI Courses', href='courses.html', img=B('ssi-pool-training'),
         desc='Certification from beginner to professional level.', chip='Certification', chipcls='chip-cyan', exp='SSI Course'),
    dict(name='Guided Fun Dives', href='diving.html#fun-dives', img=B('guided-fun-dive'),
         desc='Safe, exciting dives with expert instructors.', chip='Guided', chipcls='chip', exp='Guided Fun Dive'),
    dict(name='Snorkelling', href='water-sports.html#snorkelling', img=B('snorkelling'), wide=True,
         desc='Explore underwater life effortlessly, floating with a mask, snorkel and fins. No certification needed.',
         chip='No certification needed', chipcls='chip', exp='Snorkelling'),
    dict(name='Boat Diving', href='diving.html#boat-diving', img=B('boat-diving'),
         desc='Easy access to deeper dive sites.', chip='Activity', chipcls='chip', exp='Boat Diving'),
    dict(name='Shore Diving', href='diving.html#shore-diving', img=B('shore-diving'),
         desc='An easy, accessible dive from the beach.', chip='Activity', chipcls='chip', exp='Shore Diving'),
    dict(name='Confined Diving', href='diving.html#confined-diving', img=B('confined-diving'),
         desc='Skills training in controlled water.', chip='Training', chipcls='chip', exp='Confined Diving'),
    dict(name='Underwater Events', href='events.html', img=B('event-prewedding'), wide=True,
         desc='Birthdays, proposals, pre-wedding shoots and conservation dives &mdash; planned with our team.',
         chip='Signature', chipcls='chip-violet', exp='Underwater Event'),
]

WHY = [
    ('shield', 'SSI Certified', 'An internationally certified dive centre, proudly affiliated with SSI, so our training meets the highest global standards.'),
    ('people', 'Professional Guidance', 'A team of expert instructors with over 15 years of industry experience between them.'),
    ('heart', 'Safety First', 'Top-notch safety and expert guidance on every experience we run &mdash; it is the core of how we dive.'),
    ('spark', 'Beginner Friendly', 'Whether it is your first breath underwater or your hundredth dive, there is a way in for you.'),
    ('cap', 'Dive Training', 'Courses from beginner through to professional level, for divers who want to go further.'),
    ('globe', 'Underwater Adventure', 'Fun dives, snorkelling, boat and shore diving, outbound trips and underwater events.'),
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

JOURNEY = [
    ('01', 'Meet your instructor', 'You are introduced to the SSI professional who stays with you from the first briefing to the last bubble.'),
    ('02', 'Safety briefing', 'How the dive works, the signals you will use, and what happens at every stage. Questions welcome.'),
    ('03', 'Learn the equipment', 'Your mask, fins and breathing apparatus &mdash; what each part does and how it feels.'),
    ('04', 'Practice', 'Skills first, in controlled water, until breathing underwater feels ordinary.'),
    ('05', 'Enter the water', 'From shore or boat, with your instructor beside you the whole way down.'),
    ('06', 'Discover the underwater world', 'Weightless, quiet, and face to face with marine life in its own habitat.'),
]

GALLERY = [
    (B('cover-divers'), 'diving', 'Divers over the reef', 'Dive, Discover, Repeat', 'g-wide g-tall'),
    (B('ssi-pool-training'), 'courses', 'SSI training session', 'Skills in confined water', 'g-tall'),
    (B('guided-fun-dive'), 'diving', 'Guided fun dive', 'With a Dive Adda instructor', ''),
    (B('snorkelling'), 'snorkelling', 'Snorkelling', 'Mask, snorkel and fins', ''),
    (B('dive-centre-storefront'), 'destinations', 'The Dive Adda centre', 'Scuba dive centre', 'g-tall'),
    (B('boat-diving'), 'boat', 'Boat diving', 'Entry from the boat', 'g-wide'),
    (B('confined-diving'), 'courses', 'Confined water training', 'Controlled environment', ''),
    (B('shore-diving'), 'diving', 'Shore diving', 'Walking in from the beach', ''),
    (B('outbound-trip'), 'destinations', 'Outbound trip', 'Diving together', 'g-wide'),
    (B('event-birthday'), 'events', 'Underwater birthday', 'Celebrating below the surface', ''),
    (B('event-proposal'), 'events', 'Underwater proposal', 'The question, underwater', ''),
    (B('event-prewedding'), 'events', 'Pre-wedding shoot', 'Underwater portraits', ''),
    (B('event-conservation'), 'events', 'Conservation dive', 'Waste recovered from the water', ''),
]

GALLERY_FILTERS = [('all', 'All'), ('diving', 'Diving'), ('courses', 'Courses'), ('snorkelling', 'Snorkelling'),
                   ('boat', 'Boat Diving'), ('events', 'Underwater Events'), ('destinations', 'Destinations')]

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

FAQS = [
    ('Do I need diving experience?',
     'No. Dive Adda trains divers at every level, from beginners taking their first breath underwater through to advanced divers and professionals. If it is your first time, an instructor stays with you from the briefing to the end of the dive.'),
    ('What is scuba diving?',
     'Scuba diving is an underwater adventure that allows you to explore the marine world using a Self-Contained Underwater Breathing Apparatus (SCUBA). It enables divers to breathe underwater and move freely while exploring coral reefs, shipwrecks and marine life. It is both a recreational and a professional activity, with applications in marine research, underwater photography, rescue operations and even archaeology.'),
    ('What happens during a first dive?',
     'You meet your instructor and get a full safety briefing, learn how the equipment works, and practise the core skills in controlled water. Only then do you enter the water &mdash; with your instructor beside you the whole way &mdash; to discover the underwater world.'),
    ('What courses are available?',
     'Dive Adda runs SSI certified courses from beginner to professional level: Open Water, Advanced Adventurer, React Right, Diver Stress &amp; Rescue and Dive Master.'),
    ('What equipment is provided?',
     'Scuba diving uses a Self-Contained Underwater Breathing Apparatus; snorkelling uses a mask, snorkel and fins. Exactly what is included depends on the experience you book &mdash; the dive desk confirms it with you before your dive.'),
    ('How do I book?',
     'Use the booking assistant on this site, send an enquiry through the contact form, message us on WhatsApp, or call the dive desk on %s. We confirm availability for your date and take it from there.' % PHONE_TXT),
    ('Where are Dive Adda experiences available?',
     'Our SSI certified scuba centre is in Vizag (Visakhapatnam), and we run scuba diving and water sport experiences in Rajahmundry and Goa.'),
    ('Is Dive Adda SSI certified?',
     'Yes. Dive Adda is an internationally certified dive centre, proudly affiliated with SSI (Scuba Schools International), which means our training programmes meet the highest global standards.'),
]

NAV = [
    ('home', 'Home', 'index.html', None),
    ('diving', 'Diving', 'diving.html', [('All Diving', 'diving.html')] + [('Scuba Diving', 'diving.html#scuba-diving'), ('Guided Fun Dives', 'diving.html#fun-dives'), ('Boat Diving', 'diving.html#boat-diving'), ('Shore Diving', 'diving.html#shore-diving'), ('Confined Diving', 'diving.html#confined-diving')]),
    ('courses', 'Courses', 'courses.html', [('All Courses', 'courses.html')] + [(c['name'], 'courses.html#' + c['id']) for c in COURSES]),
    ('water-sports', 'Water Sports', 'water-sports.html', None),
    ('destinations', 'Destinations', 'index.html#destinations', [('All Destinations', 'index.html#destinations')] + [(d['name'], d['file']) for d in DESTS]),
    ('events', 'Events', 'events.html', [('All Events', 'events.html')] + [(e['name'], 'events.html#' + e['id']) for e in EVENTS]),
    ('gallery', 'Gallery', 'gallery.html', None),
    ('about', 'About', 'about.html', None),
    ('faq', 'FAQ', 'faq.html', None),
    ('contact', 'Contact', 'contact.html', None),
]


# ---------------------------------------------------------------- chrome
def city_bar(page):
    chips = ''.join(
        '<a href="%s" class="city-chip%s" data-city="%s"><span class="pin"></span>%s</a>'
        % (d['file'], ' is-current' if page == d['id'] else '', d['id'], d['name']) for d in DESTS)
    return ('''    <div class="city-bar">
      <div class="cities">
        <span class="hidden sm:inline text-[9.5px] font-bold uppercase tracking-[0.28em] text-brand-glow/70 mr-1 shrink-0">Dive with us in</span>
        ''' + chips + '''
      </div>
      <div class="bar-meta">
        <span class="inline-flex items-center gap-2 font-semibold tracking-wide"><img src="assets/img/ssi-dive-center.png" alt="" class="w-5 h-5" loading="lazy"> SSI Certified Dive Centre</span>
        <a href="tel:''' + PHONE_TEL + '''" class="inline-flex items-center gap-1.5">''' + svg('phone', 'w-3.5 h-3.5') + PHONE_TXT + '''</a>
      </div>
    </div>''')


def nav(page, section):
    desktop = []
    mobile = []
    for key, label, href, children in NAV:
        active = ' is-active' if section == key else ''
        aria = ' aria-current="page"' if section == key else ''
        if children:
            drop = ''.join('<a href="%s"><span class="dot"></span>%s</a>' % (h, l) for l, h in children)
            desktop.append(
                '<div class="nav-item"><button type="button" class="nav-link%s" aria-expanded="false" aria-haspopup="true">%s'
                '<svg class="caret" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7"></path></svg>'
                '</button><div class="nav-drop glass-deep theme-scope"><span class="drop-title">%s</span>%s</div></div>'
                % (active, label, 'Underwater Events' if key == 'events' else label, drop))
            mobile.append(
                '<details class="m-group"><summary>%s<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7"></path></svg></summary>'
                '<div class="m-links">%s</div></details>'
                % (label, ''.join('<a href="%s">%s</a>' % (h, l) for l, h in children)))
        else:
            desktop.append('<a href="%s" class="nav-link%s"%s>%s</a>' % (href, active, aria, label))
            mobile.append('<a href="%s" class="m-link">%s</a>' % (href, label))

    return '''    <nav id="navbar" class="pre-dive post-dive-in fixed w-full z-50 transition-all duration-500 py-4 px-4 sm:px-6 md:px-12 top-0">
''' + city_bar(page) + '''
      <div id="navPill" class="glass-deep theme-scope relative max-w-7xl mx-auto flex justify-between items-center px-5 py-3 rounded-2xl transition-all duration-500">

        <a href="index.html" class="flex items-center gap-3 group shrink-0" aria-label="Dive Adda — home">
          <img src="assets/img/logo-mark-light.png" alt="" class="brand-mark logo-light" width="56" height="38">
          <img src="assets/img/logo-mark.png" alt="" class="brand-mark logo-dark" width="56" height="38">
          <span class="leading-none">
            <span class="brand-word block text-[19px] text-white">DIVE ADDA</span>
            <span class="brand-tag block mt-1">Discover &mdash; The Deep</span>
          </span>
        </a>

        <div class="hidden xl:flex items-center gap-5 font-medium text-[13px]">
          ''' + '\n          '.join(desktop) + '''
          <button type="button" data-book class="btn-bio liquid ripple-host px-5 py-2.5 rounded-full font-semibold text-[13px] whitespace-nowrap">Book Now</button>
        </div>

        <div class="flex items-center gap-3 xl:ml-4">
          <button id="themeToggle" class="theme-toggle" type="button" role="switch" aria-checked="false" aria-label="Switch between dark and light theme" title="Switch theme">
            <span class="knob">
              <svg class="ic ic-moon" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
              <svg class="ic ic-sun" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17a5 5 0 100-10 5 5 0 000 10zm0 2.5a1 1 0 011 1V22a1 1 0 11-2 0v-1.5a1 1 0 011-1zm0-19a1 1 0 011 1V3a1 1 0 11-2 0V1.5a1 1 0 011-1zM3.5 11h1.5a1 1 0 110 2H3.5a1 1 0 110-2zm15.5 0h1.5a1 1 0 110 2H19a1 1 0 110-2zM5.6 4.2l1.1 1.1a1 1 0 11-1.4 1.4L4.2 5.6a1 1 0 011.4-1.4zm11.7 11.7l1.1 1.1a1 1 0 11-1.4 1.4l-1.1-1.1a1 1 0 011.4-1.4zM18.4 4.2a1 1 0 011.4 1.4l-1.1 1.1a1 1 0 11-1.4-1.4zM6.7 15.9a1 1 0 011.4 1.4l-1.1 1.1a1 1 0 11-1.4-1.4z"/></svg>
            </span>
          </button>
          <button id="mobileMenuBtn" class="xl:hidden text-brand-glow focus:outline-none p-1" aria-label="Toggle navigation" aria-expanded="false" aria-controls="mobileMenu">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
          </button>
        </div>

        <div id="mobileMenu" class="glass-deep theme-scope absolute top-full mt-3 left-0 right-0 hidden flex-col p-6 rounded-2xl transform origin-top transition-all">
          ''' + '\n          '.join(mobile) + '''
          <button type="button" data-book class="btn-bio liquid ripple-host w-full mt-4 px-6 py-3 rounded-full font-bold">Book Now</button>
        </div>
      </div>
    </nav>
'''


def float_widgets():
    return '''    <a href="''' + wa_link("Hi Dive Adda! I'd like to ask about diving with you.") + '''"
       target="_blank" rel="noopener"
       class="pre-dive post-dive-in float-widget fixed bottom-6 left-6 z-[90] w-14 h-14 rounded-full text-white flex items-center justify-center group liquid ripple-host animate-float bg-[#128C4A]/90 border border-[#4ade80]/35 shadow-[0_14px_36px_-10px_rgba(37,211,102,0.55)] hover:shadow-[0_18px_46px_-8px_rgba(37,211,102,0.85)] backdrop-blur-md"
       aria-label="Chat with Dive Adda on WhatsApp">
        <span class="absolute inset-0 rounded-full bg-[#25D366]/30 blur-lg bio-pulse" style="--dur:5s" aria-hidden="true"></span>
        <svg class="relative w-7 h-7 drop-shadow-md" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
        </svg>
        <span class="absolute left-[68px] glass-deep text-brand-ink px-3 py-1.5 rounded-xl text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap pointer-events-none">Chat on WhatsApp</span>
    </a>

    <div id="callRail" class="pre-dive post-dive-in theme-scope" aria-label="Quick contact">
        <a href="tel:''' + PHONE_TEL + '''" class="call-pill glass-deep" aria-label="Call the Dive Adda dive desk on ''' + PHONE_TXT + '''" title="Dive desk: ''' + PHONE_TXT + '''">
            <span class="call-ic">''' + svg('phone', 'w-4 h-4') + '''</span>
            <span class="call-text">
                <span class="block text-[9px] uppercase tracking-[0.22em] text-brand-glow">Dive desk</span>
                <span class="block text-sm font-bold text-white leading-tight">''' + PHONE_TXT + '''</span>
            </span>
        </a>
        <button type="button" data-book class="group ripple-host glass-deep border-r-0 rounded-l-2xl py-6 px-2 md:px-3 flex flex-col items-center gap-3 text-brand-ink transition-all duration-500 hover:pr-4 hover:shadow-[-10px_0_40px_-8px_rgba(34,211,238,0.55)]">
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
    explore = [('Scuba Diving', 'diving.html#scuba-diving'), ('SSI Courses', 'courses.html'),
               ('Water Sports', 'water-sports.html'), ('Underwater Events', 'events.html'),
               ('Gallery', 'gallery.html'), ('About Us', 'about.html'), ('FAQ', 'faq.html')]
    return '''    <footer class="theme-scope relative py-14 px-6 md:px-12 border-t border-white/[0.06] bg-brand-abyss/70 backdrop-blur-xl overflow-hidden">
        <div class="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-brand-accent/45 to-transparent" aria-hidden="true"></div>
        <div class="absolute inset-0 pointer-events-none" aria-hidden="true" style="background: radial-gradient(70% 80% at 50% 120%, rgba(34,211,238,0.10), transparent 65%);"></div>

        <div class="relative max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div class="md:col-span-1">
                <a href="index.html" class="inline-block mb-5" aria-label="Dive Adda — home">
                    <img src="assets/img/logo-full-light.png" alt="Dive Adda — Discover the Deep" class="logo-light w-[168px] h-auto" width="168" height="138" loading="lazy">
                    <img src="assets/img/logo-full.png" alt="Dive Adda — Discover the Deep" class="logo-dark w-[168px] h-auto" width="168" height="138" loading="lazy">
                </a>
                <p class="text-sm text-brand-dim/80 mb-5 leading-relaxed">An internationally certified dive centre, proudly affiliated with SSI. Safe, exciting and unforgettable diving experiences &mdash; for your first breath underwater and every dive after it.</p>
                <div class="flex items-center gap-4 mb-5">
                    <img src="assets/img/ssi-dive-center.png" alt="SSI Official Partner Dive Center" class="w-16 h-16" loading="lazy" width="64" height="64">
                    <span class="text-[11px] uppercase tracking-[0.2em] text-brand-glow/80 font-bold leading-relaxed">SSI Certified<br>Dive Centre</span>
                </div>
                <div class="flex gap-3">
                    <a href="''' + IG + '''" target="_blank" rel="noopener" aria-label="Dive Adda on Instagram" class="w-9 h-9 rounded-xl flex items-center justify-center text-brand-dim bg-white/[0.04] border border-white/[0.08] hover:text-brand-violet hover:border-brand-violet/45 hover:shadow-[0_0_22px_-6px_rgba(167,139,250,0.7)] transition-all duration-500">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                    </a>
                    <a href="''' + FB + '''" target="_blank" rel="noopener" aria-label="Dive Adda on Facebook" class="w-9 h-9 rounded-xl flex items-center justify-center text-brand-dim bg-white/[0.04] border border-white/[0.08] hover:text-brand-glow hover:border-brand-accent/45 hover:shadow-[0_0_22px_-6px_rgba(34,211,238,0.7)] transition-all duration-500">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M22 12a10 10 0 10-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0022 12z"/></svg>
                    </a>
                </div>
            </div>

            <div>
                <h4 class="font-bold text-white mb-4 text-sm uppercase tracking-[0.16em]">Explore</h4>
                <ul class="space-y-2.5 text-sm text-brand-dim/80">
                    ''' + ''.join('<li><a href="%s" class="hover:text-brand-glow transition-colors">%s</a></li>' % (h, l) for l, h in explore) + '''
                </ul>
            </div>

            <div>
                <h4 class="font-bold text-white mb-4 text-sm uppercase tracking-[0.16em]">Destinations</h4>
                <ul class="space-y-2.5 text-sm text-brand-dim/80">
                    ''' + ''.join('<li><a href="%s" class="hover:text-brand-glow transition-colors">%s</a></li>' % (d['file'], d['name']) for d in DESTS) + '''
                </ul>
                <h4 class="font-bold text-white mb-3 mt-7 text-sm uppercase tracking-[0.16em]">Courses</h4>
                <ul class="space-y-2.5 text-sm text-brand-dim/80">
                    ''' + ''.join('<li><a href="courses.html#%s" class="hover:text-brand-glow transition-colors">%s</a></li>' % (c['id'], c['name']) for c in COURSES) + '''
                </ul>
            </div>

            <div>
                <h4 class="font-bold text-white mb-4 text-sm uppercase tracking-[0.16em]">Contact</h4>
                <ul class="space-y-3 text-sm text-brand-dim/80">
                    <li><a href="tel:''' + PHONE_TEL + '''" class="inline-flex items-center gap-2 hover:text-brand-glow transition-colors">''' + svg('phone', 'w-4 h-4') + PHONE_TXT + '''</a></li>
                    <li><a href="''' + wa_link('Hi Dive Adda!') + '''" target="_blank" rel="noopener" class="inline-flex items-center gap-2 hover:text-brand-glow transition-colors">''' + svg('chat', 'w-4 h-4') + '''WhatsApp</a></li>
                    <li><a href="''' + IG + '''" target="_blank" rel="noopener" class="hover:text-brand-glow transition-colors">@diveaddaindia</a></li>
                    <li>www.diveaddaindia.com</li>
                    <li class="pt-1"><span class="chip-cyan px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.14em]">Booking open</span></li>
                </ul>
                <button type="button" data-book class="btn-bio liquid ripple-host mt-6 px-6 py-3 rounded-full font-display font-bold text-sm w-full">Book Your Dive</button>
            </div>
        </div>
        <div class="relative max-w-7xl mx-auto text-center text-brand-dim/45 text-xs pt-8 border-t border-white/[0.06]">
            &copy; <span data-year>2026</span> Dive Adda &mdash; Discover the Deep. All rights reserved.
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
                    <li class="flex items-center gap-3 text-brand-ink"><span class="w-1.5 h-1.5 rounded-full bg-brand-accent shadow-[0_0_10px_#22D3EE]"></span>Vizag, Rajahmundry and Goa</li>
                </ul>
                <div class="flex flex-col sm:flex-row gap-3">
                    <button type="button" id="bookModalGo" class="btn-bio liquid ripple-host flex-1 px-6 py-3.5 rounded-full font-display font-bold tracking-wide">Book Now</button>
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
        "description": "Dive Adda is an internationally certified scuba diving centre affiliated with SSI, running SSI courses, guided fun dives, snorkelling and underwater events.",
        "telephone": PHONE_TEL,
        "logo": {"@type": "ImageObject", "url": DOMAIN + "assets/img/logo-full.png"},
        "sameAs": [IG, FB],
    }


def ld_centre():
    return {
        "@type": ["LocalBusiness", "SportsActivityLocation"],
        "@id": CENTRE_ID,
        "name": "Dive Adda — SSI Certified Scuba Centre",
        "url": DOMAIN,
        "description": "SSI certified scuba diving centre in Vizag offering SSI courses, guided fun dives, snorkelling, boat, shore and confined diving, and underwater events.",
        "telephone": PHONE_TEL,
        "address": {"@type": "PostalAddress", "addressLocality": "Visakhapatnam", "addressRegion": "Andhra Pradesh", "addressCountry": "IN"},
        "areaServed": [{"@type": "City", "name": n} for n in ("Visakhapatnam", "Rajahmundry", "Goa")],
        "image": [DOMAIN + B('cover-divers'), DOMAIN + B('ssi-pool-training'), DOMAIN + B('guided-fun-dive')],
        "parentOrganization": {"@id": ORG_ID},
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "serviceType": t}}
            for n, t in [("Scuba Diving", "Guided scuba diving"), ("SSI Courses", "Scuba certification course"),
                         ("Guided Fun Dives", "Guided scuba diving"), ("Snorkelling", "Guided snorkelling"),
                         ("Boat Diving", "Guided scuba diving"), ("Shore Diving", "Guided scuba diving"),
                         ("Confined Diving", "Scuba skills training"), ("Underwater Events", "Underwater event")]
        ],
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
            "areaServed": [{"@type": "City", "name": n} for n in ("Visakhapatnam", "Rajahmundry", "Goa")]}


def ld_course(c):
    return {"@type": "Course", "name": html.unescape(c['full']),
            "description": html.unescape(c['long']),
            "provider": {"@id": ORG_ID},
            "educationalCredentialAwarded": "SSI certification",
            "url": DOMAIN + "courses.html#" + c['id'],
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "onsite",
                                  "location": {"@id": CENTRE_ID}}}


# ---------------------------------------------------------------- shell
def shell(page, section, depth, title, desc, path, body, ld, hero_img=None,
          use_map=False, book_modal=False, lightbox=False, profile=False, span=18):
    graph = [ld_org(), ld_centre()] + ld
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    preload = ('    <link rel="preload" as="image" fetchpriority="high" href="%s">\n' % src_of(hero_img)) if hero_img else ''
    leaflet_css = '    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>\n' if use_map else ''
    leaflet_js = '    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>\n' if use_map else ''
    og_img = DOMAIN + B('cover-divers')

    return '''<!DOCTYPE html>
<html lang="en" class="scroll-smooth gate-open">
<head>
    <meta charset="UTF-8">

    <script>
        /* Applied before the first paint so the page never flashes the wrong
           theme. Dark is the brand default; light is opt-in and remembered. */
        (function () {
            var t = 'dark';
            try { if (localStorage.getItem('db-theme') === 'light') t = 'light'; } catch (e) {}
            document.documentElement.setAttribute('data-theme', t);
        })();
    </script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark">
    <title>''' + title + '''</title>

    <meta name="description" content="''' + E(desc) + '''">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta name="author" content="Dive Adda">
    <meta name="theme-color" content="#04121F" media="(prefers-color-scheme: dark)">
    <meta name="theme-color" content="#F3FAFC" media="(prefers-color-scheme: light)">
    <link rel="canonical" href="''' + DOMAIN + path + '''">
    <link rel="icon" href="assets/img/logo-mark.png" type="image/png">
    <link rel="apple-touch-icon" href="assets/img/logo-mark.png">

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

''' + preload + '''    <script src="https://cdn.tailwindcss.com"></script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">

''' + leaflet_css + '''    <link rel="stylesheet" href="assets/css/dive-adda.css">
    <link rel="stylesheet" href="assets/css/dive-adda-pages.css">

''' + FIREBASE + '''

''' + TWCONFIG + '''

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
    <script src="assets/js/dive-adda.js"></script>
    <script src="assets/js/dive-adda-pages.js"></script>
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


def page_hero(eyebrow, title, desc, img, depth, crumbs, ghost=None, ctas='', extra=''):
    crumb = ' <span class="opacity-40">/</span> '.join(
        ['<a href="%s">%s</a>' % (h, n) if h else '<span class="text-white/80">%s</span>' % n for n, h in crumbs])
    return '''    <header class="page-hero">
        ''' + photo(img, '', 'ph-img', '100vw', lazy=False) + '''
        <div class="ph-shade"></div>
        <div class="ph-glow"></div>
        ''' + ('<span class="city-ghost" aria-hidden="true">%s</span>' % ghost if ghost else '') + '''
        <div class="ph-inner reveal active">
            <nav class="crumbs mb-7" aria-label="Breadcrumb">''' + crumb + '''</nav>
            <div class="flex flex-wrap items-center gap-3 mb-5">
                <span class="chip-cyan rounded-full px-4 py-1.5 font-bold tracking-[0.22em] uppercase text-[10px]">''' + eyebrow + '''</span>
                <span class="chip depth-chip rounded-full px-3.5 py-1.5 text-[10px] font-bold tracking-[0.18em] uppercase">&minus;''' + str(depth) + ''' m</span>
            </div>
            <h1 class="ph-title font-display font-bold text-white heading-glow mb-6">''' + title + '''</h1>
            <p class="text-lg md:text-xl text-brand-ink/85 max-w-2xl leading-relaxed">''' + desc + '''</p>
            ''' + ctas + extra + '''
        </div>
    </header>
'''


def hero_ctas(primary='Book Your Dive', experience='', destination=''):
    return ('<div class="flex flex-col sm:flex-row gap-4 mt-9 w-full sm:w-auto">'
            '<button type="button" data-book data-experience="%s" data-destination="%s" class="btn-bio liquid liquid-strong ripple-host px-8 py-4 rounded-full font-display font-bold text-lg">%s</button>'
            '<a href="contact.html#enquire" class="btn-ghost liquid ripple-host px-8 py-4 rounded-full font-bold text-lg flex items-center justify-center gap-2.5">Send an enquiry %s</a>'
            '</div>' % (experience, destination, primary, svg('arrow', 'w-4 h-4 text-brand-glow')))


def bento(e, delay=''):
    span = 'md:col-span-2 md:row-span-2' if e.get('big') else ('md:col-span-2' if e.get('wide') else '')
    title_size = 'text-3xl' if e.get('big') else 'text-xl'
    return ('<a href="%s" class="group relative %s rounded-3xl overflow-hidden bento-card on-media liquid %s glow-hover bio-edge isolate reveal %s block">'
            '%s'
            '<div class="absolute inset-0 duotone"></div>'
            '<div class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/55 to-transparent"></div>'
            '<div class="absolute inset-0 p-6 md:p-7 flex flex-col justify-end transform transition-transform duration-700 group-hover:translate-y-[-8px] z-[4]">'
            '<span class="%s w-fit px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.14em] mb-3">%s</span>'
            '<h3 class="font-display %s font-bold text-white mb-2">%s</h3>'
            '<p class="text-brand-ink/75 text-sm max-w-md">%s</p>'
            '<span class="mt-4 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.2em] text-brand-glow">Explore %s</span>'
            '</div></a>'
            % (e['href'], span, 'liquid-strong' if e.get('big') else '', delay,
               photo(e['img'], e['name'], 'absolute inset-0 w-full h-full object-cover bento-image',
                     '(max-width: 767px) 100vw, 50vw' if e.get('big') or e.get('wide') else '(max-width: 767px) 100vw, 25vw'),
               e['chipcls'], e['chip'], title_size, e['name'], e['desc'],
               svg('arrow', 'w-3.5 h-3.5 group-hover:translate-x-1 transition-transform duration-500')))


def experiences_section():
    cards = ''.join(bento(e, ['', 'delay-100', 'delay-200', 'delay-300'][i % 4]) for i, e in enumerate(EXPERIENCES))
    return ('<section id="experiences" class="mb-32">'
            + sec_head('01', 'Experiences', 'Select your adventure',
                       'From your first breath underwater to professional training, every Dive Adda experience is guided by SSI certified instructors.',
                       ('See all courses', 'courses.html'))
            + '<div class="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-4 gap-6 auto-rows-[250px]">' + cards + '</div></section>')


def why_section():
    cards = ''.join(
        '<div class="trust-card glass-panel bio-edge reveal %s">'
        '<span class="trust-ic bg-brand-accent/12 border border-brand-accent/30 text-brand-glow shadow-[0_0_26px_-8px_rgba(34,211,238,0.8)] mb-5">%s</span>'
        '<h3 class="font-display text-xl font-bold text-white mb-2">%s</h3>'
        '<p class="text-brand-dim text-sm leading-relaxed">%s</p></div>'
        % (['', 'delay-100', 'delay-200'][i % 3], svg(ic, 'w-6 h-6'), t, d)
        for i, (ic, t, d) in enumerate(WHY))
    return ('<section id="why" class="mb-32">'
            + sec_head('02', 'Why Dive Adda', 'Trust, training and the deep',
                       'Everything we claim here comes from how we actually run the centre.', center=True)
            + '<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">' + cards + '</div></section>')


def story_section():
    return '''<section id="story" class="mb-32">
        ''' + sec_head('03', 'Our Story', 'Rooted in the world beneath the waves',
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
                    <img src="assets/img/ssi-dive-center.png" alt="SSI Official Partner Dive Center" class="ssi-badge w-20 h-20" loading="lazy" width="80" height="80">
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
                <a href="about.html" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold inline-flex items-center gap-2.5">Read our full story ''' + svg('arrow', 'w-4 h-4 text-brand-glow') + '''</a>
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
            '<a href="courses.html#%s" class="mt-5 btn-ghost liquid ripple-host px-5 py-2.5 rounded-full text-sm font-semibold inline-flex items-center justify-center gap-2">Explore course %s</a>'
            '</div></article>'
            % (['', 'delay-100', 'delay-200'][i % 3],
               photo(c['img'], c['full'], 'bento-image', '(max-width: 767px) 100vw, 33vw'),
               c['step'], c['level'], c['name'], c['short'], c['id'],
               svg('arrow', 'w-3.5 h-3.5 text-brand-glow')))


def courses_section(num='05'):
    path = ''.join(
        '<span class="chip px-3.5 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-[0.16em]">%s</span>%s'
        % (c['name'], '<span class="cp-arrow"></span>' if i < len(COURSES) - 1 else '')
        for i, c in enumerate(COURSES))
    return ('<section id="courses" class="mb-32">'
            + sec_head(num, 'SSI Courses', 'Certified, beginner to professional',
                       'SSI certified courses from beginners to professional level, taught by our instructor team.',
                       ('All courses', 'courses.html'))
            + '<div class="course-path mb-10 reveal">' + path + '</div>'
            + '<div class="grid sm:grid-cols-2 xl:grid-cols-3 gap-6">'
            + ''.join(course_card(c, i) for i, c in enumerate(COURSES)) + '</div></section>')


def activities_section(num='06'):
    tabs = ''.join(
        '<button type="button" class="act-tab glass-panel" role="tab" aria-selected="%s" aria-controls="act-%s">'
        '<span class="at-n">%s</span><span class="font-display font-bold">%s</span></button>'
        % ('true' if i == 0 else 'false', a['id'], a['n'], a['name'])
        for i, a in enumerate(ACTIVITIES))
    slides = ''.join(
        '<div class="act-slide on-media %s" id="act-%s" role="tabpanel">'
        '%s'
        '<span class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/50 to-brand-abyss/10"></span>'
        '<div class="absolute inset-0 p-7 md:p-10 flex flex-col justify-end as-copy">'
        '<span class="chip-cyan w-fit px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.14em] mb-4">Activity %s</span>'
        '<h3 class="font-display text-3xl md:text-4xl font-bold text-white mb-3">%s</h3>'
        '<p class="text-brand-ink/85 max-w-xl leading-relaxed mb-6">%s</p>'
        '<div class="flex flex-wrap gap-3">'
        '<button type="button" data-book data-experience="%s" class="btn-bio liquid ripple-host px-6 py-3 rounded-full font-bold text-sm">Book %s</button>'
        '<a href="diving.html#%s" class="btn-ghost liquid ripple-host px-6 py-3 rounded-full font-semibold text-sm">Learn more</a>'
        '</div></div></div>'
        % ('is-on' if i == 0 else '', a['id'],
           photo(a['img'], a['name'], '', '100vw', lazy=(i != 0)),
           a['n'], a['name'], a['text'], a['name'], a['name'], a['id'])
        for i, a in enumerate(ACTIVITIES))
    return ('<section id="activities" class="mb-32" data-act>'
            + sec_head(num, 'Diving Activities', 'Boat, shore and confined',
                       'Three ways into the water, each with its own reason to choose it.')
            + '<div class="grid lg:grid-cols-[minmax(0,1fr)_2fr] gap-8 items-start">'
            + '<div class="act-tabs lg:flex-col reveal" role="tablist" aria-label="Diving activities">' + tabs + '</div>'
            + '<div class="act-stage glass-panel p-2 reveal delay-100">' + slides + '</div>'
            + '</div></section>')


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
        % (e['id'], ['', 'delay-100', 'delay-200', 'delay-300'][i], 'md:col-span-2' if i == 0 else '',
           photo(e['img'], e['name'], 'absolute inset-0 w-full h-full object-cover bento-image', '(max-width: 767px) 100vw, 50vw'),
           svg(e['icon'], 'w-5 h-5'), e['name'], e['text'])
        for i, e in enumerate(EVENTS))
    return ('<section id="underwater-events" class="mb-32">'
            + sec_head(num, 'Underwater Events', 'Celebrate below the surface',
                       'The moments people remember, moved underwater and planned with our team.',
                       ('All underwater events', 'events.html'))
            + '<div class="grid md:grid-cols-4 gap-6 auto-rows-[260px]">' + cards + '</div></section>')


def dest_card(d, i):
    acts = ''.join('<span class="chip px-3 py-1 rounded-full text-[10px] font-semibold uppercase tracking-[0.14em]">%s</span>' % a for a in d['acts'][:5])
    return ('<article class="dest-card bento-card on-media group liquid glow-hover bio-edge" data-dest-id="%s" data-label="%s">'
            '%s'
            '<div class="absolute inset-0 duotone"></div>'
            '<div class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/55 to-transparent"></div>'
            '<div class="absolute inset-0 p-7 md:p-9 flex flex-col justify-end z-[4]">'
            '<span class="chip-cyan w-fit px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.16em] mb-4">%s</span>'
            '<h3 class="dc-name text-white mb-3">%s</h3>'
            '<p class="text-brand-ink/80 leading-relaxed max-w-md mb-5">%s</p>'
            '<div class="flex flex-wrap gap-2 mb-6">%s</div>'
            '<div class="flex flex-wrap gap-3">'
            '<a href="%s" class="btn-bio liquid ripple-host px-6 py-3 rounded-full font-bold text-sm">Explore %s</a>'
            '<button type="button" data-book data-destination="%s" class="btn-ghost liquid ripple-host px-6 py-3 rounded-full font-semibold text-sm">Book here</button>'
            '</div></div></article>'
            % (d['id'], d['name'],
               photo(d['img'], 'Dive Adda ' + d['name'], 'absolute inset-0 w-full h-full object-cover bento-image', '(max-width: 767px) 100vw, 50vw', lazy=(i != 0)),
               d['sub'], d['name'], d['blurb'], acts, d['file'], d['name'], d['name']))


def destinations_section(num='08', with_map=True):
    cards = ''.join(dest_card(d, i) for i, d in enumerate(DESTS))
    mp = ''
    if with_map:
        mp = ('<div class="grid lg:grid-cols-3 gap-8 items-stretch mt-12">'
              '<div class="lg:col-span-1 reveal">'
              '<h3 class="font-display text-2xl font-bold text-white mb-4">Where we dive</h3>'
              '<p class="text-brand-dim leading-relaxed mb-6">Our SSI certified scuba centre is in Vizag, and we run scuba diving and water sports in Rajahmundry and Goa. '
              'Meeting points and timings are confirmed by the dive desk when you book.</p>'
              '<ul class="space-y-3">'
              + ''.join('<li><a href="%s" class="glass-panel liquid rounded-2xl p-4 flex items-start gap-4 group">'
                        '<span class="shrink-0 p-2.5 rounded-xl bg-brand-accent/12 border border-brand-accent/30 text-brand-glow shadow-[0_0_22px_-8px_rgba(34,211,238,0.8)]">%s</span>'
                        '<span><span class="block text-white font-bold">%s</span>'
                        '<span class="block text-sm text-brand-dim/85">%s</span></span></a></li>'
                        % (d['file'], svg('pin'), d['name'], d['sub']) for d in DESTS)
              + '</ul></div>'
              '<div class="lg:col-span-2 h-[460px] relative rounded-3xl overflow-hidden glass-panel p-2 reveal delay-200">'
              '<div id="diveMap"></div></div></div>')
    return ('<section id="destinations" class="mb-32">'
            + sec_head(num, 'Destinations', 'Three ways to dive with us',
                       'Vizag, Rajahmundry and Goa &mdash; swipe through and pick where you want to be underwater.')
            + '<div class="carousel reveal" data-autoplay data-map-sync>'
            + '<div class="carousel-track" tabindex="0" role="group" aria-label="Dive Adda destinations">' + cards + '</div>'
            + '<div class="flex items-center justify-between mt-2">'
            + '<div class="car-dots" role="tablist" aria-label="Choose a destination"></div>'
            + '<div class="flex gap-3">'
            + '<button type="button" data-car-prev class="car-btn glass-panel liquid" aria-label="Previous destination"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg></button>'
            + '<button type="button" data-car-next class="car-btn glass-panel liquid" aria-label="Next destination"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></button>'
            + '</div></div></div>' + mp + '</section>')


def journey_section(num='09'):
    steps = ''.join(
        '<div class="j-step"><span class="j-node">%s</span>'
        '<div class="j-card glass-panel"><h3 class="font-display font-bold text-white mb-1.5">%s</h3>'
        '<p class="text-sm text-brand-dim leading-relaxed">%s</p></div></div>' % (n, t, d)
        for n, t, d in JOURNEY)
    return ('<section id="first-dive" class="mb-32">'
            + sec_head(num, 'Your First Dive', 'What actually happens',
                       'No experience needed. This is how a first dive with Dive Adda goes, start to finish.', center=True)
            + '<div class="journey reveal"><span class="journey-line" aria-hidden="true"><span></span></span>' + steps + '</div>'
            + '<div class="text-center mt-12 reveal"><button type="button" data-book data-experience="Scuba Diving (first dive)" class="btn-bio liquid liquid-strong ripple-host px-8 py-4 rounded-full font-display font-bold text-lg">Book your first dive</button></div>'
            + '</section>')


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
           photo(img, cap, '', '(max-width: 767px) 50vw, 25vw', extra='data-full="%s"' % img),
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
            + '<div class="grid md:grid-cols-3 gap-6">' + cards + '</div>'
            + '<div class="text-center mt-10 reveal"><a href="events.html#conservation-diving" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold inline-flex items-center gap-2.5">Join a conservation dive %s</a></div>'
            % svg('arrow', 'w-4 h-4 text-brand-glow')
            + '</section>')


def faq_section(num='13', items=None, head=True):
    items = items or FAQS[:7]
    acc = ''.join(
        '<details class="faq-item glass-panel reveal"%s><summary>%s<span class="fq-icon">%s</span></summary>'
        '<div class="fq-body">%s</div></details>' % (' open' if i == 0 else '', q, svg('plus', 'w-4 h-4'), a)
        for i, (q, a) in enumerate(items))
    h = sec_head(num, 'FAQ', 'Questions before you dive',
                 'Everything below is answered by the Dive Adda team &mdash; no guesswork.', center=True) if head else ''
    return ('<section id="faq" class="mb-32">' + h
            + '<div class="max-w-3xl mx-auto grid gap-4" data-faq-group>' + acc + '</div>'
            + '<p class="text-center text-brand-dim mt-10 reveal">Still unsure? <a href="contact.html#enquire" class="link-glow font-semibold">Send us your question</a> or call <a href="tel:%s" class="link-glow font-semibold">%s</a>.</p>'
            % (PHONE_TEL, PHONE_TXT)
            + '</section>')


def enquiry_section(num='14'):
    dest_opts = ''.join('<option value="%s">%s</option>' % (d['name'], d['name']) for d in DESTS)
    exp_opts = ''.join('<option value="%s">%s</option>' % (html.unescape(n), n) for n in
                       ['Scuba Diving (first dive)', 'Guided Fun Dive', 'SSI Course', 'Snorkelling', 'Boat Diving',
                        'Shore Diving', 'Confined Diving', 'Water Sports', 'Underwater Event', 'Outbound Trip'])
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
    return '<main class="theme-scope flex-grow pt-24 pb-20 px-6 md:px-12 max-w-7xl mx-auto w-full">'


# ---------------------------------------------------------------- pages
def page_home():
    dest_tpls = ''.join(
        '<template id="destTpl-%s"><div class="dp-in">'
        '<p class="text-brand-ink/85 leading-relaxed mb-3">%s</p>'
        '<div class="flex flex-wrap items-center justify-center gap-2">%s'
        '<a href="%s" class="link-glow text-[11px] font-bold uppercase tracking-[0.2em] ml-1">Explore %s &rarr;</a>'
        '</div></div></template>'
        % (d['id'], d['blurb'],
           ''.join('<span class="chip px-3 py-1 rounded-full text-[10px] font-semibold uppercase tracking-[0.14em]">%s</span>' % a for a in d['acts'][:4]),
           d['file'], d['name'])
        for d in DESTS)

    hero = '''    <header class="relative w-full h-screen min-h-[780px] flex items-center justify-center pt-28 pb-16 overflow-hidden">
        <video id="heroVideo" autoplay loop muted playsinline preload="none"
               poster="''' + B('cover-divers') + '''"
               class="absolute inset-0 w-full h-full object-cover z-0 opacity-60 saturate-[.85]">
            <!-- Swap in a self-hosted Dive Adda clip here for motion: <source src="assets/video/dive-adda.mp4" type="video/mp4"> -->
        </video>

        <div class="absolute inset-0 bg-gradient-to-b from-brand-abyss/85 via-brand-deep/55 to-brand-deep z-[5]"></div>
        <div class="absolute inset-0 z-[6] pointer-events-none" style="background: radial-gradient(80% 55% at 50% 45%, rgba(34,211,238,0.10), transparent 65%);"></div>
        <div id="heroFish" class="absolute inset-0 z-[7] overflow-hidden pointer-events-none" aria-hidden="true"></div>

        <div class="relative z-10 text-center px-4 max-w-4xl mx-auto flex flex-col items-center reveal active">
            <span class="float-organic inline-flex items-center gap-2.5 chip-cyan rounded-full px-4 py-1.5 font-semibold tracking-[0.22em] uppercase text-[10px] mb-8">
                <span class="w-1.5 h-1.5 rounded-full bg-brand-glow shadow-[0_0_10px_#67E8F9]"></span>
                SSI Certified Scuba Centre &middot; Vizag
            </span>

            <h1 class="font-display text-6xl md:text-8xl lg:text-[8.5rem] font-bold text-white leading-[0.95] mb-5 heading-glow tracking-tight">
                DIVE <span class="text-gradient-bio">ADDA</span>
            </h1>
            <p class="text-[11px] md:text-sm font-bold uppercase tracking-[0.5em] text-brand-glow/80 mb-7">Discover &mdash; The Deep</p>
            <p class="text-lg md:text-xl text-brand-ink/80 mb-9 max-w-2xl font-medium leading-relaxed">
                Scuba diving, SSI courses, guided fun dives and underwater events &mdash; safe, exciting and unforgettable, with expert guidance from your first breath underwater.
            </p>

            <div class="flex flex-col sm:flex-row gap-4 w-full sm:w-auto mb-12">
                <button type="button" data-book class="btn-bio liquid liquid-strong ripple-host px-8 py-4 rounded-full font-display font-bold text-lg">
                    Book Your Dive
                </button>
                <a href="#experiences" class="btn-ghost liquid ripple-host px-8 py-4 rounded-full font-bold text-lg flex items-center justify-center gap-2.5">
                    Explore Experiences
                    <svg class="w-5 h-5 text-brand-glow cue-dot" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                </a>
            </div>

            <div class="w-full max-w-xl">
                <p class="text-[10px] font-bold uppercase tracking-[0.3em] text-brand-dim/60 mb-4">Choose your destination</p>
                <div class="dest-select mb-5" role="tablist" aria-label="Destinations" data-dest-select="heroDestPanel">
                    ''' + ''.join('<button type="button" role="tab" data-dest="%s" aria-selected="%s">%s</button>' % (d['id'], 'true' if i == 0 else 'false', d['name']) for i, d in enumerate(DESTS)) + '''
                </div>
                <div class="dest-panel glass-panel rounded-2xl p-5 text-sm" id="heroDestPanel" aria-live="polite"></div>
            </div>

            <div class="mt-12 flex flex-col items-center gap-2 text-[10px] uppercase tracking-[0.3em] text-brand-dim/50">
                <span>Descend</span>
                <span class="relative w-[1px] h-10 bg-gradient-to-b from-brand-accent/60 to-transparent"></span>
            </div>
        </div>
    </header>
''' + dest_tpls

    body = (hero + main_open()
            + experiences_section() + why_section() + story_section() + scuba_cards_section()
            + courses_section() + activities_section() + events_section() + destinations_section()
            + journey_section() + gallery_section() + team_section() + conservation_section()
            + faq_section() + enquiry_section() + '</main>')

    ld = [
        {"@type": "WebSite", "@id": DOMAIN + "#website", "url": DOMAIN, "name": "Dive Adda",
         "inLanguage": "en", "publisher": {"@id": ORG_ID}},
        {"@type": "WebPage", "@id": DOMAIN + "#webpage", "url": DOMAIN,
         "name": "Dive Adda | SSI Certified Scuba Diving Centre",
         "isPartOf": {"@id": DOMAIN + "#website"}, "about": {"@id": CENTRE_ID}},
        ld_faq(FAQS[:7]),
    ] + [ld_course(c) for c in COURSES]

    return shell('home', 'home', 18,
                 'Dive Adda | SSI Certified Scuba Diving Centre in Vizag, Rajahmundry &amp; Goa',
                 'Dive Adda is an SSI certified scuba diving centre: SSI courses, guided fun dives, snorkelling, boat, shore and confined diving, and underwater events in Vizag, Rajahmundry and Goa.',
                 '', body, ld, hero_img=B('cover-divers'),
                 use_map=True, book_modal=True, lightbox=True, profile=True)


def page_diving():
    detail = ''
    for i, a in enumerate(ACTIVITIES):
        flip = (i % 2 == 1)
        detail += ('<section id="%s" class="mb-28 scroll-mt-32">'
                   '<div class="grid lg:grid-cols-2 gap-10 items-center">'
                   '<div class="reveal %s"><div class="frame-photo glass-panel p-2 h-[340px] md:h-[440px]">%s</div></div>'
                   '<div class="reveal delay-100 %s">'
                   '<p class="eyebrow mb-4">Activity %s</p>'
                   '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-4 heading-glow">%s</h2>'
                   '<p class="text-brand-dim text-lg leading-relaxed mb-7">%s</p>'
                   '<div class="flex flex-wrap gap-3">'
                   '<button type="button" data-book data-experience="%s" class="btn-bio liquid ripple-host px-6 py-3.5 rounded-full font-bold text-sm">Book %s</button>'
                   '<a href="contact.html?experience=%s#enquire" class="btn-ghost liquid ripple-host px-6 py-3.5 rounded-full font-semibold text-sm">Ask a question</a>'
                   '</div></div></div></section>'
                   % (a['id'], 'lg:order-2' if flip else '',
                      photo(a['img'], a['name'], 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'),
                      'lg:order-1' if flip else '', a['n'], a['name'], a['text'], a['name'], a['name'], quote(html.unescape(a['name']))))

    fun = ('<section id="fun-dives" class="mb-28 scroll-mt-32">'
           '<div class="grid lg:grid-cols-2 gap-10 items-center">'
           '<div class="reveal"><div class="frame-photo glass-panel p-2 h-[340px] md:h-[460px]">%s</div></div>'
           '<div class="reveal delay-100">'
           '<p class="eyebrow mb-4">Guided</p>'
           '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-4 heading-glow">Guided Fun Dives</h2>'
           '<p class="text-brand-dim text-lg leading-relaxed mb-6">Experience safe and exciting guided fun dives with expert instructors, exploring breathtaking underwater wonders.</p>'
           '<ul class="space-y-3 mb-7">%s</ul>'
           '<button type="button" data-book data-experience="Guided Fun Dive" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Book a fun dive</button>'
           '</div></div></section>'
           % (photo(B('guided-fun-dive'), 'Guided fun dive with a Dive Adda instructor', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'),
              ''.join('<li class="benefit-pill glass-panel"><span class="bp-dot"></span><span class="text-brand-ink text-sm">%s</span></li>' % b
                      for b in ['Expert instructors on every dive', 'Certified divers and first-timers both welcome',
                                'Breathtaking underwater wonders, at your pace'])))

    scuba = ('<section id="scuba-diving" class="mb-28 scroll-mt-32">'
             + sec_head('01', 'Scuba Diving', 'Breathe underwater',
                        'Scuba diving is an underwater adventure that allows you to explore the marine world using a Self-Contained Underwater Breathing Apparatus.')
             + '<div class="grid sm:grid-cols-2 gap-6">'
             + ''.join(
                 '<button type="button" class="info-card glass-panel bio-edge text-left reveal %s" aria-expanded="%s">'
                 '<span class="ic-num" aria-hidden="true">%s</span><span class="ic-icon mb-5">%s</span>'
                 '<h3 class="font-display text-xl font-bold text-white mb-2">%s</h3>'
                 '<p class="text-brand-dim text-sm leading-relaxed">%s</p>'
                 '<span class="ic-more"><div><div class="text-brand-dim text-sm leading-relaxed pt-4 border-t border-white/[0.08]">%s</div></div></span>'
                 '<span class="mt-5 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.2em] text-brand-glow"><span class="ic-toggle">%s</span> Read more</span>'
                 '</button>'
                 % (['', 'delay-100', 'delay-200', 'delay-300'][i], 'true' if i == 0 else 'false',
                    n, svg(ic, 'w-6 h-6'), t, teaser, more, svg('plus', 'w-3.5 h-3.5'))
                 for i, (n, ic, t, teaser, more) in enumerate(SCUBA_CARDS))
             + '</div></section>')

    outbound = ('<section id="outbound-trips" class="mb-28 scroll-mt-32">'
                '<div class="cta-band glass-deep bio-edge reveal">'
                '<div class="relative grid lg:grid-cols-2 gap-8 items-center">'
                '<div class="frame-photo h-[280px] md:h-[340px]">%s</div>'
                '<div><p class="eyebrow mb-4">Also from Dive Adda</p>'
                '<h2 class="font-display text-3xl font-bold text-white mb-3">Outbound Trips</h2>'
                '<p class="text-brand-dim text-lg leading-relaxed mb-6">Experience thrilling outbound scuba diving trips to exotic locations, exploring vibrant marine life safely.</p>'
                '<button type="button" data-book data-experience="Outbound Trip" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Ask about the next trip</button>'
                '</div></div></div></section>'
                % photo(B('outbound-trip'), 'A Dive Adda outbound trip group', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'))

    body = (page_hero('Diving', 'Diving with <span class="text-gradient-bio">Dive Adda</span>',
                      'Scuba diving, guided fun dives, and boat, shore and confined diving &mdash; every one of them run by SSI certified instructors.',
                      B('guided-fun-dive'), 12,
                      [('Home', 'index.html'), ('Diving', None)],
                      ghost='DIVE', ctas=hero_ctas('Book a dive'))
            + main_open() + scuba + fun + activities_section('02') + detail + outbound
            + journey_section('03')
            + cta_band('Ready for your first breath underwater?',
                       'Tell us your destination and dates &mdash; our team will confirm availability and take care of the rest.')
            + '</main>')

    ld = [ld_breadcrumb([('Home', ''), ('Diving', 'diving.html')]),
          ld_service('Scuba Diving', 'Guided scuba diving, fun dives, boat diving, shore diving and confined water training with SSI certified instructors.', 'diving.html')]
    return shell('diving', 'diving', 12,
                 'Scuba Diving, Fun Dives, Boat &amp; Shore Diving | Dive Adda',
                 'Scuba diving with Dive Adda: guided fun dives, boat diving, shore diving and confined water training with SSI certified instructors in Vizag, Rajahmundry and Goa.',
                 'diving.html', body, ld, hero_img=B('guided-fun-dive'))


def page_courses():
    details = ''
    for i, c in enumerate(COURSES):
        flip = (i % 2 == 1)
        details += ('<section id="%s" class="mb-24 scroll-mt-32">'
                    '<div class="grid lg:grid-cols-2 gap-10 items-center">'
                    '<div class="reveal %s"><div class="frame-photo glass-panel p-2 h-[320px] md:h-[420px]">%s</div></div>'
                    '<div class="reveal delay-100 %s">'
                    '<div class="flex items-center gap-3 mb-4">'
                    '<span class="chip-cyan px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-[0.14em]">%s</span>'
                    '<span class="eyebrow">Step %s</span></div>'
                    '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-2 heading-glow">%s</h2>'
                    '<p class="text-[11px] uppercase tracking-[0.2em] text-brand-glow mb-5">%s</p>'
                    '<p class="text-brand-dim text-lg leading-relaxed mb-6">%s</p>'
                    '<ul class="space-y-2.5 mb-7">%s</ul>'
                    '<div class="flex flex-wrap gap-3">'
                    '<button type="button" data-book data-experience="SSI Course" class="btn-bio liquid ripple-host px-6 py-3.5 rounded-full font-bold text-sm">Enquire about this course</button>'
                    '<a href="contact.html?course=%s&amp;experience=SSI%%20Course#enquire" class="btn-ghost liquid ripple-host px-6 py-3.5 rounded-full font-semibold text-sm">Send an enquiry</a>'
                    '</div></div></div></section>'
                    % (c['id'], 'lg:order-2' if flip else '',
                       photo(c['img'], c['full'], 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'),
                       'lg:order-1' if flip else '', c['level'], c['step'], c['name'], c['full'], c['long'],
                       ''.join('<li class="benefit-pill glass-panel"><span class="bp-dot"></span><span class="text-brand-ink text-sm">%s</span></li>' % b for b in c['learn']),
                       quote(html.unescape(c['name']))))

    benefits = ('<section class="mb-28">'
                + sec_head('02', 'Benefits', 'Why take a scuba course',
                           'What a course gives you, beyond the certification card.', center=True)
                + '<div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">'
                + ''.join('<div class="trust-card glass-panel bio-edge reveal"><span class="ic-icon mb-4">%s</span>'
                          '<h3 class="font-display font-bold text-white text-lg leading-tight">%s</h3></div>'
                          % (svg(ic, 'w-5 h-5'), b)
                          for ic, b in [('cap', 'Learn essential diving skills'), ('shield', 'Enhanced safety'),
                                        ('globe', 'Global certification'), ('people', 'Career &amp; volunteering opportunities'),
                                        ('heart', 'Physical &amp; mental health benefits'), ('chat', 'Meet a community of divers'),
                                        ('camera', 'Underwater photography &amp; videography'), ('spark', 'A reason to keep diving')])
                + '</div></section>')

    ssi_intro = ('<section class="mb-24"><div class="cta-band glass-deep bio-edge reveal">'
                 '<div class="relative grid lg:grid-cols-[auto_1fr] gap-8 items-center">'
                 '<img src="assets/img/ssi-dive-center.png" alt="SSI Official Partner Dive Center" class="ssi-badge mx-auto" width="132" height="132">'
                 '<div><h2 class="font-display text-3xl font-bold text-white mb-3">An internationally certified SSI dive centre</h2>'
                 '<p class="text-brand-dim text-lg leading-relaxed">We are proudly affiliated with SSI (Scuba Schools International), ensuring our training programmes meet the highest global standards. '
                 'Our team provides professional dive training for all levels &mdash; from beginners taking their first dive to professionals looking to enhance their skills.</p>'
                 '</div></div></div></section>')

    body = (page_hero('SSI Courses', 'Get <span class="text-gradient-bio">certified</span>',
                      'SSI certified courses from beginner to professional level, taught by instructors with over 15 years of industry experience.',
                      B('ssi-pool-training'), 9,
                      [('Home', 'index.html'), ('Courses', None)],
                      ghost='SSI', ctas=hero_ctas('Start a course', experience='SSI Course'))
            + main_open() + ssi_intro + courses_section('01') + details + benefits
            + faq_section('03', [FAQS[3], FAQS[0], FAQS[4], FAQS[7]])
            + cta_band('Not sure which course fits?',
                       'Tell us where you are starting from and our instructors will point you to the right programme.',
                       experience='SSI Course')
            + '</main>')

    ld = [ld_breadcrumb([('Home', ''), ('Courses', 'courses.html')])] + [ld_course(c) for c in COURSES] + [ld_faq([FAQS[3], FAQS[0], FAQS[4], FAQS[7]])]
    return shell('courses', 'courses', 9,
                 'SSI Scuba Diving Courses | Open Water to Dive Master | Dive Adda',
                 'SSI certified scuba courses with Dive Adda: Open Water, Advanced Adventurer, React Right, Diver Stress & Rescue and Dive Master, from beginner to professional level.',
                 'courses.html', body, ld, hero_img=B('ssi-pool-training'))


def page_water_sports():
    cards = ''.join(
        '<article class="trust-card glass-panel bio-edge reveal %s">'
        '<span class="ic-icon mb-5">%s</span>'
        '<h3 class="font-display text-xl font-bold text-white mb-2">%s</h3>'
        '<p class="text-brand-dim text-sm leading-relaxed mb-5">%s</p>'
        '<a href="%s" class="link-glow text-[11px] font-bold uppercase tracking-[0.2em]">%s &rarr;</a>'
        '</article>'
        % (['', 'delay-100', 'delay-200'][i % 3], svg(ic, 'w-6 h-6'), t, d, href, cta)
        for i, (ic, t, d, href, cta) in enumerate([
            ('wave', 'Snorkelling', 'Explore underwater life effortlessly, floating with a mask, snorkel and fins. No certification needed.', '#snorkelling', 'See snorkelling'),
            ('bolt', 'Try Scuba', 'Your first breath underwater, with an instructor beside you the whole time.', 'diving.html#scuba-diving', 'About scuba diving'),
            ('boat', 'Boat Diving', 'Head out from the boat for easy access to deeper dive sites.', 'diving.html#boat-diving', 'About boat diving'),
        ]))

    by_dest = ''.join(
        '<article class="bento-card on-media group relative rounded-3xl overflow-hidden liquid glow-hover bio-edge reveal %s" style="min-height:320px">'
        '%s<div class="absolute inset-0 duotone"></div>'
        '<div class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/55 to-transparent"></div>'
        '<div class="absolute inset-0 p-7 flex flex-col justify-end z-[4]">'
        '<h3 class="font-display text-2xl font-bold text-white mb-2">%s</h3>'
        '<p class="text-brand-ink/80 text-sm mb-4">%s</p>'
        '<div class="flex flex-wrap gap-2 mb-5">%s</div>'
        '<a href="%s" class="btn-ghost liquid ripple-host px-5 py-2.5 rounded-full text-sm font-semibold w-fit">Explore %s</a>'
        '</div></article>'
        % (['', 'delay-100', 'delay-200'][i], photo(d['img'], d['name'], 'absolute inset-0 w-full h-full object-cover bento-image', '(max-width: 767px) 100vw, 33vw'),
           d['name'], d['blurb'],
           ''.join('<span class="chip px-3 py-1 rounded-full text-[10px] font-semibold uppercase tracking-[0.14em]">%s</span>' % a
                   for a in (['Snorkelling', 'Scuba Diving'] if d['id'] == 'vizag' else ['Scuba Diving', 'Water Sports'])),
           d['file'], d['name'])
        for i, d in enumerate(DESTS))

    snorkel = ('<section id="snorkelling" class="mb-28 scroll-mt-32">'
               '<div class="grid lg:grid-cols-2 gap-10 items-center">'
               '<div class="reveal"><div class="frame-photo glass-panel p-2 h-[340px] md:h-[460px]">%s</div></div>'
               '<div class="reveal delay-100">'
               '<p class="eyebrow mb-4">No certification needed</p>'
               '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-4 heading-glow">Snorkelling</h2>'
               '<p class="text-brand-dim text-lg leading-relaxed mb-7">Explore underwater life effortlessly, floating with a mask, snorkel and fins. It is the easiest way into the water &mdash; and often the first step towards a dive.</p>'
               '<div class="flex flex-wrap gap-3">'
               '<button type="button" data-book data-experience="Snorkelling" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Book snorkelling</button>'
               '<a href="diving.html#scuba-diving" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold">Or try scuba</a>'
               '</div></div></div></section>'
               % photo(B('snorkelling'), 'Snorkelling with Dive Adda', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'))

    note = ('<section class="mb-28"><div class="glass-panel rounded-3xl p-7 md:p-9 reveal max-w-3xl mx-auto text-center">'
            '<span class="ic-icon mx-auto mb-5">%s</span>'
            '<h3 class="font-display text-2xl font-bold text-white mb-3">What is running on your dates?</h3>'
            '<p class="text-brand-dim leading-relaxed mb-6">Water sport sessions vary by destination, season and sea conditions. '
            'Tell us where and when you want to be in the water and the dive desk will confirm exactly what is available.</p>'
            '<div class="flex flex-col sm:flex-row gap-3 justify-center">'
            '<button type="button" data-book data-experience="Water Sports" class="btn-bio liquid ripple-host px-7 py-3.5 rounded-full font-bold">Check availability</button>'
            '<a href="%s" target="_blank" rel="noopener" class="btn-ghost liquid ripple-host px-7 py-3.5 rounded-full font-semibold">Ask on WhatsApp</a>'
            '</div></div></section>'
            % (svg('clock', 'w-6 h-6'), wa_link('Hi Dive Adda! Which water sports are available on my dates?')))
    # NOTE FOR THE OWNER: list your specific water sports here once confirmed
    # (e.g. jet ski, banana boat, kayaking). Nothing is listed that we cannot verify.

    body = (page_hero('Water Sports', 'Scuba <span class="text-gradient-bio">+ water sports</span>',
                      'Snorkelling, scuba and water sport experiences across our destinations &mdash; for everyone from non-swimmers-turned-floaters to certified divers.',
                      B('snorkelling'), 4,
                      [('Home', 'index.html'), ('Water Sports', None)],
                      ghost='SURF', ctas=hero_ctas('Book water sports', experience='Water Sports'))
            + main_open()
            + '<section class="mb-28">' + sec_head('01', 'On the water', 'Ways to get wet with us',
                                                   'Every experience below is run by the Dive Adda team.')
            + '<div class="grid sm:grid-cols-3 gap-6">' + cards + '</div></section>'
            + snorkel
            + '<section class="mb-28">' + sec_head('02', 'By destination', 'Where water sports run',
                                                   'Scuba and water sports across Vizag, Rajahmundry and Goa.')
            + '<div class="grid md:grid-cols-3 gap-6">' + by_dest + '</div></section>'
            + note
            + cta_band('Bringing a group?', 'Birthdays, college groups, families and corporate outings &mdash; tell us the numbers and we will plan the day.',
                       experience='Water Sports')
            + '</main>')

    ld = [ld_breadcrumb([('Home', ''), ('Water Sports', 'water-sports.html')]),
          ld_service('Water Sports', 'Snorkelling, scuba diving and water sport experiences with Dive Adda in Vizag, Rajahmundry and Goa.', 'water-sports.html')]
    return shell('water-sports', 'water-sports', 4,
                 'Water Sports &amp; Snorkelling | Dive Adda',
                 'Snorkelling, scuba and water sport experiences with Dive Adda across Vizag, Rajahmundry and Goa. No certification needed to start.',
                 'water-sports.html', body, ld, hero_img=B('snorkelling'))


def page_destination(d):
    others = [x for x in DESTS if x['id'] != d['id']]
    acts = ''.join(
        '<div class="benefit-pill glass-panel reveal"><span class="bp-dot"></span>'
        '<span class="text-brand-ink text-sm font-semibold">%s</span></div>' % a for a in d['acts'])

    gal = [g for g in GALLERY if g[1] in ('diving', 'courses', 'snorkelling', 'events', 'destinations')][:6]
    gal = [(img, cat, cap, sub, span if i < 2 else '') for i, (img, cat, cap, sub, span) in enumerate(gal)]

    other_cards = ''.join(
        '<a href="%s" class="group relative rounded-3xl overflow-hidden bento-card on-media liquid glow-hover bio-edge reveal block" style="min-height:260px">'
        '%s<div class="absolute inset-0 duotone"></div>'
        '<div class="absolute inset-0 bg-gradient-to-t from-brand-abyss via-brand-abyss/50 to-transparent"></div>'
        '<div class="absolute inset-0 p-6 flex flex-col justify-end z-[4]">'
        '<h3 class="font-display text-2xl font-bold text-white mb-1">%s</h3>'
        '<p class="text-brand-ink/75 text-sm">%s</p></div></a>'
        % (o['file'], photo(o['img'], o['name'], 'absolute inset-0 w-full h-full object-cover bento-image', '(max-width: 767px) 100vw, 50vw'),
           o['name'], o['sub'])
        for o in others)

    centre = ''
    if d['id'] == 'vizag':
        centre = ('<section class="mb-28"><div class="grid lg:grid-cols-2 gap-10 items-center">'
                  '<div class="reveal"><div class="frame-photo glass-panel p-2 h-[380px] md:h-[500px]">%s</div></div>'
                  '<div class="reveal delay-100">'
                  '<p class="eyebrow mb-4">The centre</p>'
                  '<h2 class="font-display text-3xl md:text-4xl font-bold text-white mb-4 heading-glow">Our SSI certified scuba centre</h2>'
                  '<p class="text-brand-dim text-lg leading-relaxed mb-6">Dive Adda is an internationally certified dive centre, proudly affiliated with SSI. '
                  'Training runs from confined water through to guided open water dives, for complete beginners and certified divers alike.</p>'
                  '<div class="glass-panel rounded-2xl p-5 flex items-center gap-5 mb-7">'
                  '<img src="assets/img/ssi-dive-center.png" alt="SSI Official Partner Dive Center" class="w-16 h-16" loading="lazy" width="64" height="64">'
                  '<p class="text-sm text-brand-dim leading-relaxed">Our training programmes meet the highest global standards.</p></div>'
                  '<p class="text-sm text-brand-dim/80">The exact meeting point and timings are confirmed by the dive desk when you book.</p>'
                  '</div></div></section>'
                  % photo(B('dive-centre-storefront'), 'The Dive Adda scuba dive centre', 'rounded-3xl', '(max-width: 1023px) 100vw, 50vw'))

    body = (page_hero('Destination', 'Dive Adda <span class="text-gradient-bio">%s</span>' % d['name'],
                      d['long'], d['hero'], 10,
                      [('Home', 'index.html'), ('Destinations', 'index.html#destinations'), (d['name'], None)],
                      ghost=d['name'].upper()[:9],
                      ctas=hero_ctas('Book in ' + d['name'], destination=d['name']))
            + main_open()
            + '<section class="mb-24">' + sec_head('01', d['name'], 'What you can do here',
                                                   'Verified experiences our team runs in %s.' % d['name'])
            + '<div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">' + acts + '</div>'
            + '<p class="text-sm text-brand-dim/80 mt-6 reveal">Sessions, meeting points and timings are confirmed by the dive desk when you book.</p>'
            + '</section>'
            + centre
            + '<section class="mb-24">' + sec_head('02', 'On the map', 'Find us in %s' % d['name'], '')
            + '<div class="h-[420px] relative rounded-3xl overflow-hidden glass-panel p-2 reveal">'
            + '<div id="diveMap" data-focus="%s"></div></div></section>' % d['id']
            + '<section class="mb-24">' + sec_head('03', 'Gallery', 'From our dives', '', ('Full gallery', 'gallery.html'))
            + gallery_grid('gallery' + d['id'].title(), gal, filters=False) + '</section>'
            + '<section class="mb-24">' + sec_head('04', 'Other destinations', 'Also with Dive Adda', '')
            + '<div class="grid md:grid-cols-2 gap-6">' + other_cards + '</div></section>'
            + cta_band('Diving in %s?' % d['name'],
                       'Tell us your dates and group size &mdash; we will confirm availability with the dive desk.',
                       destination=d['name'])
            + '</main>')

    ld = [ld_breadcrumb([('Home', ''), ('Destinations', 'index.html#destinations'), (d['name'], d['file'])]),
          ld_service('Scuba diving in ' + d['name'],
                     html.unescape(d['long']), d['file'])]
    return shell(d['id'], 'destinations', 10,
                 'Scuba Diving in %s | Dive Adda' % d['name'],
                 html.unescape(d['long'])[:180],
                 d['file'], body, ld, hero_img=d['hero'], use_map=True, lightbox=True)


def page_events():
    details = ''
    for i, e in enumerate(EVENTS):
        flip = (i % 2 == 1)
        details += ('<section id="%s" class="mb-24 scroll-mt-32">'
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
    return shell('events', 'events', 15,
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
    return shell('gallery', 'gallery', 20,
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

    body = (page_hero('About', 'Our <span class="text-gradient-bio">story</span>',
                      'At Dive Adda, we bring the depths of the ocean closer to you.',
                      B('outbound-trip'), 6,
                      [('Home', 'index.html'), ('About', None)], ghost='STORY',
                      ctas=hero_ctas('Dive with us'))
            + main_open() + story_section() + who
            + scuba_cards_section('03') + passion + team_section('05') + conservation_section('06')
            + cta_band('Come and see for yourself',
                       'Book a first dive, a course or a fun dive with the team behind the story.')
            + '</main>')

    ld = [ld_breadcrumb([('Home', ''), ('About', 'about.html')]),
          {"@type": "AboutPage", "url": DOMAIN + "about.html", "about": {"@id": ORG_ID},
           "name": "About Dive Adda"}]
    return shell('about', 'about', 6,
                 'About Dive Adda | SSI Certified Dive Centre',
                 'Dive Adda was founded by a professional with 15 years in the Indian Navy, over a decade in submarines and 10 years in oil & gas. An SSI affiliated dive centre with over 15 years of team experience.',
                 'about.html', body, ld, hero_img=B('outbound-trip'), profile=True)


def page_faq():
    body = (page_hero('FAQ', 'Before you <span class="text-gradient-bio">dive in</span>',
                      'The questions we are asked most, answered by the Dive Adda team.',
                      B('confined-diving'), 22,
                      [('Home', 'index.html'), ('FAQ', None)], ghost='FAQ')
            + main_open()
            + faq_section('01', FAQS, head=False)
            + cta_band('Question not answered here?',
                       'Send it over &mdash; our team answers personally, and there is no deposit to enquire.')
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('FAQ', 'faq.html')]), ld_faq(FAQS)]
    return shell('faq', 'faq', 22,
                 'Scuba Diving FAQ | Dive Adda',
                 'Do you need experience to scuba dive? What happens on a first dive? Which SSI courses are available? Dive Adda answers the most common diving questions.',
                 'faq.html', body, ld, hero_img=B('confined-diving'))


def page_contact():
    body = (page_hero('Contact', 'Talk to the <span class="text-gradient-bio">dive desk</span>',
                      'Call, message on WhatsApp, or send an enquiry. We will confirm availability for your dates.',
                      B('boat-diving'), 24,
                      [('Home', 'index.html'), ('Contact', None)], ghost='HELLO')
            + main_open()
            + enquiry_section('01')
            + '<section class="mb-24 mt-24">' + sec_head('02', 'Destinations', 'Where to find us',
                                                          'Our SSI certified scuba centre is in Vizag, and we run experiences in Rajahmundry and Goa.')
            + '<div class="grid lg:grid-cols-3 gap-8 items-stretch">'
            + '<div class="lg:col-span-1 reveal"><ul class="space-y-3">'
            + ''.join('<li><a href="%s" class="glass-panel liquid rounded-2xl p-4 flex items-start gap-4">'
                      '<span class="shrink-0 p-2.5 rounded-xl bg-brand-accent/12 border border-brand-accent/30 text-brand-glow">%s</span>'
                      '<span><span class="block text-white font-bold">%s</span>'
                      '<span class="block text-sm text-brand-dim/85">%s</span></span></a></li>'
                      % (d['file'], svg('pin'), d['name'], d['sub']) for d in DESTS)
            + '</ul>'
            + '<div class="glass-panel rounded-2xl p-5 mt-4"><p class="text-sm text-brand-dim leading-relaxed">'
            'Meeting points and timings are confirmed by the dive desk when you book.</p></div></div>'
            + '<div class="lg:col-span-2 h-[460px] relative rounded-3xl overflow-hidden glass-panel p-2 reveal delay-200">'
            + '<div id="diveMap"></div></div></div></section>'
            + '</main>')
    ld = [ld_breadcrumb([('Home', ''), ('Contact', 'contact.html')]),
          {"@type": "ContactPage", "url": DOMAIN + "contact.html", "about": {"@id": CENTRE_ID}}]
    return shell('contact', 'contact', 24,
                 'Contact Dive Adda | Book a Dive in Vizag, Rajahmundry or Goa',
                 'Contact Dive Adda to book scuba diving, SSI courses, snorkelling or an underwater event. Call +91 89777 62155 or message us on WhatsApp.',
                 'contact.html', body, ld, hero_img=B('boat-diving'), use_map=True)


# ---------------------------------------------------------------- write
def write(name, content):
    path = os.path.join(ROOT, name)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('  %-22s %7.1f KB' % (name, len(content) / 1024.0))


def main():
    print('Building Dive Adda...')
    write('index.html', page_home())
    write('diving.html', page_diving())
    write('courses.html', page_courses())
    write('water-sports.html', page_water_sports())
    for d in DESTS:
        write(d['file'], page_destination(d))
    write('events.html', page_events())
    write('gallery.html', page_gallery())
    write('about.html', page_about())
    write('faq.html', page_faq())
    write('contact.html', page_contact())

    pages = ['', 'diving.html', 'courses.html', 'water-sports.html'] + [d['file'] for d in DESTS] + \
            ['events.html', 'gallery.html', 'about.html', 'faq.html', 'contact.html']
    today = '2026-09-16'
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        sm.append('  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>monthly</changefreq>\n  </url>' % (DOMAIN, p, today))
    sm.append('</urlset>')
    write('sitemap.xml', '\n'.join(sm) + '\n')
    write('robots.txt', 'User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n' % DOMAIN)
    print('Done.')


if __name__ == '__main__':
    main()
