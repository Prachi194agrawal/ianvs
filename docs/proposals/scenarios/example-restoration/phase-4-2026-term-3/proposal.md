# Comprehensive Example Restoration for KubeEdge Ianvs — Phase IV

**LFX Mentorship, 2026 Term 3 (September – November)**
**Upstream issue:** [kubeedge/ianvs#230](https://github.com/kubeedge/ianvs/issues/230)

> **Status:** LFX Mentorship application proposal, submitted for mentor review ahead of
> Term 3 mentee selection. This is not yet an accepted phase — see
> [`../README.md`](../README.md) for the phases that have been accepted and merged
> (Phase 1–3). This document follows the same structure so it can be folded in as
> `phase-4-2026-term-3/` if selected.

| | |
|---|---|
| **Applicant** | Prachi Agrawal |
| **GitHub** | [@Prachi194agrawal](https://github.com/Prachi194agrawal) |
| **Email** | agrawalprachi7718@gmail.com |
| **LinkedIn** | *(to be added before final submission)* |
| **Timezone / availability** | *(to be added before final submission)* |
| **Project** | CNCF – KubeEdge: Comprehensive Example Restoration for KubeEdge Ianvs, Phase IV |

---

## 1. Summary

Ianvs has 29 example families containing 46 runnable benchmarking jobs. I wrote a
static validator and ran it against every one of them. It reports **235 defects
across 19 of the 29 families** — broken file references, absolute paths pointing
into strangers' home directories, dataset fields that Ianvs itself overwrites, and
one `benchmarkingjob.yaml` that has never been valid YAML.

None of these require a GPU, a dataset, or a model checkpoint to detect. All of
them are invisible to the project's current CI, which lints `core/` and nothing
else.

This proposal does three things, in this order:

1. **Stop the bleeding.** Land a config validator and a CI gate so no new example
   can regress. This ships in Week 3, before any bulk fixing, so that every fix
   afterwards is permanent.
2. **Work the backlog down.** Repair the 235 findings family by family, with the
   validator's baseline file shrinking as the ratchet.
3. **Fix the causes, not just the symptoms.** Four of the defect classes exist
   because `core` accepts bad configuration silently and fails much later with a
   message that names the wrong thing. Patch `core` so the failure arrives at
   parse time and says what to change.

I am not proposing to survey the problem. The survey is done and attached; the
tooling is written and tested. This proposal is about executing on it.

---

## 2. Prior work on Ianvs

I have been contributing to Ianvs since February 2026.

**Merged / open pull requests**

| PR | Title | Status |
|---|---|---|
| [#339](https://github.com/kubeedge/ianvs/pull/339) | Fix KeyError crashes and division by zero in LLM inference benchmark | Open, 9 review comments, `size/S` |
| [#820](https://github.com/kubeedge/ianvs/pull/820) | Feature/simulation sandbox | Open, `kind/design` `kind/feature` `size/XXL` |

**Issues filed** — six, all reproduced from source before filing:

| Issue | Subject |
|---|---|
| [#819](https://github.com/kubeedge/ianvs/issues/819) | Simulation controller: 13 verified breakages in the 2022 implementation |
| [#719](https://github.com/kubeedge/ianvs/issues/719) | `Cloud_Robotics/Semantic_Segmentation` missing its vendored `RFNet/` tree |
| [#718](https://github.com/kubeedge/ianvs/issues/718) | `requirement.txt` invalid pip syntax aborts the entire install |
| [#717](https://github.com/kubeedge/ianvs/issues/717) | Three module URLs in `perception_reasoning.yaml` use the wrong directory |
| [#716](https://github.com/kubeedge/ianvs/issues/716) | `benchmarkingjob.yaml` references a non-existent directory |
| [#338](https://github.com/kubeedge/ianvs/issues/338) | KeyError crashes in the cloud-edge collaborative LLM inference benchmark |

Issues #716–#719 are the seed of this proposal. I filed them one at a time, then
realised I was finding the same four defect shapes over and over by hand and that
the sensible response was to write the thing that finds them all at once. That
tool is Section 5.1.

---

## 3. What the data actually shows

Method: parse all 151 YAML files under `examples/`, resolve every path-bearing key
against the repository, and cross-check each key against how `core` consumes it.

### 3.1 Findings by class

| Class | Count | Consequence |
|---|---:|---|
| `broken-reference` | 130 | A `url:` names a file that does not exist. Ianvs resolves URLs lazily at import time, so this surfaces minutes into a run. |
| `derived-dataset-field` | 52 | `train_url:` / `test_url:` set from YAML. See 3.3. |
| `absolute-path` | 44 | Paths hardcoded to a contributor's machine. Cannot resolve for anyone else. |
| `missing-section` | 7 | `rank:` absent or misindented under `test_object`. See 3.4. |
| `yaml-parse` | 1 | File is not valid YAML at all. See 3.5. |
| `untrimmed-path` | 1 | Trailing space creates a directory literally named `workspace-perception-reasoning `. |
| **Total** | **235** | across 19 of 29 example families |

### 3.2 Why there are 130 broken references

They are not 130 independent mistakes. Examples were reorganised at some point in
the project's history — `pedestrian_tracking/` moved under `MOT17/`,
`curb-detection/lifelong_learning_bench/` moved under `cityscapes-synthia/` — and
the configs were never updated to match. The *filenames* survived the move; only
the directory prefixes went stale.

That is why **120 of the 130 are mechanically repairable**: the target file still
exists somewhere under `examples/`, and can be located by basename and ranked by
directory proximity to the config doing the referencing. The remaining 10 point at
files that are genuinely gone and need a human decision.

The single worst example is `Cloud_Robotics/singletask_learning_bench/Semantic_Segmentation`,
which spells its own directory **four different ways** across three config files —
`cloud_robot`, `cloud-robotics`, `cloud_robotics`, `cloudrobotics` — with two
additional typos (`single_task_learing`, `sinlge_task_learning`). Not one of the
four resolves.

### 3.3 `train_url` is not a configuration field

`Dataset.process_dataset()` *derives* `train_url` and `test_url` from
`train_index` / `train_data` / `train_data_info`. But `Dataset._parse_config` is:

```python
for attr, value in config.items():
    if attr in self.__dict__:
        self.__dict__[attr] = value
```

`train_url` is in `__dict__` because `__init__` initialises it to `""`. So a
testenv that writes `train_url:` is accepted without complaint, passes
`_check_fields()` (which never inspects it), and then dies inside
`process_dataset()` with:

```
NotImplementedError: not one of train_index/train_data/train_data_info
```

— naming three fields the author did not write, and not naming the one they did.
The same loop silently discards misspelled keys, so `test_idnex:` is a no-op that
resurfaces as the identical message.

**52 dataset blocks are currently in this state.** This is the highest-volume
defect in the repository and it is a `core` bug expressed as 52 config bugs.

### 3.4 A missing `rank:` section fails at the very end

`BenchmarkingJob` initialises `self.rank = None` and `run()` finishes with
`self.rank.save(...)`. A job whose `rank:` block is missing — or, as in
Semantic_Segmentation, indented one level too deep so it sits inside
`test_object` — parses cleanly, runs every epoch of training, and then raises
`AttributeError` on the final statement. The full compute cost is paid before the
failure appears.

Relatedly, every guard in `Rank._check_fields` is written
`if not X and not isinstance(X, dict)` where the intent is `or`. With `and` the
guards are dead: `sort_by: []` passes and yields a silently empty leaderboard.
`save_mode` is a string but its guard tests `isinstance(..., list)` and its error
message advises list type.

### 3.5 One file has never parsed

`examples/cifar100/fci_ssl/fedavg/benchmarkingjob.yaml`, line 17:

```yaml
    algorithms:conda
```

A stray shell paste committed to the repository. This file cannot be loaded by any
YAML parser, so that example has never run since the line was introduced.

### 3.6 Why CI did not catch any of this

`.github/workflows/main.yaml` runs pylint against `core/` on Python 3.7, 3.8 and
3.9. All three are end-of-life (June 2023, October 2024, October 2025). Nothing in
the repository has ever read `examples/`. There is no gate that a broken example
could possibly fail, which is precisely why 235 findings accumulated without
anyone noticing.

---

## 4. Position relative to Phases I–III

Issue #230 has been worked in prior terms; see [`../README.md`](../README.md) for
the accepted Phase 1–3 proposals. This proposal is deliberately not a re-statement
of the issue text.

What earlier phases delivered was **per-example repair** and, in Phase 3, the first
CI classification framework verified against a single restored example
(`llm_simple_qa`). That work was real and valuable, and the 130 broken references
found here are evidence that per-example repair alone does not compose — fixing
example N does not protect examples 1 through N−1, and nothing prevents example
N+1 from arriving broken.

Phase IV's distinguishing bet is **ordering, applied repository-wide**: build the
gate first, then fix behind it, for all 29 families rather than one at a time. A
fix landed in Week 6 without a gate is a fix that can silently regress by Week 20.
A fix landed in Week 6 behind a ratcheting baseline is permanent. The issue's third
expected outcome — *"block PRs that break validated examples"* — is listed last but
is the one that makes the other two durable, so I propose to deliver it first.

---

## 5. Deliverables

Mapped to the three expected outcomes in issue #230.

### 5.1 Workstream A — CI pipeline and validation gate

*(Issue #230 expected outcome 3)*

**`scripts/validate_examples.py`** — written, tested, attached to this proposal.

- Resolves every path-bearing key statically. No dataset, no weights, no GPU;
  full-repository run completes in about one second.
- Six rule classes: `broken-reference`, `derived-dataset-field`, `absolute-path`,
  `missing-section`, `yaml-parse`, `untrimmed-path`.
- `--fix` repairs unambiguous broken references by basename resolution, ranked by
  directory proximity, and **declines to guess** when two candidates are equally
  close. Substitution is textual rather than a YAML round-trip because these files
  are roughly 70% explanatory comments that users read, and PyYAML discards them.
- `--baseline` suppresses the known backlog so CI fails only on *new* breakage.
  This is what makes the gate mergeable on day one instead of after a 235-fix
  mega-PR. Removing a line from the baseline is how a fix gets locked in.

Verified end-to-end: on `examples/Cloud_Robotics/` it went 6 findings → 0 with
`--fix`, comments intact. With the baseline in place, injecting a fresh typo into
`examples/pcb-aoi/` produced exactly 2 new findings, correct repair suggestions,
and a non-zero exit while the other 235 stayed suppressed.

**`.github/workflows/examples-validation.yaml`** — three jobs:

- *config validation* against the baseline, with a failure message that tells the
  contributor the exact command to run locally.
- *dependency manifests*: `pip install --dry-run` over every
  `examples/**/requirement*.txt`. This catches the #718 class in seconds. Note
  that pip validates an entire requirements file before installing anything, so
  one malformed line disables every package above it — which is why a single
  character broke that example's whole setup.
- *pylint* on Python **3.9–3.12**, retiring the two EOL versions while keeping 3.9
  for one release to protect existing users.

**Acceptance:** a PR that breaks an example config cannot merge green.

### 5.2 Workstream B — Diagnose and fix across examples

*(Issue #230 expected outcome 1)*

Sequenced by leverage, not by directory order.

**B1 — `core` hardening (removes whole defect classes).** Two patches, drafted:

- `core/testenvmanager/dataset/dataset.py`: reject derived fields at parse time
  with a message naming the field the author should have used (`train_url` with a
  `.txt` value → "use `train_index`"), and reject unknown keys instead of
  discarding them. Converts 52 late `NotImplementedError`s into 52 immediate,
  actionable errors.
- `core/storymanager/rank/rank.py`: correct the inverted `and`/`or` guards and the
  `save_mode` type check.

**B2 — bulk path repair.** `--fix` across the repository, reviewed family by
family, submitted as one PR per example family so reviewers can reason about each
in isolation. 120 references expected to resolve mechanically.

**B3 — the 10 genuinely-missing targets.** Each needs a judgement call: restore
from history, re-point at the correct file, or mark the example deprecated. I will
open one issue per case with the git history that explains how it went missing,
rather than deciding unilaterally.

**B4 — dependency manifests.** Fix every `requirement*.txt` that fails
`pip --dry-run`. Beyond the #718 syntax error, the same file names `pytorch` (not
the PyTorch distribution — the module `torch` ships as `torch`) and omits
`opencv-python` despite `cloud_edge_dispacher.py` importing `cv2` at module scope,
so the example fails even after a "successful" install.

**B5 — RFNet de-duplication.** Issue #719 reports that
`Cloud_Robotics/Semantic_Segmentation` lacks a vendored `RFNet/` tree while four
siblings have one. I no longer think vendoring a fifth copy is the right fix. I
diffed the existing four: **they have all diverged** — 11 differing `.py` files
between just two of them. Adding a fifth compounds a maintenance problem rather
than solving one. I will bring a consolidation design to the mentors rather than
assume the answer.

**B6 — license scan.** Per the issue's first expected outcome, audit vendored
third-party trees for license headers and compatibility, and reconcile with the
existing FOSSA workflow.

**Acceptance:** baseline shrinks from 235 toward zero; each PR deletes the lines
it fixes.

### 5.3 Workstream C — Documentation modernisation

*(Issue #230 expected outcome 2)*

- **Reproducible quickstart** for a designated reference example, verified from a
  clean container — meaning I run it from `git clone` on a fresh image, not from
  my configured machine, which is how the 44 absolute paths got committed in the
  first place.
- **Debugging playbook** keyed to the failure *messages* users actually see, since
  the messages frequently misdescribe the cause. Entry one is
  `NotImplementedError: not one of train_index/train_data/train_data_info` →
  "you probably wrote `train_url:`". Entry two is
  `AttributeError: 'NoneType' object has no attribute 'save'` → "your `rank:`
  section is missing or indented under `test_object`".
- **Example authoring guide**: the config contract, the difference between
  configurable and derived dataset fields, and how to run the validator before
  opening a PR.
- **KubeEdge blog post** on the restoration, as the issue requests.

**Acceptance:** a contributor with no prior Ianvs exposure runs the reference
example to completion following only the written guide.

---

## 6. Timeline

Twelve weeks, September – November 2026. Weekly written check-in; mid-point demo.

| Week | Focus | Exit condition |
|---|---|---|
| 1 | Onboarding. Confirm scope with mentors; agree the reference example; walk through the 235-finding audit together. | Scope signed off. |
| 2 | Land `validate_examples.py` + baseline as a standalone PR, no CI gate yet. Respond to review on rule semantics. | Validator merged. |
| 3 | Land the CI workflow. **Gate active.** | No new example config can regress. |
| 4 | B1: `dataset.py` and `rank.py` core patches, with unit tests. | 52-finding class cannot recur. |
| 5–6 | B2: bulk path repair, one PR per example family, ~5 families/week. | ≥120 references resolved. |
| 7 | B4 dependency manifests + the `algorithms:conda` parse failure + the 44 absolute paths. | `pip --dry-run` green repo-wide. |
| **7** | **Mid-point demo:** gate live, baseline down by ~80%. | Mentor review. |
| 8 | B3: the 10 missing targets — one issue each, resolved with mentors. | Decisions recorded. |
| 9 | B5: RFNet consolidation design; implement if mentors approve. | Design accepted or deferred with rationale. |
| 10 | C: quickstart + authoring guide, verified from a clean container. | Cold-start run succeeds. |
| 11 | C: debugging playbook; B6 license scan. | Playbook covers every failure seen in weeks 4–10. |
| 12 | KubeEdge blog post; handover notes; file follow-up issues for anything unfinished. | Backlog documented, not abandoned. |

**Buffer policy.** Weeks 5–6 are the most schedule-sensitive because PR review
throughput, not my typing speed, is the constraint. If review lags I will narrow
B2 to the highest-traffic families and move the remainder to documented follow-up
issues rather than let the gate or the documentation slip. The gate is the
deliverable that must not slip.

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| A 235-fix PR is unreviewable and stalls. | The baseline mechanism exists precisely so the gate lands independently of the fixes. One PR per example family thereafter. |
| `--fix` proposes a wrong path. | It refuses to guess when candidates are equally close, and every fix is human-reviewed. It is an assistant to review, not a substitute for it. |
| Some examples cannot be verified without datasets or GPUs I lack. | Validation is static by design. Where a runtime check is genuinely required I will say so explicitly rather than claim a verification I did not perform. |
| Core patches change behaviour for existing users. | Both patches convert silent-accept-then-crash into fail-fast. Anything they newly reject was already broken; the change is *when* and *how clearly* it fails. I will flag them for explicit maintainer sign-off. |
| Scope creep from the simulation work in #819/#820. | Out of scope here. Tracked separately. |

---

## 8. Why me

I have already done the diagnostic phase of this project without being asked to. I
filed six reproduced issues, opened two PRs, then built and tested the tooling
attached to this proposal — including finding, in the course of verifying my own
issue reports, a sixth broken path that #716 and #717 between them had missed, and
three `core` bugs that no filed issue covers.

I would rather bring a correction than a claim: my own issue #719 proposed
vendoring a fifth RFNet copy, and having diffed the existing four I now think that
is the wrong fix. I would rather revise a position in public than defend it.

The attached artefacts are runnable today, not sketches — see
[`attachments/README.md`](./attachments/README.md) for how to try them:

- `scripts/validate_examples.py` — validator, tested end-to-end (landed at its
  real target path in this branch)
- `.github/workflows/examples-validation.yaml` — CI gate (landed at its real
  target path in this branch)
- `.ci/examples-baseline.json` — 235-entry ratchet, verified to suppress known
  findings and catch injected ones (landed at its real target path)
- [`attachments/patches/01-dataset-config-validation.patch`](./attachments/patches/01-dataset-config-validation.patch)
- [`attachments/patches/02-rank-check-fields-logic.patch`](./attachments/patches/02-rank-check-fields-logic.patch)
- Corrected configs for both `Cloud_Robotics` examples, plus a pip-verified
  `requirement.txt`, under [`attachments/fixes/`](./attachments/fixes/)

---

## 9. References

- Project issue: [kubeedge/ianvs#230](https://github.com/kubeedge/ianvs/issues/230)
- Accepted prior phases: [`../README.md`](../README.md)
- Ianvs: <https://github.com/kubeedge/ianvs>
- KubeEdge SIG AI: <https://github.com/kubeedge/community/tree/master/sig-ai>
