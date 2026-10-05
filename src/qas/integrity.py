"""Atomic evidence persistence and SHA-256 manifests; no pickle deserialization."""

import hashlib
import json
import os
from pathlib import Path


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def seal(directory):
    directory = Path(directory).resolve()
    if (directory / "manifest.json").exists():
        raise ValueError("Evidence is already sealed")
    files = {
        p.relative_to(directory).as_posix(): digest(p)
        for p in directory.rglob("*")
        if p.is_file() and not p.name.endswith(".tmp")
    }
    atomic_json(directory / "manifest.json", {"algorithm": "sha256", "files": files})
    return files


def verify(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("algorithm") != "sha256" or not isinstance(manifest.get("files"), dict):
        raise ValueError("Invalid manifest")
    for relative, expected in manifest["files"].items():
        file = (directory / relative).resolve()
        if not file.is_relative_to(directory) or not file.is_file() or digest(file) != expected:
            raise ValueError(f"Corrupt or missing evidence: {relative}")
    observed = {
        p.relative_to(directory).as_posix()
        for p in directory.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    }
    if observed != set(manifest["files"]):
        raise ValueError("Unmanifested evidence files")
    return {"verified_files": len(observed), "status": "VERIFIED"}
