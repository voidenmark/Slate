/**
 * Browser module foundations for Phase 2.
 */

export const SLATE_MAKER = 'VOIDENMARK';

export class BrowserTab {
  /**
   * @param {{ id: string, url: string, title?: string, isPinned?: boolean, isActive?: boolean }} input
   */
  constructor(input) {
    if (!input?.id || !input?.url) {
      throw new Error('BrowserTab requires both id and url.');
    }

    this.id = input.id;
    this.url = input.url;
    this.title = input.title ?? input.url;
    this.isPinned = Boolean(input.isPinned);
    this.isActive = Boolean(input.isActive);
  }

  toJSON() {
    return {
      id: this.id,
      url: this.url,
      title: this.title,
      isPinned: this.isPinned,
      isActive: this.isActive
    };
  }
}

export class BrowserModule {
  constructor() {
    /** @type {Map<string, BrowserTab>} */
    this.tabs = new Map();
    /** @type {{ url: string, title: string, visitedAt: string }[]} */
    this.history = [];
    /** @type {Map<string, { url: string, title: string, createdAt: string }>} */
    this.bookmarks = new Map();
    /** @type {{ id: string, url: string, status: 'queued' | 'in_progress' | 'completed' | 'failed', savedPath: string | null }[]} */
    this.downloads = [];
    /** @type {Set<string>} */
    this.adBlockRules = new Set();
  }

  /** @param {{ id: string, url: string, title?: string, isPinned?: boolean }} input */
  openTab(input) {
    if (this.tabs.has(input.id)) {
      throw new Error(`Tab with id "${input.id}" already exists.`);
    }

    const nextTab = new BrowserTab({ ...input, isActive: false });
    if (this.tabs.size === 0) {
      nextTab.isActive = true;
    }

    this.tabs.set(nextTab.id, nextTab);
    this.recordVisit(nextTab.url, nextTab.title);
    return nextTab;
  }

  /** @param {string} tabId */
  closeTab(tabId) {
    const tab = this.tabs.get(tabId);
    if (!tab) {
      return false;
    }

    const wasActive = tab.isActive;
    this.tabs.delete(tabId);

    if (wasActive && this.tabs.size > 0) {
      const firstRemaining = this.listTabs()[0];
      firstRemaining.isActive = true;
    }

    return true;
  }

  /** @param {string} tabId */
  activateTab(tabId) {
    const target = this.tabs.get(tabId);
    if (!target) {
      throw new Error(`Unknown tab: ${tabId}`);
    }

    for (const tab of this.tabs.values()) {
      tab.isActive = false;
    }

    target.isActive = true;
    return target;
  }

  /** @param {string} tabId @param {string} url */
  navigateTab(tabId, url) {
    const tab = this.tabs.get(tabId);
    if (!tab) {
      throw new Error(`Unknown tab: ${tabId}`);
    }

    tab.url = url;
    tab.title = url;
    this.recordVisit(url, url);
    return tab;
  }

  listTabs() {
    return [...this.tabs.values()].sort((a, b) => Number(b.isPinned) - Number(a.isPinned));
  }

  /** @param {string} tabId @param {boolean} pinned */
  pinTab(tabId, pinned = true) {
    const tab = this.tabs.get(tabId);
    if (!tab) {
      throw new Error(`Unknown tab: ${tabId}`);
    }

    tab.isPinned = pinned;
    return tab;
  }

  /** @param {string} url @param {string} title */
  addBookmark(url, title = url) {
    const createdAt = new Date().toISOString();
    this.bookmarks.set(url, { url, title, createdAt });
    return this.bookmarks.get(url);
  }

  /** @param {string} url */
  removeBookmark(url) {
    return this.bookmarks.delete(url);
  }

  listBookmarks() {
    return [...this.bookmarks.values()].sort((a, b) => a.title.localeCompare(b.title));
  }

  /** @param {string} url @param {string} title */
  recordVisit(url, title = url) {
    this.history.unshift({ url, title, visitedAt: new Date().toISOString() });
    return this.history[0];
  }

  listHistory(limit = 20) {
    return this.history.slice(0, Math.max(0, limit));
  }

  /** @param {string} pattern */
  addAdBlockRule(pattern) {
    this.adBlockRules.add(pattern.toLowerCase());
    return this.adBlockRules.size;
  }

  /** @param {string} url */
  isBlocked(url) {
    const lowerUrl = url.toLowerCase();
    for (const pattern of this.adBlockRules) {
      if (lowerUrl.includes(pattern)) {
        return true;
      }
    }
    return false;
  }

  /** @param {{ id: string, url: string }} input */
  queueDownload(input) {
    if (this.downloads.some((download) => download.id === input.id)) {
      throw new Error(`Download with id "${input.id}" already exists.`);
    }

    const job = {
      id: input.id,
      url: input.url,
      status: 'queued',
      savedPath: null
    };

    this.downloads.push(job);
    return job;
  }

  /** @param {string} id @param {'queued'|'in_progress'|'completed'|'failed'} status @param {string | null} [savedPath] */
  updateDownload(id, status, savedPath = null) {
    const download = this.downloads.find((job) => job.id === id);
    if (!download) {
      throw new Error(`Unknown download: ${id}`);
    }

    download.status = status;
    download.savedPath = savedPath;
    return download;
  }

  /**
   * Lightweight webview descriptor for IPC integration.
   * @param {string} tabId
   */
  webviewConfig(tabId) {
    const tab = this.tabs.get(tabId);
    if (!tab) {
      throw new Error(`Unknown tab: ${tabId}`);
    }

    return {
      tabId: tab.id,
      src: tab.url,
      sandbox: true,
      adBlocked: this.isBlocked(tab.url)
    };
  }

  toJSON() {
    return {
      maker: SLATE_MAKER,
      tabs: this.listTabs().map((tab) => tab.toJSON()),
      bookmarks: this.listBookmarks(),
      history: [...this.history],
      downloads: [...this.downloads],
      adBlockRules: [...this.adBlockRules]
    };
  }

  /** @param {{ tabs?: Array<any>, bookmarks?: Array<any>, history?: Array<any>, downloads?: Array<any>, adBlockRules?: Array<string> }} payload */
  static fromJSON(payload = {}) {
    const browser = new BrowserModule();

    for (const tabInput of payload.tabs ?? []) {
      const tab = new BrowserTab(tabInput);
      browser.tabs.set(tab.id, tab);
    }

    for (const bookmark of payload.bookmarks ?? []) {
      browser.bookmarks.set(bookmark.url, bookmark);
    }

    browser.history = [...(payload.history ?? [])];
    browser.downloads = [...(payload.downloads ?? [])];
    browser.adBlockRules = new Set((payload.adBlockRules ?? []).map((rule) => rule.toLowerCase()));

    return browser;
  }
}
