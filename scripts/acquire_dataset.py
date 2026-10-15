"""Resumable acquisition of version-pinned NEMAR EEG sidecars and recordings."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SUBJECTS = [f"sub-{i:03d}" for i in range(1, 13)] + ["sub-014", "sub-015", "sub-016", "sub-018", "sub-019", "sub-020"]
FILES = [
    "{subject}_task-nback_eeg.eeg",
    "{subject}_task-nback_eeg.vhdr",
    "{subject}_task-nback_eeg.vmrk",
    "{subject}_task-nback_events.tsv",
    "{subject}_task-nback_channels.tsv",
    "{subject}_task-nback_eeg.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def acquire_subject(subject: str, root: Path, base_url: str) -> dict:
    directory = root / subject / "eeg"
    directory.mkdir(parents=True, exist_ok=True)
    records = {}
    for template in FILES:
        name = template.format(subject=subject)
        target = directory / name
        url = f"{base_url}/{subject}/eeg/{name}"
        subprocess.run(["curl", "-L", "--fail", "--retry", "3", "-C", "-", "-sS", url, "-o", str(target)], check=True)
        records[name] = {"bytes": target.stat().st_size, "sha256": sha256(target), "url": url}
    return {"subject": subject, "files": records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="+", default=SUBJECTS)
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--base-url", default="https://data.nemar.org/on007169/v1.0.0")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    manifests = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(acquire_subject, subject, args.output, args.base_url) for subject in args.subjects]
        for future in as_completed(futures):
            result = future.result()
            manifests.append(result)
            print(json.dumps({"subject": result["subject"], "files": len(result["files"])}, sort_keys=True), flush=True)
    manifests.sort(key=lambda item: item["subject"])
    path = args.output / "acquisition_manifest.json"
    path.write_text(json.dumps({"dataset": "on007169", "version": "v1.0.0", "subjects": manifests}, indent=2) + "\n")
    print(f"ACQUISITION_OK subjects={len(manifests)} manifest={path}")


if __name__ == "__main__":
    main()
