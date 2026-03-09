// static/js/participation.js
// Robust version: uses event delegation, defensive selectors, and clearer logging.

(function () {
  'use strict';

  // helper: read cookie (CSRF token)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const c = cookies[i].trim();
        if (c.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(c.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  // format seconds -> HH:MM:SS (returns '-' when falsy)
  function formatSeconds(val) {
    val = Number(val);
    if (!val && val !== 0) return '-';
    const h = Math.floor(val / 3600);
    const m = Math.floor((val % 3600) / 60);
    const s = Math.floor(val % 60);
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  // Get the update URL template from DOM. We're defensive about missing element.
  function getUpdateUrlTemplate() {
    const page = document.getElementById('page') || document.querySelector('[data-update-url-template]');
    if (!page) return null;
    return page.dataset.updateUrlTemplate || page.getAttribute('data-update-url-template') || null;
  }

  function buildUpdateUrl(startId) {
    const tpl = getUpdateUrlTemplate();
    if (!tpl) {
      console.error('Update URL template not found (data-update-url-template).');
      return null;
    }
    // Common patterns:
    if (tpl.includes('/0/')) return tpl.replace('/0/', `/${startId}/`);
    if (tpl.endsWith('/0')) return tpl.replace(/\/0$/, `/${startId}`);
    // fallback: replace the first standalone "/0" or "0" occurrence
    const replaceOnce = tpl.replace('/0', `/${startId}`);
    if (replaceOnce !== tpl) return replaceOnce;
    return tpl.replace('0', String(startId));
  }

  // Delegated handler for toggle checkbox
  async function handleCheckboxToggle(checkbox, tr) {
    if (!tr) return;
    const startId = tr.getAttribute('data-start-id') || tr.dataset.startId || tr.dataset.startid || tr.dataset.start;
    if (!startId) {
      console.warn('startId not found on row for participation toggle.');
      checkbox.checked = !checkbox.checked;
      return;
    }
    const checked = checkbox.checked;
    const url = buildUpdateUrl(startId);
    if (!url) {
      alert('Configuration error: update URL not found.');
      checkbox.checked = !checked;
      return;
    }
    const payload = { is_participated: checked };
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!data || !data.ok) throw new Error('failed');
    } catch (err) {
      console.error('Participation update failed', err);
      alert('Failed to update participation');
      checkbox.checked = !checked;
    }
  }

  // Delegated handler to open the modal and populate fields
  function openEditModalForRow(tr) {
    if (!tr) return;
    const startId = tr.getAttribute('data-start-id') || tr.dataset.startId || tr.dataset.startid || tr.dataset.start;
    const modal = document.getElementById('editModal');
    if (!modal) {
      console.warn('Modal element (#editModal) not found.');
      return;
    }

    document.getElementById('startEntryId').value = startId || '';
    document.getElementById('f_age_group').value = (tr.querySelector('.age_group_cell')?.innerText || '').trim();
    document.getElementById('f_gender').value = (tr.querySelector('.gender_cell')?.innerText || '').trim();
    document.getElementById('f_total_lap_time_seconds').value = "";
    document.getElementById('f_end_time').value = (tr.querySelector('.end_time_cell')?.innerText || '').trim();

    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
  }

  // Delegated submit handler for the modal form
  async function submitParticipationForm() {
    const startId = document.getElementById('startEntryId').value;
    const payload = {
      age_group: document.getElementById('f_age_group').value || null,
      gender: document.getElementById('f_gender').value || null,
      total_lap_time_seconds: document.getElementById('f_total_lap_time_seconds').value || null,
      end_time: document.getElementById('f_end_time').value || null
    };
    const url = buildUpdateUrl(startId);
    if (!url) {
      alert('Configuration error: update URL not found.');
      return;
    }
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!data || !data.ok) throw new Error('save failed');

      const tr = document.querySelector(`tr[data-start-id='${startId}']`);
      if (tr) {
        if (payload.age_group !== null) tr.querySelector('.age_group_cell').innerText = payload.age_group || "";
        if (payload.gender !== null) tr.querySelector('.gender_cell').innerText = payload.gender || "";
        if (payload.total_lap_time_seconds) {
          tr.querySelector('.lap_time_cell').innerText = formatSeconds(payload.total_lap_time_seconds);
        }
        tr.querySelector('.end_time_cell').innerText = payload.end_time || "";
      }

      const modal = document.getElementById('editModal');
      if (modal) {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
      }
    } catch (err) {
      console.error('Save failed', err);
      alert('Failed to save participation');
    }
  }

  // Close modal helper
  function closeModal() {
    const modal = document.getElementById('editModal');
    if (modal) {
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  // Main init using delegation (one listener on document)
  function initDelegatedHandlers() {
    // checkbox change (delegated)
    document.addEventListener('change', function (ev) {
      const target = ev.target;
      if (!target) return;
      if (target.matches && target.matches('.is-participated-checkbox')) {
        const tr = target.closest('tr');
        handleCheckboxToggle(target, tr);
      }
    });

    // click for edit buttons (delegated)
    document.addEventListener('click', function (ev) {
      const target = ev.target;
      if (!target) return;

      // "Edit" button: support both <button class="edit-btn"> and elements inside it (icon/text)
      const editBtn = target.closest && target.closest('.edit-btn');
      if (editBtn) {
        const tr = editBtn.closest('tr');
        openEditModalForRow(tr);
        return;
      }

      // modal close button
      if (target.matches && target.matches('#modalClose')) {
        closeModal();
        return;
      }
    });

    // form submit (modal)
    const form = document.getElementById('participationForm');
    if (form) {
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        submitParticipationForm();
      });
    } else {
      console.warn('#participationForm not found on page.');
    }

    // close modal on ESC
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') closeModal();
    });
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDelegatedHandlers);
  } else {
    initDelegatedHandlers();
  }

})();
