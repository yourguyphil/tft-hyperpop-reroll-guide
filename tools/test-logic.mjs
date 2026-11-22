// Tests the guide's pure logic (Hype ETA, copy finder, board trait counts).
// Usage: node tools/test-logic.mjs      (runs the //#region testable block of index.html)
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const html = readFileSync(fileURLToPath(new URL("../index.html", import.meta.url)), "utf8");
const m = /\/\/#region testable[^\n]*\n([\s\S]*?)\/\/#endregion testable/.exec(html);
assert.ok(m, "testable region not found in index.html");
const api = new Function(m[1] + "\nreturn {PATCH,U,UK,I,hypeEta,copyOdds,traitCount,parseStage,BV,baseHype};")();
const { PATCH, UK, I, hypeEta, copyOdds, traitCount, parseStage, BV, baseHype } = api;

let n = 0;
const t = (name, fn) => { try { fn(); n++; } catch (e) { console.error("FAIL", name, "\n ", e.message); process.exitCode = 1; } };
/* ---- patch data sanity ---- */
t("odds rows sum to 100", () => Object.entries(PATCH.odds).forEach(([l, r]) => assert.equal(r.reduce((a, b) => a + b, 0), 100, "level " + l)));
t("hype per star", () => assert.deepEqual([1, 2, 3, 4].map(s => PATCH.hype[s]), [4, 6, 12, 40]));
t("base hype", () => assert.equal(baseHype([3, 3, 2, 2]), 36));

/* ---- hype ETA ---- */
t("hype done", () => assert.ok(hypeEta(950, 10, "4-1").done));
t("hype rounds + stage skip carousel/PvE", () => { const r = hypeEta(800, 50, "4-2"); assert.equal(r.rounds, 2); assert.equal(r.at, "4-5"); });
t("hype no gain", () => assert.equal(hypeEta(100, 0, "3-1").rounds, undefined));
t("hype crosses stage", () => assert.equal(hypeEta(0, 300, "3-6").at, "4-3"));

/* ---- copy finder ---- */
t("copy finder basic", () => { const r = copyOdds({ cost: 1, level: 5, own: 6, seen: 0, taken: 0 }); assert.equal(r.need, 3); assert.equal(r.left, 24); assert.ok(Math.abs(r.perShop - 5 * 0.45 * 24 / 444) < 1e-9); });
t("copy finder impossible", () => assert.equal(copyOdds({ cost: 1, level: 5, own: 3, seen: 22 }).enough, false));
t("copy finder level clamps", () => assert.ok(isFinite(copyOdds({ cost: 2, level: 12, own: 3 }).gold)));

/* ---- boards: trait counts + validity ---- */
const tc = id => Object.fromEntries(traitCount(BV.find(b => b.id === id).cells.map(c => c[2])).map(x => [x.t, x]));
t("standard board traits", () => { const x = tc("std"); assert.equal(x.Hyperpop.on, 5); assert.equal(x.Choreographer.on, 2); assert.equal(x.Frontman.on, 2); assert.equal(x.Arcanist.on, 2); });
t("high cap = Choreographer 3", () => assert.equal(tc("cap").Choreographer.on, 3));
t("no Teemo = Hyperpop 4", () => assert.equal(tc("noteemo").Hyperpop.on, 4));
t("frontline variant = Hyperpop 4, Frontman 3 (2 active)", () => { const x = tc("front"); assert.equal(x.Hyperpop.on, 4); assert.equal(x.Frontman.c, 3); assert.equal(x.Frontman.on, 2); });
t("stabilize = Hyperpop 4", () => assert.equal(tc("stab").Hyperpop.on, 4));
t("boards: unit count = level, valid units/items/hexes, no overlaps", () => BV.forEach(b => {
  assert.equal(b.cells.length, b.lvl, b.id);
  const seen = new Set();
  b.cells.forEach(([r, c, u, st, its]) => { assert.ok(UK[u], u); assert.ok(r >= 0 && r < 4 && c >= 0 && c < 7); assert.ok(st >= 1 && st <= 3); its.forEach(i => assert.ok(I[i], i)); assert.ok(!seen.has(r + "-" + c), b.id + " overlap"); seen.add(r + "-" + c); });
}));
t("every unit trait has breakpoints or is a known early trait", () => Object.values(UK).forEach(u => u.t.forEach(tr => assert.ok(PATCH.traits[tr] || ["Heartsteel", "Beach Pop"].includes(tr), tr))));

console.log(process.exitCode ? "\nSome tests failed." : `All ${n} tests passed.`);
