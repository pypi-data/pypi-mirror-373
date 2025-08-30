const getStoredTheme = () => localStorage.getItem('theme');
const setStoredTheme = theme => localStorage.setItem('theme', theme);

// === Bootstrap: Get Preferred Theme ===
const getPreferredTheme = () => {
  const storedTheme = getStoredTheme();
  if (storedTheme) return storedTheme;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

// === Bootstrap: Set Theme ===
const setTheme = theme => {
  const effectiveTheme = theme === 'auto'
    ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : theme;
  document.documentElement.setAttribute('data-bs-theme', effectiveTheme);
};

// === Bootstrap: Show Active Theme ===
const showActiveTheme = (theme, focus = false) => {
  const themeSwitcher = document.querySelector('#bd-theme');
  if (!themeSwitcher) return;
  const themeSwitcherText = document.querySelector('#bd-theme-text');
  const activeIconUse = document.querySelector('.theme-icon-active use');
  const btnToActivate = document.querySelector(`[data-bs-theme-value="${theme}"]`);
  const svgHref = btnToActivate?.querySelector('svg use')?.getAttribute('href');
  document.querySelectorAll('[data-bs-theme-value]').forEach(el => {
    el.classList.remove('active');
    el.setAttribute('aria-pressed', 'false');
  });
  btnToActivate?.classList.add('active');
  btnToActivate?.setAttribute('aria-pressed', 'true');
  activeIconUse?.setAttribute('href', svgHref);
  themeSwitcher.setAttribute(
    'aria-label',
    `${themeSwitcherText?.textContent} (${btnToActivate?.dataset.bsThemeValue})`
  );
  if (focus) themeSwitcher.focus();
};

// === Bootstrap: Init Theme Listener ===
const initThemeListener = () => {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const storedTheme = getStoredTheme();
    if (!['light', 'dark'].includes(storedTheme)) {
      setTheme(getPreferredTheme());
    }
  });
};

// === Bootstrap: Init Theme Switcher ===
const initThemeSwitcher = () => {
  showActiveTheme(getPreferredTheme());
  document.querySelectorAll('[data-bs-theme-value]').forEach(toggle => {
    toggle.addEventListener('click', () => {
      const theme = toggle.getAttribute('data-bs-theme-value');
      setStoredTheme(theme);
      setTheme(theme);
      showActiveTheme(theme, true);
    });
  });
};

// === Bootstrap: Init Tooltips ===
const initTooltips = () => {
  const triggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...triggers].forEach(el => new bootstrap.Tooltip(el));
};

// === MkDocs: Init Search Modal ===
const initSearchModal = () => {
  const searchModal = document.getElementById('search');
  const searchInput = document.getElementById('mkdocs-search-query');

  searchModal.addEventListener('shown.bs.modal', () => {
    searchInput.focus();
  });

  if (!searchModal) return;

  const modal = bootstrap.Modal.getOrCreateInstance(searchModal);
  let pendingHash = null;

  // Delegate clicks on result links inside the modal
  searchModal.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a) return;

    const url = new URL(a.getAttribute('href'), location.href);

    // Same-page anchor?
    if (url.pathname === location.pathname && url.hash) {
      e.preventDefault();
      pendingHash = url.hash;      // remember where to scroll
      modal.hide();                // close first; scrolling comes after hidden.bs.modal
      return;
    }
  });

  // After the modal is fully hidden, do the jump/scroll
  searchModal.addEventListener('hidden.bs.modal', () => {
    if (!pendingHash) return;

    const id = decodeURIComponent(pendingHash.slice(1));
    const target = document.getElementById(id);

    // Optional: account for a fixed header (Bootstrap .navbar.fixed-top / your header)
    const header = document.querySelector('.navbar.fixed-top, .md-header, header.navbar-fixed-top');
    const offset = header ? header.offsetHeight : 0;

    if (target) {
      const y = target.getBoundingClientRect().top + window.pageYOffset - offset - 8;
      window.scrollTo({ top: y, behavior: 'smooth' });

      // Update URL without triggering another jump
      history.pushState(null, '', `#${encodeURIComponent(id)}`);

      // A11y: move focus to the heading without re-scrolling
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
    } else {
      // Fallback: let the browser try the default behavior
      location.hash = pendingHash;
    }

    pendingHash = null;
  });
};

// === Init highlight.js ===
const initHljs = () => {
  document.querySelectorAll('pre[class^="language-"]').forEach((block) => {
    hljs.highlightElement(block);
  });
};

// === Signified: Init Clipboard ===
const initClipboard = () => {
  const clipboardIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard" viewBox="0 0 16 16"><path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1z"/><path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0z"/></svg>';
  const checkIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16"><path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425z"/></svg>';
  clipboard('.prose pre:not(.mermaid)', {
    template: `<div class="position-relative float-end w-100 d-none d-sm-block"><button class="position-absolute top-0 end-0 mt-1 me-1 d-block btn btn-sm" type="button" data-bs-toggle="tooltip" data-bs-placement="left" data-bs-title="Copy to clipboard">${clipboardIcon}</button></div>`
  }, function(clipboard, element) {
    let button = clipboard.querySelector('button');
    let tooltip = new bootstrap.Tooltip(button);
    button.addEventListener('click', function() {
      tooltip.setContent({
        '.tooltip-inner': 'Copied!'
      });
      button.innerHTML = checkIcon;
    });
    button.addEventListener('mouseleave', function() {
      tooltip.setContent({
        '.tooltip-inner': 'Copy to clipboard'
      });
      button.innerHTML = clipboardIcon;
    });
  });
};

// === Signified: Init Sortable ===
const initSortable = () => {
  sortable('.prose table');
};

// === Init ===
window.addEventListener('DOMContentLoaded', () => {
  setTheme(getPreferredTheme());
  initThemeListener();
  initThemeSwitcher();
  initTooltips();
  initSearchModal();
  initHljs();
  initClipboard();
  initSortable();
});
