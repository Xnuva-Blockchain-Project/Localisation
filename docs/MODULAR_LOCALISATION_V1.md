# Modular Localisation Architecture V1

## Status

Experimental development milestone.

Proposed version: 0.1.0-alpha.

This milestone is not a production release.

## Ownership

XNUVA Blockchain Project.

The Localisation repository is maintained independently
of individual cryptocurrency implementations.

## Supported project architecture

- Denzuve (DZUV)
- Aurzola (AUZV)
- Sestovi (SEZQ)
- Asveru (ASVR)
- Duprezo (DPZE)

The shared project architecture uses individual identity
manifests and compatible application source inventories.

Denzuve is the initial integration target. The other four
identities have been exercised as experimental portability
fixtures, not as qualified application integrations.

## Immutable inherited archive

common/inherited/qt contains the inherited Qt catalogues.

Original catalogue contents, upstream provenance and
licensing must be preserved.

Generated outputs must never overwrite the archive.

## Module components

- tools/identity.py
  Identity manifest validation.

- tools/branding.py
  Portable branding template rendering.

- tools/generate_catalogues.py
  Deterministic translation catalogue generation.

- tools/validate_catalogues.py
  Independent generated catalogue integrity verification.

- tools/filter_catalogues.py
  Application-aware catalogue filtering and experimental
  conservative suppression of suspected stale translations.

## Identity contract

Each integrating cryptocurrency supplies its identity
through a schema-compatible JSON manifest.

The manifest includes project identity, ticker,
application name, executable names, payment URI label,
denomination labels and fallback language.

Princeps and Principes are denomination presentation
labels. They do not authorise changes to monetary
arithmetic or consensus rules.

## Template inventory

migration/common-gui-templates.json preserves the
original 15-template qualification baseline.

migration/common-templates-v2.json contains the expanded
25 active portable templates.

Application source keys must be compatible with the
rendered templates.

## Integration contract

1. Provide a validated identity manifest.
2. Extract the application's authoritative source keys.
3. Render the portable migration templates.
4. Generate project-specific catalogues.
5. Independently validate the generated catalogues.
6. Filter against the application source inventory.
7. Review suspected stale translations.
8. Compile native Qt QM catalogues.
9. Perform runtime and application-level qualification.

The module does not automatically rewrite arbitrary
application source code.

## Translation safety

Do not blindly substitute cryptocurrency names inside
translated sentences.

Where a translation is unavailable or suspected to carry
incorrect branding, prefer verified English fallback.

Preserve translator metadata, plural behaviour and
legitimate upstream attribution.

## Engineering boundaries

Localisation must not modify:

- Blockchain history.
- Consensus rules.
- Monetary policy.
- Wallet balances or private keys.
- Transaction serialization.
- Proof-of-work or proof-of-stake behaviour.
- Production node configuration.

## Version management

Integrating projects should pin a specific independently
reviewed Localisation revision.

Changes to the shared module require regression testing
and application-specific requalification.

No automatic production upgrades are authorised.
