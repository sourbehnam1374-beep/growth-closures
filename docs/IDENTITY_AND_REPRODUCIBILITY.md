# Identity ingress and reproducible verification

Date: 27 October 2026. Original audited head: `85f76771fa0bfb3d3492f9520da42c6d62403517`.

## Failure reproduced and repaired

Two atoms can have the same payload/address and different descriptors.
PR #4 already rejected that conflict in `close_field` and `close_incremental`.
`two_phase` still assigned into its add map directly, losing the conflicting
record before the guard saw it. With two additional D1 context atoms,
reversing the conflicting additions produced either 3 or 6 parts.

`two_phase` now uses the same `_insert_by_address` guard. Every addition is
checked before removal filtering, so a tombstone cannot hide a conflict.
The guard copies the record on insertion; advancing an input generator
cannot mutate the stored descriptor through the original dictionary.
Identical duplicates remain idempotent and remove-wins behavior is retained.

The new ingress suite reproduced **9 failures and 11 passes** on the original
PR head. After repair, all 20 ingress tests pass. The existing 10 deletion
properties also pass. Eight conflicting two-phase operation orders are
additionally checked in the independent adversarial verifier.

## Corpus custody

All three consumers (`test_anomaly_characterization`, `corpus_cohorts`, and
`corpus_o5`) now load the same lossless gzip snapshot through `corpus_fixture`.
The loader checks both compressed and decompressed SHA-256 digests, raw
length, UTF-8 decoding, and Gutenberg body boundaries. Missing or corrupted
data fails verification; it is never reported as an offline skip.

Source: <https://www.gutenberg.org/files/2701/2701-0.txt>.
Retrieved 27 October 2026; HTTP Last-Modified: 9 October 2026.
Raw SHA-256: `f12eb530502755ef2b8f535e2ecef3e95802eab584e60ac7992ccf856256fdbe`.
The downloaded source is unmodified (1,234,646 bytes); gzip is only packaging.
The original 1851 work and the complete downloaded source/license text are retained.

| Measurement | Historical paper / prior audit | Pinned 27 October revision |
| --- | ---: | ---: |
| Extracted sentences | 8,636 | 8,637 |
| Distinct sentence payloads | 8,597 | 8,598 |
| Duplicate mass | 39 | 39 |
| Sentences with a descriptor | 8,631 | 8,632 |
| Atom mass in cohorts of size ≥4 | 5,014 | 5,013 |

[The successful 7 October CI run](https://github.com/sourbehnam1374-beep/growth-closures/actions/runs/37555848606)
records the historical 8,631 / 5,014 counts. That run did not retain the raw
corpus bytes or their digest. The new snapshot is a reproducible revision,
not a reconstruction of the missing historical input. The manifest retains
both results explicitly. Paper sources, PDFs, archived packs, and Lean
theorem statements are unchanged.

## Verification and CI integration

`requirements-verification.txt` pins the Python verification dependencies.
`run_verification.py` runs all eight Python verification/measurement scripts
and the collected regression/property suite. It rejects Python optimization,
source proof placeholders, missing checks, timeouts, and nonzero results.
It records exact source/input hashes, Python/dependency versions, Git head,
and whether the working tree contained changes. With `--lean`, it requires
Lean 4.30.0 and checks the unchanged formal development.

The growth, necessity, and unified ledgers now return failure to their caller
when a claimed check fails. Three injected-failure regressions verify this
behavior. Corpus regressions cover offline execution, missing files,
corrupted archives/raw bytes, changed expected counts, and missing markers.

The workflow runs on PRs targeting `main`, pushes to `main`, and manual
dispatch. Its token has read-only repository permissions. Logs and a JSON
receipt are retained as a GitHub Actions artifact even when a check fails.

Local verification: all eight scripts and **41 collected tests** passed on
Python 3.12.14. The plotting consumer also generated its PDF/PNG and matching
statistics from the pinned input. Local Lean could not start in this runner
(`failed to locate application`); the new commit's GitHub Actions result is
the authority for its fresh Lean execution.

## Contract for SHIVA memory adapters

Use these functions as the ingress boundary; never collapse records into an
address-keyed dictionary before passing them to the guard.

| Operation | Entry point | Required input |
| --- | --- | --- |
| Initial closure | `close_field(seed)` | All incoming records, including duplicates |
| Incremental growth | `close_incremental(existing, delta)` | An already-closed store and the full delta |
| Add/remove event replay | `two_phase(ops)` | The full operation stream; conflicts checked even for removed identities |

Persist a new result only after successful return. Surface `ValueError` as
an identity conflict requiring resolution, rather than retrying with a
first-wins or last-wins policy. Exact duplicates are safe to replay. Derive
descriptors deterministically from the payload: the atom address format
still commits the payload, and this patch does not change stored addresses.

The intentionally order-sensitive `naive_sequential` function remains a
counterexample for the paper, not a memory-ingress adapter. This work
integrates the reference implementation and verification paths; it does not
claim to have deployed an adapter into a separate SHIVA application.
