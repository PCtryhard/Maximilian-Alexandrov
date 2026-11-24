# Maximilian-Alexandrov

My portfolio site. Live at **https://pctryhard.github.io/Maximilian-Alexandrov/**

`index.html` is the site, hand-written, no build step. `data.js` holds every number the
page draws, plus the coordinates for the rotating structure in the header. Between them
they cover the computational biology and conservation work I have done, what each project
actually produced, and what is still open.

The three PDFs are papers and proposals the site links to:

| file | what it is |
|---|---|
| `anti-crispr-zero-shot-paper.pdf` | Zero-shot detection of anti-CRISPR proteins under family-level holdout. Code and data: [acr-lofo-benchmark](https://github.com/PCtryhard/acr-lofo-benchmark) |
| `atrazine-biodegradation-proposal.pdf` | Pesticide biodegradation proposal, *Pseudomonas* metabolic pathways |
| `brains-affected-by-menopause-and-estrogen.pdf` | Neural signaling in menopause |

## Figures and data

`data.js` is one object, `window.D`. The thirteen figures are built from it in JS at load,
so correcting a number means editing `data.js` and the chart redraws itself. With JS off
the page falls back to the text, which carries the same numbers.

| key | what | where it came from |
|---|---|---|
| `spec` | 260 CA positions with pLDDT, the 6NT ligand, four side chains, two H-bonds | `protein-madness`, `data/rescored/cif/01_mm_d8ca9d.cif` |
| `branches` `noise` `depth` | gate rates, score-term noise ratios, 1-cycle vs 3-cycle | `protein-madness` RUNLOG §15 and §16 |
| `layers` `scaling` `perfam` `methods` | all 121 layers of 5 ESM-2 sizes, per-family results, method comparison | `acr-lofo-benchmark`, `results/metrics/` |
| `vol` `trp` | van der Waals volumes and the tryptophan comparison | `OrthCom`, `src/analyze_shape_gap.py` |
| `errbins` `mods` | surrogate error histogram, modification composition | `orthcom-immuno`, `results/step2/` |

The header model is the Boltz-2 prediction of design
`01_fastrelax_motif_af3.01.c04.mutate.d8ca9d`, the top-scoring design of run
`01-01-95cdcf`. To swap in another one, re-extract a CIF into `D.spec` and update the HUD
text and the caption in `index.html`.

## Deploying

Pushing to `main` publishes the site. Two things run on each push: the
`Deploy static content to Pages` workflow in `.github/workflows/static.yml`, and
GitHub's own `pages build and deployment`. Pages is currently configured to deploy from
the branch, so the second one is what actually serves the site and the workflow is
redundant. Both succeed, so this is untidy rather than broken. Removing the workflow, or
switching the Pages source to GitHub Actions, would leave one path instead of two.

## Related repositories

- [acr-lofo-benchmark](https://github.com/PCtryhard/acr-lofo-benchmark), the anti-CRISPR
  holdout benchmark
- [OrthCom](https://github.com/PCtryhard/OrthCom), designing a pocket for a non-canonical
  amino acid
- [orthcom-immuno](https://github.com/PCtryhard/orthcom-immuno), how wrong the
  canonical-surrogate shortcut is for MHC-I prediction

## Social card

`og-card.png` is the preview image for links to the site. It is a render of
design `01.c04.mutate.d8ca9d` — the same structure as the one in the header,
same pLDDT colouring, with the 6NT substrate in the pocket.

```
python tools/render_card.py og-card.png
```

That reads the coordinates out of `data.js`, so it stays in step with whatever
the header is showing. Needs Pillow; the typeface is fetched once and cached.
