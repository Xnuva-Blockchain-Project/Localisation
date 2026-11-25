# Shared Localisation Build Integration V1

## Status

Experimental development milestone.

Operator-reported qualification:
26DD-K17J-C1 and 26DD-K17J-C2-R2.

The standalone CMake consumer is qualified on the
tested Linux development toolchain.

Production wallet integration remains outstanding.

## Shared components

- tools/build_localisation.py
  Complete identity-driven catalogue preparation.

- tools/generate_resources.py
  Project-independent Qt language resource aliases.

- tools/build_qt_resource.py
  Isolated resource generation and atomic publication.

- cmake/XnuvaLocalisation.cmake
  Reusable application build integration interface.

## Integration contract

Each cryptocurrency provides:

1. A compatible identity manifest.
2. An authoritative application source inventory.
3. A CMake consumer target.
4. A pinned Localisation repository revision.
5. Compatible Qt6 and Python development tools.

The shared module provides catalogue generation,
validation, filtering, QM compilation and resource
source generation.

## Example CMake integration

    include(path/to/Localisation/cmake/XnuvaLocalisation.cmake)

    xnuva_add_localisation(
        wallet_target
        IDENTITY identity.json
        SOURCE_INVENTORY source-inventory.ts
    )

The consumer target must already exist.

The supplied application inventory must contain the
rendered portable template keys and exclude their
superseded source keys.

## Build behaviour

The shared CMake interface generates translation
resource source in the application build directory.

Unchanged inputs do not trigger unnecessary
resource regeneration.

Changes to declared dependencies trigger regeneration.

An incompatible application source inventory is rejected.

The previous generated resource source remains intact
if the replacement generation fails before publication.

A generation failure must still fail the current build.

## Reproducibility

Qt resource generation originally embedded variable
temporary paths and resource structure metadata.

The corrected wrapper normalises temporary QM
modification timestamps, supplies SOURCE_DATE_EPOCH
to rcc and canonicalises temporary path comments.

The fixed timestamp is 2000-01-01 UTC.

This timestamp is a build metadata convention only.
It does not represent a cryptocurrency launch date,
blockchain timestamp or consensus parameter.

Original inherited catalogues are never modified.

## Recorded qualification

- 56 Python regression tests passed.
- 100 language aliases preserved.
- 100 embedded catalogue executions passed.
- 75,454 native runtime comparisons reproduced.
- Initial and incremental CMake builds passed.
- Inventory timestamp-triggered regeneration passed.
- Three resource generation outputs were identical.
- Existing resource survived incompatible input failure.

Recorded generated resource SHA-256:

    2e0eab7b36fb1ed92a260993ea1bfd74afd06cecfccc59ea5b530a0142ceea4a

This checksum applies to the recorded Denzuve input
inventory and tested toolchain, not arbitrary projects
or different Qt versions.

## Tested toolchain

- Python 3.10.12
- CMake 3.22.1
- GNU C++ 11.4.0
- Qt 6.2.4

## Outstanding qualification

- Actual Denzuve wallet integration.
- Static-library resource initialisation.
- Automatic authoritative source inventory refresh.
- Real source content change qualification.
- Persistent integration regression test automation.
- Base-language and regional-language fallback.
- Cross-platform and cross-toolchain qualification.
- Expanded five-coin end-to-end portability.
- Comprehensive translation and placeholder correctness.
- Full application release qualification.

The shared module does not automatically rewrite
arbitrary cryptocurrency application source code.

No production readiness or mainnet activation
is authorised by this milestone.
