"""Shared, byte-pinned corpus input for the three corpus consumers.

No network access is performed. The extraction rules match the published
scripts; corpus revisions are recorded in the manifest, never normalized
to make a historical count pass.
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re

DATA_DIR = Path(__file__).resolve().parent / "data"
STOP = set("""the a an and or but of to in on at by for with from as is are was were be been
being it its this that these those he she they we you i his her their our your my me him them
us not no nor so if then than there here when where which who whom what all any some such own
same very can will just do does did done have has had may might must shall should would could
about into over under again further once more most other only out up down off above below""".split())


def load_corpus():
    manifest = json.loads((DATA_DIR / "moby_dick.json").read_text(encoding="utf-8"))
    packed = (DATA_DIR / "moby_dick_2701_2026-10-27.txt.gz").read_bytes()
    if hashlib.sha256(packed).hexdigest() != manifest["gzip_sha256"]:
        raise ValueError("Pinned corpus archive SHA-256 mismatch")
    data = gzip.decompress(packed)
    if len(data) != manifest["bytes"] or hashlib.sha256(data).hexdigest() != manifest["sha256"]:
        raise ValueError("Pinned corpus bytes or SHA-256 mismatch")
    return data.decode("utf-8"), manifest


def extract_sentences(raw):
    start, end = raw.find("*** START"), raw.find("*** END")
    header_end = raw.find("\n", start)
    if start < 0 or end <= start or header_end < 0 or header_end >= end:
        raise ValueError("Pinned corpus is missing its Gutenberg body boundaries")
    body = raw[header_end:end]
    return [text.strip() for text in re.split(r"[.!?]+", body) if len(text.strip()) >= 20]


def descriptor_cohorts(sentences):
    cohorts = collections.Counter()
    for sentence in sentences:
        words = [word for word in re.findall(r"[a-z]+", sentence.lower())
                 if len(word) >= 3 and word not in STOP]
        if words:
            descriptor = sorted(collections.Counter(words).items(),
                                key=lambda item: (-item[1], item[0]))[0][0]
            cohorts[descriptor] += 1
    return cohorts


def corpus_statistics(sentences):
    cohorts = descriptor_cohorts(sentences)
    return {
        "sentences": len(sentences),
        "distinct_payloads": len(set(sentences)),
        "duplicate_mass": len(sentences) - len(set(sentences)),
        "atoms": sum(cohorts.values()),
        "descriptors": len(cohorts),
        "mass_ge_4": sum(n for n in cohorts.values() if n >= 4),
        "max_cohort": max(cohorts.values(), default=0),
        "bindable_cohorts": sum(n >= 3 for n in cohorts.values()),
    }
