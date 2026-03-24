import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

import { BrowserModule } from './browser.js';

export class BrowserStore {
  /**
   * @param {string} path
   */
  constructor(path) {
    this.path = path;
  }

  async saveSnapshot(userId, browser) {
    const payload = await this.#loadAll();
    payload[userId] = browser.toJSON();

    await mkdir(dirname(this.path), { recursive: true });
    await writeFile(this.path, JSON.stringify(payload, null, 2), 'utf8');
  }

  async loadSnapshot(userId) {
    const payload = await this.#loadAll();
    const snapshot = payload[userId] ?? {};
    return BrowserModule.fromJSON(snapshot);
  }

  async #loadAll() {
    try {
      const raw = await readFile(this.path, 'utf8');
      return JSON.parse(raw);
    } catch (error) {
      if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
        return {};
      }
      throw error;
    }
  }
}
