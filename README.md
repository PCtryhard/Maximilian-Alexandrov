# Maximilian-Alexandrov

My portfolio site. Live at **https://pctryhard.github.io/Maximilian-Alexandrov/**

`index.html` is the whole site, hand-written, no build step. It covers the computational
biology and conservation work I have done, what each project actually produced, and what
is still open.

The three PDFs are papers and proposals the site links to:

| file | what it is |
|---|---|
| `anti-crispr-zero-shot-paper.pdf` | Zero-shot detection of anti-CRISPR proteins under family-level holdout. Code and data: [acr-lofo-benchmark](https://github.com/PCtryhard/acr-lofo-benchmark) |
| `atrazine-biodegradation-proposal.pdf` | Pesticide biodegradation proposal, *Pseudomonas* metabolic pathways |
| `brains-affected-by-menopause-and-estrogen.pdf` | Neural signaling in menopause |

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
