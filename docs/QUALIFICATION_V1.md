# Experimental Localisation Qualification V1

## Evidence status

Operator-reported development checkpoint results,
subject to engineering review.

Latest checkpoint: 26DD-K17I-G4C.

## Recorded qualification

| Component | Result |
|---|---|
| Python regression tests | 56/56 PASS |
| Inherited catalogues preserved | 100 |
| Initial portable templates | 15 |
| Expanded active portable templates | 25 |
| Expanded migrated entries | 1417 |
| Original message entries | 67121 |
| Extracted Denzuve source keys | 1249 |
| Excluded inactive entries | 1261 |
| Suppressed suspected stale translations | 59 |
| Filtered output entries | 65860 |
| Retained entries compared | 65801 |
| Native catalogue executions | 100 |
| Native runtime comparisons | 75454 |
| Native suppressed fallback entries tested | 59 |
| Filtered compilation matching diagnostics | 0 |

## Translation coverage

Across 100 catalogues and 1249 active source keys:

- Possible catalogue/source combinations: 124900.
- Nonempty translation entries: 62618.
- Nonempty finished translation entries: 121.
- Empty translation entries: 3242.
- Missing active source keys: 59040.

These figures describe catalogue contents, not complete
linguistic or runtime translation coverage.

Inherited nonempty unfinished translations are retained
under the tested default Qt compilation policy.

## Tested environment

- GNU C++ 11.4.0.
- Qt 6.2.4.
- GNU gettext 0.21.
- Python 3 development environment.

## Reproduce Python regression tests

From the Localisation repository root:

    PYTHONDONTWRITEBYTECODE=1 \
        python3 -m unittest discover -s tests -v

## Native qualification infrastructure

Reusable native qualification source is preserved under
tests/native.

Independent catalogue verification is implemented in
tests/qualify_filtered_catalogues.py.

The native harness compares retained translations and
exercises English fallback for suppressed entries.

## Outstanding qualification

- Complete integrated Denzuve application build.
- Actual wallet language selection and resource loading.
- Expanded five-coin end-to-end portability.
- Comprehensive linguistic correctness.
- Comprehensive Qt and printf placeholder validation.
- Review of conservative branding suppression decisions.
- Broader legacy branding detection.
- Native fallback harness hardening.
- Full application release regression gates.

The initial source inventory is specific to the tested
Denzuve development baseline. It must be refreshed when
the application source changes.

GNU gettext extraction warnings were recorded. The
compared core inventories differed only by a generated
copyright attribution entry.

No complete CMake translation regeneration was performed.

No production readiness or complete language support
is claimed.
