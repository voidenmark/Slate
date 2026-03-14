export type SlateModuleId =
  | 'browser'
  | 'watch'
  | 'listen'
  | 'chat'
  | 'mail'
  | 'notes'
  | 'code'
  | 'design'
  | 'finance'
  | 'work'
  | 'ai';

export interface SlateModule {
  id: SlateModuleId;
  name: string;
  icon: string;
  description: string;
  enabledByDefault: boolean;
}

export const CORE_MODULES: SlateModule[] = [
  {
    id: 'browser',
    name: 'Browse',
    icon: '🌐',
    description: 'Tab-based browsing with bookmarks, history, and privacy controls.',
    enabledByDefault: true,
  },
  {
    id: 'watch',
    name: 'Watch',
    icon: '📺',
    description: 'Unified video and streaming experiences.',
    enabledByDefault: true,
  },
  {
    id: 'listen',
    name: 'Listen',
    icon: '🎵',
    description: 'Music, podcasts, and audio tools in one place.',
    enabledByDefault: true,
  },
  {
    id: 'chat',
    name: 'Chat',
    icon: '💬',
    description: 'Unified conversations across messaging providers.',
    enabledByDefault: true,
  },
  {
    id: 'mail',
    name: 'Mail',
    icon: '📧',
    description: 'Unified inbox with smart categorization.',
    enabledByDefault: true,
  },
  {
    id: 'notes',
    name: 'Notes',
    icon: '📝',
    description: 'Block-based collaborative knowledge workspace.',
    enabledByDefault: true,
  },
  {
    id: 'code',
    name: 'Code',
    icon: '💻',
    description: 'Integrated code workspace with terminal and Git.',
    enabledByDefault: true,
  },
  {
    id: 'design',
    name: 'Design',
    icon: '🎨',
    description: 'Raster and vector editing with AI helpers.',
    enabledByDefault: true,
  },
  {
    id: 'finance',
    name: 'Finance',
    icon: '💰',
    description: 'Banking, budgeting, and portfolio monitoring.',
    enabledByDefault: true,
  },
  {
    id: 'work',
    name: 'Work',
    icon: '💼',
    description: 'Task boards, calendar, and time tracking.',
    enabledByDefault: true,
  },
  {
    id: 'ai',
    name: 'AI',
    icon: '🤖',
    description: 'Context-aware assistant across all modules.',
    enabledByDefault: true,
  },
];
