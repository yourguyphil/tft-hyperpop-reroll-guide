// Tests the guide's pure logic (decision helper, Hype ETA, copy finder, board trait counts).
// Usage: node tools/test-logic.mjs      (runs the //#region testable block of index.html)
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const html = readFileSync(fileURLToPath(new URL("../index.html", import.meta.url)), "utf8");
const m = /\/\/#region testable[^\n]*\n([\s\S]*?)\/\/#endregion testable/.exec(html);
assert.ok(m, "testable region not found in index.html");
const api = new Function(m[1] + "\nreturn {PATCH,U,UK,I,decide,hypeEta,copyOdds,traitCount,parseStage,starTxt,BV,baseHype};")();
const { PATCH, UK, I, decide, hypeEta, copyOdds, traitCount, parseStage, starTxt, BV, baseHype } = api;

let n = 0;
const t = (name, fn) => { try { fn(); n++; } catch (e) { console.error("FAIL", name, "\n ", e.message); process.exitCode = 1; } };
const base = { stage: "3-2", level: 5, hp: 80, gold: 50, z: 3, k: 3, s: 0, contested: "no", mood: "even", cup: false };
const D = o => decide({ ...base, ...o });

/* ---- patch data sanity ---- */
t("odds rows sum to 100", () => Object.entries(PATCH.odds).forEach(([l, r]) => assert.equal(r.reduce((a, b) => a + b, 0), 100, "level " + l)));
t("hype per star", () => assert.deepEqual([1, 2, 3, 4].map(s => PATCH.hype[s]), [4, 6, 12, 40]));
t("base hype", () => assert.equal(baseHype([3, 3, 2, 2]), 36));

/* ---- input validation ---- */
t("bad stage", () => assert.ok(D({ stage: "9-9" }).err.length));
t("empty hp", () => assert.ok(D({ hp: "" }).err.some(e => /HP/.test(e))));
t("copies > 9", () => assert.ok(D({ z: 12 }).err.some(e => /Ziggs/.test(e))));
t("negative gold", () => assert.ok(D({ gold: -5 }).err.length));
t("decimal level", () => assert.ok(D({ level: 5.5 }).err.length));
t("0 hp = game over", () => assert.ok(D({ hp: 0 }).err[0].includes("over")));
t("unknown enums fall back", () => assert.ok(D({ contested: "x", mood: "y" }).main));
t("warns on lvl 8 in stage 2", () => assert.ok(D({ stage: "2-3", level: 8 }).warn.length));
t("warns kobuko without 2★ ziggs", () => assert.ok(D({ z: 1, k: 2 }).warn.length));
t("parseStage", () => { assert.deepEqual(parseStage(" 4-5 "), [4, 5]); assert.equal(parseStage("4"), null); });
t("starTxt", () => { assert.equal(starTxt(0), "none"); assert.equal(starTxt(4), "2★ +1"); assert.equal(starTxt(9), "3★"); });

/* ---- decisions ---- */
t("stage 2 default: no XP, save", () => { const r = D({ stage: "2-1", level: 4, gold: 10, z: 1, k: 0 }); assert.match(r.main.do, /No XP/); assert.ok(r.more.some(x => /Reroll 4/.test(x.do))); assert.ok(r.more.some(x => /2★ Ziggs/.test(x.do))); });
t("stage 2 after carousel: no Seraphine reminder", () => assert.ok(!D({ stage: "2-5", level: 4, gold: 20 }).more.some(x => /Reroll 4/.test(x.do))));
t("stage 2 bleeding: spend", () => assert.equal(D({ stage: "2-5", level: 4, hp: 55, gold: 20, mood: "bad" }).main.tone, "red"));
t("stage 3 healthy above 50: slow roll the excess", () => { const r = D({ gold: 64 }); assert.match(r.main.do, /spend 14g/); });
t("stage 3 at exactly 50: hold", () => assert.match(D({ gold: 50 }).main.do, /At 50g: hold/));
t("stage 3 healthy below 50: econ", () => assert.match(D({ gold: 38 }).main.do, /econ to 50g \(12g/));
t("stage 3 low HP: roll down", () => { const r = D({ hp: 35, gold: 40 }); assert.equal(r.main.tone, "red"); assert.match(r.main.do, /Roll down/); });
t("stage 3 close to 3★: roll", () => assert.match(D({ z: 8, gold: 40 }).main.do, /close \(8/));
t("3-1 roll-down when hurting", () => assert.match(D({ stage: "3-1", hp: 62, gold: 42 }).main.do, /3-1 roll-down/));
t("3-1 healthy: no roll-down", () => assert.doesNotMatch(D({ stage: "3-1", hp: 90, gold: 42, mood: "win" }).main.do, /roll-down/));
t("hard contested", () => assert.match(D({ contested: "two", gold: 40 }).main.do, /contested/i));
t("core done in stage 3: level 6", () => assert.match(D({ z: 9, k: 9 }).main.do, /level to 6/));
t("stage 4 missing core, few copies: stop chasing", () => assert.match(D({ stage: "4-2", level: 6, z: 4, k: 9 }).main.do, /Stop chasing/));
t("stage 4 missing core, 7 copies, healthy: keep rolling", () => assert.match(D({ stage: "4-2", level: 6, z: 7, k: 9, gold: 60 }).main.do, /Keep slow-rolling/));
t("stage 4 core done, lvl 6, rich: level up", () => assert.match(D({ stage: "4-3", level: 6, z: 9, k: 9, s: 3, gold: 60 }).main.do, /Level up/));
t("stage 4 seraphine close", () => assert.match(D({ stage: "4-1", level: 6, z: 9, k: 9, s: 7, gold: 55 }).main.do, /Seraphine at 7/));
t("stage 5 not lvl 8: level", () => assert.match(D({ stage: "5-1", level: 7, z: 9, k: 9, gold: 50 }).main.do, /Level to 8/));
t("stage 5 low: all-in", () => assert.match(D({ stage: "5-2", level: 8, hp: 20, gold: 30 }).main.do, /All-in/));
t("stage 5 strong rich: consider 9", () => assert.match(D({ stage: "5-3", level: 8, hp: 75, gold: 70, z: 9, k: 9, mood: "win" }).main.do, /Lvl 9/));
t("Top Cut raises danger line", () => { assert.notEqual(D({ hp: 48, gold: 40 }).main.tone, "red"); assert.equal(D({ hp: 48, gold: 40, cup: true }).main.tone, "red"); });
t("Top Cut adds note", () => assert.ok(D({ cup: true }).more.some(x => /Top Cut/.test(x.do))));
t("every decision has do + why", () => {
  for (const stage of ["1-3", "2-2", "3-1", "3-5", "4-1", "4-5", "5-2", "6-1"]) for (const hp of [15, 45, 80]) for (const gold of [0, 30, 60])
    for (const z of [0, 5, 8, 9]) for (const mood of ["win", "bad"]) for (const contested of ["no", "two"]) {
      const r = D({ stage, hp, gold, z, k: z, s: 3, mood, contested, level: +stage[0] + 2 });
      assert.ok(r.main && r.main.do && r.main.why && r.more.length <= 3, JSON.stringify({ stage, hp, gold, z }));
    }
});

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
