// Space Slate Theme - palette helpers used for the store preview
import { readFile } from 'node:fs/promises';

const SURFACES = {
  canvas: '#F0EEFC',
  sidebar: '#E4E2EF',
  selection: '#CBCAD4',
};

export class Palette {
  constructor(seed = 'slate') {
    this.seed = seed;
    this.rings = ['inner', 'middle', 'outer'];
  }

  /** Blend two hex colors into one calm, low contrast tone. */
  mix(from, to, ratio = 0.5) {
    const parse = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
    const [a, b] = [parse(from), parse(to)];
    const blend = a.map((v, i) => Math.round(v + (b[i] - v) * ratio));
    return '#' + blend.map((v) => v.toString(16).padStart(2, '0')).join('');
  }

  async describe(file) {
    const source = await readFile(file, 'utf8');
    const surfaces = Object.entries(SURFACES)
      .filter(([, hex]) => hex.length === 7)
      .map(([name, hex]) => `${name} -> ${hex.toUpperCase()}`);
    return { file, bytes: source.length, surfaces };
  }
}

const palette = new Palette('space-slate');
console.log(await palette.describe('palette.json'));
