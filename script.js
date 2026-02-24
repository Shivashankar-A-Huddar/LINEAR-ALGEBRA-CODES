// ============================================================
// SCRIPT.JS - Linear Algebra Lab | Educational Website
// ============================================================

'use strict';

// ── Utility: DOM selector shortcuts ────────────────────────
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

// ============================================================
// 1. PROGRESS BAR
// ============================================================
const progressBar = $('#progress-bar');

function updateProgress() {
    const scrolled = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const pct = total > 0 ? (scrolled / total) * 100 : 0;
    if (progressBar) progressBar.style.width = `${pct.toFixed(1)}%`;
}

// ============================================================
// 2. DARK MODE TOGGLE
// ============================================================
const THEME_KEY = 'la-lab-theme';

function getStoredTheme() {
    return localStorage.getItem(THEME_KEY) ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = $('#theme-icon');
    if (icon) icon.textContent = theme === 'dark' ? 'Light' : 'Dark';
}

function initTheme() {
    applyTheme(getStoredTheme());
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
}

// ============================================================
// 3. NAVIGATION — sticky scroll + active link highlight
// ============================================================
const navbar = $('.navbar');
const sections = $$('section[id]');
const navLinks = $$('.nav-links a, .mobile-menu a');

function onScroll() {
    updateProgress();

    // Navbar shadow
    if (navbar) {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    }

    // Back to top button
    const btt = $('#back-to-top');
    if (btt) btt.classList.toggle('visible', window.scrollY > 400);

    // Active nav link
    const scrollY = window.scrollY + 100;
    let current = '';
    sections.forEach(sec => {
        if (sec.offsetTop <= scrollY) current = sec.getAttribute('id');
    });
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) link.classList.add('active');
    });

    // Intersection animations
    $$('.fade-in-up').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.9) el.classList.add('visible');
    });
}

// ============================================================
// 4. HAMBURGER MENU
// ============================================================
function initMobileMenu() {
    const ham = $('#hamburger');
    const menu = $('#mobile-menu');
    if (!ham || !menu) return;

    ham.addEventListener('click', () => {
        const isOpen = menu.classList.toggle('open');
        ham.classList.toggle('open', isOpen);
        ham.setAttribute('aria-expanded', isOpen);
    });

    // Close on link click
    $$('#mobile-menu a').forEach(link => {
        link.addEventListener('click', () => {
            menu.classList.remove('open');
            ham.classList.remove('open');
            ham.setAttribute('aria-expanded', 'false');
        });
    });

    // Close on outside click
    document.addEventListener('click', e => {
        if (!ham.contains(e.target) && !menu.contains(e.target)) {
            menu.classList.remove('open');
            ham.classList.remove('open');
        }
    });
}

// ============================================================
// 5. COPY TO CLIPBOARD
// ============================================================
function initCopyButtons() {
    $$('.btn-copy').forEach(btn => {
        btn.addEventListener('click', async () => {
            const targetId = btn.dataset.target;
            const codeEl = $(`#${targetId}`);
            if (!codeEl) return;

            // Strip HTML tags to get plain text
            const text = codeEl.innerText || codeEl.textContent;

            try {
                await navigator.clipboard.writeText(text);
                const original = btn.innerHTML;
                btn.classList.add('copied');
                btn.innerHTML = 'Copied!';
                setTimeout(() => {
                    btn.classList.remove('copied');
                    btn.innerHTML = original;
                }, 2000);
            } catch {
                // Fallback for older browsers
                const ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                btn.innerHTML = 'Copied!';
                setTimeout(() => btn.innerHTML = 'Copy', 2000);
            }
        });
    });
}

// ============================================================
// 6. EXPANDABLE EXPLANATIONS
// ============================================================
function initExpandables() {
    $$('.expand-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const isOpen = btn.classList.toggle('open');
            const body = btn.nextElementSibling;
            if (body) body.classList.toggle('open', isOpen);
            const arrow = btn.querySelector('.expand-arrow');
            if (arrow) arrow.textContent = isOpen ? '▲' : '▼';
        });
    });
}

// ============================================================
// 7. NOTE ACCORDIONS
// ============================================================
function initNoteAccordions() {
    $$('.note-card').forEach(card => {
        const toggle = card.querySelector('.note-toggle');
        if (!toggle) return;
        toggle.addEventListener('click', () => {
            card.classList.toggle('open');
        });
    });
}

// ============================================================
// 8. BACK TO TOP
// ============================================================
function initBackToTop() {
    const btt = $('#back-to-top');
    if (!btt) return;
    btt.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ============================================================
// 9. LAZY VIDEO LOADING
// ============================================================
function initLazyVideo() {
    const video = $('#install-video');
    if (!video) return;
    // Only load when section is in view
    const observer = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                video.load();
                observer.disconnect();
            }
        });
    }, { rootMargin: '200px' });
    observer.observe(video);
}

// ============================================================
// 10. FADE-IN ANIMATIONS (Intersection Observer)
// ============================================================
function initFadeAnims() {
    $$('.program-card, .note-card, .resource-card, .step-item').forEach(el => {
        el.classList.add('fade-in-up');
    });

    const observer = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.classList.add('visible');
                observer.unobserve(e.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    $$('.fade-in-up').forEach(el => observer.observe(el));
}

// ============================================================
// 11. SMOOTH HASH SCROLLING (fixes navbar offset)
// ============================================================
function initSmoothScroll() {
    $$('a[href^="#"]').forEach(link => {
        link.addEventListener('click', e => {
            const id = link.getAttribute('href').slice(1);
            const target = document.getElementById(id);
            if (!target) return;
            e.preventDefault();
            const navH = navbar ? navbar.offsetHeight : 64;
            const top = target.getBoundingClientRect().top + window.scrollY - navH - 12;
            window.scrollTo({ top, behavior: 'smooth' });
        });
    });
}

// ============================================================
// 12. KEYBOARD ACCESSIBILITY
// ============================================================
function initKeyboard() {
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            const menu = $('#mobile-menu');
            const ham = $('#hamburger');
            if (menu?.classList.contains('open')) {
                menu.classList.remove('open');
                ham?.classList.remove('open');
            }
        }
    });
}

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    initCopyButtons();
    initExpandables();
    initNoteAccordions();
    initBackToTop();
    initLazyVideo();
    initFadeAnims();
    initSmoothScroll();
    initKeyboard();

    // Wire up theme toggle
    const themeBtn = $('#theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    // Initial scroll handling
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // run once on load
});
