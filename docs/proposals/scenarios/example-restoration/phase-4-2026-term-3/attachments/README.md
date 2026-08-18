# Ianvs Example Restoration — deliverables bundle

Everything here was produced against `kubeedge/ianvs` at `main` and verified by
running it. Repository state at time of audit: 151 YAML configs under `examples/`,
29 example families, 46 benchmarking jobs, **235 findings across 19 families**.

## Contents

```
../proposal.md                              the proposal
scripts/validate_examples.py                the validator (landed at its real repo path)
.github/workflows/examples-validation.yaml  the CI gate (landed at its real repo path)
.ci/examples-baseline.json                  235-entry ratchet (landed at its real repo path)
patches/01-dataset-config-validation.patch  core: reject derived/unknown dataset keys
patches/02-rank-check-fields-logic.patch    core: fix inverted guards in Rank
fixes/requirement.txt                       issue #718, pip-verified
fixes/Semantic_Segmentation/               issue #719 configs, fully corrected
```

The validator, CI workflow and baseline are committed at their real target
locations (`scripts/`, `.github/workflows/`, `.ci/`) in this branch, since those
are meant to land as-is. The patches and corrected example configs stay here as
review-ready attachments rather than being applied directly, since applying them
is proposed as its own reviewed PR (see the proposal's Section 6 timeline and
`../proposal.md`'s "Suggested upstream sequence" below).

## Try it

```bash
git clone https://github.com/kubeedge/ianvs.git && cd ianvs
pip install pyyaml

python scripts/validate_examples.py                    # 235 findings
python scripts/validate_examples.py examples/pcb-aoi   # one family
python scripts/validate_examples.py --format json      # machine-readable

# repair what is unambiguous, then inspect the diff
python scripts/validate_examples.py --fix && git diff

# generate the ratchet, then confirm it suppresses the backlog
python scripts/validate_examples.py --write-baseline .ci/examples-baseline.json
python scripts/validate_examples.py --baseline .ci/examples-baseline.json; echo $?   # 0
```

Exit codes: `0` clean or fully baselined, `1` new finding, `2` validator could not run.

## Suggested upstream sequence

Land these as separate PRs, in this order. The gate goes first so every later fix
is permanent.

1. **`scripts/validate_examples.py` + `.ci/examples-baseline.json`** — tool only,
   no CI wiring. Easy to review on its own merits.
2. **`.github/workflows/examples-validation.yaml`** — activates the gate. Also
   retires Python 3.7/3.8 from the pylint matrix and adds 3.10–3.12.
3. **`patches/01`** — closes the 52-finding `train_url` class at the source.
   Flag for explicit maintainer sign-off: it converts silent-accept-then-crash
   into fail-fast, so configs that "worked" (they did not) now error at parse time.
4. **`patches/02`** — small, independent, low risk.
5. **`fixes/requirement.txt`** → closes #718.
6. **`fixes/Semantic_Segmentation/`** → closes #716, #717 and part of #719.
   Delete the corresponding lines from the baseline in the same PR.

## Notes on the open issues this proposal builds on

- **#716 + #717** together list five broken paths. There are **six** — the sixth
  is `testenv/testenv.yaml → acc.py`. Worth a comment on one of the issues so the
  fix is complete.
- **#719** — worth reconsidering the proposed fix. The four existing vendored
  `RFNet/` trees have all diverged (11 differing `.py` files between just two of
  them), so adding a fifth copy compounds the problem. Reframing the issue toward
  consolidation is a stronger contribution than satisfying it as written.

## Before submitting the application

- Fill the placeholder rows in `../proposal.md`'s applicant table (LinkedIn,
  timezone/availability).
- Confirm the 2026 Term 3 deadline on <https://mentorship.lfx.linuxfoundation.org>
  — Term 3 runs September–November and applications typically close in August.
- Consider posting a short comment on issue #230 with the finding counts. It is
  public evidence of the diagnostic work and mentors read the thread.
