# Weekly content implementation plan

**Goal:** Two reliable weekly refreshes for secondary Miss Stream sections, preserving existing articles and schedules.
**Approved design:** Wednesday adds one illustrated lookbook entry. Sunday adds up to four decor objects and one verified alternative pair, maintains product health and packs, updates quiz/home selections. Preserve prior collections; publish only valid changes. No LinkedIn publishing.
**Architecture:** Shared product validation and incremental collection helpers. Explicit Wednesday/Sunday CLI modes. Existing GitHub Actions handle deployment; build and offline regression tests precede content commits. Unknown upstream responses preserve existing data.

- [x] Add offline regression tests for preservation, deduplication, product-status handling, invalid generated references, and schedule execution.
- [x] Replace conflicting full-regeneration path with bounded incremental generation using real scraped product identities/prices and validated images. Remove catalog-size stop conditions.
- [x] Extend health checks across guides and all data collections with deduplication, bounded checks, persisted cursor and report; confirmed unavailability must be distinguished from upstream errors.
- [x] Derive quiz/home selections from shared catalogs; seasonal banner follows calendar; label streamer equipment as suggestions unless sourced.
- [x] Schedule Wednesday inspiration and Sunday maintenance, no duplicate Sunday generator. Gate commits on tests and build, report results and preserve existing content on generation failures.
- [x] Run tests/build; review changes; deployment and production checks follow in the active run.
