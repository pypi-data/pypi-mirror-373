// === Helpers ===
const $ = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);
const isDark = () => window.matchMedia('(prefers-color-scheme: dark)').matches;

// === Theme Storage ===
const getStoredTheme = () => localStorage.getItem('theme');
const setStoredTheme = theme => localStorage.setItem('theme', theme);

// === Bootstrap: Theme Prefs ===
const getPreferredTheme = () => getStoredTheme() || (isDark() ? 'dark' : 'light');

const setTheme = theme => {
  const effective = theme === 'auto' ? (isDark() ? 'dark' : 'light') : theme;
  document.documentElement.dataset.bsTheme = effective;
};

const showActiveTheme = (theme, focus = false) => {
  const switcher = $('#bd-theme');
  if (!switcher) return;

  const switcherText = $('#bd-theme-text');
  const activeIconUse = $('.theme-icon-active use');
  const btn = $(`[data-bs-theme-value="${theme}"]`);
  const svgHref = btn?.querySelector('svg use')?.getAttribute('href');

  $$('[data-bs-theme-value]').forEach(el => {
    el.classList.remove('active');
    el.setAttribute('aria-pressed', 'false');
  });

  btn?.classList.add('active');
  btn?.setAttribute('aria-pressed', 'true');
  activeIconUse?.setAttribute('href', svgHref);
  switcher.setAttribute(
    'aria-label',
    `${switcherText?.textContent} (${btn?.dataset.bsThemeValue})`
  );
  if (focus) switcher.focus();
};

const initThemeListener = () => {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const stored = getStoredTheme();
    if (!['light', 'dark'].includes(stored)) setTheme(getPreferredTheme());
  });
};

const initThemeSwitcher = () => {
  showActiveTheme(getPreferredTheme());
  $$('[data-bs-theme-value]').forEach(toggle => {
    toggle.addEventListener('click', () => {
      const theme = toggle.dataset.bsThemeValue;
      setStoredTheme(theme);
      setTheme(theme);
      showActiveTheme(theme, true);
    });
  });
};

// === Bootstrap: Tooltips ===
const initTooltips = () => {
  $$('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
};

// === Mermaid ===
const initMermaid = () => {
  const renderMermaid = async theme => {
    mermaid.initialize({
      theme,
      startOnLoad: false,
      themeVariables: {
        darkMode: theme === 'dark',
        fontFamily: '"Roboto", sans-serif'
      }
    });

    for (const el of $$('.mermaid')) {
      const code = el.dataset.mermaidCode || el.textContent.trim();
      el.dataset.mermaidCode = code;
      try {
        const { svg } = await mermaid.render('m' + Math.random().toString(36).slice(2), code);
        el.innerHTML = svg;
      } catch (err) {
        console.error('Mermaid render error:', err);
      }
    }
  };

  // Initial render
  renderMermaid(document.documentElement.dataset.bsTheme === 'dark' ? 'dark' : 'default');

  // Re-render on theme change
  new MutationObserver(muts => {
    if (muts.some(m => m.attributeName === 'data-bs-theme')) {
      const theme = document.documentElement.dataset.bsTheme === 'dark' ? 'dark' : 'default';
      renderMermaid(theme);
    }
  }).observe(document.documentElement, { attributes: true });
};

// === MkDocs: Search Modal ===
const initSearchModal = () => {
  const modalEl = $('#search');
  if (!modalEl) return;

  const searchInput = $('#mkdocs-search-query');
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  let pendingHash = null;

  modalEl.addEventListener('shown.bs.modal', () => searchInput.focus());

  modalEl.addEventListener('click', e => {
    const a = e.target.closest('a[href]');
    if (!a) return;

    const url = new URL(a.getAttribute('href'), location.href);
    if (url.pathname === location.pathname && url.hash) {
      e.preventDefault();
      pendingHash = url.hash;
      modal.hide();
    }
  });

  modalEl.addEventListener('hidden.bs.modal', () => {
    if (!pendingHash) return;

    const id = decodeURIComponent(pendingHash.slice(1));
    const target = document.getElementById(id);
    const header = $('.navbar.fixed-top, .md-header, header.navbar-fixed-top');
    const offset = header ? header.offsetHeight : 0;

    if (target) {
      const y = target.getBoundingClientRect().top + window.pageYOffset - offset - 8;
      window.scrollTo({ top: y, behavior: 'smooth' });

      history.pushState(null, '', `#${encodeURIComponent(id)}`);

      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
    } else {
      location.hash = pendingHash; // fallback
    }

    pendingHash = null;
  });
};

// === Highlight.js ===
const initHljs = () => $$('pre[class^="language-"]').forEach(block => hljs.highlightElement(block));

// === Clipboard ===
const initClipboard = () => {
  const clipboardIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard" viewBox="0 0 16 16"><path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1z"/><path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0z"/></svg>';
  const checkIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16"><path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425z"/></svg>';

  clipboard('.prose pre:not(.mermaid)', {
    template: `<div class="position-relative float-end w-100 d-none d-sm-block"><button class="position-absolute top-0 end-0 mt-1 me-1 d-block btn btn-sm" type="button" data-bs-toggle="tooltip" data-bs-placement="left" data-bs-title="Copy to clipboard">${clipboardIcon}</button></div>`
  }, (clip, el) => {
    const button = clip.querySelector('button');
    const tooltip = new bootstrap.Tooltip(button);

    button.addEventListener('click', () => {
      tooltip.setContent({ '.tooltip-inner': 'Copied!' });
      button.innerHTML = checkIcon;
    });

    button.addEventListener('mouseleave', () => {
      tooltip.setContent({ '.tooltip-inner': 'Copy to clipboard' });
      button.innerHTML = clipboardIcon;
    });
  });
};

// === Sortable ===
const initSortable = () => sortable('.prose table');

// === Init All ===
window.addEventListener('DOMContentLoaded', () => {
  [
    () => setTheme(getPreferredTheme()),
    initThemeListener,
    initThemeSwitcher,
    initTooltips,
    initMermaid,
    initSearchModal,
    initHljs,
    initClipboard,
    initSortable
  ].forEach(fn => fn());
});
