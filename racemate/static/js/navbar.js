


/* navbar.js — Racemate */
(function () {
  "use strict";

  /* ── Dropdown logic ── */
  function initDropdown(triggerId, menuId) {
    var trigger = document.getElementById(triggerId);
    var menu    = document.getElementById(menuId);
    if (!trigger || !menu) return;

    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      var isOpen = menu.classList.contains("rm-open");

      // Close every open dropdown first
      closeAll();

      if (!isOpen) {
        menu.classList.add("rm-open");
        trigger.setAttribute("aria-expanded", "true");
      }
    });
  }

  function closeAll() {
    document.querySelectorAll(".rm-dd-menu.rm-open").forEach(function (m) {
      m.classList.remove("rm-open");
    });
    document.querySelectorAll("[aria-expanded='true']").forEach(function (t) {
      t.setAttribute("aria-expanded", "false");
    });
  }

  // Click outside → close all
  document.addEventListener("click", closeAll);

  // Escape → close all
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAll();
  });

  initDropdown("account-trigger", "account-menu");
  initDropdown("lists-trigger",   "lists-menu");
  initDropdown("tournaments-trigger", "tournaments-menu");

  /* ── Mobile hamburger ── */
  var hamburger  = document.getElementById("mobile-toggle");
  var mobileMenu = document.getElementById("mobile-menu");

  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = mobileMenu.classList.toggle("rm-open");
      hamburger.setAttribute("aria-expanded", String(open));
      mobileMenu.setAttribute("aria-hidden",  String(!open));
      hamburger.textContent = open ? "✕" : "☰";
    });

    // Clicking inside the drawer should NOT close it
    mobileMenu.addEventListener("click", function (e) {
      e.stopPropagation();
    });
  }

})();