/**
 * Royal Square Financial - Adviser Dashboard Mock Data Store
 * Professional Red & Black Executive Financial Services Portal
 *
 * NOTE: All figures and metrics contained herein are DEMO/MOCK data
 * for prototype presentation purposes. They do not represent real Royal Square
 * Financial figures and are not sourced from a live backend database.
 */

window.ADVISER_MOCK_DATA = {
  // Adviser Profile
  adviser: {
    name: "Sarah Adams",
    greetingName: "Sarah",
    role: "Financial Adviser",
    branch: "Cape Town",
    initials: "SA",
    email: "s.adams@royalsquare.co.za",
    fspNumber: "FSP 44821"
  },

  // 4 Main Dashboard Summary Metrics
  summaryMetrics: {
    activeCases: {
      label: "Active Cases",
      value: 127,
      change: "+12% from last month",
      trend: "up",
      icon: "briefcase",
      statusType: "primary"
    },
    humanIntervention: {
      label: "Requires Adviser Review",
      value: 8,
      alertNote: "Exceptions automation cannot resolve",
      trend: "alert",
      icon: "alert-circle",
      statusType: "danger"
    },
    waitingOnClient: {
      label: "Waiting on Client",
      value: 21,
      alertNote: "Pending client responses",
      trend: "warning",
      icon: "clock",
      statusType: "warning"
    },
    progressingNormally: {
      label: "Progressing Normally",
      value: 98,
      alertNote: "Meeting operational SLAs",
      trend: "success",
      icon: "check-circle",
      statusType: "success"
    }
  },

  // Cases Requiring Attention (Exceptions Automation Cannot Resolve)
  casesRequiringAttention: [
    {
      claimId: "RS-1042",
      client: "Thandi M.",
      clientEmail: "thandi.m@example.com",
      event: "Accident",
      stage: "Repair Authorisation",
      status: "Adviser Review Required",
      statusVariant: "danger",
      reason: "Insurer response overdue",
      lastUpdated: "2 hours ago",
      priority: "High"
    },
    {
      claimId: "RS-1038",
      client: "Liam K.",
      clientEmail: "liam.k@example.com",
      event: "Accident",
      stage: "Information Check",
      status: "Client Information Required",
      statusVariant: "warning",
      reason: "Police case number missing",
      lastUpdated: "4 hours ago",
      priority: "Medium"
    },
    {
      claimId: "RS-1029",
      client: "Nomsa P.",
      clientEmail: "nomsa.p@example.com",
      event: "Document Request",
      stage: "Document Verification",
      status: "Adviser Review Required",
      statusVariant: "danger",
      reason: "Document needs review",
      lastUpdated: "5 hours ago",
      priority: "High"
    }
  ],

  // Recent Activity Feed
  recentActivity: [
    {
      id: "act-1",
      claimId: "RS-1042",
      type: "escalation",
      title: "Insurer Follow-up Triggered",
      description: "Automated SLA reminder sent to Discovery Insure assessors for claim RS-1042.",
      timestamp: "18 mins ago",
      icon: "mail",
      isAutomated: true
    },
    {
      id: "act-2",
      claimId: "RS-1038",
      type: "reminder",
      title: "Document Request SMS Sent",
      description: "SMS alert dispatched to Liam K. requesting SAPS collision accident report.",
      timestamp: "1 hour ago",
      icon: "message-square",
      isAutomated: true
    },
    {
      id: "act-3",
      claimId: "RS-1029",
      type: "upload",
      title: "Proof of Identity Uploaded",
      description: "Nomsa P. submitted scanned Smart ID card. Verification flag raised for signature mismatch.",
      timestamp: "3 hours ago",
      icon: "file-text",
      isAutomated: false
    },
    {
      id: "act-4",
      claimId: "RS-1035",
      type: "approval",
      title: "Claim Automatically Progressed",
      description: "RS-1035 passed document verification and moved to insurer review automatically.",
      timestamp: "5 hours ago",
      icon: "check-circle",
      isAutomated: true
    }
  ],

  // Operational Analytics (Demo / Mock metrics)
  operationalAnalytics: {
    disclaimer: "Demo / mock metrics. Illustrative layout data not connected to backend.",
    automationRate: 94,
    avgProcessingTime: "18 minutes",
    claimsActivity: {
      days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      opened: [12, 16, 14, 18, 15, 6, 4],
      completed: [11, 15, 16, 17, 14, 5, 4]
    },
    caseDistribution: [
      { label: "Progressing Normally", count: 98, percentage: 77, type: "normal" },
      { label: "Waiting on Client", count: 21, percentage: 17, type: "waiting" },
      { label: "Adviser Review", count: 8, percentage: 6, type: "review" }
    ]
  },

  // Financial & Automation Impact (Demo Financial Metrics)
  financialImpact: {
    disclaimer: "Illustrative mock figures for dashboard layout only. These are not real Royal Square Financial results and are not sourced from the backend.",
    estimatedRevenue: 250000,
    estimatedOperationalCosts: 185000,
    estimatedProfit: 65000, // 250000 - 185000
    automationSavings: 45000,
    savingsPeriod: "saved this month (sample)",
    savingsExplanation: "Mock illustration of operational cost avoided through automated case handling.",
    sixMonths: {
      months: ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
      revenue: [210000, 218000, 225000, 232000, 241000, 250000],
      costs: [178000, 180000, 182000, 183000, 184000, 185000],
      profit: [32000, 38000, 43000, 49000, 57000, 65000]
    }
  },

  // Client Financial Goals (Visual goal tracking for clients)
  clientFinancialGoals: {
    client: "Thandi M.",
    clientId: "CLI-4892",
    summary: "Monitoring individual and shared client goals to provide proactive advice when automation flags exceptions.",
    goals: [
      {
        id: "goal-1",
        title: "Emergency Fund",
        current: 18000,
        target: 30000,
        progress: 60,
        monthlyContribution: 2000
      },
      {
        id: "goal-2",
        title: "Retirement Savings",
        current: 4500,
        target: 6000,
        progress: 75,
        monthlyContribution: 500
      }
    ],
    upcomingAction: {
      title: "Monthly contribution reminder",
      schedule: "Reminder scheduled automatically for 24 September 2026.",
      adviserActionRequired: false,
      statusNote: "No adviser action required."
    }
  },

  // Notifications Page Dataset
  notifications: [
    {
      id: "notif-1",
      claimId: "RS-1042",
      type: "attention",
      title: "Insurer Response SLA Breach",
      message: "RS-1042: Insurer response is overdue after automated follow-ups.",
      time: "20 minutes ago",
      unread: true,
      requiresAction: true,
      actionLink: "claim-details.html"
    },
    {
      id: "notif-2",
      claimId: "RS-1038",
      type: "attention",
      title: "Client Information Required",
      message: "RS-1038: Missing police case number.",
      time: "45 minutes ago",
      unread: true,
      requiresAction: true,
      actionLink: "cases.html"
    },
    {
      id: "notif-3",
      claimId: "RS-1029",
      type: "attention",
      title: "Document Review Required",
      message: "RS-1029: Document needs adviser review.",
      time: "1 hour ago",
      unread: true,
      requiresAction: true,
      actionLink: "cases.html"
    },
    {
      id: "notif-4",
      claimId: "RS-1035",
      type: "automated",
      title: "Automated Case Progression",
      message: "RS-1035: Automatically progressed to insurer review.",
      time: "2 hours ago",
      unread: false,
      requiresAction: false,
      actionLink: "cases.html"
    }
  ],

  // Cases Portfolio Dataset (Showing 7 of 127 active cases)
  casesSummaryMetrics: {
    allCases: {
      label: "All Cases",
      value: 127,
      change: "+12% total volume",
      trend: "up",
      icon: "folder"
    },
    adviserReview: {
      label: "Adviser Review",
      value: 8,
      change: "Requires human judgement",
      trend: "alert",
      icon: "alert-circle"
    },
    waitingOnClient: {
      label: "Waiting on Client",
      value: 21,
      change: "Awaiting documents/info",
      trend: "warning",
      icon: "clock"
    },
    progressingNormally: {
      label: "Progressing Normally",
      value: 98,
      change: "Automated workflow on SLA",
      trend: "success",
      icon: "check-circle"
    }
  },

  casesList: [
    {
      claimId: "RS-1042",
      client: "Thandi M.",
      clientEmail: "thandi.m@example.com",
      clientPhone: "+27 82 555 1042",
      event: "Accident",
      stage: "Repair Authorisation",
      status: "Adviser Review Required",
      category: "Adviser Review",
      statusVariant: "danger",
      reason: "Insurer response overdue",
      lastUpdated: "2 hours ago",
      priority: "High"
    },
    {
      claimId: "RS-1038",
      client: "Liam K.",
      clientEmail: "liam.k@example.com",
      clientPhone: "+27 83 444 1038",
      event: "Accident",
      stage: "Information Check",
      status: "Client Information Required",
      category: "Waiting on Client",
      statusVariant: "warning",
      reason: "Police case number missing",
      lastUpdated: "4 hours ago",
      priority: "Medium"
    },
    {
      claimId: "RS-1029",
      client: "Nomsa P.",
      clientEmail: "nomsa.p@example.com",
      clientPhone: "+27 71 333 1029",
      event: "Document Request",
      stage: "Document Verification",
      status: "Adviser Review Required",
      category: "Adviser Review",
      statusVariant: "danger",
      reason: "Document needs review",
      lastUpdated: "5 hours ago",
      priority: "High"
    },
    {
      claimId: "RS-1033",
      client: "Brandon V.",
      clientEmail: "brandon.v@example.com",
      clientPhone: "+27 82 999 1033",
      event: "Vehicle Damage",
      stage: "Police Report Submission",
      status: "Client Information Required",
      category: "Waiting on Client",
      statusVariant: "warning",
      reason: "Awaiting sworn affidavit",
      lastUpdated: "1 day ago",
      priority: "Medium"
    },
    {
      claimId: "RS-1024",
      client: "Lerato M.",
      clientEmail: "lerato.m@example.com",
      clientPhone: "+27 76 888 1024",
      event: "Windscreen Crack",
      stage: "Third-party Details",
      status: "Client Information Required",
      category: "Waiting on Client",
      statusVariant: "warning",
      reason: "Awaiting driver licence copy",
      lastUpdated: "1 day ago",
      priority: "Low"
    },
    {
      claimId: "RS-1045",
      client: "Johan B.",
      clientEmail: "johan.b@example.com",
      clientPhone: "+27 84 777 1045",
      event: "Bumper Collision",
      stage: "Quotation Assessment",
      status: "Progressing Normally",
      category: "Progressing Normally",
      statusVariant: "success",
      reason: "Assessor review scheduled on time",
      lastUpdated: "3 hours ago",
      priority: "Low"
    },
    {
      claimId: "RS-1035",
      client: "Anathi Z.",
      clientEmail: "anathi.z@example.com",
      clientPhone: "+27 83 222 1035",
      event: "Theft Attempt",
      stage: "Insurer Review",
      status: "Progressing Normally",
      category: "Progressing Normally",
      statusVariant: "success",
      reason: "Fast-track automation in progress",
      lastUpdated: "5 hours ago",
      priority: "Low"
    }
  ],

  // Full Details for RS-1042
  claimRS1042Details: {
    claimId: "RS-1042",
    claimNumber: "Claim #RS-1042",
    claimType: "Accident Claim",
    client: "Thandi M.",
    date: "18 September 2026",
    statusBanner: {
      status: "ADVISER REVIEW REQUIRED",
      reason: "Insurer response overdue after automated follow-ups."
    },
    aiSummary: {
      badge: "AI-generated summary",
      text: "Accident reported on 18 September. Required documents have been verified. The claim is currently waiting for insurer repair authorisation. Automated insurer follow-ups were sent, but no response was received within the SLA."
    },
    requirements: {
      completionText: "7 of 8 requirements complete",
      completedCount: 7,
      totalCount: 8,
      items: [
        { name: "Accident details", completed: true },
        { name: "Driver details", completed: true },
        { name: "Vehicle details", completed: true },
        { name: "Photos", completed: true },
        { name: "Police information", completed: true },
        { name: "Tow invoice", completed: true },
        { name: "Repair quote", completed: false }
      ]
    },
    documents: [
      { name: "Police receipt", status: "Verified", statusType: "success" },
      { name: "Tow invoice", status: "Verified", statusType: "success" },
      { name: "Vehicle photos", status: "Verified", statusType: "success" },
      { name: "Repair quote", status: "Missing", statusType: "danger" }
    ],
    timeline: [
      { timestamp: "18 Sep 10:15", title: "Client submitted accident" },
      { timestamp: "18 Sep 10:18", title: "Tow invoice uploaded" },
      { timestamp: "18 Sep 10:19", title: "AI extracted police information" },
      { timestamp: "18 Sep 10:25", title: "Documents validated" },
      { timestamp: "18 Sep 10:30", title: "Claim sent to insurer" },
      { timestamp: "21 Sep 10:30", title: "Automated insurer follow-up sent" },
      { timestamp: "21 Sep 10:30", title: "SLA breached", isAlert: true },
      { timestamp: "21 Sep 10:31", title: "Escalated to adviser", isEscalation: true }
    ],
    adviserActions: [
      { id: "actionContactInsurer", label: "Contact Insurer", variant: "primary" },
      { id: "actionRequestDoc", label: "Request Missing Document", variant: "secondary" },
      { id: "actionUpdateClient", label: "Update Client", variant: "secondary" }
    ]
  }
};
