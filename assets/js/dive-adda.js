        /* ==========================================================
           0. MOTION ENVIRONMENT
           ========================================================== */
        const REDUCE_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const HAS_GSAP = typeof window.gsap !== 'undefined';
        const IS_MOBILE = window.matchMedia('(max-width: 767px)').matches;
        const LOW_POWER = IS_MOBILE || (navigator.hardwareConcurrency || 4) <= 4;

        const rand = (min, max) => Math.random() * (max - min) + min;

        // Single source of truth for the WhatsApp number used by the booking
        // handoff and the enquiry fallback (the floating button carries it in
        // its href so it keeps working without JavaScript).
        const WA_NUMBER = '918977762155';   // Dive Adda: +91 89777 62155

        /* ==========================================================
           1. AMBIENT PARTICLES (plankton / micro-bubbles)
           ========================================================== */
        function seedParticles(host, count, opts = {}) {
            if (!host || REDUCE_MOTION) return;
            const frag = document.createDocumentFragment();
            for (let i = 0; i < count; i++) {
                const p = document.createElement('span');
                p.className = 'particle';
                const size = rand(opts.minSize || 2, opts.maxSize || 7);
                p.style.setProperty('--x', rand(0, 100).toFixed(2) + '%');
                p.style.setProperty('--size', size.toFixed(1) + 'px');
                p.style.setProperty('--dur', rand(opts.minDur || 20, opts.maxDur || 46).toFixed(1) + 's');
                p.style.setProperty('--delay', (-rand(0, opts.maxDur || 46)).toFixed(1) + 's');
                p.style.setProperty('--drift', rand(-70, 70).toFixed(0) + 'px');
                p.style.setProperty('--peak', rand(0.18, 0.62).toFixed(2));
                frag.appendChild(p);
            }
            host.appendChild(frag);
        }

        seedParticles(document.getElementById('particleField'), LOW_POWER ? 14 : 34);
        seedParticles(document.getElementById('gateParticles'), LOW_POWER ? 10 : 22, { minSize: 3, maxSize: 10, minDur: 14, maxDur: 30 });

        /* ==========================================================
           1b. MARINE LIFE — fish crossing the background
           ========================================================== */
        const DEPTHS = {
            far:  { cls: 'd-far',  dur: [70, 120], size: [26, 42], bob: [3, 6],  wag: [1.15, 1.5] },
            mid:  { cls: 'd-mid',  dur: [46, 78],  size: [46, 70], bob: [5, 9],  wag: [0.85, 1.15] },
            near: { cls: 'd-near', dur: [30, 52],  size: [78, 118], bob: [8, 13], wag: [0.6, 0.85] }
        };

        function makeFish(species, depth, opts) {
            const tpl = document.getElementById(species);
            if (!tpl) return null;
            const d = DEPTHS[depth];
            const o = opts || {};

            const fish = document.createElement('div');
            fish.className = 'fish ' + d.cls;

            // Half swim left-to-right, half the other way (artwork mirrors)
            const rtl = o.rtl !== undefined ? o.rtl : Math.random() < 0.5;
            if (rtl) {
                fish.classList.add('rtl');
                fish.style.setProperty('--from', '126vw');
                fish.style.setProperty('--to', '-26vw');
            }

            const dur = o.dur || rand(d.dur[0], d.dur[1]);
            fish.style.setProperty('--top', (o.top !== undefined ? o.top : rand(6, 88)).toFixed(2) + '%');
            fish.style.setProperty('--size', (o.size || rand(d.size[0], d.size[1])).toFixed(0) + 'px');
            fish.style.setProperty('--dur', dur.toFixed(1) + 's');
            fish.style.setProperty('--delay', (-rand(0, dur)).toFixed(1) + 's');   // already mid-crossing
            fish.style.setProperty('--bob', rand(d.bob[0], d.bob[1]).toFixed(1) + 'px');
            fish.style.setProperty('--bob-dur', rand(4.2, 7.5).toFixed(2) + 's');
            fish.style.setProperty('--wag', rand(d.wag[0], d.wag[1]).toFixed(2) + 's');

            const bob = document.createElement('div');
            bob.className = 'fish-bob';
            bob.appendChild(tpl.content.cloneNode(true));
            fish.appendChild(bob);
            return fish;
        }

        // A shoal is one moving wrapper with members pinned inside, so a
        // blurred distant shoal rasterises once and is then only translated.
        function makeShoal(count, depth, opts) {
            const tpl = document.getElementById('tplJack');
            if (!tpl) return null;
            const d = DEPTHS[depth];
            const o = opts || {};

            const fish = document.createElement('div');
            fish.className = 'fish ' + d.cls;

            const rtl = o.rtl !== undefined ? o.rtl : Math.random() < 0.5;
            if (rtl) {
                fish.classList.add('rtl');
                fish.style.setProperty('--from', '126vw');
                fish.style.setProperty('--to', '-26vw');
            }

            const dur = rand(d.dur[0], d.dur[1]);
            fish.style.setProperty('--top', rand(8, 84).toFixed(2) + '%');
            fish.style.setProperty('--size', rand(150, 230).toFixed(0) + 'px');
            fish.style.setProperty('--dur', dur.toFixed(1) + 's');
            fish.style.setProperty('--delay', (-rand(0, dur)).toFixed(1) + 's');

            const shoal = document.createElement('div');
            shoal.className = 'shoal';
            for (let i = 0; i < count; i++) {
                const m = document.createElement('div');
                m.className = 'shoal-member';
                m.style.left = rand(0, 72).toFixed(1) + '%';
                m.style.top = rand(0, 46).toFixed(1) + '%';
                m.style.width = rand(17, 30).toFixed(1) + '%';
                m.style.opacity = rand(0.55, 1).toFixed(2);
                m.appendChild(tpl.content.cloneNode(true));
                shoal.appendChild(m);
            }
            fish.appendChild(shoal);
            return fish;
        }

        function seedMarineLife() {
            if (REDUCE_MOTION) return;

            const field = document.getElementById('fishField');
            if (field) {
                const cast = LOW_POWER
                    ? [['shoal', 5, 'far'], ['tplReef', 0, 'mid'], ['tplTang', 0, 'mid']]
                    : [['shoal', 7, 'far'], ['shoal', 5, 'far'],
                       ['tplReef', 0, 'mid'], ['tplTang', 0, 'mid'], ['tplJack', 0, 'mid'],
                       ['tplReef', 0, 'near'], ['tplRay', 0, 'far']];

                const frag = document.createDocumentFragment();
                cast.forEach(([kind, n, depth]) => {
                    const el = kind === 'shoal'
                        ? makeShoal(n, depth)
                        : makeFish(kind, depth, kind === 'tplRay' ? { size: 190, dur: 150 } : undefined);
                    if (el) frag.appendChild(el);
                });
                field.appendChild(frag);
            }

            // The hero hides the ambient layer behind its own footage, so it gets
            // its own shoal - this is the screen everybody actually sees.
            const heroField = document.getElementById('heroFish');
            if (heroField) {
                const cast = LOW_POWER
                    ? [['tplReef', 'mid'], ['shoal', 5, 'far']]
                    : [['tplReef', 'mid'], ['tplTang', 'mid'], ['tplJack', 'near'],
                       ['shoal', 7, 'far'], ['shoal', 5, 'mid']];

                const frag = document.createDocumentFragment();
                cast.forEach((item) => {
                    const el = item[0] === 'shoal'
                        ? makeShoal(item[1], item[2])
                        : makeFish(item[0], item[1]);
                    if (el) frag.appendChild(el);
                });
                heroField.appendChild(frag);
            }

            // A little life behind the loader as well
            const gateField = document.getElementById('gateFish');
            if (gateField && !LOW_POWER) {
                const frag = document.createDocumentFragment();
                const shoal = makeShoal(6, 'far', { rtl: false });
                const single = makeFish('tplReef', 'mid', { top: 74 });
                if (shoal) frag.appendChild(shoal);
                if (single) frag.appendChild(single);
                gateField.appendChild(frag);
            }
        }
        seedMarineLife();

        /* ==========================================================
           2. ORGANIC FLOAT — randomize timing so nothing bobs in sync
           ========================================================== */
        function humanizeFloats() {
            document.querySelectorAll('.animate-float, .animate-float-delayed, .float-organic, .bio-pulse').forEach(el => {
                if (!el.style.getPropertyValue('--dur')) {
                    el.style.setProperty('--dur', rand(5.6, 10.4).toFixed(2) + 's');
                }
                el.style.setProperty('--delay', (-rand(0, 6)).toFixed(2) + 's');
                el.style.setProperty('--amp', rand(6, 15).toFixed(1) + 'px');
                el.style.setProperty('--dx', rand(-7, 7).toFixed(1) + 'px');
                el.style.setProperty('--rot', rand(-1.6, 1.6).toFixed(2) + 'deg');
            });
        }
        humanizeFloats();

        /* ==========================================================
           3. LIQUID HOVER + WATER CURSOR
           One pointermove listener and one rAF loop drive the hover
           bloom, the refraction lens, the wake, the ripples and the
           bubble motes. The loop parks itself when nothing is moving.
           ========================================================== */
        (function waterInteractions() {
            const fineHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

            const layer  = document.getElementById('waterCursor');
            const canvas = document.getElementById('waterCanvas');
            const lens   = layer ? layer.querySelector('.wc-lens') : null;
            const dot    = layer ? layer.querySelector('.wc-dot') : null;
            const ctx    = (canvas && canvas.getContext) ? canvas.getContext('2d') : null;

            // Ripples fire on touch too; the lens and wake need a real pointer.
            const CANVAS_FX  = !!ctx && !REDUCE_MOTION;
            const POINTER_FX = CANVAS_FX && fineHover;
            const TRAIL_MAX  = LOW_POWER ? 12 : 24;

            if (POINTER_FX) {
                document.documentElement.classList.add('wc-on');
                if (LOW_POWER) layer.classList.add('wc-nolens');
            }

            /* ---------- shared pointer state ---------- */
            let px = -999, py = -999;      // raw pointer
            let lx = -999, ly = -999;      // spring-lagged lens
            let vhx = 1, vhy = 0;          // last meaningful heading
            let idle = 999;                // frames since the pointer last moved
            let running = false;
            let bloomTarget = null, bloomDirty = false;

            const trail = [], ripples = [], motes = [];
            let sinceRipple = 0;           // distance travelled since the last motion ripple

            /* ---------- canvas sizing ---------- */
            let dpr = 1, W = 0, H = 0;
            function resize() {
                if (!ctx) return;
                dpr = Math.min(window.devicePixelRatio || 1, 2);
                W = window.innerWidth;
                H = window.innerHeight;
                canvas.width = Math.round(W * dpr);
                canvas.height = Math.round(H * dpr);
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            }

            if (CANVAS_FX) {
                resize();
                let queued = false;
                window.addEventListener('resize', () => {
                    if (queued) return;
                    queued = true;
                    requestAnimationFrame(() => { queued = false; resize(); });
                }, { passive: true });
            }

            /* ---------- emitters ---------- */
            function spawnRipple(x, y, strength, delay) {
                if (!CANVAS_FX) return;
                ripples.push({
                    x: x, y: y,
                    t: -(delay || 0),
                    life: 0.75 + strength * 0.55,
                    r0: 4 + strength * 6,
                    r1: 46 + strength * 130,
                    w: 1 + strength * 1.6,
                    a: 0.20 + strength * 0.42
                });
                if (ripples.length > 26) ripples.shift();
            }

            function spawnMote(x, y) {
                if (!CANVAS_FX) return;
                motes.push({
                    x: x + rand(-14, 14),
                    y: y + rand(-10, 10),
                    vx: rand(-0.35, 0.35),
                    vy: rand(-0.5, -0.05),
                    r: rand(0.9, 2.8),
                    t: 0,
                    life: rand(0.7, 1.7)
                });
                if (motes.length > 90) motes.shift();
            }

            /* ---------- painters ---------- */
            function drawWake() {
                const n = trail.length;
                if (n < 3) return;
                const from = Math.max(1, n - 5);
                const speed = trail[n - 1].s;
                const base = Math.min(2 + speed * 0.22, 13);

                // Two passes - a wide soft body plus a bright core - gives the glow
                // without shadowBlur, which is the expensive way to do it.
                for (let pass = 0; pass < 2; pass++) {
                    ctx.beginPath();
                    ctx.moveTo(trail[from - 1].x, trail[from - 1].y);
                    for (let i = from; i < n - 1; i++) {
                        const mx = (trail[i].x + trail[i + 1].x) / 2;
                        const my = (trail[i].y + trail[i + 1].y) / 2;
                        ctx.quadraticCurveTo(trail[i].x, trail[i].y, mx, my);
                    }
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';
                    ctx.lineWidth = pass === 0 ? base : base * 0.36;
                    ctx.strokeStyle = pass === 0 ? 'rgba(34, 211, 238, 0.085)'
                                                 : 'rgba(207, 250, 254, 0.16)';
                    ctx.stroke();
                }
            }

            function drawRipples(dt) {
                for (let i = ripples.length - 1; i >= 0; i--) {
                    const r = ripples[i];
                    r.t += dt;
                    if (r.t < 0) continue;
                    const p = r.t / r.life;
                    if (p >= 1) { ripples.splice(i, 1); continue; }

                    const ease = 1 - Math.pow(1 - p, 3);
                    const rad = r.r0 + (r.r1 - r.r0) * ease;
                    const a = r.a * (1 - p) * (1 - p);

                    ctx.beginPath();
                    ctx.arc(r.x, r.y, rad, 0, 6.2832);
                    ctx.strokeStyle = 'rgba(103, 232, 249, ' + a.toFixed(3) + ')';
                    ctx.lineWidth = Math.max(0.5, r.w * (1 - p * 0.7));
                    ctx.stroke();

                    // Inner crest, trailing the leading edge
                    if (rad > 16) {
                        ctx.beginPath();
                        ctx.arc(r.x, r.y, rad * 0.76, 0, 6.2832);
                        ctx.strokeStyle = 'rgba(207, 250, 254, ' + (a * 0.5).toFixed(3) + ')';
                        ctx.lineWidth = Math.max(0.4, r.w * 0.55 * (1 - p));
                        ctx.stroke();
                    }
                }
            }

            function drawMotes(dt) {
                const f = dt * 60;
                for (let i = motes.length - 1; i >= 0; i--) {
                    const m = motes[i];
                    m.t += dt;
                    if (m.t >= m.life) { motes.splice(i, 1); continue; }
                    m.vy -= 0.014 * f;              // buoyancy
                    m.vx *= 1 - 0.015 * f;
                    m.x += m.vx * f;
                    m.y += m.vy * f;
                    const a = (1 - m.t / m.life) * 0.7;
                    ctx.beginPath();
                    ctx.arc(m.x, m.y, m.r, 0, 6.2832);
                    ctx.fillStyle = 'rgba(207, 250, 254, ' + a.toFixed(3) + ')';
                    ctx.fill();
                }
            }

            /* ---------- the single frame loop ---------- */
            let prev = 0;
            function frame(ts) {
                const dt = prev ? Math.min((ts - prev) / 1000, 0.05) : 0.016;
                prev = ts;

                // Hover bloom (this used to own a second rAF of its own)
                if (bloomDirty && bloomTarget) {
                    const r = bloomTarget.getBoundingClientRect();
                    bloomTarget.style.setProperty('--mx', ((px - r.left) / r.width * 100).toFixed(2) + '%');
                    bloomTarget.style.setProperty('--my', ((py - r.top) / r.height * 100).toFixed(2) + '%');
                    bloomDirty = false;
                }

                if (POINTER_FX) {
                    // Spring toward the pointer, then squash-stretch along the heading
                    const nx = lx + (px - lx) * 0.17;
                    const ny = ly + (py - ly) * 0.17;
                    const dx = nx - lx, dy = ny - ly;
                    lx = nx; ly = ny;

                    const speed = Math.sqrt(dx * dx + dy * dy);
                    if (speed > 0.35) { vhx = dx; vhy = dy; }
                    const stretch = Math.min(speed / 30, 0.34);

                    if (lens) {
                        lens.style.transform =
                            'translate3d(' + lx.toFixed(2) + 'px,' + ly.toFixed(2) + 'px,0) rotate(' +
                            Math.atan2(vhy, vhx).toFixed(3) + 'rad) scale(' +
                            (1 + stretch).toFixed(3) + ',' + (1 - stretch * 0.7).toFixed(3) + ')';
                    }
                    if (dot) {
                        dot.style.transform = 'translate3d(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px,0)';
                    }
                }

                if (CANVAS_FX) {
                    // Fade the previous frame rather than clearing it, so the wake
                    // dissipates into the water instead of snapping off.
                    ctx.globalCompositeOperation = 'destination-out';
                    ctx.fillStyle = 'rgba(0,0,0,0.11)';
                    ctx.fillRect(0, 0, W, H);
                    ctx.globalCompositeOperation = 'lighter';
                    if (POINTER_FX) drawWake();
                    drawRipples(dt);
                    drawMotes(dt);
                    ctx.globalCompositeOperation = 'source-over';
                }

                idle++;
                const settling = POINTER_FX && (Math.abs(px - lx) > 0.5 || Math.abs(py - ly) > 0.5);
                const busy = ripples.length > 0 || motes.length > 0 || settling || idle < 70;

                if (busy && document.visibilityState === 'visible') {
                    requestAnimationFrame(frame);
                } else {
                    // Park the loop: an idle tab must not burn frames
                    running = false;
                    prev = 0;
                    trail.length = 0;
                    if (ctx) ctx.clearRect(0, 0, W, H);
                }
            }

            function kick() {
                if (running || document.visibilityState !== 'visible') return;
                running = true;
                requestAnimationFrame(frame);
            }

            /* ---------- one pointer handler for all of it ---------- */
            if (fineHover && !REDUCE_MOTION) {
                document.addEventListener('pointermove', (e) => {
                    if (e.pointerType === 'touch') return;

                    px = e.clientX;
                    py = e.clientY;
                    idle = 0;

                    const host = e.target.closest ? e.target.closest('.glow-hover') : null;
                    bloomTarget = host;
                    if (host) bloomDirty = true;

                    if (POINTER_FX) {
                        if (lx < -900) { lx = px; ly = py; }   // first sighting: no fly-in
                        layer.classList.add('wc-live');

                        const last = trail[trail.length - 1];
                        const d = last ? Math.hypot(px - last.x, py - last.y) : 0;
                        trail.push({ x: px, y: py, s: d });
                        if (trail.length > TRAIL_MAX) trail.shift();

                        // Motion ripples are gated by DISTANCE travelled, not a timer,
                        // so slow reading stays calm and fast gestures make waves.
                        sinceRipple += d;
                        if (d > 5 && sinceRipple > 150) {
                            sinceRipple = 0;
                            spawnRipple(px, py, 0.34);
                            if (!LOW_POWER) spawnMote(px, py);
                        }
                    }
                    kick();
                }, { passive: true });

                // Fade the cursor out only when the pointer genuinely leaves the
                // window. A bare document mouseleave also fires spuriously as the
                // pointer crosses between elements, which would flicker the lens.
                document.addEventListener('mouseleave', (e) => {
                    const gone = e.relatedTarget === null && (
                        e.clientX <= 0 || e.clientY <= 0 ||
                        e.clientX >= window.innerWidth || e.clientY >= window.innerHeight
                    );
                    if (gone && layer) layer.classList.remove('wc-live');
                }, { passive: true });

                window.addEventListener('blur', () => {
                    if (layer) layer.classList.remove('wc-live');
                }, { passive: true });
            }

            /* ---------- press: button ripple + page-wide water ripple ---------- */
            document.addEventListener('pointerdown', (e) => {
                if (REDUCE_MOTION) return;
                const host = e.target.closest ? e.target.closest('.ripple-host') : null;

                // Contained ripple inside buttons (unchanged)
                if (host) {
                    const r = host.getBoundingClientRect();
                    const span = document.createElement('span');
                    const size = Math.max(r.width, r.height) * 2.4;
                    span.className = 'ripple';
                    span.style.width = span.style.height = size + 'px';
                    span.style.left = (e.clientX - r.left) + 'px';
                    span.style.top = (e.clientY - r.top) + 'px';
                    host.appendChild(span);
                    span.addEventListener('animationend', () => span.remove());
                }

                // Page-wide water ripple, skipped over .ripple-host so the two
                // never stack into a double circle.
                if (CANVAS_FX && !host) {
                    px = e.clientX;
                    py = e.clientY;
                    idle = 0;
                    if (POINTER_FX) {
                        if (lx < -900) { lx = px; ly = py; }
                        layer.classList.add('wc-live');
                    }
                    spawnRipple(px, py, 1);
                    spawnRipple(px, py, 0.6, 0.12);
                    const n = LOW_POWER ? 4 : 8;
                    for (let i = 0; i < n; i++) spawnMote(px, py);
                    kick();
                }
            }, { passive: true });

            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') kick();
            });
        })();

        /* ==========================================================
           4. DESCENT LOADER — auto-playing submerge transition
           ========================================================== */
        (function diveGate() {
            const gate = document.getElementById('diveGate');
            if (!gate) { unlock(); return; }

            let diving = false;

            function unlock() {
                document.documentElement.classList.remove('gate-open');
                document.body.classList.remove('gate-open');
            }

            function spawnRush(count) {
                if (REDUCE_MOTION) return;
                const frag = document.createDocumentFragment();
                for (let i = 0; i < count; i++) {
                    const b = document.createElement('span');
                    b.className = 'rush-bubble';
                    b.style.setProperty('--x', rand(-2, 102).toFixed(2) + '%');
                    b.style.setProperty('--size', rand(5, 26).toFixed(1) + 'px');
                    b.style.setProperty('--dur', rand(1.15, 2.1).toFixed(2) + 's');
                    b.style.setProperty('--delay', rand(0, 0.75).toFixed(2) + 's');
                    b.style.setProperty('--drift', rand(-90, 90).toFixed(0) + 'px');
                    frag.appendChild(b);
                }
                gate.appendChild(frag);
            }

            function revealChrome() {
                document.querySelectorAll('.pre-dive').forEach(el => el.classList.remove('pre-dive'));
            }

            let finished = false;
            function finish() {
                if (finished) return;
                finished = true;
                try { sessionStorage.setItem('da-dived', '1'); } catch (e) {}
                gate.querySelectorAll('.rush-bubble').forEach(b => b.remove());
                gate.style.display = 'none';
                gate.setAttribute('aria-hidden', 'true');
                unlock();
                revealChrome();
                window.dispatchEvent(new Event('dive:entered'));
            }

            function dive(e) {
                if (e) e.preventDefault();
                if (diving) return;
                diving = true;

                if (REDUCE_MOTION || !HAS_GSAP) {
                    gate.classList.add('is-diving-css');
                    revealChrome();
                    unlock();
                    setTimeout(finish, REDUCE_MOTION ? 200 : 1500);
                    return;
                }

                spawnRush(LOW_POWER ? 18 : 34);

                const tl = gsap.timeline({ defaults: { ease: 'power3.inOut' }, onComplete: finish });

                // The descent HUD sinks away, blurring as it drops into the deep
                tl.to('#diveHud', { y: 90, scale: 0.92, opacity: 0, filter: 'blur(16px)', duration: 0.95 }, 0)
                  .to('#diveHint', { y: 40, opacity: 0, duration: 0.6 }, 0)

                  // The water surface sweeps up past the viewer
                  .set('#gateWave', { opacity: 1, yPercent: 30 }, 0.05)
                  .to('#gateWave', { yPercent: -165, duration: 1.55, ease: 'power2.inOut' }, 0.05)

                  // Break-through wash of light
                  .to('#gateWash', { opacity: 0.85, duration: 0.5, ease: 'power2.out' }, 0.45)
                  .to('#gateWash', { opacity: 0, duration: 0.75, ease: 'power2.in' }, 1.0)

                  // Gate dissolves...
                  .to(gate, { opacity: 0, duration: 0.8, ease: 'power2.inOut' }, 1.05)

                  // ...revealing the site, floating up into focus
                  .fromTo('#siteRoot',
                          { scale: 1.06, opacity: 0, y: 26 },
                          { scale: 1, opacity: 1, y: 0, duration: 1.35, ease: 'power2.out',
                            onStart: unlock,
                            onComplete: () => gsap.set('#siteRoot', { clearProps: 'all' }) }, 0.8)

                  // Navigation and floating widgets surface last
                  .add(revealChrome, 1.25);

                // Safety net: requestAnimationFrame is paused while a tab is hidden, and a
                // broken tween must never strand a visitor behind the gate. Jump to the end
                // state if the timeline hasn't landed in a generous window.
                setTimeout(() => {
                    if (finished) return;
                    tl.progress(1, false);
                    finish();
                }, 6000);
            }

            // Keep the site hidden underneath until the dive begins
            if (HAS_GSAP && !REDUCE_MOTION) {
                gsap.set('#siteRoot', { opacity: 0 });
            } else {
                revealChrome();
            }

            /* ---------- auto-playing descent: no sign-in, no click ---------- */
            // Every page of the site has its own depth; the dial descends to it.
            // After the first page of a visit the loader only runs the submerge.
            const TARGET_DEPTH = parseInt(document.body.getAttribute('data-depth') || '18', 10) || 18;
            let QUICK = false;
            try { QUICK = sessionStorage.getItem('da-dived') === '1'; } catch (e) {}
            if (QUICK) gate.classList.add('gate-quick');
            const hudBarNode = document.getElementById('hudBar');
            if (hudBarNode) hudBarNode.setAttribute('aria-valuemax', TARGET_DEPTH);
            const MIN_SHOW_MS = QUICK ? 60 : (REDUCE_MOTION ? 400 : 2400);
            const HARD_CAP_MS = 5000;

            const depthEl = document.getElementById('depthNow');
            const hudBar = document.getElementById('hudBar');
            const hudArc = document.getElementById('hudArc');
            const waterLift = document.getElementById('waterLift');
            const statusEl = document.getElementById('diveStatus');

            const ARC_LEN = 697.43;          // 2 * PI * r, r = 111
            const WATER_TOP = 112;           // dial empty
            const WATER_SPAN = 224;          // travel to fully flooded

            // Stage captions, keyed to depth so the copy tracks the descent
            const STAGES = [
                [0,  'Checking regulators'],
                [4,  'Equalizing pressure'],
                [9,  'Adjusting buoyancy'],
                [14, 'Entering the blue']
            ];
            let stage = -1;

            function paintDepth(v) {
                const d = Math.round(v);
                const p = Math.max(0, Math.min(v / TARGET_DEPTH, 1));

                if (depthEl) depthEl.textContent = d;
                if (hudBar) hudBar.setAttribute('aria-valuenow', d);
                if (hudArc) hudArc.style.strokeDashoffset = (ARC_LEN * (1 - p)).toFixed(2);
                if (waterLift) {
                    waterLift.style.transform = 'translate(0px,' + (WATER_TOP - WATER_SPAN * p).toFixed(2) + 'px)';
                }

                // Swap the caption when the descent crosses into the next stage
                let next = 0;
                for (let i = 0; i < STAGES.length; i++) if (v >= STAGES[i][0]) next = i;
                if (next !== stage && statusEl) {
                    stage = next;
                    statusEl.classList.remove('stage-in');
                    void statusEl.offsetWidth;          // restart the entrance
                    statusEl.textContent = STAGES[next][1];
                    statusEl.classList.add('stage-in');
                }
            }

            if (HAS_GSAP && !REDUCE_MOTION) {
                const depth = { v: 0 };
                gsap.to(depth, {
                    v: TARGET_DEPTH,
                    duration: 1.9,
                    ease: 'power1.inOut',
                    onUpdate: () => paintDepth(depth.v)
                });
            } else {
                paintDepth(TARGET_DEPTH);
            }

            // Submerge once the descent has had time to read AND the page is ready.
            // The hard cap means a slow asset can never hold the page hostage.
            let pageReady = document.readyState === 'complete';
            let minElapsed = false;
            const tryDive = () => { if (pageReady && minElapsed) dive(); };

            setTimeout(() => { minElapsed = true; tryDive(); }, MIN_SHOW_MS);
            if (!pageReady) {
                window.addEventListener('load', () => { pageReady = true; tryDive(); }, { once: true });
            }
            setTimeout(() => dive(), HARD_CAP_MS);

            // Let impatient visitors skip straight through
            gate.addEventListener('pointerdown', () => dive());
            window.addEventListener('keydown', () => dive(), { once: true });
        })();

        /* ==========================================================
           5. NAVBAR SCROLL EFFECT  (original logic preserved)
           ========================================================== */
        const navbar = document.getElementById('navbar');
        const navContainer = document.getElementById('navPill') || navbar.firstElementChild;

        window.addEventListener('scroll', () => {
            navbar.classList.toggle('nav-scrolled', window.scrollY > 50);
            if (window.scrollY > 50) {
                navContainer.classList.add('py-2');
                navContainer.classList.remove('py-3');
                navContainer.classList.add('shadow-[0_20px_60px_-24px_rgba(1,6,13,0.95)]');
            } else {
                navContainer.classList.add('py-3');
                navContainer.classList.remove('py-2');
                navContainer.classList.remove('shadow-[0_20px_60px_-24px_rgba(1,6,13,0.95)]');
            }
        }, { passive: true });

        // Mobile Menu Toggle
        const btn = document.getElementById('mobileMenuBtn');
        const menu = document.getElementById('mobileMenu');

        function setMenu(open) {
            menu.classList.toggle('hidden', !open);
            menu.classList.toggle('flex', open);
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        }

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            setMenu(menu.classList.contains('hidden'));
        });

        // The menu used to stay open after tapping a link, covering the section
        // it had just jumped to.
        menu.addEventListener('click', (e) => {
            if (e.target.closest('a, button')) setMenu(false);
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') setMenu(false);
        });

        document.addEventListener('click', (e) => {
            if (menu.classList.contains('hidden')) return;
            if (!menu.contains(e.target) && !btn.contains(e.target)) setMenu(false);
        });

        /* ==========================================================
           6. CHATBOT — step logic untouched, styling modernised
           ========================================================== */
        const CHAT_DESTINATIONS = ['Vizag', 'Rajahmundry', 'Goa', 'Not sure yet'];
        const CHAT_EXPERIENCES = ['Scuba Diving (first dive)', 'Guided Fun Dive', 'SSI Course', 'Snorkelling', 'Boat Diving', 'Shore Diving', 'Confined Diving', 'Water Sports', 'Underwater Event'];
        const CHAT_LEVELS = ['Never dived before', 'Snorkelled before', 'Certified diver', 'Dive professional'];

        // Each step: the key it fills, the question, and how it is answered
        const CHAT_STEPS = [
            { key: 'name',        ask: () => "Hi there! 👋 Welcome to Dive Adda. I'll help you plan your dive. What's your name?", input: 'text', ph: 'Your name' },
            { key: 'destination', ask: (d) => `Nice to meet you, ${d.name}! Where would you like to dive?`, options: CHAT_DESTINATIONS },
            { key: 'experience',  ask: () => 'Which experience are you interested in?', options: CHAT_EXPERIENCES },
            { key: 'level',       ask: () => 'How much diving have you done so far?', options: CHAT_LEVELS },
            { key: 'date',        ask: () => 'Which date would you prefer?', input: 'date' },
            { key: 'guests',      ask: () => 'How many guests, including you?', input: 'number', ph: 'Number of guests' },
            { key: 'phone',       ask: () => 'Last one: your phone / WhatsApp number, so the dive desk can confirm.', input: 'tel', ph: '+91 …' }
        ];
        const CHAT_LABELS = { name: 'Name', destination: 'Destination', experience: 'Experience', level: 'Diving experience', date: 'Preferred date', guests: 'Guests', phone: 'Phone / WhatsApp' };

        let chatStep = 0;
        let chatStarted = false;
        let chatData = {};
        let chatPrefill = {};

        const escHtml = (t) => String(t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

        // Every "Book" control opens the assistant; data-destination /
        // data-experience on the control pre-answer those steps.
        function openModal(prefill) {
            openChat(prefill);
        }

        function openChat(prefill) {
            const chatWidget = document.getElementById('chatbotWidget');
            chatWidget.classList.remove('hidden');
            chatWidget.classList.add('flex');
            setTimeout(() => {
                chatWidget.classList.remove('translate-y-4', 'opacity-0');
                chatWidget.classList.add('translate-y-0', 'opacity-100');
            }, 10);

            if (prefill && typeof prefill === 'object' && !prefill.type) {
                Object.keys(prefill).forEach((k) => { if (prefill[k]) chatPrefill[k] = prefill[k]; });
            }

            if (!chatStarted) {
                chatStarted = true;
                document.getElementById('chatBody').innerHTML = '';
                askStep();
            }
        }

        function closeChat() {
            const chatWidget = document.getElementById('chatbotWidget');
            chatWidget.classList.remove('translate-y-0', 'opacity-100');
            chatWidget.classList.add('translate-y-4', 'opacity-0');
            setTimeout(() => { chatWidget.classList.add('hidden'); chatWidget.classList.remove('flex'); }, 300);
        }

        function addBotMessage(html, options = [], onPick) {
            const body = document.getElementById('chatBody');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'chat-msg flex items-start gap-2.5 max-w-[92%] transform translate-y-3 opacity-0 origin-bottom-left';
            msgDiv.innerHTML = `
                <div class="chat-avatar w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1">
                    <svg class="w-4 h-4 text-[#02131B]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
                </div>
                <div class="bubble-bot p-3.5 rounded-2xl rounded-tl-sm text-sm leading-relaxed"><div class="chat-text"></div></div>`;
            msgDiv.querySelector('.chat-text').innerHTML = html;

            if (options.length) {
                const wrap = document.createElement('div');
                wrap.className = 'flex flex-col gap-2 mt-3';
                options.forEach((opt) => {
                    const b = document.createElement('button');
                    b.type = 'button';
                    b.className = 'chat-option text-sm py-2.5 px-3.5 rounded-xl text-left font-medium tracking-wide';
                    b.textContent = opt;
                    b.addEventListener('click', () => {
                        wrap.querySelectorAll('button').forEach((x) => { x.disabled = true; x.style.opacity = x === b ? '1' : '0.45'; });
                        if (onPick) onPick(opt); else handleChatOption(opt);
                    });
                    wrap.appendChild(b);
                });
                msgDiv.querySelector('.bubble-bot').appendChild(wrap);
            }

            body.appendChild(msgDiv);
            requestAnimationFrame(() => {
                msgDiv.classList.remove('translate-y-3', 'opacity-0');
                msgDiv.classList.add('translate-y-0', 'opacity-100');
            });
            body.scrollTop = body.scrollHeight;
        }

        function addUserMessage(text) {
            const body = document.getElementById('chatBody');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'chat-msg flex items-start gap-2 max-w-[85%] self-end flex-row-reverse transform translate-y-3 opacity-0';
            msgDiv.innerHTML = '<div class="bubble-user p-3.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed"></div>';
            msgDiv.firstElementChild.textContent = text;
            body.appendChild(msgDiv);
            requestAnimationFrame(() => {
                msgDiv.classList.remove('translate-y-3', 'opacity-0');
                msgDiv.classList.add('translate-y-0', 'opacity-100');
            });
            body.scrollTop = body.scrollHeight;
        }

        function setChatInput(step) {
            const inputArea = document.getElementById('chatInputArea');
            const inputField = document.getElementById('chatInput');
            if (!step || step.options) { inputArea.classList.add('hidden'); return; }
            inputArea.classList.remove('hidden');
            inputField.type = step.input || 'text';
            inputField.placeholder = step.ph || 'Type your answer…';
            inputField.value = '';
            inputField.removeAttribute('min');
            inputField.removeAttribute('max');
            if (step.input === 'date') inputField.min = new Date().toISOString().slice(0, 10);
            if (step.input === 'number') { inputField.min = '1'; inputField.max = '24'; }
            setTimeout(() => inputField.focus({ preventScroll: true }), 350);
        }

        // Ask the current step, silently skipping anything a Book button pre-answered
        function askStep() {
            while (chatStep < CHAT_STEPS.length && chatPrefill[CHAT_STEPS[chatStep].key]) {
                chatData[CHAT_STEPS[chatStep].key] = chatPrefill[CHAT_STEPS[chatStep].key];
                chatStep++;
            }
            if (chatStep >= CHAT_STEPS.length) { showSummary(); return; }
            const step = CHAT_STEPS[chatStep];
            const safe = {};
            Object.keys(chatData).forEach((k) => { safe[k] = escHtml(chatData[k]); });
            setChatInput(step);
            setTimeout(() => addBotMessage(step.ask(safe), step.options || []), chatStep === 0 ? 0 : 500);
        }

        function validChatAnswer(step, v) {
            if (!v) return false;
            if (step.input === 'number') { const n = Number(v); return isFinite(n) && n >= 1 && n <= 24; }
            if (step.input === 'tel') return /^[+()\d\s-]{6,}$/.test(v);
            if (step.input === 'date') return v >= new Date().toISOString().slice(0, 10);
            return true;
        }

        function handleChatInput() {
            const input = document.getElementById('chatInput');
            const text = input.value.trim();
            const step = CHAT_STEPS[chatStep];
            if (!step || step.options) return;
            if (!validChatAnswer(step, text)) {
                input.classList.add('ring-2', 'ring-red-400/60');
                setTimeout(() => input.classList.remove('ring-2', 'ring-red-400/60'), 900);
                return;
            }
            addUserMessage(text);
            input.value = '';
            processChatStep(text);
        }

        function handleChatOption(option) {
            addUserMessage(option);
            processChatStep(option);
        }

        function processChatStep(input) {
            const step = CHAT_STEPS[chatStep];
            if (!step) return;
            chatData[step.key] = input;
            chatStep++;
            askStep();
        }

        function showSummary() {
            setChatInput(null);
            const rows = Object.keys(CHAT_LABELS)
                .filter((k) => chatData[k])
                .map((k) => `<span class="block"><b>${CHAT_LABELS[k]}:</b> ${escHtml(chatData[k])}</span>`)
                .join('');
            setTimeout(() => {
                addBotMessage(`Here is your dive plan:<span class="block mt-2 text-[13px] leading-6">${rows}</span>`, ['Check availability', 'Start over'], (opt) => {
                    addUserMessage(opt);
                    if (opt === 'Start over') { chatStep = 0; chatData = {}; chatPrefill = {}; askStep(); return; }
                    checkAvailability();
                });
            }, 500);
        }

        async function checkAvailability() {
            setTimeout(() => addBotMessage('Saving your request and checking with the dive desk…'), 400);

            const record = Object.assign({ type: 'chat_booking', page: location.pathname }, chatData);
            if (window.saveBookingToDB) {
                try { await window.saveBookingToDB(record); } catch (e) {}
            }

            setTimeout(() => {
                addBotMessage('Opening WhatsApp so the Dive Adda team can confirm availability for your date. See you underwater! 🤿');
                setTimeout(() => {
                    const lines = Object.keys(CHAT_LABELS).filter((k) => chatData[k]).map((k) => `*${CHAT_LABELS[k]}:* ${chatData[k]}`).join('\n');
                    const waText = encodeURIComponent(`Hi Dive Adda! I'd like to check availability.\n\n${lines}`);
                    window.open(`https://wa.me/${WA_NUMBER}?text=${waText}`, '_blank', 'noopener');
                    closeChat();
                    setTimeout(resetChat, 500);
                }, 2200);
            }, 1300);
        }

        function resetChat() {
            chatStep = 0;
            chatStarted = false;
            chatData = {};
            chatPrefill = {};
            const inputField = document.getElementById('chatInput');
            document.getElementById('chatInputArea').classList.remove('hidden');
            inputField.type = 'text';
            inputField.placeholder = 'Type your message...';
            document.getElementById('chatBody').innerHTML = '';
        }

        // Bind enter key for standard text entry submission
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleChatInput();
            });
            document.getElementById('chatSendBtn')?.addEventListener('click', handleChatInput);
        });

        /* ==========================================================
           7. LEAFLET MAP — dark matter tiles + glowing pins
           ========================================================== */
        document.addEventListener('DOMContentLoaded', () => {
            const mapEl = document.getElementById('diveMap');
            if (!mapEl || typeof L === 'undefined') return;

            // City-level pins only. Exact meeting points are shared by the dive
            // desk on booking - no street address is published until confirmed.
            const DESTINATIONS = [
                { id: 'vizag',       name: 'Vizag',       sub: 'Visakhapatnam, Andhra Pradesh', ll: [17.6868, 83.2185], pin: '#22D3EE', note: 'SSI Certified Dive Centre', href: 'vizag.html' },
                { id: 'rajahmundry', name: 'Rajahmundry', sub: 'Andhra Pradesh',               ll: [17.0005, 81.8040], pin: '#A78BFA', note: 'Scuba + water sports',     href: 'rajahmundry.html' },
                { id: 'goa',         name: 'Goa',         sub: 'West coast of India',          ll: [15.4909, 73.8278], pin: '#FF8A5B', note: 'Scuba + water sports',     href: 'goa.html' }
            ];
            const focus = mapEl.getAttribute('data-focus');

            const map = L.map('diveMap', { scrollWheelZoom: false, zoomControl: true });

            const TILE_URLS = {
                dark:  'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                light: 'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'
            };
            const startTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
            const tiles = L.tileLayer(TILE_URLS[startTheme], {
                attribution: 'Tiles &copy; <a href="https://www.esri.com/">Esri</a> &mdash; Esri, DeLorme, NAVTEQ',
                maxZoom: 16
            }).addTo(map);

            window.__diveMap = map;
            window.__diveTiles = tiles;
            window.__tileUrls = TILE_URLS;

            const markers = {};
            DESTINATIONS.forEach((d) => {
                const icon = L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div class="dive-pin" style="--pin:${d.pin}"></div>`,
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                });
                markers[d.id] = L.marker(d.ll, { icon: icon, title: 'Dive Adda ' + d.name }).addTo(map)
                    .bindPopup(`<b style="color:${d.pin};font-size:14px">Dive Adda &middot; ${d.name}</b><br>${d.sub}<br><span style="opacity:.8">${d.note}</span><br><a href="${d.href}" style="color:#67E8F9;font-weight:600">Explore ${d.name} &rarr;</a>`);
            });

            const fit = () => {
                if (focus && markers[focus]) {
                    const d = DESTINATIONS.find((x) => x.id === focus);
                    map.setView(d.ll, 10);
                    markers[focus].openPopup();
                } else {
                    map.fitBounds(L.latLngBounds(DESTINATIONS.map((d) => d.ll)), { padding: [60, 60] });
                }
            };
            fit();
            window.__focusDestination = (id) => {
                const d = DESTINATIONS.find((x) => x.id === id);
                if (!d) return;
                map.flyTo(d.ll, 9, { duration: 1.4 });
                markers[id].openPopup();
            };

            setTimeout(() => { map.invalidateSize(); fit(); }, 500);
            window.addEventListener('dive:entered', () => {
                setTimeout(() => { map.invalidateSize(); fit(); }, 120);
            });
        });

        /* ==========================================================
           8. BUOYANT SCROLL REVEALS  (+ light hero parallax)
           ========================================================== */
        (function scrollPhysics() {
            const observerOptions = {
                root: null,
                rootMargin: '0px 0px -8% 0px',
                threshold: 0.15
            };

            let started = false;

            function initReveals() {
                if (started) return;
                started = true;

                const observer = new IntersectionObserver((entries, observer) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('active');
                            // Optional: Stop observing once revealed
                            // observer.unobserve(entry.target);
                        }
                    });
                }, observerOptions);

                document.querySelectorAll('.reveal').forEach((el) => {
                    // Stagger siblings slightly so groups rise like bubbles, not as a block
                    if (!el.style.getPropertyValue('--rd') && !el.className.match(/delay-\d00/)) {
                        el.style.setProperty('--rd', Math.round(rand(0, 140)) + 'ms');
                    }
                    observer.observe(el);
                });
            }

            // Hero parallax — desktop only, transform-only, so it stays cheap
            function initParallax() {
                if (!HAS_GSAP || REDUCE_MOTION || IS_MOBILE || typeof ScrollTrigger === 'undefined') return;
                gsap.registerPlugin(ScrollTrigger);
                document.querySelectorAll('.page-hero .ph-img').forEach((img) => {
                    gsap.to(img, { yPercent: 12, scale: 1.05, ease: 'none',
                        scrollTrigger: { trigger: img.closest('.page-hero'), start: 'top top', end: 'bottom top', scrub: 0.6 } });
                });
                if (document.getElementById('heroVideo')) gsap.to('#heroVideo', {
                    yPercent: 14,
                    scale: 1.06,
                    ease: 'none',
                    scrollTrigger: { trigger: 'header', start: 'top top', end: 'bottom top', scrub: 0.6 }
                });
                gsap.to('#ambient .rays', {
                    yPercent: -8,
                    ease: 'none',
                    scrollTrigger: { trigger: document.body, start: 'top top', end: 'bottom bottom', scrub: 1.2 }
                });
            }

            window.addEventListener('dive:entered', () => { initReveals(); initParallax(); });

            document.addEventListener('DOMContentLoaded', () => {
                // If the gate is absent (or already dismissed), start immediately
                const gate = document.getElementById('diveGate');
                if (!gate || gate.style.display === 'none') { initReveals(); initParallax(); }
            });
        })();

        /* ==========================================================
           9. THEME SWITCH (dark / light)
           The attribute is set by the bootstrap in <head> before first
           paint; this only wires the control and keeps the map in step.
           ========================================================== */
        (function themeSwitch() {
            const root = document.documentElement;
            const btn = document.getElementById('themeToggle');

            const current = () => (root.getAttribute('data-theme') === 'light' ? 'light' : 'dark');

            function syncMap(theme) {
                // Swap the basemap rather than filter it: a light basemap under a
                // dark tint just reads as muddy, and vice versa.
                if (window.__diveTiles && window.__tileUrls) {
                    window.__diveTiles.setUrl(window.__tileUrls[theme]);
                }
            }

            function apply(theme, persist) {
                root.setAttribute('data-theme', theme);
                if (btn) btn.setAttribute('aria-checked', theme === 'light' ? 'true' : 'false');
                if (persist) {
                    try { localStorage.setItem('db-theme', theme); } catch (e) {}
                }
                syncMap(theme);
            }

            // Reflect whatever the bootstrap chose, without writing a preference
            apply(current(), false);

            if (btn) {
                btn.addEventListener('click', () => apply(current() === 'light' ? 'dark' : 'light', true));
            }

            // The map is built on DOMContentLoaded, after this runs
            document.addEventListener('DOMContentLoaded', () => syncMap(current()));
            window.__setTheme = (t) => apply(t === 'light' ? 'light' : 'dark', true);
        })();

        /* ==========================================================
           10. INQUIRY FORM — validation, submit, success state
           ========================================================== */
        (function inquiryForm() {
            const form = document.getElementById('inquiryForm');
            if (!form) return;

            const panel = form.parentElement;
            const success = document.getElementById('inquirySuccess');
            const formError = document.getElementById('inqFormError');
            const submitBtn = document.getElementById('inqSubmit');
            const dateEl = document.getElementById('inqDate');
            const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
            const PHONE = /^[+()\d\s-]{6,}$/;

            // A preferred date in the past is never useful
            if (dateEl) {
                const today = new Date().toISOString().slice(0, 10);
                dateEl.min = today;
                if (!dateEl.value) dateEl.value = today;
            }

            const fields = Array.prototype.slice.call(form.querySelectorAll('.field-input'));

            // Explore / Book links can pre-select ?destination=&experience=&course=
            try {
                const q = new URLSearchParams(location.search);
                ['destination', 'experience', 'course'].forEach((k) => {
                    const v = q.get(k);
                    const el = form.querySelector('[name="' + k + '"]');
                    if (v && el) {
                        const opt = Array.prototype.find.call(el.options || [], (o) => o.value.toLowerCase() === v.toLowerCase());
                        if (opt) el.value = opt.value;
                    }
                });
            } catch (e) {}

            function validate(el) {
                const v = (el.value || '').trim();
                let ok = true;

                if (el.hasAttribute('required') && !v) ok = false;
                if (ok && el.type === 'email' && v && !EMAIL.test(v)) ok = false;
                if (ok && el.type === 'tel' && v && !PHONE.test(v)) ok = false;
                if (ok && el.type === 'number') {
                    const n = Number(v);
                    if (!isFinite(n) || n < 1 || n > 24) ok = false;
                }
                if (ok && el.type === 'date' && v && dateEl && v < dateEl.min) ok = false;

                const wrap = el.closest('.field');
                if (wrap) wrap.classList.toggle('invalid', !ok);
                return ok;
            }

            fields.forEach((el) => {
                el.addEventListener('blur', () => validate(el));
                el.addEventListener('input', () => {
                    const wrap = el.closest('.field');
                    if (wrap && wrap.classList.contains('invalid')) validate(el);
                });
            });

            function collect() {
                const data = {};
                fields.forEach((el) => { data[el.name] = (el.value || '').trim(); });
                return data;
            }

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const bad = fields.filter((el) => !validate(el));
                if (bad.length) {
                    formError.textContent = bad.length === 1
                        ? 'One field still needs attention.'
                        : bad.length + ' fields still need attention.';
                    formError.classList.remove('hidden');
                    bad[0].focus();
                    return;
                }
                formError.classList.add('hidden');

                const label = submitBtn.querySelector('.inq-label');
                const was = label ? label.textContent : '';
                if (label) label.textContent = 'Sending\u2026';
                submitBtn.disabled = true;

                const data = collect();
                let saved = false;
                if (window.saveBookingToDB) {
                    try {
                        saved = await window.saveBookingToDB(Object.assign({}, data, { type: 'inquiry' }));
                    } catch (err) {
                        saved = false;
                    }
                }

                if (label) label.textContent = was;
                submitBtn.disabled = false;

                // Only claim it reached us when the write actually landed
                const copy = document.getElementById('inqSuccessCopy');
                if (copy) {
                    copy.textContent = saved
                        ? 'Thanks \u2014 your enquiry is logged and the Dive Adda team will get back to you shortly.'
                        : 'Thanks \u2014 we could not reach the booking system just now. Send the same details through on WhatsApp and we will pick them up straight away.';
                }

                window.__inquiryData = data;
                panel.classList.add('inquiry-sent');
                success.classList.add('show');
                success.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });

            function sendToWhatsApp(d, intro) {
                const row = (label, v) => (v ? '*' + label + ':* ' + v + '\n' : '');
                const text = encodeURIComponent(
                    intro + '\n\n' +
                    row('Name', d.name) + row('Phone', d.phone) + row('Email', d.email) +
                    row('Destination', d.destination) + row('Experience', d.experience) +
                    row('Course', d.course) + row('Preferred date', d.date) + row('Guests', d.guests) +
                    (d.message ? '\n' + d.message : '')
                );
                window.open('https://wa.me/' + WA_NUMBER + '?text=' + text, '_blank', 'noopener');
            }

            const wa = document.getElementById('inqWhatsapp');
            if (wa) {
                wa.addEventListener('click', () => sendToWhatsApp(window.__inquiryData || collect(), 'Hi Dive Adda! I sent an enquiry through the website.'));
            }
            const waDirect = document.getElementById('inqWaDirect');
            if (waDirect) {
                waDirect.addEventListener('click', () => sendToWhatsApp(collect(), 'Hi Dive Adda! I have an enquiry.'));
            }

            const again = document.getElementById('inqReset');
            if (again) {
                again.addEventListener('click', () => {
                    form.reset();
                    if (dateEl) dateEl.value = dateEl.min;
                    form.querySelectorAll('.field.invalid').forEach((f) => f.classList.remove('invalid'));
                    formError.classList.add('hidden');
                    panel.classList.remove('inquiry-sent');
                    success.classList.remove('show');
                    const first = document.getElementById('inqName');
                    if (first) first.focus();
                });
            }
        })();

        /* ==========================================================
           11. AUTO "BOOK NOW" MODAL
           Opens once the dive transition has landed, not before.
           ========================================================== */
        (function bookNowModal() {
            const modal = document.getElementById('bookNowModal');
            if (!modal) return;

            let lastFocus = null;

            function open() {
                if (modal.classList.contains('open')) return;
                // Do not stack on top of the assistant if it is already open
                const chat = document.getElementById('chatbotWidget');
                if (chat && !chat.classList.contains('hidden')) return;

                lastFocus = document.activeElement;
                modal.classList.add('open');
                document.documentElement.classList.add('modal-open');
                document.body.classList.add('modal-open');
                // rAF is paused in a hidden tab; a timer is not. Without the second
                // path the dialog can end up open (and blocking) but invisible.
                requestAnimationFrame(() => modal.classList.add('in'));
                setTimeout(() => modal.classList.add('in'), 60);

                const go = document.getElementById('bookModalGo');
                if (go) setTimeout(() => go.focus({ preventScroll: true }), 420);
            }

            function close() {
                if (!modal.classList.contains('open')) return;
                modal.classList.remove('in');
                document.documentElement.classList.remove('modal-open');
                document.body.classList.remove('modal-open');
                setTimeout(() => modal.classList.remove('open'), 420);
                if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
            }

            modal.querySelectorAll('[data-modal-close]').forEach((el) => el.addEventListener('click', close));
            document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

            const go = document.getElementById('bookModalGo');
            if (go) {
                go.addEventListener('click', () => {
                    close();
                    setTimeout(() => openModal(), 260);   // hands over to the chat assistant
                });
            }

            // Keep tabbing inside the dialog while it is open
            modal.addEventListener('keydown', (e) => {
                if (e.key !== 'Tab') return;
                const f = Array.prototype.slice
                    .call(modal.querySelectorAll('button, a[href], input, select, textarea'))
                    .filter((el) => el.offsetParent !== null);
                if (!f.length) return;
                const first = f[0], last = f[f.length - 1];
                if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
                else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
            });

            // Straight after the submerge transition finishes
            const once = () => {
                try {
                    if (sessionStorage.getItem('da-modal') === '1') return;
                    sessionStorage.setItem('da-modal', '1');
                } catch (e) {}
                open();
            };
            window.addEventListener('dive:entered', () => setTimeout(once, 1100));

            // And if the loader is ever removed, still greet the visitor
            document.addEventListener('DOMContentLoaded', () => {
                if (!document.getElementById('diveGate')) setTimeout(once, 1600);
            });

            window.__openBookModal = open;
            window.__closeBookModal = close;
        })();
