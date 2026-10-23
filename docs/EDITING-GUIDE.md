# Dive Adda website — Editing Guide

**What this is:** a map of every editable part of the website: where it lives, what the code looks like, and exactly what to change.

**Companion document:** [STEP-BY-STEP.md](STEP-BY-STEP.md) walks through common jobs (change a photo, add a FAQ, publish to GitHub) one click at a time.

---

## 1. How the website works (read this first)

The pages (`index.html`, `about.html`, `courses.html` …) are **generated**. You never edit them directly.

```
  YOU EDIT                                RUN                       RESULT
  ─────────────────────────────           ───────────────────       ─────────────────────
  tools/build_site.py   (text, data)  ┐
  assets/css/*.css      (styles)      ├──► python tools/build_site.py ──► all 20 .html pages,
  assets/js/*.js        (behaviour)   │                                    sitemap.xml, robots.txt,
  assets/img/...        (photos)      ┘                                    llms.txt, minified CSS/JS
```

> ⚠️ **Never edit the `.html` files, `site.min.css`, the `*.min.js` files, `tailwind.css` or any `manifest.json`.**
> The build overwrites them. Your change would disappear the next time anyone runs the build.

### Find any section in seconds

Every editable block in the code has a numbered marker like this:

```python
# ============================================================================
# EDIT HERE [E03] SSI courses: name, level, short/long text, who it's for, what you learn.
#      Course image = assets/img/courses/<id>.jpg (same file on homepage card and course page).
# ============================================================================
```

Open the file in **VS Code**, press **Ctrl + F** (Mac: **⌘ + F**), type the code, for example `[E03]`, and you land on it.
To list every marker at once, press **Ctrl + Shift + F** and search for `EDIT HERE`.

### Notes inside every file

| File type | What you'll find at the top | What you'll find in each section |
|---|---|---|
| **CSS** (`assets/css/*.css`) | `HOW TO EDIT` steps + `SECTIONS IN THIS FILE` list | an `EDIT:` line saying what that section controls |
| **JavaScript** (`assets/js/dive-adda*.js`) | `HOW TO EDIT` steps + numbered section list | an `EDIT:` line under each numbered section |
| **HTML pages** (`*.html`) | `PAGE:` which code builds the page and where its content lives | a `SECTION:` or `BLOCK:` banner with `HOW TO EDIT:` (for example *SECTION: Adventure Water Sports (#water-sports) … search [E19]*) |

The HTML notes are written automatically by `tools/html_notes.py` on every build, so they stay correct and are never lost. To read them, open any page in the browser → right-click → **View Page Source**, then Ctrl + F `SECTION:`.

---

## 2. Marker index

| Code | What you can change | File | Shows up on |
|---|---|---|---|
| **E01** | Website address, phone, WhatsApp, Instagram, Facebook | `tools/build_site.py` | Every page (header, footer, buttons) |
| **J01** | WhatsApp number used by the booking form | `assets/js/dive-adda.js` | Booking pop-up |
| **E02** | Locations (Vizag, Rajahmundry) and their activities | `tools/build_site.py` | `visakhapatnam.html`, `rajahmundry.html`, menus |
| **E03** | SSI courses | `tools/build_site.py` | Homepage, `courses.html`, each course page |
| **E04** | Try Scuba facts, schedule, inclusions, requirements, tips, FAQs | `tools/build_site.py` | `beginner-level-scuba.html`, blog post |
| **E05** | SSI specialty courses | `tools/build_site.py` | `courses.html#specialties` |
| **E06** | Google / Tripadvisor review links | `tools/build_site.py` | Homepage testimonials |
| **R01** | Tripadvisor listing ID, Google place search name | `tools/fetch_reviews.py` | Homepage testimonials |
| **E07** | Blog posts and external reading links | `tools/build_site.py` | `blog.html`, blog post page |
| **E08** | Activity photos (jet ski, kayaking, ATV …) | `assets/img/activities/` | Location pages, homepage tiles |
| **E09** | Underwater events | `tools/build_site.py` | `events.html` |
| **E10** | "What is scuba" info cards | `tools/build_site.py` | `beginner-level-scuba.html` |
| **E11** | Photo gallery | `tools/build_site.py` | `gallery.html` |
| **E12** | Team / instructors | `tools/build_site.py` | `about.html` |
| **E13** | FAQ questions and answers | `tools/build_site.py` | `faq.html` |
| **E14** | Top navigation menu | `tools/build_site.py` | Every page |
| **E15** | Footer | `tools/build_site.py` | Every page |
| **E16** | Homepage hero: badge (E16a), main sentence (E16b), background photo (E16c) | `tools/build_site.py` | Homepage top |
| **E17** | Homepage section 01 — About Us | `tools/build_site.py` | Homepage |
| **E18** | Homepage section 03 — Scuba Diving Vizag (incl. the 5 highlight boxes) | `tools/build_site.py` | Homepage |
| **E19** | Homepage section 04 — Adventure Water Sports (carousel, ride tiles, text) | `tools/build_site.py` | Homepage |
| **E20** | Homepage section 05 — Testimonials heading | `tools/build_site.py` | Homepage |
| **E21** | Homepage section 06 — booking band | `tools/build_site.py` | Homepage |
| **E22** | Privacy policy, terms, refund policy, "last updated" date | `tools/build_site.py` | Legal pages |
| **E23** | `llms.txt` (summary that AI assistants read) | `tools/seo_files.py` | `/llms.txt` |
| **S01** | Brand colours | `assets/css/dive-adda.css` | Every page |
| **S02** | Your own style overrides | `assets/css/dive-adda-responsive.css` (end of file) | Every page |

---

## 3. Rules for editing text in the code

The code is Python. Text sits **inside quotes**, and lists are separated by **commas**. Change only what is between the quotes.

```python
name='Open Water Diver',          # ✅ change the words between the quotes
name='Open Water Diver'           # ❌ comma deleted  → the build fails
name='Open Water Diver,           # ❌ closing quote deleted → the build fails
```

**Special characters.** The text is written into HTML, so a few characters are spelled as codes:

| You want | Write | | You want | Write |
|---|---|---|---|---|
| & | `&amp;` | | – (en dash) | `&ndash;` |
| ’ (apostrophe) | `&rsquo;` | | — (em dash) | `&mdash;` |
| · (middle dot) | `&middot;` | | ≈ | `&asymp;` |

A plain apostrophe `'` **inside** single-quoted text ends the text early. Use `&rsquo;` instead: `'Here&rsquo;s what guests say'`.

**After every change:** run `python tools/build_site.py`. If it prints `Done.`, your edit is valid. If it prints an error, it names the line number; check the quotes and commas on that line.

---

## 4. Section by section

### E01 — Contact details and social links

📄 `tools/build_site.py` · search `[E01]`

```python
DOMAIN = 'https://www.diveaddaindia.com/'   # ✏️ website address (keep the final /)
PHONE_TXT = '+91 89777 62155'               # ✏️ phone number as people read it
PHONE_TEL = '+918977762155'                 # ✏️ same number for the "call" link: + and digits only
WA = '918977762155'                         # ✏️ WhatsApp: country code + number, no + or spaces
IG = 'https://www.instagram.com/diveaddaindia/'   # ✏️ Instagram page
FB = 'https://www.facebook.com/diveaddaindia/'    # ✏️ Facebook page
```

🔁 **Also change J01** when the WhatsApp number changes: 📄 `assets/js/dive-adda.js` · search `[J01]`

```js
const WA_NUMBER = '918977762155';   // ✏️ must match WA above
```

---

### E02 — Locations and their activities

📄 `tools/build_site.py` · search `[E02]`

```python
dict(id='visakhapatnam', name='Visakhapatnam', short='Vizag', file='visakhapatnam.html',
     sub='Vizag &middot; Andhra Pradesh',          # ✏️ small line under the city name
     img=B('cover-divers'), hero=B('cover-divers'), # ✏️ photos (see "Images" below)
     depth=12,
     blurb='Home of our SSI certified scuba centre…',   # ✏️ one-line summary (menus, cards)
     long='Visakhapatnam (Vizag) is the coastal home…', # ✏️ intro paragraph on the page
     acts=[
         # ( 'id',          'Name',         'icon', 'Description',                     link or None )
         ('scuba-diving', 'Scuba Diving', 'wave', 'Breathe underwater with an SSI…', 'beginner-level-scuba.html'),
         ('jet-ski',      'Jet Ski',      'bolt', 'A fast, thrilling ride…',         None),
     ]),
```

| Field | Meaning |
|---|---|
| `id` | Short name used in links (`visakhapatnam.html#jet-ski`) **and** as the photo file name. Lower case, hyphens, no spaces. |
| `icon` | One of: `arrow boat bolt camera cap chat check clock eye gift globe heart people phone pin plus shield spark wave` |
| link | A page for a "Learn more" button, or `None` for no button |

➕ **Add an activity:** copy one line inside `acts=[ … ]`, paste it below, and change all five values. Then add its photo as `assets/img/activities/<id>.jpg` (see section 5).
➖ **Remove an activity:** delete its whole line, including the comma at the end.

---

### E03 — SSI courses

📄 `tools/build_site.py` · search `[E03]`

```python
dict(id='open-water',                 # photo file name: assets/img/courses/open-water.jpg
     file='open-water-diver.html',    # the page created for this course
     name='Open Water Diver',         # ✏️ short name (cards, menu)
     full='SSI Open Water Diver',     # ✏️ full name (page title)
     level='Beginner',                # ✏️ small label on the card
     step='01',                       # ✏️ order in the pathway
     depth=18,
     img=B('ssi-pool-training'),      # backup photo, used only if assets/img/courses/<id>.jpg is missing
     short='The entry-level SSI certification…',   # ✏️ card text
     long='Open Water Diver is where most divers begin…',  # ✏️ "About the course" paragraph
     who='Anyone who wants a scuba certification…',        # ✏️ "Who it's for" box
     learn=['Essential diving skills', 'How your equipment works', …]),  # ✏️ "What you'll learn" list
```

🖼️ **Course image:** replace `assets/img/courses/<id>.jpg`, for example `open-water.jpg`. The **same file** is used on the homepage card, the courses page and the course's own page.
➕ **Add a course:** copy a whole `dict( … ),` block, give it a new `id` and `file`, and add its image. The page, menu entry, sitemap and structured data are created automatically.

---

### E04 — Try Scuba (beginner page)

📄 `tools/build_site.py` · search `[E04]`

```python
TRY_FACTS = [('6:30 AM &ndash; 12:30 PM', 'Morning experience'),   # ✏️ (big value, small label)
             ('&asymp; 40 min', 'Dive time per person'), …]
TRY_STEPS = [('6:30 AM &ndash; 6:45 AM', 'Report at Centre', 'Report at the Dive Adda centre…'), …]
                                                                      # ✏️ (time, title, description)
TRY_INCLUDED = ['Boat', 'Scuba diving equipment', …]                  # ✏️ "What's included" list
TRY_REQUIREMENTS = ['Minimum age: 8 years', …]                        # ✏️ requirements list
TRY_KNOW = [('camera', 'Bring Your Essentials', 'Please bring a cap…'), …]   # ✏️ (icon, title, text)
TRY_FAQS = [ ('Question?', 'Answer.'), … ]                            # ✏️ beginner FAQs
```

These values are also reused in the blog post and in `llms.txt`, so one edit updates all three.

---

### E05 — SSI specialty courses

📄 `tools/build_site.py` · search `[E05]`

```python
dict(id='deep-diving', name='Deep Diving', icon='eye',
     text='Plan and make deeper dives with the training…'),   # ✏️ card text
```

🖼️ Image: `assets/img/courses/<id>.jpg` (for example `deep-diving.jpg`). With no image, the card shows the icon instead.

---

### E06 / R01 — Reviews

The review cards show **only real reviews**, fetched every day from the official Google and Tripadvisor services by `tools/fetch_reviews.py` (it runs automatically on GitHub; see STEP-BY-STEP §8).

📄 `tools/build_site.py` · search `[E06]`

```python
TRIPADVISOR_URL = 'https://www.tripadvisor.in/Attraction_Review-…'   # ✏️ your Tripadvisor page
GOOGLE_REVIEWS_URL = 'https://www.google.com/search?q=Dive+Adda+…'   # ✏️ where "Google" links go
```

📄 `tools/fetch_reviews.py` · search `[R01]`

```python
TA_LOCATION_ID = '33033322'                                   # ✏️ the "d" number in the Tripadvisor URL
GOOGLE_QUERY = 'Dive Adda Scuba Diving Center Visakhapatnam'  # ✏️ used if GOOGLE_PLACE_ID is not set
```

> 🚫 Never type reviews, ratings or review counts by hand. Fake or edited reviews break Google and Tripadvisor rules, and customers can tell.

---

### E07 — Blog

📄 `tools/build_site.py` · search `[E07]`

```python
BLOG_LINKS = [('SSI Blog', 'https://www.divessi.com/blog/', 'Training, marine life…'), …]  # ✏️ (name, link, text)

POSTS = [
    dict(slug='first-dive-what-to-expect',
         file='blog-first-dive-what-to-expect.html',
         title='What to expect on your first scuba dive in Vizag',   # ✏️
         date='2026-09-21', date_label='21 September 2026',          # ✏️ both dates
         read='4 min read', tag='Beginner',                          # ✏️
         img=B('guided-fun-dive'),                                   # ✏️ photo
         excerpt='Never breathed underwater before?…',               # ✏️ card + search summary
         intro='If you have never breathed underwater before…'),     # ✏️ opening paragraph
]
```

ℹ️ The body of this first post is written in `page_post()` (search `def page_post`). You can edit its headings and paragraphs there. **Adding a second post with its own body text needs a small code change.** Ask a developer, or Claude, to add it.

---

### E08 — Activity photos

📁 `assets/img/activities/`

The file name must equal the activity `id` from E02 (or the ride tiles in E19):

| Activity | File |
|---|---|
| Jet Ski / Jet Ski Ride | `jet-ski.jpg` / `jet-ski-ride.jpg` |
| Leisure Boat | `leisure-boat.jpg` |
| ATV Rides | `atv-rides.jpg` |
| Speed Boat Ride | `speed-boat-ride.jpg` |
| Kayaking | `kayaking.jpg` |
| Dragon Ride | `dragon-ride.jpg` |
| Disco Ride | `disco-ride.jpg` |
| Bumper Ride | `bumper-ride.jpg` |
| Godavari bridge / sunset | `godavari-bridge.jpg`, `river-sunset.jpg` |

Replace the file, keeping **the same name**, then run `python tools/optimize_images.py` and `python tools/build_site.py`. Record where the photo came from in `assets/img/activities/CREDITS.txt`.

---

### E09 — Events · E10 — Scuba info cards · E12 — Team · E13 — FAQs

📄 `tools/build_site.py` · search the code

```python
# [E09]
dict(id='birthday-parties', name='Birthday Parties', img=B('event-birthday'), icon='gift',
     text='Mark the day underwater…'),                          # ✏️ name, photo, icon, text

# [E10]
('01', 'bolt', 'What is Scuba?', 'An underwater adventure that lets you…'),   # ✏️ (number, icon, title, text)

# [E12]
dict(mono='DA', name='Our Founder', role='Founder, Dive Adda',   # ✏️ mono = 2–3 letters in the circle
     cert='…', exp='…', spec='…', bio='…'),                    # ✏️ shown in the profile pop-up

# [E13]
('Is Dive Adda SSI certified?',                                  # ✏️ question
 'Yes. Dive Adda is an internationally certified dive centre…'), # ✏️ answer
```

➕ To add an item, copy a complete entry including its closing `),`, paste it, and edit it. FAQs are also published as FAQ structured data for Google automatically.

---

### E11 — Photo gallery

📄 `tools/build_site.py` · search `[E11]`

```python
# ( photo,              filter,    title,                 caption,                   size )
(B('cover-divers'),     'diving',  'Divers over the reef', 'Dive, Discover, Repeat', 'g-wide g-tall'),
```

| Field | Values |
|---|---|
| photo | `B('name')` = `assets/img/brochure/name.jpg` |
| filter | `diving` `courses` `snorkelling` `destinations` `boat` `events` |
| size | `''` normal · `'g-wide'` two columns · `'g-tall'` two rows · `'g-wide g-tall'` large |

---

### E14 — Navigation menu

📄 `tools/build_site.py` · search `[E14]`

```python
('about', 'About Us', 'about.html', None),        # ✏️ (id, label, link, drop-down or None)
('more', 'More', None, [('Blog', 'blog.html'), ('Gallery', 'gallery.html'), …]),   # ✏️ drop-down items
```

The Courses drop-down fills itself from E03.

---

### E15 — Footer

📄 `tools/build_site.py` · search `[E15]` (function `footer()`). The text is ordinary HTML inside `'''…'''`. Edit the words between the tags, and leave the tags (`<li>`, `<a href="…">`) intact.

---

### E16 — Homepage hero

📄 `tools/build_site.py` · search `[E16a]`, `[E16b]`, `[E16c]`

```html
<!-- EDIT HERE [E16a]: badge text at the top of the homepage -->
    SSI Certified Scuba Dive Centre &middot; Visakhapatnam          ← ✏️ badge text

<h1 …>DIVE <span class="text-gradient-bio">ADDA</span></h1>         ← ✏️ big title
<p class="hero-tagline …">Discover &mdash; The Deep</p>              ← ✏️ tagline

<!-- EDIT HERE [E16b]: the main sentence under DIVE ADDA -->
<p class="hero-lead …">Professional Scuba Diving Centre in Vizag…</p> ← ✏️ main sentence
```

🖼️ **[E16c] background photo:** `B('cover-divers')` = `assets/img/brochure/cover-divers.jpg`. Replace that file, or change the name inside `B('…')`.
🔎 **Google title and description for the homepage:** search `return shell('home'`. The two long text lines below it are the browser-tab title and the Google snippet. Each other page has its own `return shell(…)` in its `page_…` function.

---

### E17–E21 — Homepage sections

📄 `tools/build_site.py`

| Code | Section | What to look for inside the function |
|---|---|---|
| **E17** | 01 About Us | the paragraphs in `<p>` tags |
| **E18** | 03 Scuba Diving Vizag | `highlights = [ … ]` = the 5 boxes `('icon', 'Big text', 'small text')`; photos `B('cover-divers')`, `B('ssi-pool-training')`, `B('boat-diving')` |
| **E19** | 04 Adventure Water Sports | `WS_SLIDES` = carousel photos `(file, alt text, caption)`; `WS_TILES` = ride tiles `(page, activity id, label)`; `water_sports_section()` = heading, 📍 locations, paragraphs |
| **E20** | 05 Testimonials | heading and sentence in `sec_head(…)` |
| **E21** | 06 Booking band | heading, sentence, button labels |

E19 example: add a carousel photo:

```python
WS_SLIDES = [
    ('assets/img/activities/godavari-bridge.jpg', 'The Godavari arch bridge at Rajahmundry', 'Pushkar Ghat &middot; Rajahmundry'),
    #  ✏️ photo file                               ✏️ description for blind visitors          ✏️ caption on the photo
]
```

The dots and arrows adjust to the number of photos automatically.

---

### E22 — Legal pages

📄 `tools/build_site.py` · search `[E22]`

```python
LEGAL_UPDATED = '17 September 2026'   # ✏️ change whenever a policy changes
LEGAL = [ dict(file='privacy-policy.html', … sections=[('Heading', '<p>Paragraph…</p>'), …]), … ]
```

---

### E23 — llms.txt and robots.txt

📄 `tools/seo_files.py` · search `[E23]`

`llms.txt` is a plain-text summary of Dive Adda that AI assistants (ChatGPT, Claude, Perplexity, Gemini) read. Most of it is filled in automatically from E01–E05. Edit the fixed sentences in `llms_txt()` (the summary line and "Key facts"). `robots_txt()` lists the search engines and AI crawlers that may read the site.

---

### S01 / S02 — Colours and styles

📄 `assets/css/dive-adda.css` · search `[S01]`

```css
:root {
    --ink:     #E8F6FF;   /* ✏️ main text colour (dark theme) */
    --ink-dim: #9FBCD0;   /* ✏️ secondary text colour */
    …
}
```

📄 `assets/css/dive-adda-responsive.css` · search `[S02]`. Write your own CSS **at the very end** of this file; it loads last, so it wins:

```css
/* example: make every section heading a little larger */
.xp-title { font-size: 3.5rem; }
```

Then run `python tools/build_site.py`. It bundles all CSS into `site.min.css` for you.

---

## 5. Images: complete guide

### Where each image lives

| Folder | What | How it's referenced in code |
|---|---|---|
| `assets/img/brochure/` | General photos (hero, gallery, events, sections) | `B('cover-divers')` = `assets/img/brochure/cover-divers.jpg` |
| `assets/img/activities/` | One photo per activity | automatic: file name = activity `id` |
| `assets/img/courses/` | SSI course and specialty images | automatic: file name = course / specialty `id` |
| `assets/img/` | Logos, SSI badge, icons | fixed file names (see below) |

**Current brochure photos:** `boat-diving` `confined-diving` `cover-divers` `dive-centre-storefront` `event-birthday` `event-conservation` `event-prewedding` `event-proposal` `guided-fun-dive` `outbound-trip` `shore-diving` `snorkelling` `ssi-pool-training`

**Current course images:** `open-water` `advanced-adventurer` `react-right` `diver-stress-rescue` `dive-master` `deep-diving` `enriched-air-nitrox` `perfect-buoyancy` `night-limited-visibility` (plus unused `scuba-diver`, `specialty-diver`)

**Logos:** `logo-mark.png` / `logo-mark-light.png` (navigation), `logo-full.png` / `logo-full-light.png` (footer), `ssi-dive-center.png` (SSI partner badge), `ssi-logo-icon.png` (small SSI logo in badges). After replacing a logo, run `python tools/optimize_images.py`; it re-creates the sharp `-2x` versions and the favicon.

### Photo requirements

| | Recommended |
|---|---|
| Format | **JPG** for photos (PNG only for logos with transparency) |
| Width | 1600 px for big/hero photos, 1280 px for cards; never under 1000 px |
| Size | under 500 KB before optimising |
| Names | lower case, hyphens, no spaces: `jet-ski.jpg` ✅  `Jet Ski (1).JPG` ❌ |
| Content | your own photos, or ones you have the rights to. **No other company's name, phone number or watermark.** |

### Two ways to change a photo

**A. Replace (easiest).** Save the new photo with **exactly the same file name** over the old one, in the same folder. No code change needed.

**B. Use a new photo.** Add `new-name.jpg` to `assets/img/brochure/`, then change the code reference: `B('cover-divers')` → `B('new-name')`.

**Then always run both:**

```bash
python tools/optimize_images.py
```
```bash
python tools/build_site.py
```

`optimize_images.py` creates small WebP copies (480 to 1600 px) so phones download less. That's part of what keeps the Lighthouse score above 90.

> 💡 Visitors who saw the old photo may keep it for up to one day (browser cache). Press **Ctrl + F5** (Mac: **⌘ + Shift + R**) to see the new one immediately.

---

## 6. Files you should NOT edit

| File | Why |
|---|---|
| `*.html` in the main folder | generated by the build: changes are overwritten |
| `assets/css/site.min.css`, `assets/css/tailwind.css` | generated |
| `assets/js/*.min.js` | generated (edit `dive-adda.js` / `dive-adda-pages.js` instead) |
| `assets/img/**/manifest.json`, `*-640.webp` etc. | generated by `optimize_images.py` |
| `sitemap.xml`, `robots.txt`, `llms.txt` | generated |
| `assets/data/reviews.json` | written by the daily review bot |
| `static post/` | your raw media; never uploaded (it's in `.gitignore`) |

---

## 7. Quick troubleshooting

| Problem | Fix |
|---|---|
| Build prints `SyntaxError … line 312` | Open that line: a quote or comma is missing, or a plain `'` is inside text (use `&rsquo;`). |
| My change isn't on the live site | Did you run the build **and** push? Check Vercel → Deployments shows "Ready", then press Ctrl + F5. |
| New photo not showing | Same file name and folder? Ran `optimize_images.py`? Hard refresh. |
| Lost in the code | Search `EDIT HERE`, or ask Claude: "Change [E13] FAQ …". |
