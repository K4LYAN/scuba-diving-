# Dive Adda — Website

Website for **Dive Adda**, an SSI certified scuba diving centre in **Visakhapatnam (Vizag)** with adventure water sports in **Rajahmundry**.

🌐 **Live site:** https://www.diveaddaindia.com
🚀 **Hosting:** Vercel (deploys automatically on every push to `main`)
🌍 **Domain:** Namecheap

---

## Documentation

| Document | Use it for |
|---|---|
| **[docs/EDITING-GUIDE.md](docs/EDITING-GUIDE.md)** | Reference: what every `EDIT HERE [E..]` marker controls, real code examples, images guide |
| **[docs/STEP-BY-STEP.md](docs/STEP-BY-STEP.md)** | Recipes: change text, replace photos, add FAQs or courses, set up reviews, publish to GitHub, fix Git errors |

---

## How it works

The site is plain **HTML, CSS and JavaScript** (no framework). The 20 pages are **generated** by one Python script, so content is edited in one place and every page stays consistent.

```
tools/build_site.py  ─┐
assets/css/*.css     ─┤   python tools/build_site.py   ┌─► 20 .html pages
assets/js/*.js       ─┼──────────────────────────────►─┼─► site.min.css, *.min.js
assets/img/...       ─┘                                └─► sitemap.xml, robots.txt, llms.txt
```

> ⚠️ **Do not edit the generated `.html` files.** Edit `tools/build_site.py` and rebuild. To find any editable section, search the code for **`EDIT HERE`**.
>
> Every file explains itself: CSS and JS files start with a **HOW TO EDIT** header and have an **EDIT:** note in each section; every HTML page has **SECTION:** / **BLOCK:** banners naming the exact place to change it.

---

## Quick start

### Requirements

- **Python 3.11+** with **Pillow** (`pip install pillow`)
- **Node.js LTS** (the build uses `npx` for Tailwind CSS and esbuild)
- **Git**

### Build and preview

```bash
git clone https://github.com/K4LYAN/scuba-diving-
```
```bash
cd scuba-diving-
```
```bash
python tools/build_site.py
```
```bash
python tools/serve.py
```

Open **http://127.0.0.1:8123**. The preview server compresses and caches files the way the live host does.

### After adding or replacing photos

```bash
python tools/optimize_images.py
```
```bash
python tools/build_site.py
```

### Publish

```bash
git add -A && git commit -m "Describe your change"; git pull --no-rebase --no-edit -X theirs origin main && python tools/build_site.py && git add -A && (git diff --cached --quiet || git commit -m "Rebuild pages") && git push -u origin main
```

This commits your work, merges the daily review-bot commit, rebuilds, and pushes. Vercel deploys in 1–2 minutes. Each part is explained in [STEP-BY-STEP §7](docs/STEP-BY-STEP.md#7-publishing-to-github-explained).

---

## Project structure

```
├── *.html                      Generated pages (do not edit)
├── sitemap.xml, robots.txt,    Generated
│   llms.txt
├── vercel.json                 Vercel caching + security headers
├── .vercelignore               Keeps docs/ and tools/ off the live site
├── .github/workflows/
│   └── refresh-reviews.yml     Daily job: fetch reviews → rebuild → commit
├── assets/
│   ├── css/
│   │   ├── dive-adda.css               Base styles + brand colours   [S01]
│   │   ├── dive-adda-pages.css         Page and component styles
│   │   ├── dive-adda-responsive.css    Responsive + overrides (loads last) [S02]
│   │   └── site.min.css                Generated bundle
│   ├── js/
│   │   ├── dive-adda.js                Intro, theme, booking, map   [J01]
│   │   ├── dive-adda-pages.js          Carousels, menus, page features
│   │   └── *.min.js                    Generated
│   ├── img/
│   │   ├── brochure/                   General photos  → B('name')
│   │   ├── activities/                 One photo per activity (file = activity id)
│   │   ├── courses/                    SSI course images (file = course id)
│   │   └── logo-*.png, ssi-*.png       Logos and badges
│   └── data/reviews.json               Written by the review bot
├── tools/
│   ├── build_site.py           ★ All content and page templates  [E01–E22]
│   ├── optimize_images.py      WebP sizes + retina logos + favicon
│   ├── fetch_reviews.py        Google Places + Tripadvisor APIs   [R01]
│   ├── seo_files.py            robots.txt + llms.txt              [E23]
│   ├── html_notes.py           Editing notes written into every page (SECTION: / BLOCK:)
│   ├── serve.py                Local preview server
│   ├── partials/               Intro gate + ambient background HTML
│   ├── tailwind/               Tailwind config and input
│   └── qa/                     Dev-only test tools (screenshots, Lighthouse, audits)
├── docs/                       Editing guide and step-by-step workbook
└── static post/                Raw media; local only (in .gitignore)
```

---

## Pages

| Page | File |
|---|---|
| Home | `index.html` |
| About | `about.html` |
| Beginner Level Scuba (Try Scuba) | `beginner-level-scuba.html` |
| SSI Courses | `courses.html` |
| Course pages | `open-water-diver.html` · `advanced-adventurer.html` · `react-right.html` · `diver-stress-rescue.html` · `dive-master.html` |
| Locations | `visakhapatnam.html` · `rajahmundry.html` |
| Blog | `blog.html` · `blog-first-dive-what-to-expect.html` |
| Gallery · Events · FAQ · Contact | `gallery.html` · `events.html` · `faq.html` · `contact.html` |
| Legal | `privacy-policy.html` · `terms-and-conditions.html` · `refund-policy.html` |

---

## Features

- **Light and dark theme:** follows the device setting until the visitor chooses
- **Booking:** pop-up form that sends to **WhatsApp**, plus call and WhatsApp buttons on every page
- **Real reviews:** Google and Tripadvisor via their official APIs, refreshed daily; each card links to the original review
- **SSI course pages:** generated from one data list, with the pathway and "what you'll learn"
- **Water sports carousel:** Rajahmundry and Visakhapatnam, with swipe, arrows, dots and keyboard support
- **Performance:**
  - minified CSS/JS bundles, scripts loaded after the first paint
  - responsive WebP images, lazy-loaded map, off-screen sections skipped
  - target Lighthouse score **90+**
- **SEO:**
  - per-page titles and descriptions, canonical URLs, Open Graph
  - structured data (Organization, LocalBusiness, Course, FAQ, Breadcrumb)
  - sitemap, robots.txt welcoming search engines and AI crawlers, `llms.txt`
- **Accessibility:** semantic headings, alt text, keyboard navigation, reduced-motion support, contrast checked in both themes

---

## Reviews setup (one time)

Add these **GitHub → Settings → Secrets and variables → Actions** secrets:

| Secret | Where to get it |
|---|---|
| `GOOGLE_PLACES_API_KEY` | Google Cloud → enable **Places API (New)** → create an API key |
| `TRIPADVISOR_API_KEY` | Tripadvisor Content API |
| `GOOGLE_PLACE_ID` | optional |

Then run **Actions → Refresh reviews → Run workflow**. Full steps: [STEP-BY-STEP §5](docs/STEP-BY-STEP.md#5-reviews-google--tripadvisor--one-time-setup).

> Reviews are never written by hand. Without keys, the section links to the Google and Tripadvisor pages instead.

---

## Domain (Namecheap → Vercel)

Namecheap → **Advanced DNS** should contain exactly:

| Type | Host | Value |
|---|---|---|
| A Record | `@` | `216.198.79.1` |
| CNAME Record | `www` | value shown in Vercel → Settings → Domains |

No URL Redirect record. `diveaddaindia.com` redirects to `https://www.diveaddaindia.com`.

---

## Rules

- ✅ Edit `tools/build_site.py`, the CSS/JS sources and the images, then **rebuild**
- ✅ Use your own photos, or photos you have the rights to; record sources in `CREDITS.txt`
- ❌ Don't edit generated files (`*.html`, `*.min.*`, `manifest.json`, `sitemap.xml`, `llms.txt`)
- ❌ Don't commit large media, API keys or personal documents (`static post/` is ignored)
- ❌ Don't invent reviews, ratings, prices or certifications

---

© Dive Adda · Discover — The Deep
