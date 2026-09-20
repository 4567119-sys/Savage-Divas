(function () {
  'use strict';

  const state = {
    currentView: 'login',
    currentStep: 1,
    isHighContrast: false,
    textSize: 'normal',
    isOfflineSimulated: false,
    isActuallyOnline: navigator.onLine,
    isSpeaking: false,
    voiceId: sessionStorage.getItem('rsf_voice') || '1',
    readAloudPref: false,
    smsReminderEnabled: true,
    currentUser: null,
    idMethod: 'said',
    genericType: 'document',
    editingClaimId: null,
    formData: {
      date: '',
      time: '',
      location: '',
      vehicleReg: '',
      description: '',
      caseNumber: '482/09/2026',
      station: 'Cape Town Central',
      officer: 'Sgt. Dlamini',
      documents: {
        damage: null,
        license: null,
        police: null,
        other: null
      }
    },
    claims: []
  };

  const DEFAULT_USER = {
    name: 'Nokuthula Dlamini',
    idNumber: '8001015009087',
    passport: '',
    idMethod: 'said',
    phone: '082 555 0192',
    email: 'nokuthula@example.co.za',
    vehiclePlate: 'CA 145-987'
  };

  const INITIAL_CLAIMS = [
    {
      id: 'RS-1042',
      type: 'Accident',
      date: '12 Sep 2026',
      location: 'Cape Town CBD',
      description: 'Rear bumper damage. Police documentation still needed.',
      status: 'action_needed',
      pipeline: 'submitted'
    },
    {
      id: 'RS-0988',
      type: 'Document',
      date: '04 Sep 2026',
      location: '—',
      description: 'Annual investment statement received.',
      status: 'approved',
      pipeline: 'completed'
    }
  ];

  const GENERIC_COPY = {
    document: {
      title: 'I need a document',
      titleKey: 'requestDocumentTitle',
      lead: 'Tell us which statement, policy document or certificate you need.',
      leadKey: 'requestDocumentDesc',
      placeholder: 'e.g. I need my latest policy schedule and a tax certificate.'
    },
    renewal: {
      title: 'I need to renew something',
      titleKey: 'requestRenewalTitle',
      lead: 'Tell us what is coming up for renewal and when.',
      leadKey: 'requestRenewalDesc',
      placeholder: 'e.g. My vehicle policy renews next month. Please start the review.'
    },
    details: {
      title: 'I need to update my details',
      titleKey: 'requestDetailsTitle',
      lead: 'Tell us what has changed — address, phone, email or banking details.',
      leadKey: 'requestDetailsDesc',
      placeholder: 'e.g. I have a new mobile number and I have moved to Observatory.'
    },
    beneficiary: {
      title: 'Death / beneficiary claim',
      titleKey: 'requestBeneficiaryTitle',
      lead: 'We will guide you. You do not need to know the form name. Tell us who the policy belongs to and what has happened.',
      leadKey: 'requestBeneficiaryDesc',
      placeholder: 'Share only what you are comfortable sharing. An adviser will follow up.'
    },
    plan: {
      title: 'Help with my financial plan',
      titleKey: 'requestPlanTitle',
      lead: 'Ask for a review, a goal check-in, or a conversation with your adviser.',
      leadKey: 'requestPlanDesc',
      placeholder: 'e.g. I want to review my retirement contributions before year-end.'
    },
    other: {
      title: 'Something else',
      titleKey: 'requestOtherTitle',
      lead: 'Describe what you need in your own words. We will route it to the right person.',
      leadKey: 'requestOtherDesc',
      placeholder: 'Tell us what happened or what you are trying to do.'
    }
  };

  const $ = (id) => document.getElementById(id);

  const DOM = {
    viewWelcome: $('view-welcome'),
    viewLogin: $('view-login'),
    appShell: $('app-shell'),
    srAnnouncer: $('sr-announcer'),
    mainContent: $('main-content'),
    langSelect: $('langSelect'),
    mainLangSelect: $('mainLangSelect'),
    btnReadAloud: $('btnReadAloud'),
    btnVoiceMenu: $('btnVoiceMenu'),
    voicePanel: $('voicePanel'),
    settingsVoiceSelect: $('settingsVoiceSelect'),
    toggleContrastInput: $('toggleContrastInput'),
    toggleReadAloudPref: $('toggleReadAloudPref'),
    toggleOfflineSim: $('toggleOfflineSim'),
    toggleSms: $('toggleSms'),
    networkBadge: $('networkBadge'),
    networkIcon: $('networkIcon'),
    networkStatusText: $('networkStatusText'),
    btnUserAuth: $('btnUserAuth'),
    userAuthLabel: $('userAuthLabel'),
    brandLogoLink: $('brandLogoLink'),
    offlineNotice: $('offlineNotice'),
    onlineSyncNotice: $('onlineSyncNotice'),
    pendingCount: $('pendingCount'),
    btnSyncNow: $('btnSyncNow'),
    claimsList: $('claimsList'),
    viewHome: $('view-home'),
    viewReport: $('view-report'),
    viewRequests: $('view-requests'),
    viewGoals: $('view-goals'),
    viewMessages: $('view-messages'),
    viewSettings: $('view-settings'),
    viewGeneric: $('view-generic'),
    btnReadGuidance: $('btnReadGuidance'),
    guideNext: $('guideNext'),
    progressSteps: [$('pStep1'), $('pStep2'), $('pStep3'), $('pStep4')],
    step1: $('step-1'),
    step2: $('step-2'),
    step3: $('step-3'),
    step4: $('step-4'),
    formStep1: $('formStep1'),
    inputDate: $('inputDate'),
    inputTime: $('inputTime'),
    inputLocation: $('inputLocation'),
    inputVehicleReg: $('inputVehicleReg'),
    inputDescription: $('inputDescription'),
    btnStep1Cancel: $('btnStep1Cancel'),
    fileDamage: $('fileDamage'),
    btnSampleDamage: $('btnSampleDamage'),
    scanBoxDamage: $('scanBoxDamage'),
    scanTextDamage: $('scanTextDamage'),
    scanFillDamage: $('scanFillDamage'),
    previewDamage: $('previewDamage'),
    imgPreviewDamage: $('imgPreviewDamage'),
    fileNameDamage: $('fileNameDamage'),
    btnRemoveDamage: $('btnRemoveDamage'),
    badgeDamage: $('badgeDamage'),
    fileLicense: $('fileLicense'),
    btnSampleLicense: $('btnSampleLicense'),
    scanBoxLicense: $('scanBoxLicense'),
    scanTextLicense: $('scanTextLicense'),
    scanFillLicense: $('scanFillLicense'),
    previewLicense: $('previewLicense'),
    fileNameLicense: $('fileNameLicense'),
    btnRemoveLicense: $('btnRemoveLicense'),
    badgeLicense: $('badgeLicense'),
    filePolice: $('filePolice'),
    btnSamplePolice: $('btnSamplePolice'),
    previewPolice: $('previewPolice'),
    fileNamePolice: $('fileNamePolice'),
    btnRemovePolice: $('btnRemovePolice'),
    badgePolice: $('badgePolice'),
    fileOther: $('fileOther'),
    previewOther: $('previewOther'),
    fileNameOther: $('fileNameOther'),
    btnRemoveOther: $('btnRemoveOther'),
    btnStep2Back: $('btnStep2Back'),
    btnStep2Next: $('btnStep2Next'),
    revDate: $('revDate'),
    revTime: $('revTime'),
    revLocation: $('revLocation'),
    revVehicle: $('revVehicle'),
    revDescription: $('revDescription'),
    revDocDamage: $('revDocDamage'),
    revDocLicense: $('revDocLicense'),
    revDocPolice: $('revDocPolice'),
    revDocOther: $('revDocOther'),
    revCaseNumber: $('revCaseNumber'),
    revStation: $('revStation'),
    revOfficer: $('revOfficer'),
    btnEditStep1: $('btnEditStep1'),
    btnEditStep2: $('btnEditStep2'),
    btnStep3Back: $('btnStep3Back'),
    btnSubmitClaim: $('btnSubmitClaim'),
    confirmedRefCode: $('confirmedRefCode'),
    confirmedOfflineBadge: $('confirmedOfflineBadge'),
    btnFinishReturnHome: $('btnFinishReturnHome'),
    btnPrintSummary: $('btnPrintSummary'),
    errorModal: $('errorModal'),
    btnCloseModal: $('btnCloseModal'),
    btnOpenLogin: $('btnOpenLogin'),
    btnWelcomeVoice: $('btnWelcomeVoice'),
    btnBackToWelcome: $('btnBackToWelcome'),
    btnLoginVoice: $('btnLoginVoice'),
    welcomeLangSelect: $('welcomeLangSelect'),
    loginForm: $('loginForm'),
    idMethodSa: $('idMethodSa'),
    idMethodPassport: $('idMethodPassport'),
    saIdGroup: $('saIdGroup'),
    passportGroup: $('passportGroup'),
    loginSaId: $('loginSaId'),
    loginPassport: $('loginPassport'),
    saIdError: $('saIdError'),
    passportError: $('passportError'),
    btnSignOut: $('btnSignOut'),
    settingsIdMethod: $('settingsIdMethod'),
    settingsContact: $('settingsContact'),
    genericForm: $('genericForm'),
    genericTitle: $('genericTitle'),
    genericLead: $('genericLead'),
    genericDetail: $('genericDetail'),
    btnGenericScan: $('btnGenericScan'),
    btnGenericSampleScan: $('btnGenericSampleScan'),
    genericScanInput: $('genericScanInput'),
    genericScanStatus: $('genericScanStatus'),
    btnAccidentScan: $('btnAccidentScan'),
    btnAccidentSampleScan: $('btnAccidentSampleScan'),
    accidentScanInput: $('accidentScanInput'),
    accidentScanStatus: $('accidentScanStatus'),
    btnGenericCancel: $('btnGenericCancel'),
    btnContinueClaim1042: $('btnContinueClaim1042'),
    btnScheduleReview: $('btnScheduleReview')
  };

  function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
    }
  }

  function init() {
    registerServiceWorker();
    loadPreferences();
    loadClaims();
    bindEvents();
    initSpeechSynthesis();
    updateNetworkStatus();
    renderLocalizedHomeCards();
    checkAuthGate();
    const today = new Date().toISOString().slice(0, 10);
    if (DOM.inputDate) DOM.inputDate.value = today;
  }

  function loadPreferences() {
    const savedLang = localStorage.getItem('rsf_lang') || 'en';
    if (DOM.langSelect) {
      DOM.langSelect.value = savedLang;
      setLanguage(savedLang);
    }
    if (DOM.welcomeLangSelect) DOM.welcomeLangSelect.value = savedLang;
    if (DOM.mainLangSelect) DOM.mainLangSelect.value = savedLang;
    if (localStorage.getItem('rsf_contrast') === 'high') {
      state.isHighContrast = true;
      document.documentElement.setAttribute('data-contrast', 'high');
      if (DOM.toggleContrastInput) DOM.toggleContrastInput.checked = true;
    }
    setTextSize(localStorage.getItem('rsf_textsize') || 'normal');
    setVoice(state.voiceId, false);
    state.readAloudPref = localStorage.getItem('rsf_read_aloud') === 'true';
    if (DOM.toggleReadAloudPref) DOM.toggleReadAloudPref.checked = state.readAloudPref;
    const sms = localStorage.getItem('rsf_sms_reminders');
    if (sms !== null) {
      state.smsReminderEnabled = sms === 'true';
      if (DOM.toggleSms) DOM.toggleSms.checked = state.smsReminderEnabled;
    }
  }

  function checkAuthGate() {
    // Always show the welcome choice first. A previous demo login is not used
    // to silently bypass the login screen.
    const savedUser = localStorage.getItem('rsf_user');
    if (savedUser) {
      try {
        state.currentUser = JSON.parse(savedUser);
      } catch (e) {
        state.currentUser = null;
      }
    }
    showWelcome();
  }

  function showWelcome() {
    state.currentView = 'welcome';
    if (DOM.viewWelcome) DOM.viewWelcome.hidden = false;
    DOM.viewLogin.hidden = true;
    DOM.appShell.hidden = true;
    if (DOM.welcomeLangSelect) DOM.welcomeLangSelect.value = currentLang || 'en';
    if (DOM.mainLangSelect) DOM.mainLangSelect.value = currentLang || 'en';
  }

  function showLogin() {
    state.currentView = 'login';
    if (DOM.viewWelcome) DOM.viewWelcome.hidden = true;
    DOM.viewLogin.hidden = false;
    DOM.appShell.hidden = true;
  }

  function showAuthenticatedApp() {
    if (DOM.viewWelcome) DOM.viewWelcome.hidden = true;
    DOM.viewLogin.hidden = true;
    DOM.appShell.hidden = false;
    updateUserHeaderUI();
    navigateTo('home');
    if (state.readAloudPref) {
      speakText('What would you like to report or do? Tell us what happened and we will guide you through the next steps.');
    }
  }

  function updateUserHeaderUI() {
    if (!state.currentUser) return;
    DOM.userAuthLabel.textContent = state.currentUser.name.split(' ')[0];
    if (DOM.settingsIdMethod) {
      DOM.settingsIdMethod.textContent = state.currentUser.idMethod === 'passport'
        ? 'Passport Number'
        : 'South African ID Number';
    }
    if (DOM.settingsContact) {
      DOM.settingsContact.textContent = `${state.currentUser.phone} · ${state.currentUser.email || DEFAULT_USER.email}`;
    }
    if (DOM.inputVehicleReg && !DOM.inputVehicleReg.value) {
      DOM.inputVehicleReg.value = state.currentUser.vehiclePlate || DEFAULT_USER.vehiclePlate;
    }
  }

  function loadClaims() {
    const stored = localStorage.getItem('rsf_claims');
    if (stored) {
      try {
        state.claims = JSON.parse(stored);
      } catch (e) {
        state.claims = INITIAL_CLAIMS.slice();
      }
    } else {
      state.claims = INITIAL_CLAIMS.slice();
      saveClaims();
    }
  }

  function saveClaims() {
    localStorage.setItem('rsf_claims', JSON.stringify(state.claims));
  }

  function announce(message) {
    if (DOM.srAnnouncer) DOM.srAnnouncer.textContent = message;
  }

  function setTextSize(size) {
    state.textSize = size;
    localStorage.setItem('rsf_textsize', size);
    if (size === 'normal') document.documentElement.removeAttribute('data-text-size');
    else document.documentElement.setAttribute('data-text-size', size);
    document.querySelectorAll('.text-size-btn').forEach((btn) => {
      btn.classList.toggle('selected', btn.getAttribute('data-size') === size);
    });
    announce(`Text size ${size}`);
  }

  function toggleHighContrast() {
    state.isHighContrast = !state.isHighContrast;
    if (state.isHighContrast) {
      document.documentElement.setAttribute('data-contrast', 'high');
      localStorage.setItem('rsf_contrast', 'high');
      announce('High contrast on');
    } else {
      document.documentElement.removeAttribute('data-contrast');
      localStorage.removeItem('rsf_contrast');
      announce('High contrast off');
    }
    if (DOM.toggleContrastInput) DOM.toggleContrastInput.checked = state.isHighContrast;
  }

  function setVoice(id, speakSample) {
    state.voiceId = String(id);
    sessionStorage.setItem('rsf_voice', state.voiceId);
    document.querySelectorAll('.voice-option').forEach((btn) => {
      btn.classList.toggle('selected', btn.getAttribute('data-voice') === state.voiceId);
    });
    if (DOM.settingsVoiceSelect) DOM.settingsVoiceSelect.value = state.voiceId;
    if (speakSample) speakText('This is the selected voice for Royal Square Financial.');
  }

  function initSpeechSynthesis() {
    if (!('speechSynthesis' in window)) {
      if (DOM.btnReadAloud) DOM.btnReadAloud.disabled = true;
      if (DOM.btnReadGuidance) DOM.btnReadGuidance.disabled = true;
    }
  }

  function voiceProfile() {
    const map = {
      1: { gender: 'female', pitch: 1.12, rate: 0.92 },
      2: { gender: 'male', pitch: 0.84, rate: 0.9 },
      3: { gender: 'female', pitch: 1.02, rate: 0.88 },
      4: { gender: 'male', pitch: 0.78, rate: 0.86 }
    };
    return map[state.voiceId] || map[1];
  }

  function getBestVoice() {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices.length) return null;
    const langObj = (typeof I18N_DATA !== 'undefined' && I18N_DATA[currentLang]) || { speechCode: 'en-ZA' };
    const code = (langObj.speechCode || 'en-ZA').toLowerCase();
    let candidates = voices.filter((v) => v.lang.toLowerCase() === code);
    if (!candidates.length) candidates = voices.filter((v) => v.lang.toLowerCase().startsWith(code.slice(0, 2)));
    if (!candidates.length) candidates = voices;
    const profile = voiceProfile();
    const male = ['david', 'george', 'mark', 'richard', 'james', 'male', 'guy'];
    const female = ['zira', 'susan', 'hazel', 'catherine', 'female', 'samantha', 'victoria', 'zira'];
    const names = profile.gender === 'male' ? male : female;
    const altOffset = state.voiceId === '3' || state.voiceId === '4' ? 1 : 0;
    const matches = candidates.filter((v) => names.some((n) => v.name.toLowerCase().includes(n)));
    return matches[altOffset] || matches[0] || candidates[0];
  }

  function speakText(text) {
    if (!('speechSynthesis' in window)) return;
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      setSpeakingState(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    const langObj = (typeof I18N_DATA !== 'undefined' && I18N_DATA[currentLang]) || { speechCode: 'en-ZA' };
    utterance.lang = langObj.speechCode || 'en-ZA';
    const profile = voiceProfile();
    utterance.pitch = profile.pitch;
    utterance.rate = profile.rate;
    const matched = getBestVoice();
    if (matched) utterance.voice = matched;
    utterance.onstart = () => setSpeakingState(true);
    utterance.onend = () => setSpeakingState(false);
    utterance.onerror = () => setSpeakingState(false);
    window.speechSynthesis.speak(utterance);
  }

  function setSpeakingState(speaking) {
    state.isSpeaking = speaking;
    if (!DOM.btnReadAloud) return;
    DOM.btnReadAloud.textContent = speaking ? 'Stop' : '🔊 Read Aloud';
  }

  function readWelcomePage() {
    const text = [
      t('authTitle'),
      t('authSubtitle'),
      t('loginChoicePrompt'),
      t('signInBtn'),
      t('languageLabel')
    ].join('. ');
    speakText(text);
  }

  function readLoginPage() {
    const text = [
      t('authTitle'),
      t('authSubtitle'),
      t('tabSignIn'),
      t('labelSaIdNumber'),
      t('labelPassportNumber'),
      t('btnContinueLogin') || t('btnVerifyOtp')
    ].join('. ');
    speakText(text);
  }

  function readCurrentGuidance() {
    let text = '';
    if (state.currentView === 'home') {
      text = 'What would you like to report or do? Tell us what happened and we will guide you through the next steps. You can report an accident, request a document, renew something, update your details, ask about a death or beneficiary claim, get help with your financial plan, or describe something else.';
    } else if (state.currentView === 'report') {
      if (state.currentStep === 1) text = 'Step 1. Tell us what happened. Enter the date, approximate time, location, vehicle registration and a short description.';
      else if (state.currentStep === 2) text = 'Step 2. Provide supporting documents. You can upload police documentation, photos, vehicle documents or other evidence.';
      else if (state.currentStep === 3) text = 'Step 3. Review information. We detected a SAPS case number, police station and investigating officer. You can correct these before submitting.';
      else text = 'Claim status. Your claim has been submitted. Next comes assessment, then awaiting authorisation if needed, then completed.';
    } else if (state.currentView === 'settings') {
      text = 'Settings. Account, accessibility, language, notifications, and privacy.';
    } else {
      text = document.querySelector('.page-lead') ? document.querySelector('.page-lead').textContent : 'Royal Square Financial.';
    }
    speakText(text);
  }

  function isEffectiveOnline() {
    if (state.isOfflineSimulated) return false;
    return state.isActuallyOnline;
  }

  function updateNetworkStatus() {
    const online = isEffectiveOnline();
    if (!DOM.networkBadge) return;
    if (online) {
      DOM.networkBadge.className = 'network-badge online';
      DOM.networkIcon.textContent = '●';
      DOM.networkStatusText.textContent = 'Online';
      DOM.offlineNotice.style.display = 'none';
      const pending = state.claims.filter((c) => c.status === 'waiting_to_sync');
      if (pending.length) {
        DOM.pendingCount.textContent = pending.length;
        DOM.onlineSyncNotice.style.display = 'flex';
      } else {
        DOM.onlineSyncNotice.style.display = 'none';
      }
    } else {
      DOM.networkBadge.className = 'network-badge offline';
      DOM.networkIcon.textContent = '●';
      DOM.networkStatusText.textContent = "You're offline";
      DOM.offlineNotice.style.display = 'flex';
      DOM.onlineSyncNotice.style.display = 'none';
    }
    renderClaimsList();
  }

  function toggleSimulateOffline(on) {
    state.isOfflineSimulated = on;
    if (DOM.toggleOfflineSim) DOM.toggleOfflineSim.checked = on;
    announce(on ? "You're offline. Requests can still be saved on this device." : 'Connection restored.');
    updateNetworkStatus();
  }

  function syncPendingClaims() {
    const pending = state.claims.filter((c) => c.status === 'waiting_to_sync');
    if (!pending.length) return;
    DOM.btnSyncNow.disabled = true;
    DOM.btnSyncNow.textContent = 'Submitting…';
    setTimeout(() => {
      state.claims.forEach((c) => {
        if (c.status === 'waiting_to_sync') {
          c.status = 'review';
          c.pipeline = 'assessment';
        }
      });
      saveClaims();
      renderClaimsList();
      DOM.btnSyncNow.disabled = false;
      DOM.btnSyncNow.textContent = 'Request submitted successfully';
      announce('Request submitted successfully');
      setTimeout(() => {
        DOM.onlineSyncNotice.style.display = 'none';
        DOM.btnSyncNow.textContent = 'Sync Request';
      }, 2200);
    }, 900);
  }

  function setNav(viewName) {
    document.querySelectorAll('.nav-link').forEach((link) => {
      const isCurrent = link.getAttribute('data-nav') === viewName;
      if (isCurrent) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }

  function hideAllViews() {
    [DOM.viewHome, DOM.viewReport, DOM.viewRequests, DOM.viewGoals, DOM.viewMessages, DOM.viewSettings, DOM.viewGeneric]
      .forEach((el) => { if (el) el.hidden = true; });
  }

  function navigateTo(viewName, step) {
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      setSpeakingState(false);
    }
    state.currentView = viewName;
    hideAllViews();
    const navViews = ['home', 'requests', 'goals', 'messages', 'settings'];
    setNav(navViews.includes(viewName) ? viewName : 'home');

    if (viewName === 'home') DOM.viewHome.hidden = false;
    else if (viewName === 'requests') {
      DOM.viewRequests.hidden = false;
      renderClaimsList();
    } else if (viewName === 'goals') DOM.viewGoals.hidden = false;
    else if (viewName === 'messages') DOM.viewMessages.hidden = false;
    else if (viewName === 'settings') DOM.viewSettings.hidden = false;
    else if (viewName === 'generic') DOM.viewGeneric.hidden = false;
    else if (viewName === 'report') {
      DOM.viewReport.hidden = false;
      goToStep(step || 1);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
    DOM.mainContent.focus();
  }

  function renderLocalizedHomeCards() {
    document.querySelectorAll('.request-card').forEach((card) => {
      const type = card.getAttribute('data-request');
      const titleEl = card.querySelector('h3');
      const descEl = card.querySelector('p');
      if (!titleEl || !descEl) return;
      if (type === 'accident') {
        titleEl.textContent = t('reportAccidentCardTitle');
        descEl.textContent = t('reportAccidentCardDesc');
        return;
      }
      const copy = GENERIC_COPY[type];
      if (copy) {
        titleEl.textContent = copy.titleKey ? t(copy.titleKey) : copy.title;
        descEl.textContent = copy.leadKey ? t(copy.leadKey) : copy.lead;
      }
    });
  }

  function showAiStatus(el, message, success = false) {
    if (!el) return;
    el.hidden = false;
    el.textContent = message;
    el.classList.toggle('success', success);
  }

  function demoExtractGeneric(type) {
    const examples = {
      document: 'I need my latest policy schedule and my annual tax certificate.',
      renewal: 'Please renew my vehicle insurance policy. My current policy is due for renewal next month.',
      details: 'I have moved to a new address and need my contact details updated.',
      beneficiary: 'I need help starting a beneficiary claim. Please contact me about the required documents and next steps.',
      plan: 'I would like a review of my financial plan and my current savings goals.',
      other: 'I need help with a request. Please review the attached document and tell me what I need to do next.'
    };
    return examples[type] || examples.other;
  }

  function runGenericAiScan(file) {
    const label = file ? file.name : 'demo-document.jpg';
    showAiStatus(DOM.genericScanStatus, t('aiScanning'));
    setTimeout(() => {
      DOM.genericDetail.value = demoExtractGeneric(state.genericType);
      showAiStatus(DOM.genericScanStatus, `${t('aiFilled')} (${label})`, true);
      announce(t('aiFilled'));
    }, 900);
  }

  function runAccidentAiScan(file) {
    const label = file ? file.name : 'demo-accident-document.jpg';
    showAiStatus(DOM.accidentScanStatus, t('aiScanning'));
    setTimeout(() => {
      const d = new Date();
      const iso = new Date(d.getTime() - 86400000).toISOString();
      DOM.inputDate.value = iso.slice(0, 10);
      DOM.inputTime.value = '14:30';
      DOM.inputLocation.value = 'Main Road, Cape Town CBD';
      DOM.inputVehicleReg.value = 'CA 145-987';
      DOM.inputDescription.value = 'Another vehicle reversed into the front of my car in a parking area. The front bumper was damaged.';
      showAiStatus(DOM.accidentScanStatus, `${t('aiFilled')} (${label})`, true);
      announce(t('aiFilled'));
    }, 1100);
  }

  function openGeneric(type) {
    state.genericType = type;
    const copy = GENERIC_COPY[type];
    DOM.genericTitle.textContent = copy.titleKey ? t(copy.titleKey) : copy.title;
    DOM.genericLead.textContent = copy.leadKey ? t(copy.leadKey) : copy.lead;
    DOM.genericDetail.placeholder = copy.placeholder;
    DOM.genericDetail.value = '';
    navigateTo('generic');
  }

  function goToStep(stepNumber) {
    state.currentStep = stepNumber;
    [DOM.step1, DOM.step2, DOM.step3, DOM.step4].forEach((el) => {
      if (el) el.hidden = true;
    });
    DOM.progressSteps.forEach((stepEl, idx) => {
      const stepIdx = idx + 1;
      stepEl.classList.remove('active', 'completed');
      if (stepIdx < stepNumber) stepEl.classList.add('completed');
      else if (stepIdx === stepNumber) {
        stepEl.classList.add('active');
        stepEl.setAttribute('aria-current', 'step');
      } else stepEl.removeAttribute('aria-current');
    });
    const nextCopy = {
      1: 'Enter the date, approximate time, location, vehicle registration and a short description.',
      2: 'Upload police documentation, photos, vehicle documents or other evidence.',
      3: 'Check the detected police information and correct anything that is wrong.',
      4: 'Your request is in. Watch the status so you always know what happens next.'
    };
    DOM.guideNext.textContent = nextCopy[stepNumber];
    if (stepNumber === 1) DOM.step1.hidden = false;
    if (stepNumber === 2) DOM.step2.hidden = false;
    if (stepNumber === 3) {
      DOM.step3.hidden = false;
      populateReviewData();
    }
    if (stepNumber === 4) DOM.step4.hidden = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (state.readAloudPref) readCurrentGuidance();
  }

  function statusLabel(status) {
    if (status === 'approved') return 'Completed';
    if (status === 'review') return 'Assessment';
    if (status === 'action_needed') return 'Action required';
    if (status === 'waiting_to_sync') return 'Saved on this device';
    return status;
  }

  function renderClaimsList() {
    if (!DOM.claimsList) return;
    DOM.claimsList.innerHTML = '';
    if (!state.claims.length) {
      DOM.claimsList.innerHTML = '<p class="empty-note">No requests yet. Start from Home.</p>';
      return;
    }
    state.claims.forEach((claim) => {
      const card = document.createElement('article');
      card.className = 'claim-card';
      const pillClass = claim.status === 'approved' ? 'approved'
        : claim.status === 'review' ? 'review'
          : claim.status === 'waiting_to_sync' ? 'waiting-sync'
            : 'action-needed';
      card.innerHTML = `
        <div class="claim-info-main">
          <div class="claim-ref-line" style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;">
            <h2 class="claim-ref-number">${claim.id}</h2>
            <span class="status-pill ${pillClass}">${statusLabel(claim.status)}</span>
          </div>
          <div class="claim-meta-details">
            <span>${claim.type || 'Request'}</span>
            <span>${claim.date}</span>
            <span>${claim.location}</span>
          </div>
          <p style="margin-top:0.35rem;">${claim.description}</p>
        </div>
        <div>
          ${claim.status === 'action_needed' ? `<button type="button" class="btn btn-primary btn-sm btn-upload-direct" data-claim-id="${claim.id}">Continue</button>` : ''}
          <button type="button" class="btn btn-secondary btn-sm btn-claim-details" data-claim-id="${claim.id}">View</button>
        </div>
      `;
      DOM.claimsList.appendChild(card);
    });
    DOM.claimsList.querySelectorAll('.btn-upload-direct').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.editingClaimId = btn.getAttribute('data-claim-id');
        navigateTo('report', 2);
      });
    });
    DOM.claimsList.querySelectorAll('.btn-claim-details').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-claim-id');
        const c = state.claims.find((item) => item.id === id);
        if (c) {
          navigateTo('report', c.id === 'RS-1042' && c.status === 'action_needed' ? 2 : 4);
          if (DOM.confirmedRefCode) DOM.confirmedRefCode.textContent = c.id;
        }
      });
    });
  }

  function validateStep1() {
    const loc = DOM.inputLocation.value.trim();
    const desc = DOM.inputDescription.value.trim();
    if (!loc) {
      DOM.inputLocation.focus();
      announce('Please enter a location.');
      return false;
    }
    if (!desc) {
      DOM.inputDescription.focus();
      announce('Please enter a short description.');
      return false;
    }
    state.formData.date = DOM.inputDate.value;
    state.formData.time = DOM.inputTime.value;
    state.formData.location = loc;
    state.formData.vehicleReg = DOM.inputVehicleReg.value.trim();
    state.formData.description = desc;
    return true;
  }

  function simulateDocumentScan(cardName, fileName, previewUrl) {
    const scanBox = cardName === 'damage' ? DOM.scanBoxDamage : DOM.scanBoxLicense;
    const scanText = cardName === 'damage' ? DOM.scanTextDamage : DOM.scanTextLicense;
    const scanFill = cardName === 'damage' ? DOM.scanFillDamage : DOM.scanFillLicense;
    const previewBox = cardName === 'damage' ? DOM.previewDamage : DOM.previewLicense;
    const fileNameEl = cardName === 'damage' ? DOM.fileNameDamage : DOM.fileNameLicense;
    const badgeEl = cardName === 'damage' ? DOM.badgeDamage : DOM.badgeLicense;
    if (scanBox) {
      scanBox.hidden = false;
      scanFill.style.width = '30%';
      scanText.textContent = 'Uploading…';
    }
    setTimeout(() => {
      if (scanFill) scanFill.style.width = '100%';
      if (scanBox) scanBox.hidden = true;
      if (cardName === 'damage' && previewUrl) DOM.imgPreviewDamage.src = previewUrl;
      fileNameEl.textContent = fileName;
      previewBox.hidden = false;
      previewBox.style.display = 'flex';
      if (badgeEl) {
        badgeEl.className = 'status-pill approved';
        badgeEl.textContent = 'Uploaded';
      }
      announce(`${fileName} saved on this device.`);
    }, 700);
  }

  function populateReviewData() {
    DOM.revDate.textContent = state.formData.date || DOM.inputDate.value || 'Not specified';
    DOM.revTime.textContent = state.formData.time || DOM.inputTime.value || 'Not specified';
    DOM.revLocation.textContent = state.formData.location || 'Not specified';
    DOM.revVehicle.textContent = state.formData.vehicleReg || 'Not specified';
    DOM.revDescription.textContent = state.formData.description || '—';
    DOM.revDocPolice.textContent = state.formData.documents.police ? state.formData.documents.police.name : 'Not uploaded';
    DOM.revDocDamage.textContent = state.formData.documents.damage ? state.formData.documents.damage.name : 'Not uploaded';
    DOM.revDocLicense.textContent = state.formData.documents.license ? state.formData.documents.license.name : 'None provided';
    DOM.revDocOther.textContent = state.formData.documents.other ? state.formData.documents.other.name : 'None provided';
  }

  function setPipelineUI(stage) {
    const order = ['submitted', 'assessment', 'auth', 'completed'];
    const els = [$('stSubmitted'), $('stAssessment'), $('stAuth'), $('stDone')];
    const idx = order.indexOf(stage);
    els.forEach((el, i) => {
      if (!el) return;
      el.classList.remove('done', 'current');
      if (i < idx) el.classList.add('done');
      if (i === idx) el.classList.add('current');
    });
  }

  function submitAccidentReport() {
    const online = isEffectiveOnline();
    state.formData.caseNumber = DOM.revCaseNumber.value;
    state.formData.station = DOM.revStation.value;
    state.formData.officer = DOM.revOfficer.value;

    let ref = state.editingClaimId || 'RS-' + (1000 + Math.floor(Math.random() * 900));
    const existing = state.claims.find((c) => c.id === state.editingClaimId);
    if (existing) {
      existing.status = online ? 'review' : 'waiting_to_sync';
      existing.pipeline = online ? 'assessment' : 'submitted';
      if (state.formData.description) existing.description = state.formData.description;
      if (state.formData.location) existing.location = state.formData.location;
      ref = existing.id;
    } else {
      state.claims.unshift({
        id: ref,
        type: 'Accident',
        date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
        location: state.formData.location,
        description: state.formData.description,
        status: online ? 'review' : 'waiting_to_sync',
        pipeline: online ? 'assessment' : 'submitted'
      });
    }
    saveClaims();
    DOM.confirmedRefCode.textContent = ref;
    DOM.confirmedOfflineBadge.hidden = online;
    setPipelineUI(online ? 'assessment' : 'submitted');
    goToStep(4);
    if (!online) {
      announce('Your request has been saved on this device and will be submitted when your connection returns.');
    } else {
      announce('Request submitted successfully. What happens next: assessment, then authorisation if needed.');
    }
  }

  function digitsOnly(value) {
    return value.replace(/\D/g, '');
  }

  function setIdMethod(method) {
    state.idMethod = method;
    const isSa = method === 'said';
    DOM.idMethodSa.setAttribute('aria-pressed', isSa ? 'true' : 'false');
    DOM.idMethodPassport.setAttribute('aria-pressed', isSa ? 'false' : 'true');
    DOM.saIdGroup.hidden = !isSa;
    DOM.passportGroup.hidden = isSa;
    DOM.saIdError.classList.remove('visible');
    DOM.passportError.classList.remove('visible');
    DOM.loginSaId.classList.remove('invalid');
    DOM.loginPassport.classList.remove('invalid');
  }

  function handleLogin(e) {
    e.preventDefault();
    if (state.idMethod === 'said') {
      const id = digitsOnly(DOM.loginSaId.value);
      DOM.loginSaId.value = id;
      if (id.length !== 13) {
        DOM.saIdError.classList.add('visible');
        DOM.loginSaId.classList.add('invalid');
        DOM.loginSaId.focus();
        return;
      }
      DOM.saIdError.classList.remove('visible');
      DOM.loginSaId.classList.remove('invalid');
      state.currentUser = {
        ...DEFAULT_USER,
        idNumber: id,
        idMethod: 'said',
        passport: ''
      };
    } else {
      const raw = DOM.loginPassport.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
      DOM.loginPassport.value = raw;
      const ok = /^[A-Z]{2}[0-9]{4}$/.test(raw);
      if (!ok) {
        DOM.passportError.classList.add('visible');
        DOM.loginPassport.classList.add('invalid');
        DOM.loginPassport.focus();
        return;
      }
      DOM.passportError.classList.remove('visible');
      DOM.loginPassport.classList.remove('invalid');
      state.currentUser = {
        ...DEFAULT_USER,
        idMethod: 'passport',
        passport: raw,
        idNumber: ''
      };
    }
    localStorage.setItem('rsf_user', JSON.stringify(state.currentUser));
    showAuthenticatedApp();
    announce('Signed in. Welcome to your client dashboard.');
  }

  function signOutUser() {
    state.currentUser = null;
    localStorage.removeItem('rsf_user');
    showLogin();
    announce('Signed out.');
  }

  function bindDocUploads() {
    DOM.btnSampleDamage.addEventListener('click', () => {
      state.formData.documents.damage = { name: 'vehicle_damage_sample.jpg', url: 'assets/damage_sample.jpg' };
      simulateDocumentScan('damage', 'vehicle_damage_sample.jpg', 'assets/damage_sample.jpg');
    });
    $('btnUploadDamage').addEventListener('click', () => DOM.fileDamage.click());
    DOM.fileDamage.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
        state.formData.documents.damage = { name: file.name, url: evt.target.result };
        simulateDocumentScan('damage', file.name, evt.target.result);
      };
      reader.readAsDataURL(file);
    });
    DOM.btnRemoveDamage.addEventListener('click', () => {
      state.formData.documents.damage = null;
      DOM.previewDamage.hidden = true;
      DOM.badgeDamage.className = 'status-pill action-needed';
      DOM.badgeDamage.textContent = 'Still needed';
    });

    $('btnUploadLicense').addEventListener('click', () => DOM.fileLicense.click());
    DOM.btnSampleLicense.addEventListener('click', () => {
      state.formData.documents.license = { name: 'vehicle_licence.jpg' };
      simulateDocumentScan('license', 'vehicle_licence.jpg');
    });
    DOM.fileLicense.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      state.formData.documents.license = { name: file.name };
      simulateDocumentScan('license', file.name);
    });
    DOM.btnRemoveLicense.addEventListener('click', () => {
      state.formData.documents.license = null;
      DOM.previewLicense.hidden = true;
    });

    $('btnUploadPolice').addEventListener('click', () => DOM.filePolice.click());
    DOM.btnSamplePolice.addEventListener('click', () => {
      state.formData.documents.police = { name: 'saps_case_482_09_2026.pdf' };
      DOM.fileNamePolice.textContent = 'saps_case_482_09_2026.pdf';
      DOM.previewPolice.hidden = false;
      DOM.previewPolice.style.display = 'flex';
      DOM.badgePolice.className = 'status-pill approved';
      DOM.badgePolice.textContent = 'Uploaded';
      $('cardDocPolice').classList.add('has-file');
    });
    DOM.filePolice.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      state.formData.documents.police = { name: file.name };
      DOM.fileNamePolice.textContent = file.name;
      DOM.previewPolice.hidden = false;
      DOM.previewPolice.style.display = 'flex';
      DOM.badgePolice.className = 'status-pill approved';
      DOM.badgePolice.textContent = 'Uploaded';
    });
    DOM.btnRemovePolice.addEventListener('click', () => {
      state.formData.documents.police = null;
      DOM.previewPolice.hidden = true;
      DOM.badgePolice.className = 'status-pill action-needed';
      DOM.badgePolice.textContent = 'Still needed';
    });

    $('btnUploadOther').addEventListener('click', () => DOM.fileOther.click());
    DOM.fileOther.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      state.formData.documents.other = { name: file.name };
      DOM.fileNameOther.textContent = file.name;
      DOM.previewOther.hidden = false;
      DOM.previewOther.style.display = 'flex';
    });
    DOM.btnRemoveOther.addEventListener('click', () => {
      state.formData.documents.other = null;
      DOM.previewOther.hidden = true;
    });
  }

  function bindEvents() {
    DOM.langSelect.addEventListener('change', (e) => {
      setLanguage(e.target.value);
    });
    if (DOM.mainLangSelect) DOM.mainLangSelect.addEventListener('change', (e) => setLanguage(e.target.value));
    if (DOM.welcomeLangSelect) {
      DOM.welcomeLangSelect.addEventListener('change', (e) => {
        setLanguage(e.target.value);
      });
    }
    document.addEventListener('rsf:languagechanged', () => {
      const lang = currentLang || 'en';
      if (DOM.langSelect) DOM.langSelect.value = lang;
      if (DOM.mainLangSelect) DOM.mainLangSelect.value = lang;
      if (DOM.welcomeLangSelect) DOM.welcomeLangSelect.value = lang;
      renderLocalizedHomeCards();
      if (state.currentView === 'generic' && GENERIC_COPY[state.genericType]) {
        const copy = GENERIC_COPY[state.genericType];
        DOM.genericTitle.textContent = copy.titleKey ? t(copy.titleKey) : copy.title;
        DOM.genericLead.textContent = copy.leadKey ? t(copy.leadKey) : copy.lead;
        DOM.genericDetail.placeholder = copy.placeholder;
      }
    });
    DOM.btnOpenLogin.addEventListener('click', () => {
      showLogin();
      DOM.loginSaId.focus();
    });
    DOM.btnWelcomeVoice.addEventListener('click', readWelcomePage);
    DOM.btnBackToWelcome.addEventListener('click', showWelcome);
    DOM.btnLoginVoice.addEventListener('click', readLoginPage);
    DOM.btnReadAloud.addEventListener('click', readCurrentGuidance);
    DOM.btnReadGuidance.addEventListener('click', readCurrentGuidance);

    DOM.btnVoiceMenu.addEventListener('click', () => {
      const open = DOM.voicePanel.hidden;
      DOM.voicePanel.hidden = !open;
      DOM.btnVoiceMenu.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', (e) => {
      if (!DOM.voicePanel.hidden && !DOM.voicePanel.contains(e.target) && e.target !== DOM.btnVoiceMenu) {
        DOM.voicePanel.hidden = true;
        DOM.btnVoiceMenu.setAttribute('aria-expanded', 'false');
      }
    });
    document.querySelectorAll('.voice-option').forEach((btn) => {
      btn.addEventListener('click', () => setVoice(btn.getAttribute('data-voice'), true));
    });
    DOM.settingsVoiceSelect.addEventListener('change', (e) => setVoice(e.target.value, true));

    document.querySelectorAll('.text-size-btn').forEach((btn) => {
      btn.addEventListener('click', () => setTextSize(btn.getAttribute('data-size')));
    });
    DOM.toggleContrastInput.addEventListener('change', toggleHighContrast);
    DOM.toggleReadAloudPref.addEventListener('change', (e) => {
      state.readAloudPref = e.target.checked;
      localStorage.setItem('rsf_read_aloud', state.readAloudPref ? 'true' : 'false');
    });
    DOM.toggleSms.addEventListener('change', (e) => {
      state.smsReminderEnabled = e.target.checked;
      localStorage.setItem('rsf_sms_reminders', e.target.checked ? 'true' : 'false');
    });
    DOM.toggleOfflineSim.addEventListener('change', (e) => toggleSimulateOffline(e.target.checked));

    DOM.btnCloseModal.addEventListener('click', () => DOM.errorModal.classList.remove('active'));

    DOM.btnUserAuth.addEventListener('click', () => navigateTo('settings'));
    DOM.btnSignOut.addEventListener('click', signOutUser);

    document.querySelectorAll('.nav-link').forEach((link) => {
      link.addEventListener('click', () => navigateTo(link.getAttribute('data-nav')));
    });
    DOM.brandLogoLink.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo('home');
    });

    document.querySelectorAll('.request-card').forEach((card) => {
      card.addEventListener('click', () => {
        const type = card.getAttribute('data-request');
        if (type === 'accident') {
          state.editingClaimId = null;
          navigateTo('report', 1);
        } else openGeneric(type);
      });
    });
    DOM.btnContinueClaim1042.addEventListener('click', () => {
      state.editingClaimId = 'RS-1042';
      navigateTo('report', 2);
    });
    DOM.btnScheduleReview.addEventListener('click', () => openGeneric('plan'));
    DOM.btnGenericCancel.addEventListener('click', () => navigateTo('home'));
    DOM.btnGenericScan.addEventListener('click', () => DOM.genericScanInput.click());
    DOM.btnGenericSampleScan.addEventListener('click', () => runGenericAiScan(null));
    DOM.genericScanInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) runGenericAiScan(file);
      e.target.value = '';
    });

    DOM.btnAccidentScan.addEventListener('click', () => DOM.accidentScanInput.click());
    DOM.btnAccidentSampleScan.addEventListener('click', () => runAccidentAiScan(null));
    DOM.accidentScanInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) runAccidentAiScan(file);
      e.target.value = '';
    });

    DOM.genericForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const detail = DOM.genericDetail.value.trim();
      if (!detail) {
        DOM.genericDetail.focus();
        return;
      }
      const online = isEffectiveOnline();
      const id = 'RS-' + (1100 + Math.floor(Math.random() * 800));
      state.claims.unshift({
        id,
        type: GENERIC_COPY[state.genericType].title,
        date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
        location: '—',
        description: detail,
        status: online ? 'review' : 'waiting_to_sync',
        pipeline: 'submitted'
      });
      saveClaims();
      if (!online) {
        announce('Your request has been saved on this device and will be submitted when your connection returns.');
      } else {
        announce('Request submitted successfully.');
      }
      navigateTo('requests');
    });

    window.addEventListener('online', () => {
      state.isActuallyOnline = true;
      updateNetworkStatus();
    });
    window.addEventListener('offline', () => {
      state.isActuallyOnline = false;
      updateNetworkStatus();
    });
    DOM.btnSyncNow.addEventListener('click', syncPendingClaims);

    DOM.idMethodSa.addEventListener('click', () => setIdMethod('said'));
    DOM.idMethodPassport.addEventListener('click', () => setIdMethod('passport'));
    DOM.loginSaId.addEventListener('input', () => {
      DOM.loginSaId.value = digitsOnly(DOM.loginSaId.value).slice(0, 13);
    });
    DOM.loginPassport.addEventListener('input', () => {
      DOM.loginPassport.value = DOM.loginPassport.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
    });
    DOM.loginForm.addEventListener('submit', handleLogin);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        DOM.errorModal.classList.remove('active');
        DOM.voicePanel.hidden = true;
      }
    });

    DOM.btnStep1Cancel.addEventListener('click', () => navigateTo('home'));
    DOM.formStep1.addEventListener('submit', (e) => {
      e.preventDefault();
      if (validateStep1()) goToStep(2);
    });
    bindDocUploads();
    DOM.btnStep2Back.addEventListener('click', () => goToStep(1));
    DOM.btnStep2Next.addEventListener('click', () => goToStep(3));
    DOM.btnEditStep1.addEventListener('click', () => goToStep(1));
    DOM.btnEditStep2.addEventListener('click', () => goToStep(2));
    DOM.btnStep3Back.addEventListener('click', () => goToStep(2));
    DOM.btnSubmitClaim.addEventListener('click', submitAccidentReport);
    DOM.btnFinishReturnHome.addEventListener('click', () => navigateTo('home'));
    DOM.btnPrintSummary.addEventListener('click', () => window.print());
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
