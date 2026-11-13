// node web/static/url_engine.test.mjs: the JS resolver agrees with django.urls.resolve on every case in
// tests/fixtures/resolve_cases.json (made by scripts/make_resolve_fixture.py) using the exported pattern tree.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { appendSlash, resolve } from './url_engine.js';

const here = new URL('.', import.meta.url);
const cases = JSON.parse(readFileSync(new URL('../../tests/fixtures/resolve_cases.json', here)));
const patterns = JSON.parse(readFileSync(new URL('../../tests/fixtures/url_patterns.json', here)));
let n = 0;
for (const c of cases) {
  const r = resolve(patterns, c.path);
  assert.equal(r.match, c.match, `match ${JSON.stringify(c.path)}`);
  if (c.match) {
    assert.equal(r.view, c.view, c.path);
    assert.equal(r.name, c.name, c.path);
    assert.deepEqual(r.kwargs, c.kwargs, c.path);
    assert.equal(r.namespace, c.namespace, c.path);
  } else {
    assert.equal(appendSlash(patterns, c.path), c.append_slash, `append_slash ${JSON.stringify(c.path)}`);
  }
  n++;
}
assert.ok(n >= 20);
console.log(`url_engine: ${n} cases agree with Django`);
