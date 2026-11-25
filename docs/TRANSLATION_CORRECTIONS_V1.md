# Permanent translation corrections — experimental V1

## Purpose

The XNUVA Blockchain Project maintains an independent
localisation architecture shared by its cryptocurrency
implementations.

The inherited translation catalogues remain immutable.
Corrections are maintained separately from the historical
source material.

## Build sequence

1. Load the project identity.
2. Generate project-specific translation source keys.
3. Validate the inherited catalogue migration.
4. Apply explicitly registered translation corrections.
5. Filter against the active application source inventory.
6. Suppress unresolved legacy branding where appropriate.
7. Compile the Qt language catalogues.
8. Generate the application translation resources.

## Correction policy

Each registered correction identifies:

- Language.
- Translation context.
- Exact source text.
- Disambiguation comment.
- Plural metadata.
- Original translation forms.
- Original translation attributes.
- Replacement translation forms.
- Review status and correction category.

A correction must match the reviewed original content.
Unexpected content or ambiguous message matches require
further engineering review.

Original source keys and plural structures are preserved.

Corrected translations retain their unfinished status.
They are not represented as professionally certified
native-language translations.

## Denzuve prototype qualification

Checkpoint 26DD-K17J-F6-R3 demonstrated:

- 69 targeted correction rules applied.
- No skipped correction rules.
- 100 compiled language catalogues.
- 65,860 retained catalogue messages.
- 65,791 unrelated messages preserved.
- 117 successful native translation comparisons.
- 66 successful module regression tests.
- Byte-identical QM output across repeated builds.
- Original inherited catalogue checksums preserved.

These are scoped development qualification results.

## Portability

The correction engine uses project-independent language
identifiers and generic cryptocurrency terminology.

Every consuming cryptocurrency requires individual
source-inventory, applicability and runtime qualification.

The module does not modify blockchain consensus,
monetary arithmetic, wallet keys or historical balances.

## Remaining qualification

- Complete application source-inventory regeneration.
- Broader linguistic and security-warning review.
- Actual core formatting-path verification.
- Regional translator precedence verification.
- Compatible source-content regeneration testing.
- Final application resource and executable qualification.

The earlier inherited localisation build remains an
explicit engineering recovery option where supported.

No production release or mainnet activation is authorised
by these development results.
