import test from 'node:test';
import assert from 'node:assert/strict';

import { Slate } from '../src/index.js';

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
  assert.equal(emptyQuery.length, 0);
});
