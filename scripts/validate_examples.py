# Copyright 2026 The KubeEdge Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Static validator for Ianvs example configurations.

Ianvs resolves every ``url`` in a benchmarking config *lazily*, at the moment the
module is imported. A config that points at a path which no longer exists
therefore fails many minutes into a run -- after the dataset has been staged and
the model loaded -- or, worse, fails on a contributor's machine only.

This validator resolves the same references *statically*, in under a second and
with no dataset, no GPU and no model weights. It is the check that CI runs on
every pull request.

Usage
-----
    python scripts/validate_examples.py                    # validate everything
    python scripts/validate_examples.py examples/pcb-aoi   # validate one example
    python scripts/validate_examples.py --fix              # repair what is safe
    python scripts/validate_examples.py --baseline .ci/examples-baseline.json
    python scripts/validate_examples.py --write-baseline .ci/examples-baseline.json

Exit codes
----------
    0   no findings (or every finding is already in the baseline)
    1   at least one new finding
    2   the validator itself could not run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - the CI job installs pyyaml
    sys.stderr.write("validate_examples: PyYAML is required (pip install pyyaml)\n")
    sys.exit(2)


# --------------------------------------------------------------------------- #
# Schema knowledge
# --------------------------------------------------------------------------- #

#: Keys whose value is a path to a file that must exist inside the repository.
#: These are resolved by ``core`` relative to the working directory that ``ianvs``
#: is invoked from, which the docs define as the project root.
REPO_PATH_KEYS = frozenset({"url", "testenv"})

#: Keys that name an output directory. Never required to exist -- Ianvs creates
#: them -- but stray whitespace still produces a literal directory named
#: ``"workspace-foo "`` that no shell completion will ever match.
OUTPUT_PATH_KEYS = frozenset({"workspace"})

#: Keys whose value points at data or weights the user supplies out of band.
#: We never require these to exist, but we do reject absolute paths, because an
#: absolute path is by definition unreproducible on anybody else's machine.
USER_SUPPLIED_PATH_KEYS = frozenset(
    {
        "train_index",
        "test_index",
        "train_data",
        "test_data",
        "train_data_info",
        "test_data_info",
        "label",
        "initial_model_url",
        "model_url",
    }
)

#: ``Dataset`` assigns these itself in ``process_dataset()`` from ``train_index`` /
#: ``train_data`` / ``train_data_info``. ``Dataset._parse_config`` writes any key it
#: finds in ``__dict__``, so setting them from YAML is silently accepted at parse
#: time and then raises ``NotImplementedError`` from ``process_dataset()`` -- long
#: after the run has started, with a message that names none of the three fields
#: the author actually meant.
DERIVED_DATASET_KEYS = frozenset({"train_url", "test_url"})

#: Suggested replacement, keyed by the file extension of the value.
DERIVED_KEY_REPLACEMENT = {
    "train_url": {".txt": "train_index", ".json": "train_data", ".jsonl": "train_data"},
    "test_url": {".txt": "test_index", ".json": "test_data", ".jsonl": "test_data"},
}

#: Sections ``BenchmarkingJob`` and ``Rank`` require. A benchmarkingjob missing
#: ``rank`` parses fine, runs the full paradigm, and then dies in
#: ``BenchmarkingJob.run()`` on ``self.rank.save(...)`` with an AttributeError --
#: after every epoch of training has already been paid for.
REQUIRED_JOB_KEYS = ("name", "workspace", "testenv", "test_object", "rank")
REQUIRED_RANK_KEYS = ("sort_by", "visualization", "selected_dataitem", "save_mode")
REQUIRED_DATAITEM_KEYS = ("paradigms", "modules", "metrics")

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    """A single problem found in a single config file."""

    rule: str
    severity: str
    path: str          # repo-relative path of the offending config file
    location: str      # dotted key path inside that file, e.g. algorithm.modules[0].url
    detail: str
    suggestion: Optional[str] = None

    def key(self) -> str:
        """Stable identity used for baseline matching."""
        return f"{self.path}::{self.location}::{self.rule}"

    def render(self) -> str:
        head = f"{self.path}:{self.location}: {self.severity}: [{self.rule}] {self.detail}"
        if self.suggestion:
            return f"{head}\n    suggestion: {self.suggestion}"
        return head


@dataclass
class Report:
    findings: List[Finding] = field(default_factory=list)
    files_checked: int = 0
    fixes_applied: List[str] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    @property
    def errors(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == SEVERITY_ERROR]


# --------------------------------------------------------------------------- #
# YAML traversal
# --------------------------------------------------------------------------- #

def iter_scalars(node: Any, prefix: str = "") -> Iterator[Tuple[str, str, Any]]:
    """Yield ``(location, key, value)`` for every scalar leaf in a parsed document."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from iter_scalars(value, child)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from iter_scalars(value, f"{prefix}[{index}]")
    else:
        leaf = prefix.rsplit(".", 1)[-1].split("[", 1)[0]
        yield prefix, leaf, node


def find_config_files(root: str, targets: Sequence[str]) -> List[str]:
    """Collect every YAML file under the requested targets."""
    roots = [os.path.join(root, t) for t in targets] if targets else [os.path.join(root, "examples")]
    found: List[str] = []
    for base in roots:
        if os.path.isfile(base):
            found.append(base)
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "workspace"}]
            for name in filenames:
                if name.endswith((".yaml", ".yml")):
                    found.append(os.path.join(dirpath, name))
    return sorted(set(found))


# --------------------------------------------------------------------------- #
# Repair suggestions
# --------------------------------------------------------------------------- #

def build_basename_index(root: str) -> Dict[str, List[str]]:
    """Map every filename under ``examples/`` to the repo-relative paths holding it.

    A broken reference is nearly always a stale *directory prefix* left behind by an
    example being renamed or moved; the filename itself survives. Indexing by
    basename lets us propose the new home of a file with high confidence.
    """
    index: Dict[str, List[str]] = defaultdict(list)
    examples_dir = os.path.join(root, "examples")
    for dirpath, dirnames, filenames in os.walk(examples_dir):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "workspace"}]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            index[name].append("./" + rel.replace(os.sep, "/"))
    return index


def suggest_path(
    broken: str,
    source_file: str,
    root: str,
    index: Dict[str, List[str]],
) -> Optional[str]:
    """Propose a replacement for a broken reference, or ``None`` if it is ambiguous.

    Candidates are ranked by how much of the directory prefix they share with the
    config file doing the referencing -- an example almost always points at its own
    subtree, so the nearest candidate is the right one.
    """
    candidates = index.get(os.path.basename(broken), [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    source_parts = os.path.dirname(os.path.relpath(source_file, root)).split(os.sep)

    def shared_prefix(candidate: str) -> int:
        parts = os.path.dirname(candidate[2:]).split("/")
        count = 0
        for left, right in zip(source_parts, parts):
            if left != right:
                break
            count += 1
        return count

    ranked = sorted(candidates, key=shared_prefix, reverse=True)
    best, runner_up = shared_prefix(ranked[0]), shared_prefix(ranked[1])
    # Refuse to guess when two candidates are equally close to the referencing file.
    return ranked[0] if best > runner_up else None


def suggest_dataset_key(key: str, value: str) -> str:
    ext = os.path.splitext(value)[1].lower()
    return DERIVED_KEY_REPLACEMENT[key].get(ext, DERIVED_KEY_REPLACEMENT[key][".txt"])


# --------------------------------------------------------------------------- #
# Rules
# --------------------------------------------------------------------------- #

def check_job_structure(document: Any, rel_path: str, report: Report) -> None:
    """Verify a benchmarkingjob declares every section core will later dereference."""
    if not isinstance(document, dict) or "benchmarkingjob" not in document:
        return
    job = document.get("benchmarkingjob")
    if not isinstance(job, dict):
        return

    for required in REQUIRED_JOB_KEYS:
        if required in job:
            continue
        detail = f"benchmarkingjob has no '{required}' section"
        suggestion = None
        if required == "rank":
            # Almost always an indentation slip: the keys exist but sit under
            # test_object, where nothing reads them.
            misplaced = [k for k in REQUIRED_RANK_KEYS if isinstance(job.get("test_object"), dict)
                         and k in job["test_object"]]
            if misplaced:
                detail += f" but {', '.join(misplaced)} appear under test_object"
                suggestion = (
                    "move these keys out of test_object into a sibling 'rank:' section"
                )
            else:
                suggestion = "add a 'rank:' section with sort_by, visualization, " \
                             "selected_dataitem and save_mode"
        report.add(
            Finding(
                rule="missing-section",
                severity=SEVERITY_ERROR,
                path=rel_path,
                location=f"benchmarkingjob.{required}",
                detail=detail,
                suggestion=suggestion,
            )
        )

    rank = job.get("rank")
    if isinstance(rank, dict):
        for required in REQUIRED_RANK_KEYS:
            if required not in rank:
                report.add(
                    Finding(
                        rule="missing-section",
                        severity=SEVERITY_ERROR,
                        path=rel_path,
                        location=f"benchmarkingjob.rank.{required}",
                        detail=f"rank has no '{required}'; Rank._check_fields() rejects this",
                    )
                )
        dataitem = rank.get("selected_dataitem")
        if isinstance(dataitem, dict):
            for required in REQUIRED_DATAITEM_KEYS:
                if required not in dataitem:
                    report.add(
                        Finding(
                            rule="missing-section",
                            severity=SEVERITY_ERROR,
                            path=rel_path,
                            location=f"benchmarkingjob.rank.selected_dataitem.{required}",
                            detail=f"selected_dataitem has no '{required}'",
                        )
                    )


def check_file(
    abs_path: str,
    root: str,
    index: Dict[str, List[str]],
    report: Report,
) -> Dict[str, str]:
    """Validate one config file. Returns ``{location: replacement}`` for --fix."""
    rel_path = os.path.relpath(abs_path, root).replace(os.sep, "/")
    report.files_checked += 1
    repairs: Dict[str, str] = {}

    try:
        with open(abs_path, encoding="utf-8") as handle:
            raw = handle.read()
        document = yaml.safe_load(raw)
    except yaml.YAMLError as err:
        first_line = str(err).strip().splitlines()[0]
        report.add(
            Finding(
                rule="yaml-parse",
                severity=SEVERITY_ERROR,
                path=rel_path,
                location="<file>",
                detail=f"file is not valid YAML and can never be loaded: {first_line}",
            )
        )
        return repairs
    except OSError as err:
        report.add(
            Finding(
                rule="unreadable",
                severity=SEVERITY_ERROR,
                path=rel_path,
                location="<file>",
                detail=str(err),
            )
        )
        return repairs

    if not isinstance(document, (dict, list)):
        return repairs

    check_job_structure(document, rel_path, report)

    for location, key, value in iter_scalars(document):
        if not isinstance(value, str) or not value.strip():
            continue

        # --- derived dataset fields ------------------------------------------------
        if key in DERIVED_DATASET_KEYS:
            replacement = suggest_dataset_key(key, value)
            report.add(
                Finding(
                    rule="derived-dataset-field",
                    severity=SEVERITY_ERROR,
                    path=rel_path,
                    location=location,
                    detail=(
                        f"'{key}' is assigned by Dataset.process_dataset(), not read from "
                        f"config; setting it here is accepted silently and then raises "
                        f"NotImplementedError at run time"
                    ),
                    suggestion=f"rename '{key}' to '{replacement}'",
                )
            )
            continue

        if key in OUTPUT_PATH_KEYS:
            if value != value.strip():
                report.add(
                    Finding(
                        rule="untrimmed-path",
                        severity=SEVERITY_WARNING,
                        path=rel_path,
                        location=location,
                        detail=(
                            f"workspace {value!r} has leading or trailing whitespace and "
                            f"will create a directory whose name contains a space"
                        ),
                        suggestion=f"use {value.strip()!r}",
                    )
                )
            continue

        if key not in REPO_PATH_KEYS and key not in USER_SUPPLIED_PATH_KEYS:
            continue

        # --- absolute paths --------------------------------------------------------
        if os.path.isabs(value) or (len(value) > 1 and value[1] == ":"):
            report.add(
                Finding(
                    rule="absolute-path",
                    severity=SEVERITY_ERROR,
                    path=rel_path,
                    location=location,
                    detail=f"absolute path '{value}' cannot resolve on any other machine",
                    suggestion=(
                        "use a path relative to the project root, e.g. ./examples/... "
                        "or ./dataset/..."
                    ),
                )
            )
            continue

        # --- stray whitespace ------------------------------------------------------
        if value != value.strip():
            report.add(
                Finding(
                    rule="untrimmed-path",
                    severity=SEVERITY_WARNING,
                    path=rel_path,
                    location=location,
                    detail=f"path {value!r} has leading or trailing whitespace",
                    suggestion=f"use {value.strip()!r}",
                )
            )

        if key in USER_SUPPLIED_PATH_KEYS:
            # Datasets and weights are downloaded by the user; existence is not our call.
            continue

        # --- broken in-repo references --------------------------------------------
        candidate = value.strip()
        resolved = os.path.normpath(os.path.join(root, candidate.lstrip("./")))
        if os.path.exists(resolved):
            continue

        replacement = suggest_path(candidate, abs_path, root, index)
        report.add(
            Finding(
                rule="broken-reference",
                severity=SEVERITY_ERROR,
                path=rel_path,
                location=location,
                detail=f"'{candidate}' does not exist in the repository",
                suggestion=(
                    f"did you mean '{replacement}'?" if replacement
                    else "no file of that name exists under examples/ -- the target is missing"
                ),
            )
        )
        if replacement:
            repairs[candidate] = replacement

    return repairs


def apply_repairs(abs_path: str, repairs: Dict[str, str], report: Report, root: str) -> None:
    """Rewrite broken references in place.

    Deliberately a textual substitution rather than a YAML round-trip: PyYAML does
    not preserve comments, and these files are ~70% comments that users read.
    """
    if not repairs:
        return
    with open(abs_path, encoding="utf-8") as handle:
        text = handle.read()
    original = text
    for broken, fixed in repairs.items():
        text = text.replace(broken, fixed)
    if text != original:
        with open(abs_path, "w", encoding="utf-8") as handle:
            handle.write(text)
        rel = os.path.relpath(abs_path, root).replace(os.sep, "/")
        for broken, fixed in repairs.items():
            report.fixes_applied.append(f"{rel}: {broken} -> {fixed}")


# --------------------------------------------------------------------------- #
# Baseline
# --------------------------------------------------------------------------- #

def load_baseline(path: str) -> set:
    if not path or not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as handle:
        return set(json.load(handle).get("accepted", []))


def write_baseline(path: str, findings: Sequence[Finding]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload = {
        "_comment": (
            "Pre-existing example-config findings, accepted so CI can gate new "
            "breakage while the backlog is worked down. Entries may be removed as "
            "they are fixed; adding an entry requires reviewer sign-off."
        ),
        "accepted": sorted({f.key() for f in findings}),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Ianvs example configurations without running them."
    )
    parser.add_argument("targets", nargs="*", help="paths to check (default: examples/)")
    parser.add_argument("--root", default=None, help="project root (default: parent of this script)")
    parser.add_argument("--fix", action="store_true", help="rewrite unambiguous broken references")
    parser.add_argument("--baseline", default=None, help="JSON file of accepted findings")
    parser.add_argument("--write-baseline", default=None, help="record current findings and exit 0")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args(argv)

    root = args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isdir(os.path.join(root, "examples")):
        sys.stderr.write(f"validate_examples: no examples/ directory under {root}\n")
        return 2

    index = build_basename_index(root)
    report = Report()

    for config in find_config_files(root, args.targets):
        repairs = check_file(config, root, index, report)
        if args.fix:
            apply_repairs(config, repairs, report, root)

    if args.write_baseline:
        write_baseline(args.write_baseline, report.findings)
        print(
            f"wrote baseline with {len(set(f.key() for f in report.findings))} accepted "
            f"findings to {args.write_baseline}"
        )
        return 0

    accepted = load_baseline(args.baseline)
    new_findings = [f for f in report.findings if f.key() not in accepted]

    if args.format == "json":
        print(json.dumps(
            {
                "files_checked": report.files_checked,
                "total": len(report.findings),
                "new": [f.__dict__ for f in new_findings],
                "fixes_applied": report.fixes_applied,
            },
            indent=2,
        ))
    else:
        by_file: Dict[str, List[Finding]] = defaultdict(list)
        for finding in new_findings:
            by_file[finding.path].append(finding)
        for path in sorted(by_file):
            print(f"\n{path}")
            for finding in by_file[path]:
                print("  " + finding.render().split(": ", 1)[1].replace("\n    ", "\n      "))

        suppressed = len(report.findings) - len(new_findings)
        print(
            f"\n{report.files_checked} config files checked, "
            f"{len(new_findings)} new finding(s)"
            + (f", {suppressed} suppressed by baseline" if suppressed else "")
        )
        for line in report.fixes_applied:
            print(f"  fixed: {line}")

    blocking = [f for f in new_findings if f.severity == SEVERITY_ERROR]
    if args.warnings_as_errors:
        blocking = new_findings
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
