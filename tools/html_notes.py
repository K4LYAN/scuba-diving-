"""Editing notes written into every generated page as HTML comments.

The .html files are rebuilt from tools/build_site.py on every build, so a note
typed into an .html file by hand would be lost. Instead, write() in
build_site.py passes each page through annotate(), which adds:

  * a header at the top of the page: which code builds it and how to edit it
  * a named banner before every section and shared block (menu, hero, footer,
    pop-ups...) saying exactly where to change it

Comments are invisible to visitors and cost about 1-2 KB per page after
compression. To change a note, edit the tables below.
"""
import html
import re

RULE = '=' * 78
DONT = 'Do not edit this .html file: run  python tools/build_site.py  after changing the source.'

# ------------------------------------------------------------------ pages
# file -> (page name, function in build_site.py, where its content lives)
PAGES = {
    'index.html': ('Homepage', 'page_home()', 'sections 01-06 below; each banner names its EDIT HERE code'),
    'about.html': ('About Us', 'page_about()', 'story, team [E12] and conservation sections'),
    'beginner-level-scuba.html': ('Beginner Level Scuba (Try Scuba)', 'page_first_time_scuba()', 'TRY_FACTS, TRY_STEPS, TRY_INCLUDED, TRY_REQUIREMENTS, TRY_KNOW, TRY_FAQS [E04] and SCUBA_CARDS [E10]'),
    'courses.html': ('SSI Courses', 'page_courses()', 'COURSES [E03] and SPECIALTIES [E05]'),
    'visakhapatnam.html': ('Location: Visakhapatnam', 'page_destination()', "the 'visakhapatnam' entry in DESTS [E02]"),
    'rajahmundry.html': ('Location: Rajahmundry', 'page_destination()', "the 'rajahmundry' entry in DESTS [E02]"),
    'blog.html': ('Blog', 'page_blog()', 'POSTS and BLOG_LINKS [E07]'),
    'gallery.html': ('Gallery', 'page_gallery()', 'GALLERY [E11]'),
    'events.html': ('Underwater Events', 'page_events()', 'EVENTS [E09]'),
    'faq.html': ('FAQ', 'page_faq()', 'GENERAL_FAQS [E13]'),
    'contact.html': ('Contact', 'page_contact()', 'contact details [E01] and enquiry_section()'),
}
COURSE_FILES = {'open-water-diver.html', 'advanced-adventurer.html', 'react-right.html',
                'diver-stress-rescue.html', 'dive-master.html'}
LEGAL_FILES = {'privacy-policy.html', 'terms-and-conditions.html', 'refund-policy.html'}

# ------------------------------------------------------------------ sections by id
# id -> (section name, how to edit)
SECTIONS = {
    'about': ('About Us', 'tools/build_site.py, search [E17] (about_home_section). Edit the paragraph text between the <p> tags.'),
    'courses': ('SSI Courses', 'Course cards come from COURSES, search [E03]. Card photo = assets/img/courses/<id>.jpg (same file as the course page).'),
    'scuba-diving': ('Scuba Diving - Vizag', 'Search [E18] (scuba_vizag_section): photos B(...), paragraphs, and highlights = [...] for the 5 boxes (icon, big text, small text).'),
    'water-sports': ('Adventure Water Sports', 'Search [E19]: WS_SLIDES = carousel photos (file, alt text, caption); WS_TILES = ride tiles; water_sports_section() = heading, locations, paragraphs.'),
    'testimonials': ('Testimonials (Google + Tripadvisor)', 'Heading: search [E20]. Review cards are REAL reviews fetched daily (tools/fetch_reviews.py, links [E06]). Never type reviews by hand.'),
    'book': ('Booking band', 'Search [E21] (book_section): heading, sentence and button labels.'),
    'story': ('Our story', 'Search def story_section in tools/build_site.py: text and photo.'),
    'team': ('Team / instructors', 'Search [E12] (TEAM): name, role, certification, experience, speciality, bio.'),
    'conservation': ('Conservation', 'Search def conservation_section in tools/build_site.py.'),
    'what-is-scuba': ('What is scuba (info cards)', 'Search [E10] (SCUBA_CARDS): (number, icon, title, text).'),
    'itinerary': ('Your morning, step by step', 'Search [E04], list TRY_STEPS: (time, title, description).'),
    'try-scuba-faq': ('Try Scuba FAQ', 'Search [E04], list TRY_FAQS: (question, answer).'),
    'specialties': ('SSI specialty courses', 'Search [E05] (SPECIALTIES). Image = assets/img/courses/<id>.jpg; without one the card shows the icon.'),
    'faq': ('Frequently asked questions', 'Search [E13] (GENERAL_FAQS) or [E04] TRY_FAQS on the beginner page: (question, answer).'),
    'general-faq': ('General FAQ', 'Search [E13] (GENERAL_FAQS): (question, answer).'),
    'activities': ('Activities at this location', 'Search [E02] (DESTS), list acts=[...] of this city: (id, name, icon, description, link). Photo = assets/img/activities/<id>.jpg [E08].'),
    'underwater-events': ('Underwater events', 'Search [E09] (EVENTS): name, photo, icon, text.'),
    'birthday-parties': ('Event: Birthday Parties', 'Search [E09], entry id=birthday-parties.'),
    'marriage-proposals': ('Event: Marriage Proposals', 'Search [E09], entry id=marriage-proposals.'),
    'pre-wedding-shoots': ('Event: Pre-Wedding Shoots', 'Search [E09], entry id=pre-wedding-shoots.'),
    'conservation-diving': ('Event: Conservation Diving', 'Search [E09], entry id=conservation-diving.'),
    'enquire': ('Enquiry form', 'Search def enquiry_section in tools/build_site.py (labels, options). Form checks: assets/js/dive-adda.js section 10.'),
}

# ------------------------------------------------------------------ sections by heading
# for sections without an id: words in the visible heading -> how to edit
HEADINGS = [
    ('About the course', "Text = 'long' and 'who' of this course in COURSES (search [E03]). Photo = assets/img/courses/<id>.jpg."),
    ('Learn', "The 'learn' list of this course in COURSES (search [E03])."),
    ('Course Pathway', "Built automatically from the order of COURSES ('step'). Change a course's step to reorder."),
    ('Start ', "The closing call-to-action: cta_band(...) at the end of page_course() in tools/build_site.py."),
    ('Ready to', "The closing call-to-action: cta_band(...) near the end of this page's function in tools/build_site.py."),
]

# ------------------------------------------------------------------ shared blocks
# (regex for the opening tag, block name, how to edit)
BLOCKS = [
    (r'<div id="ambient"', 'Background (light, rays, fish)',
     'HTML: tools/partials/ambient.html. Look: assets/css/dive-adda.css "AMBIENT UNDERWATER BACKGROUND". Fish: assets/js/dive-adda.js section 1b.'),
    (r'<div id="diveGate"', 'Intro screen (0-40 m depth dial)',
     'Text: tools/partials/gate.html. Timing and captions: assets/js/dive-adda.js section 4. Look: dive-adda.css "THE \\"DIVE IN\\" GATE".'),
    (r'<div id="callRail"', 'Floating call / WhatsApp / booking buttons',
     'def float_widgets in tools/build_site.py. Phone and WhatsApp numbers: [E01].'),
    (r'<nav ', 'Navigation menu',
     'Menu items: search [E14] (NAV). Logo files: assets/img/logo-mark*.png. Courses drop-down fills itself from [E03].'),
    (r'<header class="home-hero', 'Homepage hero',
     'Search [E16a] badge, [E16b] main sentence, [E16c] background photo (assets/img/brochure/cover-divers.jpg).'),
    (r'<header class="page-hero', 'Page hero (top banner)',
     'Set by page_hero(...) inside this page\'s function: arguments = eyebrow, title, description, background photo.'),
    (r'<main ', 'Main content',
     'Everything between here and the footer. Each section below has its own banner.'),
    (r'<footer', 'Footer',
     'Search [E15] (def footer): text, links, contact block. Year updates itself.'),
    (r'<div id="bookNowModal"', 'Booking pop-up',
     'Text and fields: BOOK_MODAL in tools/build_site.py. When it opens: assets/js/dive-adda.js section 11.'),
    (r'<div id="profileModal"', 'Team profile pop-up', 'PROFILE_MODAL in tools/build_site.py; content comes from [E12].'),
    (r'<div id="lightbox"', 'Photo viewer (gallery)', 'LIGHTBOX in tools/build_site.py; behaviour in dive-adda-pages.js section 10.'),
    (r'<div id="chatbotWidget"', 'Booking assistant (chat)',
     'Markup: CHATBOT in tools/build_site.py. Questions and steps: assets/js/dive-adda.js section 6.'),
    (r'<script>\s*/\* Scripts start right after', 'Script loader',
     'Loads GSAP + site scripts after the first paint. Edit assets/js/dive-adda.js / dive-adda-pages.js, never the *.min.js files.'),
]


def _banner(title, how, indent=''):
    lines = [RULE, title, 'HOW TO EDIT: ' + how]
    return '%s<!-- %s\n%s-->\n' % (indent, ('\n' + indent + '     ').join(lines), indent)


def _eyebrow(chunk):
    """Visible section label, e.g. '02 — SSI Courses', used for sections without an id."""
    m = re.search(r'<p class="eyebrow[^"]*">(.*?)</p>', chunk, re.S)
    if not m:
        m = re.search(r'<h2[^>]*>(.*?)</h2>', chunk, re.S)
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''


def annotate(name, content):
    if name in COURSE_FILES:
        page = ('Course: ' + name[:-5].replace('-', ' ').title(), 'page_course()', 'this course\'s entry in COURSES [E03]; image assets/img/courses/<id>.jpg')
    elif name in LEGAL_FILES:
        page = ('Legal: ' + name[:-5].replace('-', ' ').title(), 'page_legal()', 'LEGAL and LEGAL_UPDATED [E22]')
    elif name.startswith('blog-'):
        page = ('Blog post', 'page_post()', 'its entry in POSTS [E07]; body text inside page_post()')
    else:
        page = PAGES.get(name, (name, 'tools/build_site.py', 'search EDIT HERE'))

    # 1. page header, right after <!DOCTYPE html>
    head = ('<!-- %s\n     PAGE: %s  (%s)\n     GENERATED BY: %s in tools/build_site.py\n'
            '     CONTENT: %s\n     FIND ANY PART: search this file for "SECTION:" or "BLOCK:" to see what each part is\n'
            '     and where to change it. Guides: docs/EDITING-GUIDE.md and docs/STEP-BY-STEP.md\n'
            '     %s\n     %s -->\n' % (RULE, page[0], name, page[1], page[2], DONT, RULE))
    content = content.replace('<!DOCTYPE html>\n', '<!DOCTYPE html>\n' + head, 1)

    # 2. shared blocks
    for pattern, title, how in BLOCKS:
        m = re.search(pattern, content)
        if m:
            line_start = content.rfind('\n', 0, m.start()) + 1
            indent = re.match(r'[ \t]*', content[line_start:]).group(0)
            note = _banner('BLOCK: ' + title, how, indent)
            if content[line_start:m.start()].strip():      # tag is mid-line: put the note right before it
                content = content[:m.start()] + note.strip() + content[m.start():]
            else:
                content = content[:line_start] + note + content[line_start:]

    # 3. every section (legal paragraphs excluded: the page header covers them)
    def section_note(m):
        tag = m.group(0)
        if 'legal-block' in tag:
            return tag
        sid = re.search(r'id="([^"]+)"', tag)
        label = _eyebrow(content[m.end():m.end() + 1500])
        if sid and sid.group(1) in SECTIONS:
            title, how = SECTIONS[sid.group(1)]
            title = '%s  (#%s)%s' % (title, sid.group(1), ('  shown as "%s"' % label) if label else '')
        elif label and any(k in label for k, _ in HEADINGS):
            title = label
            how = next(h for k, h in HEADINGS if k in label)
        else:
            title = label or (sid.group(1) if sid else 'Section')
            how = 'Generated by %s in tools/build_site.py: search for the heading text "%s" there.' % (page[1], (label.split('—')[-1].strip() if label else title))
        return _banner('SECTION: ' + title, how).strip() + '\n' + tag

    content = re.sub(r'<section\b[^>]*>', section_note, content)
    return content
