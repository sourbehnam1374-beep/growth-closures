"""Corpus custody, offline replay, and failure behavior."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import socket

import pytest

import corpus_fixture as cf
from test_anomaly_characterization import corpus_identity


def test_exact_snapshot_replays_without_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Corpus verification attempted network access")
    monkeypatch.setattr(socket, "socket", forbidden)
    raw, manifest = cf.load_corpus()
    stats = cf.corpus_statistics(cf.extract_sentences(raw))
    assert stats == manifest["expected"]
    assert (stats["atoms"], stats["mass_ge_4"], stats["duplicate_mass"]) == (8632, 5013, 39)
    assert manifest["historical_paper_measurement"]["atoms"] == 8631
    assert corpus_identity()


def test_missing_fixture_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(cf, "DATA_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        cf.load_corpus()


@pytest.mark.parametrize("changed", ["archive", "raw", "expected"])
def test_corruption_is_not_silently_accepted(monkeypatch, tmp_path, changed):
    for source in cf.DATA_DIR.iterdir():
        if source.is_file():
            shutil.copyfile(source, tmp_path / source.name)
    monkeypatch.setattr(cf, "DATA_DIR", tmp_path)
    packed_path = tmp_path / "moby_dick_2701_2026-10-27.txt.gz"
    manifest_path = tmp_path / "moby_dick.json"
    manifest = json.loads(manifest_path.read_text())
    if changed == "archive":
        packed_path.write_bytes(packed_path.read_bytes()[:-1])
    elif changed == "raw":
        packed = gzip.compress(gzip.decompress(packed_path.read_bytes()) + b"changed", mtime=0)
        packed_path.write_bytes(packed)
        manifest["gzip_sha256"] = hashlib.sha256(packed).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
    else:
        manifest["expected"]["atoms"] += 1
        manifest_path.write_text(json.dumps(manifest))
        assert not corpus_identity()
        return
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        cf.load_corpus()


@pytest.mark.parametrize("text", ["no markers", "*** END\n*** START\n", "*** START*** END"])
def test_missing_body_boundaries_fail(text):
    with pytest.raises(ValueError, match="boundaries"):
        cf.extract_sentences(text)
