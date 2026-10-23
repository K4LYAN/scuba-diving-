# Dive Adda website — Step-by-Step Workbook

**What this is:** follow-the-steps instructions for every common job, from editing a sentence to publishing on the live site.

**Companion document:** [EDITING-GUIDE.md](EDITING-GUIDE.md) is the reference: what every `EDIT HERE [E..]` marker controls and what the code looks like.

**Conventions**
- 🖱️ = something you click · ⌨️ = something you type · ✅ = how to know it worked
- Run every command in **Git Bash** opened inside the project folder `D:\kc\scuba`
  (in File Explorer, right-click the `scuba` folder and choose **Open Git Bash here**).

---

## 0. One-time setup (new computer)

| # | Install | Download | Check it works (type in Git Bash) |
|---|---|---|---|
| 1 | **Git** (includes Git Bash) | git-scm.com | `git --version` |
| 2 | **Python 3.11+**, with "Add to PATH" ticked during install | python.org | `python --version` |
| 3 | **Pillow** (image library for Python) | — | `pip install pillow` |
| 4 | **Node.js LTS** (the build uses it for CSS and JS) | nodejs.org | `node --version` |
| 5 | **VS Code** (editor) | code.visualstudio.com | — |

**Get the project onto a new computer:**

```bash
git clone https://github.com/K4LYAN/scuba-diving- D:/kc/scuba
```

**Tell Git who you are** (once per computer):

```bash
git config --global user.name "Your Name"
```
```bash
git config --global user.email "you@example.com"
```

✅ `python tools/build_site.py` prints a list of pages and ends with `Done.`

---

## 1. The 5-step routine for ANY change

```
 1. GET LATEST  →  2. EDIT  →  3. BUILD  →  4. PREVIEW  →  5. PUBLISH
```

**Step 1 — Get the latest version** (someone, or the daily review bot, may have changed things):

```bash
git pull origin main
```

**Step 2 — Edit.** Open the folder in VS Code (🖱️ *File → Open Folder → D:\kc\scuba*), press **Ctrl + Shift + F**, search `EDIT HERE [E..]` and make your change (recipes in §2–§6).

**Step 3 — Build the pages:**

```bash
python tools/build_site.py
```

✅ Ends with `Done.` ❌ An error names a line number: check the quotes and commas on that line (EDITING-GUIDE §3).

**Step 4 — Preview on your computer:**

```bash
python tools/serve.py
```

🖱️ Open **http://127.0.0.1:8123** in your browser and check your change. Press **Ctrl + C** in Git Bash to stop the preview.

**Step 5 — Publish** (details in §7). Replace the message in quotes with a few words about your change:

```bash
git add -A && git commit -m "Describe your change"; git pull --no-rebase --no-edit -X theirs origin main && python tools/build_site.py && git add -A && (git diff --cached --quiet || git commit -m "Rebuild pages") && git push -u origin main
```

✅ The last lines show `main -> main`. Vercel puts the site live within 1–2 minutes.

---

## 2. Text recipes

### 2.1 Change the phone or WhatsApp number — `[E01]` + `[J01]`

1. ⌨️ Ctrl + Shift + F → `[E01]` → open `tools/build_site.py`.
2. Change `PHONE_TXT`, `PHONE_TEL` and `WA`:
   ```python
   PHONE_TXT = '+91 90000 00000'
   PHONE_TEL = '+919000000000'
   WA = '919000000000'
   ```
3. ⌨️ Search `[J01]` → `assets/js/dive-adda.js` → set `WA_NUMBER = '919000000000';`
4. Build → preview → publish (§1).
5. ✅ On the live site, tap the 📞 and WhatsApp buttons; both use the new number.

### 2.2 Change the homepage headline or badge — `[E16]`

1. Search `[E16b]` (main sentence) or `[E16a]` (badge).
2. Change only the words between `>` and `<`:
   ```html
   <p class="hero-lead …">Your new sentence here.</p>
   ```
3. Build → preview → publish.

### 2.3 Edit a course description — `[E03]`

1. Search `[E03]`, find the course (for example `id='react-right'`).
2. Edit `short=` (card), `long=` (page paragraph), `who=` and the `learn=[…]` list.
3. Build → preview `http://127.0.0.1:8123/react-right.html` → publish.

### 2.4 Add a FAQ — `[E13]`

1. Search `[E13]`.
2. Copy the last question block and paste it **before** the closing `]`:
   ```python
       ('Can I dive if I wear glasses?',
        'Yes. Tell us when you book and we will arrange a suitable mask.'),
   ]
   ```
   Keep the comma after `)`, and use `&rsquo;` for apostrophes inside the text.
3. Build → preview `faq.html` → publish.

### 2.5 Add an activity to a location — `[E02]`

1. Search `[E02]`, find `acts=[` under the right city.
2. Add a line:
   ```python
   ('parasailing', 'Parasailing', 'spark', 'Fly above the beach, towed by a boat.', None),
   ```
3. Add the photo `assets/img/activities/parasailing.jpg` (§3.1).
4. Run `python tools/optimize_images.py`, then build → preview → publish.

### 2.6 Add a whole new SSI course — `[E03]`

1. Search `[E03]`. Copy one complete `dict( … ),` block and paste it after the last course.
2. Change `id`, `file` (for example `scuba-diver.html`), `name`, `full`, `level`, `step`, `short`, `long`, `who`, `learn`.
3. Add the image `assets/img/courses/<id>.jpg` (for example `scuba-diver.jpg`).
4. Run `python tools/optimize_images.py`, then build. ✅ The new page, menu entry and sitemap entry appear automatically.

### 2.7 Update a policy — `[E22]`

1. Search `[E22]`. Edit the text inside the right `sections=[ ( 'Heading', '<p>…</p>' ) ]`.
2. Change `LEGAL_UPDATED = '…'` to today's date.
3. Build → preview → publish.

---

## 3. Image recipes

### 3.1 Replace a photo (keep the same name) — easiest

1. Find the current file name (EDITING-GUIDE §5), for example `assets/img/activities/kayaking.jpg`.
2. Prepare your photo: **JPG**, about **1600 px wide**, no other company's logo or phone number on it.
3. 🖱️ Copy your photo into that folder and **rename it to exactly** `kayaking.jpg`; replace the old file when Windows asks.
4. Run:
   ```bash
   python tools/optimize_images.py
   ```
   ```bash
   python tools/build_site.py
   ```
5. Preview → publish (§1).
6. ✅ The new photo appears on every page that used the old one. On your own browser, press **Ctrl + F5** to clear the old copy.

### 3.2 Use a new photo in a section

1. Copy `my-new-photo.jpg` into `assets/img/brochure/`.
2. In the code, change the reference, for example in `[E18]`:
   ```python
   photo(B('boat-diving'), …)      →      photo(B('my-new-photo'), …)
   ```
   Also update the description text next to it (it's read aloud to blind visitors and helps Google).
3. Run `optimize_images.py` → build → preview → publish.

### 3.3 Add a photo to the gallery — `[E11]`

1. Copy the photo into `assets/img/brochure/`, for example `night-dive.jpg`.
2. Search `[E11]` and add a line inside `GALLERY = [ … ]`:
   ```python
   (B('night-dive'), 'diving', 'Night dive', 'Torches on the reef', ''),
   ```
3. `optimize_images.py` → build → preview `gallery.html` → publish.

### 3.4 Add a photo to the water sports carousel — `[E19]`

1. Copy the photo into `assets/img/activities/`, for example `beach-sunset.jpg`.
2. Search `[E19]` and add a line inside `WS_SLIDES = [ … ]`:
   ```python
   ('assets/img/activities/beach-sunset.jpg', 'Sunset at IT-SEZ Beach', 'IT-SEZ Beach &middot; Visakhapatnam'),
   ```
3. `optimize_images.py` → build → preview → publish. ✅ An extra dot appears under the carousel.

### 3.5 Change a course image — `[E03]`

Replace `assets/img/courses/<id>.jpg` as in 3.1, for example `open-water.jpg`. It updates the homepage card, `courses.html` and the course page together. SSI course cards look best at **1280 × 813 px**.

### 3.6 Change a logo

Replace `assets/img/logo-mark.png` (and `logo-mark-light.png` for light mode) with **transparent PNG** files of the same shape, then run `optimize_images.py` → build → publish.

---

## 4. Style recipes — `[S01]` / `[S02]`

**Change a brand colour:** search `[S01]` in `assets/css/dive-adda.css`, change a value such as `--ink-dim: #9FBCD0;`, then build.

**Add your own style rule:** search `[S02]` in `assets/css/dive-adda-responsive.css`, write at the **very end**:

```css
.hero-lead { font-size: 1.3rem; }
```

Build → preview **in both themes** (🌙/☀️ switch in the menu) **and on a phone width** (browser DevTools → 📱) → publish.

---

## 5. Reviews (Google + Tripadvisor) — one-time setup

Real reviews are fetched automatically every day by GitHub. They need two keys.

**Google**
1. 🖱️ console.cloud.google.com → create or select a project → **APIs & Services → Library** → enable **Places API (New)**. Only this one is needed.
2. **APIs & Services → Credentials → Create credentials → API key**. Restrict it to *Places API (New)*.
3. Billing must be enabled; a once-a-day fetch stays inside Google's free monthly usage.

**Tripadvisor**
4. Sign up for the **Tripadvisor Content API** and copy your key.

**GitHub**
5. 🖱️ github.com/K4LYAN/scuba-diving- → **Settings → Secrets and variables → Actions → New repository secret**, three times:

| Name | Value |
|---|---|
| `GOOGLE_PLACES_API_KEY` | the Google key |
| `TRIPADVISOR_API_KEY` | the Tripadvisor key |
| `GOOGLE_PLACE_ID` | optional: your Google place ID |

6. 🖱️ **Actions → Refresh reviews → Run workflow**.
7. ✅ A minute later, a commit "Refresh Google and Tripadvisor reviews" appears. On your computer, run `git pull origin main`.

> 🔒 Never paste keys into the code or a chat. They belong **only** in GitHub secrets.

---

## 6. Domain and hosting (Vercel + Namecheap)

The site is hosted on **Vercel**, which deploys automatically on every push to GitHub. The domain is registered at **Namecheap**.

**Correct DNS** (Namecheap → Domain List → Manage → **Advanced DNS**). There should be exactly these two host records:

| Type | Host | Value |
|---|---|---|
| A Record | `@` | `216.198.79.1` |
| CNAME Record | `www` | the value Vercel shows (currently `d3d5f314928bd12d.vercel-dns-017.com.`) |

There should be no "URL Redirect Record" and no other `@` A records.

✅ Vercel → project → **Settings → Domains** shows **Valid Configuration** for both `diveaddaindia.com` and `www.diveaddaindia.com`.

**Check a deployment:** Vercel → **Deployments**. The newest row should say **Ready**. If it says *Error*, click it to read why.

---

## 7. Publishing to GitHub: explained

### 7.1 The publish command, piece by piece

```bash
git add -A && git commit -m "Describe your change"; git pull --no-rebase --no-edit -X theirs origin main && python tools/build_site.py && git add -A && (git diff --cached --quiet || git commit -m "Rebuild pages") && git push -u origin main
```

| Part | What it does |
|---|---|
| `git add -A` | stages every changed file (except those in `.gitignore`) |
| `git commit -m "…"` | saves a snapshot with your message |
| `git pull --no-rebase --no-edit -X theirs origin main` | brings in GitHub's changes (often the daily review bot). On a clash in a generated page it keeps GitHub's copy, which is fine because the next step rebuilds every page anyway |
| `python tools/build_site.py` | rebuilds all pages so they include your change **and** the latest reviews |
| `git add -A && (… git commit -m "Rebuild pages")` | commits the rebuild only if something changed |
| `git push -u origin main` | uploads to GitHub → Vercel deploys automatically |

### 7.2 After pushing

1. ✅ Git Bash ends with something like `18505a7..a1b2c3d  main -> main`.
2. 🖱️ Vercel → Deployments → newest = **Ready** (1–2 minutes).
3. 🖱️ Open https://www.diveaddaindia.com → **Ctrl + F5** → check your change.

### 7.3 Checklist before you push

- [ ] `python tools/build_site.py` ended with `Done.`
- [ ] Previewed the changed page at http://127.0.0.1:8123
- [ ] Checked it on a phone-sized window and in light **and** dark theme
- [ ] New photos are JPG, sensibly sized, and have no third-party logos or phone numbers
- [ ] Ran `python tools/optimize_images.py` if you added or replaced a photo
- [ ] No API keys, passwords or personal files in the change (`git status` lists what will be uploaded)

---

## 8. Git troubleshooting

| Message | What it means | Do this |
|---|---|---|
| `nothing to commit, working tree clean` | Everything is already saved | Just run `git push -u origin main` |
| `Your local changes … would be overwritten by merge` | You pulled before committing | Use the full publish command from §1 (it commits first) |
| `rejected … (non-fast-forward)` | GitHub has newer commits | Run the full publish command again; it pulls first |
| `File … exceeds GitHub's file size limit of 100 MB` | A video or zip got included | Ask for help: the commit must be redone without it. Keep raw media in `static post/` (ignored) |
| `CONFLICT (content): Merge conflict in index.html` | Two versions of a generated page | `python tools/build_site.py`, then `git add -A`, `git commit -m "Merge and rebuild"`, `git push` |
| A screen full of `~` lines opens | Git opened its text editor (Vim) | Type `:wq` and press Enter |
| `LF will be replaced by CRLF` | Windows line-ending notice | Harmless, ignore |
| `npx not found` / Tailwind error | Node.js missing | Install Node.js LTS (§0), reopen Git Bash |
| `No module named PIL` | Pillow missing | `pip install pillow` |

**Undo a change you haven't committed yet** (⚠️ this throws away your edits to that file):

```bash
git checkout -- tools/build_site.py
```

**See what will be uploaded before you commit:**

```bash
git status
```

---

## 9. Performance check (optional, after big changes)

1. 🖱️ Open https://pagespeed.web.dev, paste `https://www.diveaddaindia.com`, and click **Analyze**.
2. ✅ Aim for **90+** on Mobile and Desktop. Test in an Incognito window or on PageSpeed itself, because browser extensions lower the score.
3. If the score drops after adding photos: did you run `optimize_images.py`? Are the photos larger than 2000 px or 1 MB?
