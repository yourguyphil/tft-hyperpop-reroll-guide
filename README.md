# Hyperpop Reroll Guide · TFT Set 19

An illustrated cheat sheet for forcing **Hyperpop Reroll** in Teamfight Tactics Set 19 *Prismatic Tour* (PBE, Nov 2026; live with patch 19.1 around Dec 2). Built with the `tft-force-guide` skill.

**The system:** a 1-cost reroll. Slow-roll above 50g at level 5 for **3★ Ziggs + 3★ Kobuko**. Items pick the carry:
- **No Tear → Ziggs:** Guinsoo's (Bow + Rod), Jeweled Gauntlet (Rod + Gloves), Hextech Gunblade (Sword + Rod)
- **Tear → Seraphine, then Teemo:** Void Staff (Bow + Tear), Spear of Shojin (Sword + Tear), Jeweled Gauntlet
- **Tank parts → Kobuko:** Gargoyle, Warmog's, Spirit Visage
- **Contested?** → Plan B, Renata Guards (2-cost reroll)

S tier on TFT Academy and tft.ninja: 83.9% top 4, 2.53 average placement (PBE Diamond+, Nov 19 2026).

## Files
- `index.html` + `assets/`: the site (host this)
- `hyperpop-reroll-guide.html`: single file with every image embedded (open this if images ever fail to load)
- `hyperpop-reroll-guide.pdf`: 3-page printout, built from `print/outline.md`
- `tools/`: `build-pdf.py`, `build-standalone.py`, `build-sw.py`, `build-icons.py`
- `deploy/`: Azure Blob static-website scripts

## Rebuild after edits
```bash
python tools/build-pdf.py          # PDF from print/outline.md
python tools/build-standalone.py   # single-file HTML
python tools/build-sw.py .         # offline cache list
```

## Host it / install on phone
`.\deploy\deploy-azure-blob.ps1 -Account <yourname>`, then on your phone: Share → Add to Home Screen (iPhone) or ⋮ → Install app (Android).

## Sources
[TFT Academy · Hyperpop Reroll](https://tftacademy.com/tierlist/comps/set-19-hyperpop-reroll) · [tft.ninja PBE comps](https://tft.ninja/comps?e=pbe) · [tft.ninja Set 19 units/traits/augments](https://tft.ninja/sets/19/units) · [Mobalytics · Hyperpop](https://mobalytics.gg/tft/set19/comps-guide/hyper-pop-3M8yhC5RAV9atbxt8QeSlEeGvgi) · [Mobalytics unlocks](https://mobalytics.gg/tft/set19/unlocks) · [tftflow unlocks](https://tftflow.com/how-to-unlock-every-champion-set19) · [TFT Academy · Renata Guards](https://tftacademy.com/tierlist/comps/set-19-renata-guards)

Set 19 is on PBE, so numbers can change. Not endorsed by Riot Games.
