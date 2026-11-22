# Hyperpop Reroll Guide · TFT Set 19

An illustrated cheat sheet for forcing **Hyperpop Reroll** in Teamfight Tactics Set 19 *Prismatic Tour* (PBE, Nov 2026; live with patch 19.1 around Dec 2). Built with the `tft-force-guide` skill.

**The system:** a 1-cost reroll. Slow-roll above 50g at level 5 for **3★ Seraphine / 3★ Ziggs + 3★ Kobuko**. Items pick the carry:
- **No Tear → Ziggs:** Guinsoo's (Bow + Rod), Jeweled Gauntlet (Rod + Gloves), Striker's Flail (Belt + Gloves)
- **Tear → Seraphine (preferred), then Teemo:** Void Staff (Bow + Tear), Spear of Shojin (Sword + Tear), Morellonomicon (Rod + Belt)
- **Tank parts → Kobuko:** Gargoyle, Warmog's, Spirit Visage
- **Level 8:** Garen is the flex unit (Nidalee at 9); Shyvana covers the slot before Teemo unlocks

## What's on the page
- **Quick reference:** rules, unlock path (earliest / aim / how / common mistake), Hype → Teemo tracker, stage plan + **checkpoints** at 3-1, 3-5, 4-1, 4-5, **When the plan breaks**, final-board variants with computed trait counts, Item Cheat Sheet, Quick Ref dock
- **Decision tools:** Item Advisor (main-carry toggle + **What am I missing?**), augments by stage (2-1 / 3-2 / 4-2) with take/avoid, positioning by matchup
- **Learn + review:** advanced mechanics (shop odds, pool, copy finder, holding units, Hype, Indie, Duplicators, when to stop chasing), Top Cut mindset, **Match log** (localStorage, JSON/CSV export + import)
- **Golden Rules** at the bottom: general item, rolling and reroll-tempo advice from Frodan (TFT Academy), dpei and Ripple (TFT Academy), each linked to where it applies in this comp

S tier on TFT Academy and tft.ninja: 83.9% top 4, 2.53 average placement (PBE Diamond+, Nov 19 2026).

## Files
- `index.html` + `assets/`: the site (host this)
- `hyperpop-reroll-guide.html`: single file with every image embedded (open this if images ever fail to load)
- `hyperpop-reroll-guide.pdf`: 4-page printout (page 4: checkpoints, recovery, Top Cut), built from `print/outline.md`
- `tools/`: `test-logic.mjs`, `build-pdf.py`, `build-standalone.py`, `build-sw.py`, `build-icons.py`
- `.nojekyll`: GitHub Pages serves the `main` branch root as-is (no workflow needed)

## Rebuild after edits
Patch-sensitive numbers (shop odds, pool sizes, Hype per star, unlock counts, trait breakpoints) live in one `PATCH` object near the top of the script in `index.html`. Change them there; every section reads from it.
```bash
node tools/test-logic.mjs          # decision helper, input checks, Hype ETA, copy finder, board trait counts
python tools/build-pdf.py          # PDF from print/outline.md
python tools/build-standalone.py   # single-file HTML
python tools/build-sw.py .         # offline cache list
```

## Host it / install on phone
Live at **https://yourguyphil.github.io/tft-hyperpop-reroll-guide/**: every push to `main` redeploys it. Open that on your phone, then: Share → Add to Home Screen (iPhone) or ⋮ → Install app (Android).

## Sources
Checked Nov 22 2026:
- **Mechanics + units + traits + augments:** tft.ninja Set 19 pages (Riot Dev Drop, Nov 15 2026)
- **Unlock numbers** (Lulu 10 casts, Tristana 5 kills, Teemo 900 Hype, Seraphine 4 rerolls): tftflow, matching tft.ninja's wording
- **Shop odds + pool sizes:** tftflow tables (labelled patch 19.1)
- **Final board + items** (Flail on Ziggs, Morello on Seraphine, Garen/Nidalee flex): TFT Academy + tft.ninja PBE comps
- **Reroll tempo rules (Golden Rules):** Ripple, [How to Play ANY Reroll Comp Like a Pro](https://www.youtube.com/watch?v=QNfN0eSp7tU) (TFT Academy). Made in Set 17; the rules are set-agnostic
- **Top Cut format:** Riot's Convergence Fest side-event page (lobbies of 8, one game per round, top 4 advance, 4 rounds then an 8-player final)

**My heuristics, not sourced:** the HP/gold thresholds in the checkpoints, augment take/avoid notes, positioning by matchup, Swain/Tristana items, the earliest/aim unlock timings.
**Not published yet:** Hype Level thresholds and rewards, the Hyperpop 3/4/5 multiplier values, the Vegas Open main-event format. The Hype tracker uses your real per-round gain instead of guessing multipliers.

[TFT Academy · Hyperpop Reroll](https://tftacademy.com/tierlist/comps/set-19-hyperpop-reroll) · [tft.ninja PBE comps](https://tft.ninja/comps?e=pbe) · [tft.ninja Set 19 units/traits/augments](https://tft.ninja/sets/19/units) · [Mobalytics · Hyperpop](https://mobalytics.gg/tft/set19/comps-guide/hyper-pop-3M8yhC5RAV9atbxt8QeSlEeGvgi) · [Mobalytics unlocks](https://mobalytics.gg/tft/set19/unlocks) · [tftflow unlocks](https://tftflow.com/how-to-unlock-every-champion-set19)

Set 19 is on PBE, so numbers can change. Not endorsed by Riot Games.
