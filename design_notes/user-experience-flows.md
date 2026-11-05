# Congressional Contact: users, activities, and experience flows

These flows were approved through an owner interview for [Define User Flow](../.work-items/define-user-flow/item.md). They describe the agreed behavior for later website design and implementation. They do not claim that the site, help content, release process, or maintenance skills have been implemented or verified.

The primary outcome is that a phone visitor finds their currently serving congressional officials and saves their contact details to their phone. A completed file download is acceptable when the platform cannot do better. Saving one official at a time is intentional: the earlier multi-contact approach did not work reliably on iPhone.

Background: [project context](../.agent_context.md), [phone import findings](../research/multi-contact-import-findings.md), and [Jekyll delivery decisions](../.work-items/research-jekyll-integration/intent.md). Appearance is governed separately by [existing site design](existing-site-design.md). The help overlay below is an agreed interaction requirement; other visual and layout choices are outside this document's scope.

> **Owner decision after approval (2026-11-05): no ZIP in the URL.** This overrides the URL-state passages below. The page never puts the ZIP in the query string, the hash or the page title, because the Jekyll page inherits the site's Google Analytics, which may record URLs (see [Jekyll integration hazard 5](../research/jekyll-integration.md)). The consequences:
> - The browser address does not reflect ZIP results.
> - "Share ZIP results" is dropped.
> - "Copy link" copies the starting-page link (or the help link), and shared help links open over the starting page.
> - The self-hosting checklist no longer checks shared ZIP-results links.
>
> "Start over" still resets the app. See the [implementation plan](../.work-items/implementation-plan/plan.md).

## Users and activities

| User | Supported activities and priorities |
|---|---|
| Constituents | Find officials by ZIP; identify the right House representative; save individual contact cards; recover from missing or unexpected results; consult saving instructions; report bad data. Phone use is primary. Desktop downloads and later import are supported at much lower priority. |
| Helpers | Share the starting page, results for a ZIP, or help instructions so the recipient can complete the task on their own phone. |
| Self-hosters | Obtain a copy; configure reporting; publish it; verify it; restyle it with their own CSS knowledge; discover and install updates while preserving their customizations. |
| Maintainers | Refresh data; correct individual errors and investigate reports; verify behavior; change the site and documentation; publish the live site and downloadable releases. The owner is currently the only human maintainer. |

The primary constituent recognizes their House representative's name. People who do not recognize it are supported through the official House lookup. DC and territory residents are supported with the congressional officials applicable to them, including delegates or the resident commissioner; three contacts are not assumed for every visitor. Desktop use is secondary: the owner plans to direct people to their phones.

Helpers do not need a separate assisted-operation mode. Their distinct activities are sharing links and help. Saving instructions have iPhone and Android versions; recipients are expected to know which kind of phone they have.

## Constituent flows

### Find officials by ZIP

1. Open the starting page. ZIP entry is immediately available alongside a brief explanation of what the site provides; there is no introductory gate.
2. Enter a ZIP and explicitly submit it using the button or the keyboard's submit action. Entering five digits alone does not trigger the lookup.
3. The page shows the matching officials and immediately offers an individual save link for each applicable official. There is no confirmation step before those links become available.
4. Results identify the officials. The page does not add a separate contact-details inspection flow; the phone's contact preview shows the card contents.
5. Results offer the saving walkthrough, ZIP correction/reset, and applicable recovery and reporting paths described below.

For a ZIP spanning multiple districts, show every candidate House representative with an immediate save link. The visitor does not have to select a representative to unlock downloads. For a ZIP spanning states, clearly associate each candidate with that state's senators. Do not select a district based on its share of the ZIP.

Show currently serving officials, including during an election transition. Switch to successors when they take office, and keep district boundaries aligned with the serving Congress. Identify a vacant seat explicitly and offer cards for the officials still serving; do not silently omit the vacancy.

The browser address reflects the ZIP-results state. A clear “Start over” action clears the current ZIP and resets the app to its initial state. This also gives visitors a way to obtain the starting-page link rather than the current-results link.

### Identify the right House representative

1. A visitor who does not recognize their representative follows a link to the official House lookup.
2. The lookup opens in a separate window or tab, preserving Congressional Contact.
3. The visitor identifies their representative there, then returns to Congressional Contact.
4. They use the save link for the matching person among the candidates already shown.

This is an external lookup and manual return, not an address-lookup integration or automatic transfer of the answer into this site.

### Save contact cards on a phone

1. Choose the save link beside the desired official.
2. The browser opens the contact preview or downloads the individual card, according to the phone's behavior.
3. Complete the save in the phone's contacts app, following the walkthrough if needed.
4. Return to the page and repeat for the remaining applicable officials.

Each card contains the available full contact details from the maintained data. Cards are generated in the browser, one vCard per official; visitors need no account, API key, or backend service.

Save links remain available after use. The page does not mark cards as saved, automatically or manually: opening or downloading a card does not establish that the visitor completed the save. The same individual-card approach is used on iPhone and Android. Exact device steps remain to be verified before the walkthroughs are written.

### Recover from missing or unexpected results

- **No ZIP matches:** explain that the lookup has no matches, offer ZIP correction and the external House lookup, and allow a bad-data report when reporting is configured. A missing match does not establish that the ZIP is invalid; valid ZIPs can be absent from the mapping.
- **Results do not include the expected representative:** explain that results may be incomplete and offer the same correction, House lookup, and reporting paths.
- **Vacant seat:** identify the vacancy and allow saving the available officials, as above.

For now, there is no alternate in-site lookup by state or official's name. If the correct official is absent from our results, the external lookup does not by itself provide a way to obtain that person's card from our page. This is an accepted limitation of the initial recovery flow.

### Consult saving instructions

1. Open help from the page or follow a shared help link.
2. Help appears as an overlay on top of the underlying page, with a clear close button.
3. Choose iPhone or Android instructions. There is one general shareable help entry point; helpers do not need separate platform-specific links.
4. Follow the walkthrough from tapping the save link through finishing the save in the contacts app. Include how to proceed if the card arrives as a downloaded file, with the normal steps first and brief troubleshooting afterward.
5. Close help to return to the same ZIP, results, and place on the page.

Shared help links preserve the underlying state: ZIP results if shared from results, otherwise the starting page. Closing the overlay reveals that state. Help belongs on the site rather than sending phone users to the repository README.

### Download on desktop for later import

1. Find officials through the same ZIP flow.
2. Download individual cards using the same save links.
3. Import them into the desired contacts service. The owner's motivating case is importing into Google Contacts through its web UI.

Provide a brief desktop-help note linking to Google's import instructions, rather than maintaining a complete desktop walkthrough. Phone use remains the recommended route.

### Report bad data

1. Choose the reporting action for missing ZIP results, unexpected matches, or incorrect contact information.
2. The site opens the visitor's email app with a draft addressed to the configured reporting recipient.
3. Prefill the current ZIP and the relevant official's name when applicable; ask the visitor to describe the error.
4. The visitor reviews and sends the email. Opening the draft alone is not a submitted report.

The reporting address is stored in page data so each self-hoster can receive their own reports. The standalone output contains a fake placeholder address, with reporting inactive until a real address is configured. On the owner's website, the owner substitutes their own address. Do not send self-hosted-site reports to the project owner by default.

## Helper flows

### Share the starting page

1. Open the starting page, or use “Start over” if viewing ZIP results.
2. Use “Copy link” and send the copied link through the helper's chosen communication channel.
3. The recipient opens the starting page on their own phone and begins with ZIP entry.

### Share ZIP results

1. Look up the intended ZIP.
2. Use the same “Copy link” action. It copies the current state, and the browser address also represents those ZIP results.
3. Send the link. The recipient opens the ZIP results and saves the appropriate cards on their own phone.

There are no separate starting-page and results copy controls. Sharing a starting-page link from results requires resetting first. A ZIP-results link opens the candidate results for that ZIP; it does not resolve a multi-district ZIP to one person for the recipient.

### Share help

1. Obtain and share the site's direct help link.
2. The recipient opens the help overlay and chooses their phone type.
3. Closing help reveals the starting page or the ZIP results preserved in the link.

## Self-hoster flows

### Obtain, configure, and publish a copy

1. Follow “Host your own” from the page to repository documentation containing downloads and setup instructions. Technical setup does not belong in the saving-help overlay.
2. Obtain the appropriate ready-made output. For standalone hosting, download the single HTML file; no local build is required.
3. Replace the fake reporting address in page data with the host's real address so reporting becomes active.
4. Upload the standalone file to a static web host and open its public URL. Self-hosters are expected to know how to upload files; provider-specific hosting tutorials are not required.
5. Run the verification checklist below.

The Jekyll alternative follows the previously settled delivery: copy four generated files into the site checkout and add the menu entry with a one-time `_config.yml` edit. A small copy script is planned for the owner's setup. See [Jekyll delivery decisions](../.work-items/research-jekyll-integration/intent.md) for the files and build arrangement; these are existing delivery decisions, not newly implemented tools.

### Verify hosting, styling, or an update

Provide a short manual checklist covering:

- ZIP lookup at the hosted URL;
- saving a contact on a phone;
- shared ZIP-results and help links at that location;
- “Start over” returning the app to its initial state;
- configuration of the reporting recipient rather than leaving the placeholder.

Reuse this checklist after initial publishing, updates, and CSS changes.

### Restyle a copy

Self-hosters modify the styling using their own CSS knowledge, then run the checklist. Setup documentation should identify the relevant styling files or sections; teaching CSS and providing a styling editor are outside scope. Existing delivery decisions collect standalone colors and fonts into CSS variables.

### Discover and install updates

1. Check repository releases, or subscribe using GitHub release notifications as explained in the documentation.
2. Download the updated standalone or Jekyll output.
3. Preserve custom CSS separately and reapply it after replacing the applicable files. Documentation must explain which files or sections an update replaces. There is no automatic preservation of styling.
4. Confirm the site's reporting address is configured, publish the updated copy, and run the checklist.

The hosted page does not need an update-notification mechanism for its operator.

## Maintainer flows

### Refresh congressional data

1. Manually initiate the local refresh, including at the start of a new Congress. Scheduled refresh automation is not required.
2. Review a summary of changed officials, contact details, and ZIP mappings, with missing data and validation failures called out. A failed upstream acquisition must leave the last good published data intact.
3. Perform a human smoke check.
4. Invoke a future **review congressional data** skill from Claude or Codex. It must perform online verification of every official's record on each full refresh, not only changed records: unchanged upstream data may still be stale.
5. The agent reports discrepancies with source links and proposed corrections.
6. The human approves the corrections to apply; the LLM agent then makes those approved changes. It does not merely tell the human to edit them, and it does not apply unapproved proposals automatically.
7. Rebuild the outputs and perform the relevant verification before publication.

The review skill is an agreed future capability, not a skill built by this design work. The baseline is manual refresh, including new-Congress updates; a more precise recurring cadence was not established.

### Correct an individual error or investigate a report

1. Receive an email report at the configured address, or identify an error independently.
2. Investigate and verify the specific issue online.
3. Have the agent propose the correction with supporting sources.
4. Approve the correction; the agent applies it.
5. Rebuild and check the affected outputs, then use the publication flow.

A targeted correction does not require a full refresh or online review of every official. Supplemental contact information can be corrected through this flow as well.

### Verify a change

Verification depends on the scope of the change:

- Data corrections receive lookup and contact-card-content checks.
- Changes affecting contact saving or navigation also receive hands-on checks on both iPhone and Android.
- The initial release receives checks on both phone types.
- Appearance changes receive visual review as part of the maintainer's review.

These are required future checks, not results from this interview. The self-hosting checklist provides the shared basic behavior checks.

### Change behavior, appearance, or documentation

1. Describe the desired change to an agent.
2. The agent makes and verifies the change locally, using checks appropriate to its scope.
3. The human reviews the result, including appearance when relevant, before publication.

### Publish an approved update

1. Build the standalone and Jekyll outputs from the shared source and data.
2. Update the owner's live Jekyll page using the established copy-to-site-checkout, commit, and push process.
3. Run the relevant smoke checks at the page's public URL.
4. After those checks pass, publish the repository release with both standalone and Jekyll downloads, notifying release subscribers through the repository's release mechanism.

Publication is complete when both the live page and downloadable release have been updated. The live checks precede the release announcement so self-hosters are notified after deployment has been checked.

## Handoff and remaining verification

The owner approved the user inventory, activities, and flows and explicitly closed the interview. This completes the experience-definition work, not site implementation or deployment.

- Verify the exact single-card saving steps on iPhone and Android before writing the walkthroughs. Existing phone research establishes the reason for individual cards but does not settle every instruction or downloaded-file recovery step.
- Build the review congressional data skill and the site, help, configuration, and release capabilities in subsequent implementation work.
- This document resolves previously open experience policies for currently serving officials, DC and territories, and vacancies. Older project-context notes calling those policies open are superseded by these approved decisions.
- Detailed validation messages, URL encoding, copy-link failure handling, and device-specific mechanics were not designed in this interview. Resolve them during implementation without treating them as existing owner decisions.
