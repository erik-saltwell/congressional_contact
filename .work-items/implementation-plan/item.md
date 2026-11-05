---
name: "Implementation plan"
status: planning
---

# Implementation plan

The phased plan for building and launching Congressional Contact. It runs from real HUD data through the lookup-and-save launch on eriksaltwell.com, the later help, reporting and self-hosting phases, and the 120th Congress refresh.

See [plan.md](plan.md). Each phase is its own work item:

| Phase | Work item |
|---|---|
| 1. HUD data and final schema | [impl-01-hud-data-and-schema](../impl-01-hud-data-and-schema/) |
| 2. Data script | [impl-02-data-script](../impl-02-data-script/) |
| 3. Review congressional data skill | [impl-03-review-data-skill](../impl-03-review-data-skill/) |
| 4. Page core and Jekyll build | [impl-04-page-core-and-build](../impl-04-page-core-and-build/) |
| 4b. Pre-launch review run | [impl-04b-prelaunch-data-review](../impl-04b-prelaunch-data-review/) |
| 5. Launch v1 on eriksaltwell.com | [impl-05-launch-v1](../impl-05-launch-v1/) |
| 6. Help overlay, walkthroughs and sharing | [impl-06-help-and-sharing](../impl-06-help-and-sharing/) |
| 7. Bad-data reporting | [impl-07-bad-data-reporting](../impl-07-bad-data-reporting/) |
| 8. Standalone file and self-hosting releases | [impl-08-standalone-and-self-hosting](../impl-08-standalone-and-self-hosting/) |
| 9. 120th Congress refresh | [impl-09-120th-congress-refresh](../impl-09-120th-congress-refresh/) |

**Owner decisions made while planning (2026-11-05):**
- No ZIP in the URL.
- Launch before January on the 119th Congress, then rebuild for the 120th.
- The review skill and a full pre-launch review gate the launch.
- The first release is lookup and save only.

## Resume note

The draft plan is waiting for the owner's review. Once the owner approves it, or edits it, start phase 1. No phase has started.
