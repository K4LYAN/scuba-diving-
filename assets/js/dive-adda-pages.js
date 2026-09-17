/* ================================================================
   DIVE ADDA — MULTI-PAGE INTERACTIONS
   Loaded after dive-adda.js, so it can use REDUCE_MOTION, HAS_GSAP,
   IS_MOBILE, rand() and openChat() from the master script.
   ================================================================ */
(function () {
    const $ = (s, r) => (r || document).querySelector(s);
    const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));

    /* ---------- 1. Book controls: open the assistant with context ---------- */
    document.addEventListener('click', (e) => {
        const b = e.target.closest ? e.target.closest('[data-book]') : null;
        if (!b) return;
        e.preventDefault();
        openChat({
            destination: b.getAttribute('data-destination') || '',
            experience: b.getAttribute('data-experience') || ''
        });
    });

    /* ---------- 2. Desktop dropdowns: hover, click and keyboard ---------- */
    const items = $$('.nav-item');
    function closeAll(except) { items.forEach((it) => { if (it !== except) { it.classList.remove('open'); const t = $('.nav-link', it); if (t) t.setAttribute('aria-expanded', 'false'); } }); }
    items.forEach((it) => {
        const trigger = $('button.nav-link', it);
        if (!trigger) return;
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const open = !it.classList.contains('open');
            closeAll(it);
            it.classList.toggle('open', open);
            trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
        it.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { closeAll(); trigger.focus(); }
        });
    });
    document.addEventListener('click', (e) => { if (!e.target.closest('.nav-item')) closeAll(); });

    /* ---------- 2b. Locations flyout: choose a location, see its activities ---------- */
    $$('.loc-drop').forEach((drop) => {
        const tabs = $$('.loc-tab', drop);
        const show = (tab) => tabs.forEach((t) => {
            const on = t === tab;
            t.setAttribute('aria-selected', on ? 'true' : 'false');
            const panel = document.getElementById(t.getAttribute('aria-controls'));
            if (panel) panel.hidden = !on;
        });
        tabs.forEach((t, i) => {
            t.addEventListener('click', (e) => { e.stopPropagation(); show(t); });
            t.addEventListener('mouseenter', () => show(t));
            t.addEventListener('focus', () => show(t));
            t.addEventListener('keydown', (e) => {
                if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
                e.preventDefault();
                tabs[(i + (e.key === 'ArrowDown' ? 1 : tabs.length - 1)) % tabs.length].focus();
            });
        });
    });

    /* ---------- 3. Mark the current page in the navigation ---------- */
    const page = document.body.getAttribute('data-page');
    if (page) {
        $$('[data-nav="' + page + '"]').forEach((a) => { a.classList.add('is-active'); a.setAttribute('aria-current', 'page'); });
        $$('.city-chip[data-city="' + page + '"]').forEach((a) => a.classList.add('is-current'));
    }

    /* ---------- 4. Depth meter: scroll progress reads as metres ---------- */
    const meter = $('#depthMeter');
    if (meter) {
        const fill = $('.dm-fill', meter);
        const read = $('.dm-read', meter);
        // Every page reads the same scale: 0 m at the top of the page, 40 m at the bottom
        const base = 0;
        const span = 40;
        let ticking = false;
        const paint = () => {
            ticking = false;
            const max = document.documentElement.scrollHeight - innerHeight;
            const p = max > 0 ? Math.min(Math.max(scrollY / max, 0), 1) : 0;
            fill.style.transform = 'scaleY(' + p.toFixed(3) + ')';
            const m = Math.round(base + span * p);
            read.textContent = (m ? '-' : '') + m + 'm';
        };
        addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(paint); } }, { passive: true });
        paint();
    }

    /* ---------- 5. Hero destination selector ---------- */
    $$('[data-dest-select]').forEach((wrap) => {
        const buttons = $$('button[data-dest]', wrap);
        const panel = document.getElementById(wrap.getAttribute('data-dest-select'));
        const tpl = (id) => document.getElementById('destTpl-' + id);
        function pick(btn) {
            buttons.forEach((b) => b.setAttribute('aria-selected', b === btn ? 'true' : 'false'));
            const t = tpl(btn.getAttribute('data-dest'));
            if (panel && t) { panel.innerHTML = ''; panel.appendChild(t.content.cloneNode(true)); }
        }
        buttons.forEach((b) => {
            b.addEventListener('click', () => pick(b));
            b.addEventListener('keydown', (e) => {
                const i = buttons.indexOf(b);
                if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const n = buttons[(i + (e.key === 'ArrowRight' ? 1 : buttons.length - 1)) % buttons.length];
                    n.focus(); pick(n);
                }
            });
        });
        if (buttons[0]) pick(buttons[0]);
    });

    /* ---------- 6. Carousels ---------- */
    $$('.carousel').forEach((car) => {
        const track = $('.carousel-track', car);
        const slides = $$('.carousel-track > *', car);
        const dotsWrap = $('.car-dots', car);
        if (!track || !slides.length) return;
        let current = 0, timer = null;

        const dots = slides.map((s, i) => {
            if (!dotsWrap) return null;
            const d = document.createElement('button');
            d.type = 'button';
            d.setAttribute('aria-label', 'Show ' + (s.getAttribute('data-label') || 'slide ' + (i + 1)));
            d.addEventListener('click', () => { go(i); stop(); });
            dotsWrap.appendChild(d);
            return d;
        });

        function go(i) {
            current = (i + slides.length) % slides.length;
            const s = slides[current];
            track.scrollTo({ left: s.offsetLeft - (track.clientWidth - s.clientWidth) / 2, behavior: REDUCE_MOTION ? 'auto' : 'smooth' });
        }
        function sync() {
            const mid = track.scrollLeft + track.clientWidth / 2;
            let best = 0, bd = Infinity;
            slides.forEach((s, i) => { const d = Math.abs(s.offsetLeft + s.clientWidth / 2 - mid); if (d < bd) { bd = d; best = i; } });
            current = best;
            dots.forEach((d, i) => d && d.setAttribute('aria-current', i === best ? 'true' : 'false'));
            if (car.hasAttribute('data-map-sync') && window.__focusDestination) {
                const id = slides[best].getAttribute('data-dest-id');
                if (id && car.__lastDest !== id) { car.__lastDest = id; if (car.__synced) window.__focusDestination(id); }
            }
        }
        let st = null;
        track.addEventListener('scroll', () => { clearTimeout(st); st = setTimeout(() => { car.__synced = true; sync(); }, 90); }, { passive: true });

        const prev = $('[data-car-prev]', car), next = $('[data-car-next]', car);
        if (prev) prev.addEventListener('click', () => { go(current - 1); stop(); });
        if (next) next.addEventListener('click', () => { go(current + 1); stop(); });
        track.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') { e.preventDefault(); go(current + 1); stop(); }
            if (e.key === 'ArrowLeft') { e.preventDefault(); go(current - 1); stop(); }
        });

        function start() { if (REDUCE_MOTION || !car.hasAttribute('data-autoplay')) return; stop(); timer = setInterval(() => go(current + 1), 6500); }
        function stop() { if (timer) clearInterval(timer); timer = null; }
        car.addEventListener('pointerenter', stop);
        car.addEventListener('focusin', stop);
        car.addEventListener('touchstart', stop, { passive: true });
        sync();
        // Only cycle while the carousel is on screen
        if ('IntersectionObserver' in window) {
            new IntersectionObserver((es) => es.forEach((en) => (en.isIntersecting ? start() : stop())), { threshold: 0.4 }).observe(car);
        }
    });

    /* ---------- 7. Expanding info cards ---------- */
    $$('.info-card[aria-expanded]').forEach((c) => {
        c.addEventListener('click', () => c.setAttribute('aria-expanded', c.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'));
    });

    /* ---------- 8. Activity switcher ---------- */
    $$('[data-act]').forEach((root) => {
        const tabs = $$('.act-tab', root);
        const slides = $$('.act-slide', root);
        function show(i) {
            tabs.forEach((t, k) => { t.setAttribute('aria-selected', k === i ? 'true' : 'false'); t.tabIndex = k === i ? 0 : -1; });
            slides.forEach((s, k) => { s.classList.toggle('is-on', k === i); s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
        }
        tabs.forEach((t, i) => {
            t.addEventListener('click', () => show(i));
            t.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); const n = (i + 1) % tabs.length; tabs[n].focus(); show(n); }
                if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); const n = (i + tabs.length - 1) % tabs.length; tabs[n].focus(); show(n); }
            });
        });
        show(0);
    });

    /* ---------- 9. First-dive journey: lights up as you scroll ---------- */
    $$('.journey').forEach((j) => {
        const steps = $$('.j-step', j);
        const line = $('.journey-line', j);
        let ticking = false;
        const paint = () => {
            ticking = false;
            const r = j.getBoundingClientRect();
            const vh = innerHeight;
            const p = Math.min(Math.max((vh * 0.78 - r.top) / (r.height + vh * 0.2), 0), 1);
            if (line) line.style.setProperty('--jp', p.toFixed(3));
            steps.forEach((s, i) => s.classList.toggle('lit', p >= (i + 0.35) / steps.length));
        };
        addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(paint); } }, { passive: true });
        addEventListener('resize', paint, { passive: true });
        addEventListener('dive:entered', paint);
        paint();
    });

    /* ---------- 10. Gallery filters + full-screen lightbox ---------- */
    const lb = $('#lightbox');
    let lbList = [], lbIndex = 0, lbLast = null;

    function lbShow(i) {
        if (!lbList.length) return;
        lbIndex = (i + lbList.length) % lbList.length;
        const t = lbList[lbIndex];
        const img = $('img', t);
        const big = $('#lbImg');
        big.src = img.getAttribute('data-full') || img.currentSrc || img.src;
        big.alt = img.alt;
        $('#lbCap').textContent = t.getAttribute('data-caption') || img.alt;
        $('#lbCount').textContent = (lbIndex + 1) + ' / ' + lbList.length;
    }
    function lbOpen(tile, scope) {
        if (!lb) return;
        lbList = $$('.gallery-tile:not(.is-hidden)', scope);
        lbLast = document.activeElement;
        lb.classList.add('open');
        document.documentElement.classList.add('modal-open');
        lbShow(lbList.indexOf(tile));
        requestAnimationFrame(() => lb.classList.add('in'));
        setTimeout(() => lb.classList.add('in'), 60);
        setTimeout(() => $('.lb-close', lb).focus({ preventScroll: true }), 200);
    }
    function lbClose() {
        if (!lb || !lb.classList.contains('open')) return;
        lb.classList.remove('in');
        document.documentElement.classList.remove('modal-open');
        setTimeout(() => lb.classList.remove('open'), 380);
        if (lbLast && lbLast.focus) lbLast.focus({ preventScroll: true });
    }
    if (lb) {
        $('.lb-close', lb).addEventListener('click', lbClose);
        $('.lb-backdrop', lb).addEventListener('click', lbClose);
        $('.lb-prev', lb).addEventListener('click', () => lbShow(lbIndex - 1));
        $('.lb-next', lb).addEventListener('click', () => lbShow(lbIndex + 1));
        document.addEventListener('keydown', (e) => {
            if (!lb.classList.contains('open')) return;
            if (e.key === 'Escape') lbClose();
            if (e.key === 'ArrowRight') lbShow(lbIndex + 1);
            if (e.key === 'ArrowLeft') lbShow(lbIndex - 1);
        });
        let sx = null;
        lb.addEventListener('touchstart', (e) => { sx = e.touches[0].clientX; }, { passive: true });
        lb.addEventListener('touchend', (e) => {
            if (sx === null) return;
            const dx = e.changedTouches[0].clientX - sx;
            if (Math.abs(dx) > 50) lbShow(lbIndex + (dx < 0 ? 1 : -1));
            sx = null;
        }, { passive: true });
    }

    $$('[data-gallery]').forEach((g) => {
        const tiles = $$('.gallery-tile', g);
        tiles.forEach((t) => {
            const b = $('.g-open', t);
            if (b) b.addEventListener('click', () => lbOpen(t, g));
        });
        const bar = document.querySelector('[data-filter-for="' + g.id + '"]');
        if (!bar) return;
        const btns = $$('.filter-btn', bar);
        btns.forEach((btn) => btn.addEventListener('click', () => {
            const f = btn.getAttribute('data-filter');
            btns.forEach((b) => b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'));
            tiles.forEach((t) => {
                const cats = (t.getAttribute('data-cat') || '').split(' ');
                const show = f === 'all' || cats.indexOf(f) !== -1;
                t.classList.toggle('is-hidden', !show);
                if (show) { t.classList.remove('is-entering'); void t.offsetWidth; t.classList.add('is-entering'); t.classList.add('active'); }
            });
        }));
    });

    /* ---------- 11. Team profile modal ---------- */
    const pm = $('#profileModal');
    if (pm) {
        let last = null;
        const open = (card) => {
            last = document.activeElement;
            ['name', 'role', 'cert', 'exp', 'spec', 'bio'].forEach((k) => {
                const el = $('[data-p="' + k + '"]', pm);
                if (el) el.textContent = card.getAttribute('data-' + k) || '';
            });
            const av = $('[data-p="avatar"]', pm);
            if (av) av.innerHTML = $('.team-avatar', card) ? $('.team-avatar', card).innerHTML : '';
            pm.classList.add('open');
            document.documentElement.classList.add('modal-open');
            requestAnimationFrame(() => pm.classList.add('in'));
            setTimeout(() => pm.classList.add('in'), 60);
            setTimeout(() => $('[data-modal-close]', pm) && $('.pm-close', pm).focus({ preventScroll: true }), 300);
        };
        const close = () => {
            if (!pm.classList.contains('open')) return;
            pm.classList.remove('in');
            document.documentElement.classList.remove('modal-open');
            setTimeout(() => pm.classList.remove('open'), 420);
            if (last && last.focus) last.focus({ preventScroll: true });
        };
        $$('[data-profile]').forEach((c) => {
            c.addEventListener('click', () => open(c));
            c.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(c); } });
        });
        $$('[data-modal-close]', pm).forEach((b) => b.addEventListener('click', close));
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    }

    /* ---------- 12. FAQ: one answer open at a time within a group ---------- */
    $$('[data-faq-group]').forEach((grp) => {
        const items = $$('details.faq-item', grp);
        items.forEach((d) => d.addEventListener('toggle', () => {
            if (d.open) items.forEach((o) => { if (o !== d) o.open = false; });
        }));
    });

    /* ---------- 13. Footer year ---------- */
    $$('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
