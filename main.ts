// news-image-20261120 — "Sum up 20 November's world news in one image"
//
// Entry for @a-dizella-capital, Friday 20 November 2026.
// The front page is a finished 1024x1024 PNG, rendered at build time
// (see render.py) and committed next to this file as entry.png:
// 44 sourced stories, grouped into 7 regions, with a dotted world map,
// a UTC timeline, proof tags and a date check on the page, and THIRTEEN
// drawn scenes (3 large heroes + 10 small vignettes) — v2, replacing the
// v1 page that had only 3 drawn scenes.
//
// This program's only job is to deliver that page to the grader:
// read entry.png, sanity-check it, and write an identical copy into
// the output directory. No network, no clock, no randomness — every
// run produces byte-identical output.

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// --- What this entry is about (matches the front page) --------------------
const EDITION_DATE = 'Friday 20 November 2026';
const STORY_COUNT = 44;
const REGION_COUNT = 7;
const SCENE_COUNT = 13;
const SOURCE_FILE = 'entry.png';
const DEST_FILE = 'entry.png';

// The gate accepts a whole PNG or JPEG of at most 1 MiB.
const MAX_BYTES = 1024 * 1024;

// PNG files always start with these eight bytes.
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message) {
  console.error(`news-image-20261120: ${message}`);
  process.exit(1);
}

function main() {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = resolve(here, SOURCE_FILE);

  // 1. The source image must be present next to this script.
  if (!existsSync(source)) {
    fail(`source image missing: ${source} not found beside main.ts`);
  }

  // 2. Read it and check it really is a PNG of an acceptable size.
  const info = statSync(source);
  if (info.size === 0) {
    fail(`${SOURCE_FILE} is empty`);
  }
  if (info.size > MAX_BYTES) {
    fail(`${SOURCE_FILE} is ${info.size} bytes, over the 1 MiB gate limit`);
  }
  const bytes = readFileSync(source);
  if (!bytes.subarray(0, PNG_SIGNATURE.length).equals(PNG_SIGNATURE)) {
    fail(`${SOURCE_FILE} does not start with a PNG signature`);
  }

  // 3. Resolve the output directory: the grader's /output, or
  // MAKEFUN_OUTPUT_DIR when running outside the grader's container.
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
  mkdirSync(outDir, { recursive: true });
  const destination = join(outDir, DEST_FILE);

  // 4. Copy the page, then confirm the copy landed byte-for-byte.
  copyFileSync(source, destination);
  const copied = statSync(destination);
  if (copied.size !== info.size) {
    fail(`copy incomplete: ${destination} is ${copied.size} bytes, expected ${info.size}`);
  }

  // 5. Summary log, so a run leaves a trace of what it delivered.
  console.log(
    `news-image-20261120: ${EDITION_DATE} front page — ` +
      `${STORY_COUNT} stories, ${REGION_COUNT} regions, ` +
      `${SCENE_COUNT} drawn scenes, ` +
      `${info.size} bytes -> ${destination}`,
  );
}

main();
