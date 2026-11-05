---
name: "Research matching users to their officials"
status: complete
---

# Research matching users to their officials

Research item: find an answer to the question in [intent.md](intent.md). The answer, sources, tradeoffs, and verification are recorded in [research/official-matching.md](../../research/official-matching.md).

Follow-up research for the user's approved ZIP-first candidate flow is saved in [research/zip-district-mapping.md](../../research/zip-district-mapping.md). It identifies a directly downloadable Census shortlist and a concrete difference from the official postal lookup; a complete postal mapping has not been verified.

The user subsequently selected HUD-USPS for the ZIP mapping and configured a local token. The [data design handoff](../../research/data-design.md) records the approved static JSON approach, candidate state references and proposed schema. No authenticated HUD request has been made.

## Completion

Completed November 4, 2026. Government documentation and live Census API requests establish that local name/state selection works without a runtime service; address lookup is also feasible without a key, but requires JSONP and deliberate congressional geography selection. ZIP codes can narrow candidates but cannot reliably identify one district. Recommendation: local state-and-name selection with an optional official lookup link. This recommendation has not been adopted as the final design. The research document also records the unresolved policy choice between currently serving officials and upcoming representation, with a recommendation for current service.

Verification limitations: sampled public addresses only; no browser/device flow or national accuracy study. No implementation was requested or performed.

## Resume note

Research is complete. The user approved the ZIP-first candidate flow with official lookup fallback and a state reference for each match, and selected HUD-USPS as the mapping source. Next step, if requested: validate authenticated HUD access, quarter/Congress alignment and sample mappings, then build the JSON index. The current-versus-upcoming representation policy remains open. Only credential setup has been performed; no matching implementation stage has started.
