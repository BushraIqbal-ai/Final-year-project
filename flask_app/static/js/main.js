/* NeuroScan AI — Main JavaScript */

// ── Theme Toggle ────────────────────────────────────────────
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    
    let currentTheme = 'dark'; // default
    if (savedTheme === 'light' || (!savedTheme && systemPrefersLight)) {
        currentTheme = 'light';
    }
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    const themeToggleBtn = document.getElementById('themeToggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', currentTheme);
            localStorage.setItem('theme', currentTheme);
            updateThemeIcon(currentTheme);
        });
    }
}

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'light' ? '🌙' : '🌞';
    }
}

// Call init immediately to prevent flash
initTheme();

// ── Navbar scroll effect ────────────────────────────────────
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        navbar.style.boxShadow = window.scrollY > 20
            ? '0 4px 30px rgba(0,0,0,0.4)'
            : '';
    }
});

// ── Mobile nav toggle ───────────────────────────────────────
const navToggle = document.getElementById('navToggle');
const navLinks  = document.getElementById('navLinks');
if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('open');
        // Animate hamburger to X
        const spans = navToggle.querySelectorAll('span');
        if (navLinks.classList.contains('open')) {
            spans[0].style.transform = 'translateY(7px) rotate(45deg)';
            spans[1].style.opacity   = '0';
            spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
        } else {
            spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
        }
    });
    // Close nav on link click
    navLinks.querySelectorAll('.nav-link, .btn').forEach(el => {
        el.addEventListener('click', () => {
            navLinks.classList.remove('open');
            navToggle.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
        });
    });
}

// ── Auto-dismiss flash messages ─────────────────────────────
document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
        flash.style.opacity    = '0';
        flash.style.transform  = 'translateX(20px)';
        flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(() => flash.remove(), 400);
    }, 5000);
});

// ── Animate stage bars on scroll ────────────────────────────
const stageObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.querySelectorAll('.stage-bar[data-width]').forEach(bar => {
                setTimeout(() => { bar.style.width = bar.dataset.width; }, 200);
            });
        }
    });
}, { threshold: 0.3 });
document.querySelectorAll('.stages-grid').forEach(el => stageObserver.observe(el));

// ── Animate elements on scroll (fade-in) ───────────────────
const fadeObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity   = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.step-card, .stage-card, .kpi-card, .glass-card').forEach(el => {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(22px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    fadeObserver.observe(el);
});

// ── Particles background ────────────────────────────────────
function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;

    const COLORS = ['rgba(6,182,212,', 'rgba(139,92,246,', 'rgba(59,130,246,'];
    const N = window.innerWidth < 768 ? 15 : 30;

    for (let i = 0; i < N; i++) {
        const p = document.createElement('div');
        const size = Math.random() * 3 + 1;
        const color = COLORS[Math.floor(Math.random() * COLORS.length)];
        const dur   = Math.random() * 20 + 10;
        const delay = Math.random() * 10;
        const x     = Math.random() * 100;
        const y     = Math.random() * 100;

        // Use CSS variables for particles if possible, but fallback is fine
        p.style.cssText = `
            position: absolute;
            width: ${size}px; height: ${size}px;
            border-radius: 50%;
            background: ${color}${Math.random() * 0.4 + 0.1});
            left: ${x}%; top: ${y}%;
            animation: particleFloat ${dur}s ${delay}s ease-in-out infinite alternate;
            pointer-events: none;
        `;
        container.appendChild(p);
    }
}

// Inject particle keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes particleFloat {
        0%   { transform: translate(0, 0) scale(1); opacity: 0.3; }
        50%  { opacity: 0.8; }
        100% { transform: translate(${Math.random() > 0.5 ? '' : '-'}${Math.floor(Math.random()*60)+20}px, -${Math.floor(Math.random()*80)+40}px) scale(1.5); opacity: 0.1; }
    }
`;
document.head.appendChild(style);
createParticles();

// ── Smooth page transitions ─────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease';
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            document.body.style.opacity = '1';
        });
    });
});

// ── Tooltip on class badges (history table) ─────────────────
document.querySelectorAll('.class-badge').forEach(badge => {
    badge.title = 'Click to view details';
    badge.style.cursor = 'default';
});

// ── Mark active nav link ────────────────────────────────────
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
    }
});

console.log('%c🧠 NeuroScan AI', 'color:#06b6d4;font-size:20px;font-weight:bold');
console.log('%cParkinson\'s Disease Dementia Detection System', 'color:#94a3b8');
