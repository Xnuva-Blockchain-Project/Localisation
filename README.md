# XNUVA Modular Localisation Framework

Status: experimental architecture foundation.

Reference implementation: Denzuve Transition Release 1.

## Purpose

Provide reusable localisation infrastructure for independently
maintained cryptocurrencies within the XNUVA Blockchain Project.

## Architecture

- common: reusable language catalogues.
- identity: cryptocurrency-specific branding metadata.
- extensions: cryptocurrency-specific translated messages.
- schema: versioned data contracts.
- migration: reviewed source-key migration mappings.
- tools: deterministic generation and validation utilities.
- tests: localisation-specific qualification.

## Engineering requirements

1. Retain the native Qt translation engine.
2. Preserve all inherited language catalogues.
3. Preserve upstream copyright and licence attribution.
4. Preserve contexts and disambiguation information.
5. Preserve formatting placeholders and plural forms.
6. Use English source-text fallback for unreviewed translations.
7. Never silently manufacture or approve translations.
8. Generate native Qt TS and QM resources.
9. Require deterministic, reproducible generation.
10. Support independent cryptocurrency builds.
11. Do not require external network services during compilation.
12. Reject ambiguous or conflicting translation keys.
13. Preserve previous catalogues until migration is qualified.

## Identity boundary

Identity manifests contain presentation metadata only.

They do not define or modify:

- Consensus rules.
- Blockchain history.
- Monetary supply.
- Denomination arithmetic.
- Wallet serialization.
- Address encoding.
- Network ports.
- Payment URI protocol handling.
- Proof-of-work activation.

Functional source remains authoritative.

## Translation key policy

Qt translation identity includes context, source text and
disambiguation information. Numerus metadata and plural forms
must also be preserved.

Shared translations may only be reused when their meanings
and formatting requirements are compatible.

Coin-specific language grammar must be reviewed. Blind runtime
substitution of project names into translated sentences is
not permitted.

## Migration strategy

1. Inventory the inherited translation catalogues.
2. Preserve their original content and provenance.
3. Identify reusable and project-specific translation entries.
4. Implement deterministic catalogue generation.
5. Validate placeholders, contexts and plural forms.
6. Qualify English fallback behaviour.
7. Integrate the generator into the Qt build system.
8. Verify generated QM resources.
9. Perform graphical and full regression qualification.

## Current status

The architecture, identity manifest and initial migration map
have been established.

The existing Qt translation pipeline remains authoritative.
No inherited language catalogues have been migrated.

The generator, complete schema validation, catalogue validation
and Qt integration remain outstanding.

## Licensing

The inherited Bitcoin Core translation material retains its
applicable copyright and licence notices.

See the accompanying COPYING file and inherited translation
documentation.

## Independent repository preservation

All 100 inherited Qt translation catalogues are preserved
under common/inherited/qt.

See common/inherited/PROVENANCE.md for source identity,
licensing and checksum verification.

The Denzuve identity manifest is the initial reference
implementation.

The existing Denzuve translation pipeline remains
authoritative until modular integration is qualified.

Catalogue migration, deterministic generation, comprehensive
validation and Qt integration remain outstanding.

No cryptocurrency release or production deployment is implied.

## Experimental modular localisation V1

The shared localisation engine is under development as an
independent component of the XNUVA Blockchain Project.

- [Modular architecture](docs/MODULAR_LOCALISATION_V1.md)
- [Qualification evidence](docs/QUALIFICATION_V1.md)

The original inherited catalogue archive is preserved.

This experimental milestone is not a production release
and does not claim complete translation coverage.

### Shared build integration

- [Experimental CMake build integration](docs/BUILD_INTEGRATION_V1.md)

The shared build interface supports deterministic
translation resource generation using project identity
manifests and compatible application source inventories.
