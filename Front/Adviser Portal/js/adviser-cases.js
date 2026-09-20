/**
 * Royal Square Financial - Adviser Cases Controller (Screen 2)
 * Manages search filtering, category tabs, metric binding, and View Case navigation.
 */

document.addEventListener('DOMContentLoaded', () => {
  const data = window.ADVISER_MOCK_DATA;
  if (!data) {
    console.error('ADVISER_MOCK_DATA is not available.');
    return;
  }

  // State
  let currentSearchQuery = '';
  let activeFilterCategory = 'All';

  // 1. Render Current Date in Header
  renderCurrentDate();

  // 2. Render Adviser Profile in Sidebar
  renderAdviserProfile(data.adviser);

  // 3. Render Screen 2 Summary Metrics

  // 4. Initial Table Render
  updateCasesTable();

  // 5. Setup Live Search
  setupSearchInput();

  // 6. Setup Category Filter Pills
  setupFilterPills();

  // 7. Setup "View Case" Click Interception
  setupViewCaseActions();

  // 8. Setup Sidebar Nav Actions
  setupSidebarNav();

  // 9. Setup Notification Bell
  setupNotifications(data.notifications);

  /**
   * Filters and renders cases based on current search & active filter
   */
  function updateCasesTable() {
    const tbody = document.getElementById('casesTableBody');
    const countBadge = document.getElementById('casesTableCountBadge');
    if (!tbody) return;

    let cases = data.casesList || [];

    // Apply Category Filter
    if (activeFilterCategory !== 'All') {
      cases = cases.filter(c => c.category === activeFilterCategory);
    }

    // Apply Search Query (Claim ID or Client Name)
    if (currentSearchQuery.trim() !== '') {
      const q = currentSearchQuery.trim().toLowerCase();
      cases = cases.filter(c =>
        c.claimId.toLowerCase().includes(q) ||
        c.client.toLowerCase().includes(q) ||
        (c.event && c.event.toLowerCase().includes(q))
      );
    }

    if (countBadge) {
      if (cases.length === (data.casesList || []).length && activeFilterCategory === 'All' && currentSearchQuery.trim() === '') {
        countBadge.textContent = 'Showing 7 of 127 active cases';
      } else {
        countBadge.textContent = `Showing ${cases.length} of 127 active cases`;
      }
    }

    tbody.innerHTML = '';

    if (cases.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7">
            <div class="table-empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <div class="table-empty-title">No matching cases found</div>
              <div class="table-empty-text">Try adjusting your search query or filter category.</div>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    cases.forEach((item) => {
      const tr = document.createElement('tr');
      tr.id = `case-row-${item.claimId}`;

      const initials = item.client
        .split(' ')
        .map(part => part[0])
        .join('')
        .toUpperCase();

      tr.innerHTML = `
        <td>
          <span class="claim-id-badge">${escapeHtml(item.claimId)}</span>
        </td>
        <td>
          <div class="client-cell">
            <div class="client-avatar-mini">${initials}</div>
            <span class="client-name-text">${escapeHtml(item.client)}</span>
          </div>
        </td>
        <td>
          <span class="event-cell">${escapeHtml(item.event)}</span>
        </td>
        <td>
          <span class="stage-pill">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            ${escapeHtml(item.stage)}
          </span>
        </td>
        <td>
          <span class="status-badge ${item.statusVariant}">
            ${escapeHtml(item.status)}
          </span>
        </td>
        <td>
          <div class="reason-text" title="${escapeHtml(item.reason)}">
            ${escapeHtml(item.reason)}
          </div>
        </td>
        <td>
          <a href="${item.claimId === 'RS-1042' ? 'claim-details.html' : 'claim-details.html?id=' + encodeURIComponent(item.claimId)}"
             class="btn-view-case"
             data-claim-id="${escapeHtml(item.claimId)}"
             aria-label="View Case ${escapeHtml(item.claimId)}">
            View Case
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </a>
        </td>
      `;

      tbody.appendChild(tr);
    });
  }

  /**
   * Sets up Search Input Listener
   */
  function setupSearchInput() {
    const searchInput = document.getElementById('casesSearchInput');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
      currentSearchQuery = e.target.value;
      updateCasesTable();
    });
  }

  /**
   * Sets up Category Filter Buttons
   */
  function setupFilterPills() {
    const filterButtons = document.querySelectorAll('.filter-pill-btn');
    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeFilterCategory = btn.getAttribute('data-category') || 'All';
        updateCasesTable();
      });
    });
  }

  /**
   * Sets up View Case button routing
   */
  function setupViewCaseActions() {
    const tbody = document.getElementById('casesTableBody');
    if (!tbody) return;

    tbody.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-view-case');
      if (!btn) return;

      const claimId = btn.getAttribute('data-claim-id');
      if (claimId) {
        window.location.href = `claim-details.html?id=${encodeURIComponent(claimId)}`;
      }
    });
  }

  /**
   * Sets up Sidebar Nav behavior on the Cases page
   */
  function setupSidebarNav() {
    const casesNav = document.getElementById('navCases');
    if (casesNav) {
      casesNav.classList.add('active');
    }
    // Notifications & Settings now have real pages — navigation handled by href directly.
  }
});

/**
 * Helper to render date string
 */
function renderCurrentDate() {
  const dateEl = document.getElementById('headerDateText');
  if (!dateEl) return;
  const now = new Date();
  const options = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' };
  dateEl.textContent = now.toLocaleDateString('en-ZA', options);
}

/**
 * Populates Adviser Profile info in Sidebar
 */
function renderAdviserProfile(adviser) {
  const nameEl = document.getElementById('sidebarAdviserName');
  const roleEl = document.getElementById('sidebarAdviserRole');
  const avatarWrap = document.getElementById('sidebarAvatarWrap');

  if (nameEl) nameEl.textContent = adviser.name || 'Adviser';
  if (roleEl) roleEl.textContent = adviser.role || 'Financial Adviser';

  if (avatarWrap) {
    avatarWrap.innerHTML = `
      <div class="avatar-fallback">${adviser.initials || 'RS'}</div>
      <span class="status-indicator" title="Online & Available"></span>
    `;
  }
}

/**
 * Sets up Notifications Drawer in Top Header
 */
function setupNotifications(notifs) {
  const notifBtn = document.getElementById('btnNotifications');
  const dropdown = document.getElementById('notificationsDropdown');
  const listEl = document.getElementById('notificationsList');

  if (!notifBtn || !dropdown || !listEl) return;

  if (notifs && notifs.length) {
    listEl.innerHTML = notifs.map(n => `
      <div class="notif-item ${n.unread ? 'unread' : ''}">
        <div class="notif-item-title">${escapeHtml(n.title)}</div>
        <div class="notif-item-text">${escapeHtml(n.text)}</div>
        <div class="notif-item-time">${escapeHtml(n.time)}</div>
      </div>
    `).join('');
  }

  notifBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('show');
  });

  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target) && !notifBtn.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });
}

let toastTimer = null;
/**
 * Toast Notice for Inactive items
 */
function showComingSoonToast(featureName) {
  const toast = document.getElementById('comingSoonToast');
  const titleEl = document.getElementById('toastFeatureName');
  if (!toast) return;

  if (titleEl) {
    titleEl.textContent = featureName;
  }

  toast.classList.add('show');

  if (toastTimer) {
    clearTimeout(toastTimer);
  }

  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

/**
 * Basic HTML escaping helper
 */
function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
