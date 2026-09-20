/**
 * Royal Square Financial - Adviser Dashboard Controller
 * Professional Red & Black Executive Financial Services Portal
 *
 * NOTE: All figures and metrics rendered are DEMO/MOCK data
 * for prototype presentation purposes.
 */

document.addEventListener('DOMContentLoaded', () => {
  const data = window.ADVISER_MOCK_DATA;
  if (!data) {
    console.error('ADVISER_MOCK_DATA is not loaded.');
    return;
  }

  // 1. Render Current Date in Header
  renderCurrentDate();

  // 2. Render Adviser Profile & Sidebar Status
  renderAdviserProfile(data.adviser);

  // 3. Render Summary Metrics Cards
  renderSummaryMetrics(data.summaryMetrics);

  // 4. Render Cases Requiring Adviser Review Table
  renderCasesTable(data.casesRequiringAttention);

  // 5. Render Recent Activity Feed
  renderRecentActivity(data.recentActivity);

  // 6. Setup Notifications Drawer & Interactions
  setupNotifications(data.notifications);

  // 7. Setup Sidebar Nav Actions
  setupNavItems();
});

/**
 * Renders the formatted current date string
 */
function renderCurrentDate() {
  const dateEl = document.getElementById('headerDateText');
  if (!dateEl) return;
  const now = new Date();
  const options = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' };
  dateEl.textContent = now.toLocaleDateString('en-ZA', options);
}

/**
 * Populates Adviser Profile info in Sidebar & Header
 */
function renderAdviserProfile(adviser) {
  const nameEl = document.getElementById('sidebarAdviserName');
  const roleEl = document.getElementById('sidebarAdviserRole');
  const avatarWrap = document.getElementById('sidebarAvatarWrap');

  if (nameEl) nameEl.textContent = adviser.name || 'Sarah Adams';
  if (roleEl) roleEl.textContent = adviser.role ? `${adviser.role} — ${adviser.branch}` : 'Financial Adviser';

  if (avatarWrap) {
    avatarWrap.innerHTML = `
      <div class="avatar-fallback">${adviser.initials || 'SA'}</div>
      <span class="status-indicator" title="Online & Available"></span>
    `;
  }
}

/**
 * Renders the 4 summary metric tiles
 */
function renderSummaryMetrics(metrics) {
  if (!metrics) return;

  // Active Cases: 127
  const activeCasesVal = document.getElementById('metricActiveCasesVal');
  if (activeCasesVal && metrics.activeCases) activeCasesVal.textContent = metrics.activeCases.value;

  // Human Intervention: 8
  const humanInterventionVal = document.getElementById('metricHumanInterventionVal');
  if (humanInterventionVal && metrics.humanIntervention) humanInterventionVal.textContent = metrics.humanIntervention.value;

  // Waiting on Client: 21
  const waitingOnClientVal = document.getElementById('metricWaitingOnClientVal');
  if (waitingOnClientVal && metrics.waitingOnClient) waitingOnClientVal.textContent = metrics.waitingOnClient.value;

  // Progressing Normally: 98
  const progressingNormallyVal = document.getElementById('metricProgressingNormallyVal');
  if (progressingNormallyVal && metrics.progressingNormally) progressingNormallyVal.textContent = metrics.progressingNormally.value;
}

/**
 * Generates table rows for Cases Requiring Adviser Review
 */
function renderCasesTable(cases) {
  const tbody = document.getElementById('casesTableBody');
  const countPill = document.getElementById('casesAttentionCount');
  if (!tbody) return;

  if (countPill) countPill.textContent = `${cases ? cases.length : 3} need review`;

  tbody.innerHTML = '';

  (cases || []).forEach((item) => {
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
        <a href="claim-details.html?id=${encodeURIComponent(item.claimId)}" class="btn-view-case" aria-label="View Case ${escapeHtml(item.claimId)}">
          View Case
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </a>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

/**
 * Generates items for the Recent Activity Timeline with automated badges
 */
function renderRecentActivity(activities) {
  const container = document.getElementById('recentActivityTimeline');
  if (!container) return;

  container.innerHTML = '';

  (activities || []).forEach((act) => {
    const item = document.createElement('div');
    item.className = 'timeline-item';

    let iconSvg = '';
    switch (act.type) {
      case 'escalation':
        iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
        break;
      case 'reminder':
        iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';
        break;
      case 'upload':
        iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>';
        break;
      default:
        iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
        break;
    }

    const autoTag = act.isAutomated
      ? `<span class="auto-badge-tag"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path></svg> Automated</span>`
      : `<span class="auto-badge-tag" style="background:#fee2e2;color:#b91c1c;">Exception</span>`;

    item.innerHTML = `
      <div class="timeline-icon-wrap ${act.type || 'approval'}">
        ${iconSvg}
      </div>
      <div class="timeline-content">
        <div class="timeline-top">
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span class="timeline-title">${escapeHtml(act.title)}</span>
            ${autoTag}
          </div>
          <span class="timeline-time">${escapeHtml(act.timestamp)}</span>
        </div>
        <div class="timeline-desc">${escapeHtml(act.description)}</div>
      </div>
    `;

    container.appendChild(item);
  });
}

/**
 * Renders Financial & Automation Impact Charts
 */
function renderFinancialCharts(financial) {
  const revenueCostsEl = document.getElementById('demoRevenueCostsChart');
  const profitEl = document.getElementById('demoProfitChart');
  if (!revenueCostsEl || !profitEl || !financial || !financial.sixMonths) return;

  const { months, revenue, costs, profit } = financial.sixMonths;

  revenueCostsEl.innerHTML = buildGroupedBarChartSvg({
    labels: months,
    series: [
      { values: revenue, color: '#111216' }, // Dark charcoal/black
      { values: costs, color: '#dc2626' }    // Royal Square Red
    ]
  });

  profitEl.innerHTML = buildProfitLineChartSvg({
    labels: months,
    values: profit
  });
}

function formatDemoRandShort(value) {
  return `R${Math.round(value / 1000)}k`;
}

function buildGroupedBarChartSvg({ labels, series }) {
  const width = 560;
  const height = 240;
  const pad = { top: 18, right: 16, bottom: 36, left: 48 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const allValues = series.flatMap(s => s.values);
  const maxVal = Math.max(...allValues) * 1.12;
  const groupCount = labels.length;
  const groupW = plotW / groupCount;
  const barGap = 4;
  const barW = Math.min(18, (groupW - 16 - barGap) / series.length);

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map(t => t * maxVal);

  const grid = yTicks.map(tick => {
    const y = pad.top + plotH - (tick / maxVal) * plotH;
    return `
      <line x1="${pad.left}" y1="${y}" x2="${width - pad.right}" y2="${y}" stroke="#e2e8f0" stroke-width="1"/>
      <text x="${pad.left - 8}" y="${y + 4}" text-anchor="end" fill="#64748b" font-size="10" font-family="Inter, sans-serif">${formatDemoRandShort(tick)}</text>
    `;
  }).join('');

  const bars = labels.map((label, i) => {
    const groupX = pad.left + i * groupW + (groupW - (series.length * barW + barGap)) / 2;
    const groupBars = series.map((s, si) => {
      const h = (s.values[i] / maxVal) * plotH;
      const x = groupX + si * (barW + barGap);
      const y = pad.top + plotH - h;
      return `<rect x="${x}" y="${y}" width="${barW}" height="${h}" rx="3" fill="${s.color}">
        <title>${label}: ${formatDemoRandShort(s.values[i])} (demo)</title>
      </rect>`;
    }).join('');
    const labelX = pad.left + i * groupW + groupW / 2;
    return `${groupBars}<text x="${labelX}" y="${height - 12}" text-anchor="middle" fill="#475569" font-size="11" font-weight="600" font-family="Inter, sans-serif">${label}</text>`;
  }).join('');

  return `
    <svg viewBox="0 0 ${width} ${height}" role="presentation" aria-hidden="true">
      ${grid}
      ${bars}
    </svg>
  `;
}

function buildProfitLineChartSvg({ labels, values }) {
  const width = 560;
  const height = 240;
  const pad = { top: 18, right: 16, bottom: 36, left: 48 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const maxVal = Math.max(...values) * 1.18;
  const minVal = 0;
  const range = maxVal - minVal;

  const points = values.map((v, i) => {
    const x = pad.left + (i / (values.length - 1)) * plotW;
    const y = pad.top + plotH - ((v - minVal) / range) * plotH;
    return { x, y, v, label: labels[i] };
  });

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map(t => t * maxVal);
  const grid = yTicks.map(tick => {
    const y = pad.top + plotH - (tick / maxVal) * plotH;
    return `
      <line x1="${pad.left}" y1="${y}" x2="${width - pad.right}" y2="${y}" stroke="#e2e8f0" stroke-width="1"/>
      <text x="${pad.left - 8}" y="${y + 4}" text-anchor="end" fill="#64748b" font-size="10" font-family="Inter, sans-serif">${formatDemoRandShort(tick)}</text>
    `;
  }).join('');

  const line = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const area = `${line} L ${points[points.length - 1].x} ${pad.top + plotH} L ${points[0].x} ${pad.top + plotH} Z`;
  const dots = points.map(p => `
    <circle cx="${p.x}" cy="${p.y}" r="4.5" fill="#dc2626" stroke="#111216" stroke-width="2">
      <title>${p.label}: ${formatDemoRandShort(p.v)} estimated profit (demo)</title>
    </circle>
  `).join('');
  const xLabels = points.map(p => `
    <text x="${p.x}" y="${height - 12}" text-anchor="middle" fill="#475569" font-size="11" font-weight="600" font-family="Inter, sans-serif">${p.label}</text>
  `).join('');

  return `
    <svg viewBox="0 0 ${width} ${height}" role="presentation" aria-hidden="true">
      <defs>
        <linearGradient id="demoProfitFillRed" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#dc2626" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="#dc2626" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      ${grid}
      <path d="${area}" fill="url(#demoProfitFillRed)"/>
      <path d="${line}" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
      ${dots}
      ${xLabels}
    </svg>
  `;
}

/**
 * Sets up Client Financial Goals demo button
 */
function setupClientFinancialGoals() {
  const btn = document.getElementById('btnViewClientGoals');
  if (!btn) return;

  btn.addEventListener('click', () => {
    showNoticeToast('Client Financial Goals', 'Loaded portfolio goals for Thandi M. (Demo)');
  });
}

/**
 * Sets up the notification popup toggle and items
 */
function setupNotifications(notifs) {
  const notifBtn = document.getElementById('btnNotifications');
  const dropdown = document.getElementById('notificationsDropdown');
  const listEl = document.getElementById('notificationsList');

  if (!notifBtn || !dropdown || !listEl) return;

  if (notifs && notifs.length) {
    listEl.innerHTML = notifs.map(n => `
      <div class="notif-item ${n.unread ? 'unread' : ''}" onclick="window.location.href='${n.actionLink || 'notifications.html'}'">
        <div class="notif-item-title">${escapeHtml(n.title)}</div>
        <div class="notif-item-text">${escapeHtml(n.message || n.text)}</div>
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

/**
 * Handles sidebar navigation links
 */
function setupNavItems() {
  const dashboardLink = document.getElementById('navDashboard');
  if (dashboardLink) {
    dashboardLink.addEventListener('click', (e) => {
      const isDashboard = window.location.pathname.endsWith('adviser-dashboard.html') || window.location.pathname.endsWith('/');
      if (isDashboard) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }
}

let noticeToastTimer = null;
function showNoticeToast(title, message) {
  let toast = document.getElementById('comingSoonToast');
  if (!toast) return;

  const titleEl = document.getElementById('toastFeatureName');
  const subEl = toast.querySelector('.toast-sub');

  if (titleEl) titleEl.textContent = title;
  if (subEl) subEl.textContent = message;

  toast.classList.add('show');

  if (noticeToastTimer) clearTimeout(noticeToastTimer);
  noticeToastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 2800);
}

/**
 * Basic HTML escaping helper for safe text rendering
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
