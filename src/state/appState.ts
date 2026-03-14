import { CORE_MODULES, type SlateModuleId } from '../types/modules';

export interface AppState {
  activeModule: SlateModuleId;
  sidebarCollapsed: boolean;
  aiPanelVisible: boolean;
  enabledModules: SlateModuleId[];
}

export const DEFAULT_APP_STATE: AppState = {
  activeModule: 'browser',
  sidebarCollapsed: false,
  aiPanelVisible: true,
  enabledModules: CORE_MODULES.filter((module) => module.enabledByDefault).map((module) => module.id),
};

export const setActiveModule = (state: AppState, moduleId: SlateModuleId): AppState => {
  if (!state.enabledModules.includes(moduleId)) {
    throw new Error(`Module ${moduleId} is disabled.`);
  }

  return {
    ...state,
    activeModule: moduleId,
  };
};

export const toggleSidebar = (state: AppState): AppState => ({
  ...state,
  sidebarCollapsed: !state.sidebarCollapsed,
});

export const toggleAIPanel = (state: AppState): AppState => ({
  ...state,
  aiPanelVisible: !state.aiPanelVisible,
});
