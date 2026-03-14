import { CORE_MODULES, type SlateModule, type SlateModuleId } from '../types/modules';

export class ModuleRegistry {
  private modules = new Map<SlateModuleId, SlateModule>();

  constructor(initialModules: SlateModule[] = CORE_MODULES) {
    initialModules.forEach((module) => {
      this.modules.set(module.id, module);
    });
  }

  list(): SlateModule[] {
    return [...this.modules.values()];
  }

  get(moduleId: SlateModuleId): SlateModule | undefined {
    return this.modules.get(moduleId);
  }

  enable(moduleId: SlateModuleId): SlateModule {
    const module = this.modules.get(moduleId);
    if (!module) {
      throw new Error(`Unknown module: ${moduleId}`);
    }

    const updatedModule = { ...module, enabledByDefault: true };
    this.modules.set(moduleId, updatedModule);
    return updatedModule;
  }

  disable(moduleId: SlateModuleId): SlateModule {
    const module = this.modules.get(moduleId);
    if (!module) {
      throw new Error(`Unknown module: ${moduleId}`);
    }

    const updatedModule = { ...module, enabledByDefault: false };
    this.modules.set(moduleId, updatedModule);
    return updatedModule;
  }
}
