export const DELIVERY_PHASES = [
  {
    id: 1,
    name: 'Foundation',
    weeks: 'Weeks 1-2',
    deliverables: [
      'Project setup and folder structure',
      'Database initialization',
      'Core architecture (IPC, state management)',
      'Basic layout with three columns',
      'Universal search shell'
    ]
  },
  {
    id: 2,
    name: 'Browser Module',
    weeks: 'Weeks 3-4',
    deliverables: ['Tab management', 'WebView integration', 'Bookmarks & history', 'Ad blocking', 'Downloads']
  },
  {
    id: 3,
    name: 'Notes Module',
    weeks: 'Weeks 5-6',
    deliverables: [
      'TipTap/BlockNote editor',
      'Rich text blocks',
      'Folder organization',
      'Database tables (Notion-like)'
    ]
  },
  {
    id: 4,
    name: 'Communication',
    weeks: 'Weeks 7-8',
    deliverables: ['Email (IMAP/SMTP)', 'AI categorization', 'Multi-protocol chat (WhatsApp, Discord)', 'Unified messaging']
  },
  {
    id: 5,
    name: 'Media',
    weeks: 'Weeks 9-10',
    deliverables: ['YouTube integration', 'Video player with PiP', 'Spotify/music player', 'Podcast RSS feeds']
  },
  {
    id: 6,
    name: 'Code & Work',
    weeks: 'Weeks 11-14',
    deliverables: ['Monaco editor', 'Terminal integration', 'Git operations', 'Kanban boards', 'Calendar sync']
  },
  {
    id: 7,
    name: 'Advanced Features',
    weeks: 'Weeks 15-16',
    deliverables: ['Finance (Plaid)', 'Design tools', 'AI Assistant (Claude)', 'Extension system']
  },
  {
    id: 8,
    name: 'Polish & Optimization',
    weeks: 'Weeks 17-18',
    deliverables: ['Performance tuning', 'Memory leak fixes', 'UI polish', 'Accessibility']
  }
];

export const buildExecutionPlan = () =>
  DELIVERY_PHASES.map((phase) => ({
    ...phase,
    status: 'pending',
    completedDeliverables: []
  }));

export const completeDeliverable = (phaseState, deliverable) => {
  if (!phaseState.deliverables.includes(deliverable)) {
    throw new Error(`Unknown deliverable: ${deliverable}`);
  }

  if (phaseState.completedDeliverables.includes(deliverable)) {
    return phaseState;
  }

  const completedDeliverables = [...phaseState.completedDeliverables, deliverable];
  const isComplete = completedDeliverables.length === phaseState.deliverables.length;

  return {
    ...phaseState,
    completedDeliverables,
    status: isComplete ? 'completed' : 'in_progress'
  };
};

export const executionProgress = (executionPlan) => {
  const totalDeliverables = executionPlan.reduce((count, phase) => count + phase.deliverables.length, 0);
  const completedDeliverables = executionPlan.reduce((count, phase) => count + phase.completedDeliverables.length, 0);

  if (totalDeliverables === 0) {
    return 0;
  }

  return completedDeliverables / totalDeliverables;
};
