// // navbar.js
// document.addEventListener('DOMContentLoaded', () => {
//   const mobileToggle = document.getElementById('mobile-toggle');
//   const mobileMenu = document.getElementById('mobile-menu');
//   const accountTrigger = document.getElementById('account-trigger');
//   const dropdownWrapper = accountTrigger?.closest('.dropdown-wrapper');

//   if (mobileToggle && mobileMenu) {
//     mobileToggle.addEventListener('click', () => {
//       const hidden = mobileMenu.getAttribute('aria-hidden') === 'true';
//       mobileMenu.setAttribute('aria-hidden', hidden ? 'false' : 'true');
//       mobileMenu.style.display = hidden ? 'block' : 'none';
//     });
//     // default hidden
//     mobileMenu.setAttribute('aria-hidden', 'true');
//     mobileMenu.style.display = 'none';
//   }

//   if (dropdownWrapper && accountTrigger) {
//     accountTrigger.addEventListener('click', () => {
//       const expanded = dropdownWrapper.getAttribute('aria-expanded') === 'true';
//       dropdownWrapper.setAttribute('aria-expanded', expanded ? 'false' : 'true');
//       const menu = dropdownWrapper.querySelector('.dropdown-menu');
//       if (menu) menu.style.display = expanded ? 'none' : 'block';
//     });
//   }
// });

// static/js/navbar.js — robust delegated dropdown + mobile handler
// Overwrite your file with this. It uses event delegation, marks itself with a global flag,
// and is defensive about missing elements or other libraries (Bootstrap).

(function () {
  'use strict';
  // Init marker for debugging
  console.log('[navbar.js] loaded for', location.pathname);
  window.__navbar_init_marker = (window.__navbar_init_marker || 0) + 1;

  // Utility
  const byId = id => document.getElementById(id);
  const isElement = el => !!(el && el.nodeType === 1);

  function isHidden(el) {
    if (!isElement(el)) return true;
    if (el.hidden) return true;
    const ar = el.getAttribute && el.getAttribute('aria-hidden');
    if (ar === 'true') return true;
    try {
      const s = getComputedStyle(el);
      return s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0';
    } catch (e) {
      return true;
    }
  }

  function showEl(el) {
    if (!isElement(el)) return;
    el.setAttribute('aria-hidden', 'false');
    if (getComputedStyle(el).display === 'none') el.style.display = 'block';
    el.classList.add('show');
  }
  function hideEl(el) {
    if (!isElement(el)) return;
    el.setAttribute('aria-hidden', 'true');
    if (getComputedStyle(el).display !== 'none') el.style.display = 'none';
    el.classList.remove('show');
  }

  // Open/close helpers for a toggle and its menu
  function findMenuForToggle(toggle) {
    if (!isElement(toggle)) return null;
    // prefer aria-controls/labelledby
    const ctrl = toggle.getAttribute('aria-controls') || toggle.getAttribute('aria-labelledby');
    if (ctrl) {
      const el = byId(ctrl);
      if (el) return el;
    }
    // nextElementSibling common pattern
    const next = toggle.nextElementSibling;
    if (next && next.classList.contains('dropdown-menu')) return next;
    // search up for parent .dropdown and then .dropdown-menu
    const parent = toggle.closest('.dropdown-wrapper, .nav-item, .lists-dropdown');
    if (parent) return parent.querySelector('.dropdown-menu');
    return null;
  }

  function toggleMenu(toggle) {
    const menu = findMenuForToggle(toggle);
    if (!menu) return;
    const open = !isHidden(menu) && menu.classList.contains('show');
    // always close other menus first
    document.querySelectorAll('.dropdown-menu.show').forEach(m => {
      if (m !== menu) hideEl(m);
    });
    if (open) {
      hideEl(menu);
      toggle.setAttribute('aria-expanded', 'false');
    } else {
      // prevent other libraries from stopping propagation (we still stop default)
      toggle.setAttribute('aria-expanded', 'true');
      showEl(menu);
      // focus first interactive element
      const focusable = menu.querySelector('a, button, [tabindex]:not([tabindex="-1"])');
      if (focusable) focusable.focus();
    }
  }

  // Delegate clicks: handles .dropdown-toggle (lists/account) and mobile-specific toggles
  document.addEventListener('click', function (ev) {
    // If someone else called stopPropagation earlier, we can't help — but delegation is most robust.
    const toggle = ev.target.closest('.dropdown-toggle, .mobile-toggle, .mobile-collapsible-trigger, .mobile-submenu-toggle');
    // MOBILE toggle (open/close mobile menu)
    if (toggle && toggle.classList.contains('mobile-toggle')) {
      ev.preventDefault();
      ev.stopPropagation();
      const mobileMenu = byId('mobile-menu');
      const isOpen = mobileMenu && mobileMenu.getAttribute('aria-hidden') === 'false';
      if (mobileMenu) {
        if (isOpen) hideEl(mobileMenu);
        else showEl(mobileMenu);
      }
      toggle.setAttribute('aria-expanded', (!isOpen).toString());
      return;
    }

    // Mobile collapsible lists
    if (toggle && (toggle.classList.contains('mobile-collapsible-trigger') || toggle.classList.contains('mobile-submenu-toggle'))) {
      ev.preventDefault();
      ev.stopPropagation();
      const sub = toggle.nextElementSibling;
      if (!sub) return;
      const isHiddenNow = !!sub.hidden;
      sub.hidden = !isHiddenNow;
      toggle.setAttribute('aria-expanded', (!isHiddenNow).toString());
      return;
    }

    // Desktop dropdown toggles (.dropdown-toggle)
    if (toggle && toggle.classList.contains('dropdown-toggle')) {
      // Some libraries (Bootstrap) also use data-bs-toggle — stop default to avoid them opening via bootstrap
      ev.preventDefault();
      ev.stopPropagation();
      toggleMenu(toggle);
      return;
    }

    // If click happened outside any dropdown or mobile menu, close all
    const clickedInsideDropdown = !!ev.target.closest('.dropdown-menu, .dropdown-toggle, #mobile-menu, .mobile-toggle');
    if (!clickedInsideDropdown) {
      document.querySelectorAll('.dropdown-menu.show').forEach(m => hideEl(m));
      const mobileMenu = byId('mobile-menu');
      if (mobileMenu && mobileMenu.getAttribute('aria-hidden') === 'false') hideEl(mobileMenu);
      // reset any mobile sublists
      document.querySelectorAll('.mobile-sublist').forEach(s => s.hidden = true);
      document.querySelectorAll('.mobile-collapsible-trigger, .mobile-submenu-toggle').forEach(t => t.setAttribute('aria-expanded', 'false'));
    }
  }, true); // use capture phase so we see events before some libs stopPropagation

  // keyboard: ESC closes; Enter/Space on toggles behave like click
  document.addEventListener('keydown', function (ev) {
    const active = document.activeElement;
    if (ev.key === 'Escape' || ev.key === 'Esc') {
      document.querySelectorAll('.dropdown-menu.show').forEach(m => hideEl(m));
      const mobileMenu = byId('mobile-menu');
      if (mobileMenu) hideEl(mobileMenu);
      return;
    }
    if ((ev.key === 'Enter' || ev.key === ' ') && active && active.classList.contains('dropdown-toggle')) {
      ev.preventDefault();
      ev.stopPropagation();
      toggleMenu(active);
    }
  });

  // Defensive: ensure mobile menu is hidden initially if present
  try {
    const mm = byId('mobile-menu');
    const mt = byId('mobile-toggle');
    if (mm) {
      if (!mm.hasAttribute('aria-hidden')) mm.setAttribute('aria-hidden', 'true');
      if (getComputedStyle(mm).display !== 'none') mm.style.display = 'none';
    }
    if (mt && !mt.hasAttribute('aria-expanded')) mt.setAttribute('aria-expanded', 'false');
  } catch (e) { /* ignore */ }

  // Small helper: expose test function so you can open menus from console during debugging
  window.__navbar_test_open = function (idToggle) {
    const t = byId(idToggle);
    if (!t) return console.warn('no toggle', idToggle);
    toggleMenu(t);
  };

})();
