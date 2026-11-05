---
name: "Research contact data source and freshness"
status: complete
---

# Research contact data source and freshness

Research item: find an answer to the question in [intent.md](intent.md).

Findings and source/coverage checks are saved in [research/contact-data-source.md](../../research/contact-data-source.md), with an [evidence summary](../../research/contact-data-source-evidence.json).

Subsequent approved decisions and the JSON proposal are saved in [research/data-design.md](../../research/data-design.md). Static JSON storage and the maintained data approach are approved; HUD is selected for ZIP mapping, using a local credential outside the published website.

## Completion

Completed November 4, 2026. Downloaded and inspected the community roster/local-office data, official House/Senate XML, and a pinned contact-form registry snapshot. Compared member IDs and counted field coverage; inspected sample official feedback and office pages without sending messages. VCF generation from static or fetched data is feasible. The proposed approach is a maintained static dataset with verified form/email supplements, not a final source/design decision.

Limits: no complete national form/email curation, number dialing, email-delivery checks, or mobile field-label/import verification. Public general-purpose email is not available for every official, and source presence does not establish current accuracy.

## Resume note

Research is complete. The user approved maintained static JSON and local HUD acquisition. Credential storage is configured; authenticated HUD requests, a generator and a published dataset have not been implemented. If requested, continue with the validation and schema decisions in the data-design handoff, then source merging and generation. Refresh cadence and supplement ownership remain open.
