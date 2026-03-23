/**
 * @typedef {Object} SurfaceInput
 * @property {string} id
 * @property {string} title
 * @property {string} [kind]
 * @property {string[]} [tags]
 */

export class Surface {
  /**
   * @param {SurfaceInput} input
   */
  constructor(input) {
    if (!input?.id || !input?.title) {
      throw new Error('Surface requires both id and title.');
    }

    this.id = input.id;
    this.title = input.title;
    this.kind = input.kind ?? 'note';
    this.tags = [...new Set(input.tags ?? [])];
  }

  /**
   * @returns {SurfaceInput}
   */
  toJSON() {
    return {
      id: this.id,
      title: this.title,
      kind: this.kind,
      tags: [...this.tags]
    };
  }

  /**
   * Build a lightweight UI card payload suitable for list rendering.
   * @returns {{id: string, title: string, subtitle: string, kind: string, badges: string[]}}
   */
  toCard() {
    return {
      id: this.id,
      title: this.title,
      subtitle: `${this.kind.toUpperCase()} · ${this.tags.length} tag${this.tags.length === 1 ? '' : 's'}`,
      kind: this.kind,
      badges: [...this.tags]
    };
  }
}

export class Slate {
  constructor() {
    /** @type {Map<string, Surface>} */
    this.surfaces = new Map();
  }

  /**
   * @param {SurfaceInput} input
   */
  addSurface(input) {
    const surface = new Surface(input);

    if (this.surfaces.has(surface.id)) {
      throw new Error(`Surface with id "${surface.id}" already exists.`);
    }

    this.surfaces.set(surface.id, surface);
    return surface;
  }

  /**
   * @param {string} id
   */
  getSurface(id) {
    return this.surfaces.get(id) ?? null;
  }

  /**
   * @param {string} tag
   */
  byTag(tag) {
    return this.listSurfaces().filter((surface) => surface.tags.includes(tag));
  }

  /**
   * @param {string} kind
   */
  byKind(kind) {
    return this.listSurfaces().filter((surface) => surface.kind === kind);
  }

  listSurfaces() {
    return [...this.surfaces.values()];
  }

  cards(query = '') {
    return this.search(query).map((surface) => surface.toCard());
  }

  /**
   * @param {string} query
   * @param {{ tag?: string, kind?: string, limit?: number }} [options]
   */
  search(query = '', options = {}) {
    const normalizedQuery = query.trim().toLowerCase();

    const { tag, kind, limit } = options;
    const normalizedTag = tag?.toLowerCase();
    const normalizedKind = kind?.toLowerCase();

    const ranked = this.listSurfaces()
      .filter((surface) => {
        if (normalizedTag && !surface.tags.some((surfaceTag) => surfaceTag.toLowerCase() === normalizedTag)) {
          return false;
        }

        if (normalizedKind && surface.kind.toLowerCase() !== normalizedKind) {
          return false;
        }

        return true;
      })
      .map((surface) => ({
        surface,
        score: normalizedQuery ? this.scoreSurface(surface, normalizedQuery) : 1
      }))
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score || a.surface.title.localeCompare(b.surface.title))
      .map((entry) => entry.surface);

    if (limit === undefined) {
      return ranked;
    }

    return ranked.slice(0, Math.max(0, limit));
  }

  /**
   * @param {Surface} surface
   * @param {string} query
   */
  scoreSurface(surface, query) {
    const lowerTitle = surface.title.toLowerCase();
    const lowerKind = surface.kind.toLowerCase();
    const lowerTags = surface.tags.map((tag) => tag.toLowerCase());

    let score = 0;

    if (lowerTitle === query) {
      score += 10;
    } else if (lowerTitle.startsWith(query)) {
      score += 6;
    } else if (lowerTitle.includes(query)) {
      score += 4;
    }

    if (lowerKind === query) {
      score += 5;
    } else if (lowerKind.includes(query)) {
      score += 2;
    }

    for (const tag of lowerTags) {
      if (tag === query) {
        score += 4;
      } else if (tag.includes(query)) {
        score += 2;
      }
    }

    return score;
  }
}
