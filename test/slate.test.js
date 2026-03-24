import { mkdtemp, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';

import {
  Slate,
  DELIVERY_PHASES,
  buildExecutionPlan,
  completeDeliverable,
  executionProgress,
  BrowserModule,
  SLATE_MAKER,
  BrowserStore
} from '../src/index.js';

test('adds and retrieves surfaces', () => {
  const slate = new Slate();

  slate.addSurface({
    id: 'home',
    title: 'Home Dashboard',
    kind: 'dashboard',
    tags: ['core', 'daily']
  });

  const home = slate.getSurface('home');
  assert.ok(home);
  assert.equal(home.title, 'Home Dashboard');
});

test('filters by tag', () => {
  const slate = new Slate();

  slate.addSurface({ id: 'a', title: 'A', tags: ['x'] });
  slate.addSurface({ id: 'b', title: 'B', tags: ['y'] });
  slate.addSurface({ id: 'c', title: 'C', tags: ['x', 'z'] });

  const xSurfaces = slate.byTag('x');
  assert.equal(xSurfaces.length, 2);
  assert.deepEqual(
    xSurfaces.map((surface) => surface.id),
    ['a', 'c']
  );
});

test('throws on duplicate ids', () => {
  const slate = new Slate();

  slate.addSurface({ id: 'dup', title: 'Original' });

  assert.throws(
    () => slate.addSurface({ id: 'dup', title: 'Collision' }),
    /already exists/
  );
});

test('supports search and kind filtering for app-style discovery', () => {
  const slate = new Slate();
  slate.addSurface({ id: '1', title: 'Sprint Board', kind: 'board', tags: ['work'] });
  slate.addSurface({ id: '2', title: 'Daily Notes', kind: 'note', tags: ['journal'] });

  assert.equal(slate.search('sprint').length, 1);
  assert.equal(slate.search('board').length, 1);
  assert.equal(slate.byKind('note').length, 1);
});

test('builds UI card payloads', () => {
  const slate = new Slate();
  slate.addSurface({ id: 'alpha', title: 'Alpha', kind: 'dashboard', tags: ['focus', 'team'] });

  const cards = slate.cards('alp');
  assert.equal(cards.length, 1);
  assert.deepEqual(cards[0], {
    id: 'alpha',
    title: 'Alpha',
    subtitle: 'DASHBOARD · 2 tags',
    kind: 'dashboard',
    badges: ['focus', 'team']
  });
});

test('search ranks exact and partial matches', () => {
  const slate = new Slate();

  slate.addSurface({ id: '1', title: 'Roadmap', kind: 'note', tags: ['planning'] });
  slate.addSurface({ id: '2', title: 'Roadmap Q4', kind: 'note', tags: ['planning', 'q4'] });
  slate.addSurface({ id: '3', title: 'Q4 Notes', kind: 'note', tags: ['q4'] });

  const matches = slate.search('roadmap');

  assert.deepEqual(
    matches.map((surface) => surface.id),
    ['1', '2']
  );
});

test('search supports filters and limits', () => {
  const slate = new Slate();

  slate.addSurface({ id: 'a', title: 'Home Dashboard', kind: 'dashboard', tags: ['core'] });
  slate.addSurface({ id: 'b', title: 'Finance Dashboard', kind: 'dashboard', tags: ['finance'] });
  slate.addSurface({ id: 'c', title: 'Finance Notes', kind: 'note', tags: ['finance'] });

  const financeDashboards = slate.search('finance', { kind: 'dashboard', tag: 'finance', limit: 1 });
  assert.equal(financeDashboards.length, 1);
  assert.equal(financeDashboards[0].id, 'b');

  const emptyQuery = slate.search('   ');
  assert.equal(emptyQuery.length, 3);

  const filteredEmptyQuery = slate.search('', { kind: 'dashboard' });
  assert.deepEqual(
    filteredEmptyQuery.map((surface) => surface.id),
    ['b', 'a']
  );
});

test('contains all requested delivery phases in order', () => {
  assert.equal(DELIVERY_PHASES.length, 8);
  assert.deepEqual(
    DELIVERY_PHASES.map((phase) => phase.name),
    [
      'Foundation',
      'Browser Module',
      'Notes Module',
      'Communication',
      'Media',
      'Code & Work',
      'Advanced Features',
      'Polish & Optimization'
    ]
  );

  const executionPlan = buildExecutionPlan();
  assert.equal(executionPlan[0].status, 'pending');
  assert.deepEqual(executionPlan[0].completedDeliverables, []);
});


test('tracks execution progress as deliverables are completed', () => {
  const plan = buildExecutionPlan();
  assert.equal(executionProgress(plan), 0);

  const foundation = completeDeliverable(plan[0], 'Database initialization');
  const updatedPlan = [foundation, ...plan.slice(1)];

  assert.equal(foundation.status, 'in_progress');
  assert.ok(executionProgress(updatedPlan) > 0);

  assert.throws(
    () => completeDeliverable(plan[0], 'Does not exist'),
    /Unknown deliverable/
  );
});


test('browser module manages tabs, bookmarks, history, ad blocking, and downloads', () => {
  const browser = new BrowserModule();

  const tab1 = browser.openTab({ id: 't1', url: 'https://example.com', title: 'Example' });
  const tab2 = browser.openTab({ id: 't2', url: 'https://news.example.com', title: 'News' });
  assert.equal(tab1.isActive, true);
  assert.equal(tab2.isActive, false);

  browser.activateTab('t2');
  assert.equal(browser.listTabs().find((tab) => tab.id === 't2')?.isActive, true);

  browser.pinTab('t2');
  assert.equal(browser.listTabs()[0].id, 't2');

  browser.addBookmark('https://example.com/docs', 'Docs');
  assert.equal(browser.listBookmarks().length, 1);

  browser.addAdBlockRule('ads.');
  assert.equal(browser.isBlocked('https://ads.example.com/banner.js'), true);

  const config = browser.webviewConfig('t2');
  assert.equal(config.src, 'https://news.example.com');

  browser.queueDownload({ id: 'd1', url: 'https://example.com/file.zip' });
  browser.updateDownload('d1', 'completed', '/tmp/file.zip');
  assert.equal(browser.downloads[0].status, 'completed');

  assert.equal(browser.closeTab('t2'), true);
  assert.equal(browser.listHistory().length >= 2, true);
});


test('serializes and restores browser module state', () => {
  const browser = new BrowserModule();
  browser.openTab({ id: 't1', url: 'https://example.com' });
  browser.navigateTab('t1', 'https://docs.example.com');
  browser.addBookmark('https://docs.example.com', 'Docs');
  browser.addAdBlockRule('ads.');
  browser.queueDownload({ id: 'd2', url: 'https://example.com/archive.zip' });

  const payload = browser.toJSON();
  assert.equal(payload.maker, SLATE_MAKER);

  const restored = BrowserModule.fromJSON(payload);
  assert.equal(restored.listTabs().length, 1);
  assert.equal(restored.listTabs()[0].url, 'https://docs.example.com');
  assert.equal(restored.listBookmarks()[0].title, 'Docs');
  assert.equal(restored.isBlocked('https://ads.example.com/x.js'), true);
});


test('removes ad-block rules', () => {
  const browser = new BrowserModule();
  browser.addAdBlockRule('ads.');
  assert.equal(browser.removeAdBlockRule('ads.'), true);
  assert.equal(browser.isBlocked('https://ads.example.com/a.js'), false);
});

test('browser store persists snapshots per user', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'slate-browser-'));
  const path = join(dir, 'browser.json');
  const store = new BrowserStore(path);

  const browser = new BrowserModule();
  browser.openTab({ id: 'a', url: 'https://example.com' });
  browser.addBookmark('https://docs.example.com', 'Docs');
  browser.addAdBlockRule('ads.');

  await store.saveSnapshot('user-1', browser);

  const restored = await store.loadSnapshot('user-1');
  assert.equal(restored.listTabs().length, 1);
  assert.equal(restored.listBookmarks()[0].title, 'Docs');
  assert.equal(restored.isBlocked('https://ads.example.com/banner.js'), true);

  const raw = JSON.parse(await readFile(path, 'utf8'));
  assert.ok(raw['user-1']);
});
