# Findings: multi-contact import on iOS and Android

Answers the question in [intent.md](intent.md). This is desk research from web searches only. Nothing was tested on a real device, and no Apple or Google primary documentation for this exact flow was found, so every claim below is secondary-source and unverified unless noted.

## Short answer

**Probably yes on iOS and on Android, but not as a true one-click import to the contacts app on either, and not verified.** A single `.vcf` file holding several `BEGIN:VCARD` / `END:VCARD` blocks is the standard way to deliver multiple contacts, and both platforms are reported to handle it. Each needs at least one extra tap after the download. The best fallback is one `.vcf` per official.

## iOS

- Opening a multi-contact `.vcf` (from Mail, Messages, Files or AirDrop) shows a preview with an **"Add All N Contacts"** option. Sources: [applevis](https://applevis.com/comment/105827), [macReports](https://macreports.com/how-to-import-a-vcard-vcf-file-into-iphone-contacts/), [univik](https://univik.com/blog/import-vcf-to-apple-contacts/).
- Safari reportedly can download and open a `.vcf` directly into the Contacts preview (supported since iOS 7 per one developer's account). Older forum threads describe Safari refusing the file, but those predate current iOS. Source: [Apple Discussions: importing a vcf from a web page](https://discussions.apple.com/thread/2169675). **Unconfirmed on current iOS.**
- A malformed file, such as a missing `END:VCARD`, may import zero contacts or only the first. Source: [correctvcf help page](https://correctvcf-web.pages.dev/help/vcf-wont-import-into-iphone-ios-contacts) (vendor page, treat with caution).
- Duplicate handling: "Add All" is reported to skip contacts that already exist by name matching, and a "Create New Contacts" option adds everything regardless. Unconfirmed against Apple documentation.

## Android

- Opening a downloaded `.vcf` is reported to hand it to the Contacts app's import flow, and a single file can hold many contacts. Native import takes the whole file, with no per-contact selection. Sources: [univik](https://univik.com/blog/import-vcf-to-android/), [cisdem](https://www.cisdem.com/resource/import-vcard-to-google-contacts.html).
- Some sources say Google Contacts cannot import several separate `.vcf` files at once, which counts against the one-file-per-official fallback on Android. Source: [cisdem](https://www.cisdem.com/resource/import-vcard-to-google-contacts.html).
- Manual import path (Contacts, then Settings or Organize, then Import from file) varies by Android version and manufacturer, and a Samsung user reported "Something went wrong while importing the contacts" for a `.vcf`. Source: [Samsung community thread](https://us.community.samsung.com/t5/A-Series-Other-Mobile/Message-quot-Something-went-wrong-while-importing-the-contacts/td-p/2518057) (no confirmed fix).
- Samsung exports vCard 2.1 and Pixel/Google write vCard 3.0 with UTF-8, so format version may matter. Source: [univik](https://univik.com/blog/import-vcf-to-android/).
- Firefox on Android is reported to fail the `.vcf` flow where Chrome works. Source: [Mozilla support thread](https://support.mozilla.org/el/questions/1304482).
- No source documented how Chrome on Android treats a `.vcf` served from a blob or `data:` URL. A 2011 thread found `data:` vCard links inconsistent across browsers. Source: [W3C public-device-apis thread](https://lists.w3.org/Archives/Public/public-device-apis/2011Jan/0038.html).

## Options compared against the project's constraints

| Option | Static, no backend | iOS | Android | Notes |
|---|---|---|---|---|
| One link to a single multi-contact `.vcf` | Yes | "Add All N Contacts" reported | Import whole file reported | Best match to "one click" goal; at least one extra tap to confirm |
| One `.vcf` per official (three links) | Yes | Three previews, three confirmations | Three separate imports; combining is reportedly not supported by Google Contacts | Fallback; clunkier, and weaker on Android |
| `navigator.share` with a `.vcf` file | Yes | Reported working in Chrome on iOS | Reported failing in Chrome on Android in one thread | Unreliable; feature-detect with `navigator.canShare` and fall back. Source: [Mozilla Discourse thread](https://discourse.mozilla.org/t/web-share-api-and-vcard/95913) |
| Generate the `.vcf` client-side (blob or `data:` URL) | Yes | Unverified | Unverified | Needed if data is not pre-built; test, or serve pre-built static files instead |

## Practical implications

- The delivery mechanism is a plain link to a `.vcf` file served as `text/vcard`. This needs no backend and fits the single-file, static constraint if the file is embedded or sits next to the page.
- Each card needs its own complete `BEGIN:VCARD` / `END:VCARD` block with consistent line endings. Writing vCard 3.0 in UTF-8 looks safest for both platforms (inference, not verified).
- Because success is "saved in the contacts app" and a completed download is the accepted fallback, the realistic target is: download, then one tap to import.

## Uncertain, needs a real-device test

1. Whether Safari on current iOS opens a linked multi-contact `.vcf` straight into the "Add All" preview.
2. Whether Chrome on current Android opens a downloaded `.vcf` into the Contacts import flow, and with what taps, on both Pixel and Samsung.
3. Whether a blob or `data:` URL works instead of a hosted file on either platform, which affects the one-file goal.
4. Whether `text/vcard` versus `text/x-vcard` as the MIME type changes behavior.

A small test page with one three-contact `.vcf`, opened on one iPhone, one Pixel and one Samsung, would settle all four.

## Second pass: the four unknowns (desk research, still unverified on devices)

**1. Does Safari open a linked multi-contact `.vcf` into an "Add All" preview?**
Likely yes, but with a usability problem. Since iOS 13, tapping a vCard link opens a preview screen instead of Contacts. Users report no obvious save button: they have to tap the share/Actions icon and pick Contacts, and many tap Done thinking it saved. Nobody in the thread found a way to skip the preview. Source: [Apple Developer Forums: Importing vCards on iOS](https://developer.apple.com/forums/thread/124193) (2019-2020 posts; the thread does not cover multi-contact files). Third-party guides describe "Add All N Contacts" appearing for multi-contact files, but those are blog posts. Implication: the page should tell iPhone users what to tap after the preview opens.

**2. Does Chrome on Android hand a downloaded `.vcf` to the Contacts import?**
Plausible. AOSP Contacts code shows a "Import contacts from vCard?" Yes/No dialog when an import starts from outside the Contacts app and the device has 0 or 1 writable accounts. With 2 or more accounts, an account picker is shown instead. This is the expected path for a handoff from a browser, but the commit does not mention browser downloads and says nothing about multi-contact files. Source: [AOSP ContactsCommon commit](https://github.com/android-security/android_packages_apps_ContactsCommon/commit/a4d49bc) (old, and Samsung uses its own Contacts app). Nothing found about Chrome's download "Open" button itself.

**3. Do blob or `data:` URLs work instead of a hosted file?**
No current evidence either way. Sources found are from the iOS 7 era or earlier, and report Safari failing on `data:` vCard URIs in 2011 and a calendar-attachment workaround that predates iOS 7 native support. Source: [Stack Overflow answer mirror](https://kaweah.freedombox.rocks/kiwix/stackoverflow.com_en_all_2023-11/a/11405271). Treat as untested. Only matters if the page must build the file in the browser; a static `.vcf` file (or one embedded as base64 in the single HTML file) avoids the question if the hosted-file link works.

**4. `text/vcard` or `text/x-vcard`?**
`text/vcard` is the registered type (RFC 6350, `.vcf` and `.vcard`), and `text/x-vcard` is the older unregistered one still seen in legacy software. Source: [IANA text/vcard registration](https://www.iana.org/assignments/media-types/text/vcard). No source says how iOS or Android differ. IANA notes that vCard 2.1 and 3.0 remain in common use and are not strictly compatible with 4.0; 3.0 is what Google/Pixel write. A static host often serves `.vcf` with the right type automatically, which matters for the self-hosting goal because a plain file host may not.

## Test plan for the devices

Make three small `.vcf` files and a test page (all static):
- `all.vcf`: three contacts in one file, each with its own `BEGIN:VCARD` / `END:VCARD`, vCard 3.0, UTF-8, CRLF line endings, and varied fields (phone, URL, email, address).
- `one.vcf`: a single contact, as the fallback baseline.
- Page links: (a) plain link to `all.vcf`, (b) link with the `download` attribute, (c) blob link built by JavaScript from the same text, (d) a `navigator.share` button with feature detection.

Run each on the iPhone (Safari) and on the Android phone (Chrome), recording per link: what appears, taps needed, whether all three contacts land in the Contacts app, and which account they were saved to. Also try `text/x-vcard` by serving a second copy, if the host lets you set the type. Repeat once on a second Android browser or Contacts app if one is handy, since Samsung and Pixel differ.

## Device test results

Test page: branch `vcard-test`, served from GitHub Pages (`text/x-vcard`), with three fake "Test …" contacts in `all.vcf`.

### Android (2026-11-04)

Browser: Chrome 156 on Android 10 (the user agent hides the device model, shown only as "K"). Contacts app and taps per flow not yet recorded.

Page log: `share: true, canShare: true`; `all.vcf` served as `text/x-vcard` and loaded with 3 cards; blob link and `data:` URL handlers ran; the share button logged `NotAllowedError: Permission denied` on every tap (seven times).

| Link | Result |
|---|---|
| A. Plain link to `all.vcf` | Worked |
| B. Link with `download` attribute | Worked |
| C. File built in the browser (blob) | Worked |
| D. Web Share API button | Nothing visible on tap. The log shows `NotAllowedError: Permission denied` each time, although `canShare` returned true. Cause not established; not pursued |
| E. `one.vcf`, single contact | Imported one contact, as expected |
| F. `data:` URL | Worked |

Reading so far (provisional): on this Android phone, a plain link to a static multi-contact `.vcf` is enough, and building the file in the browser also works, so the single-file, no-hosted-files goal looks feasible on Android. The Web Share API is not worth using. "Worked" is taken to mean all three contacts arrived; confirm.

### iPhone (2026-11-05)

Safari with iOS 18.7 (user agent shows Version/26.6.1). Page log: `share: true, canShare: true`; `all.vcf` served as `text/x-vcard` and loaded with 3 cards; blob and `data:` handlers ran; the share button logged `AbortError: Abort due to cancellation of share`, meaning the share sheet opened and was dismissed.

| Link | Result |
|---|---|
| A. Plain link to `all.vcf` | Showed a single contact card (Test Senator One only). Could share it to Contacts or tap Add New Contact. Only Senator One was added. |
| B. `download` attribute | Same as A |
| C. Browser-built blob | Same as A |
| D. Web Share API | Share sheet opened; the same single card flow appeared. Sharing works on iPhone, unlike on the tested Android phone |
| E. `one.vcf` | Not reported |
| F. `data:` URL | Not reported separately; the user reported no option imported all three |

**Finding:** on iPhone, none of the tested routes imported all three contacts from a multi-contact `.vcf`. Safari shows only the first card. No "Add All 3 Contacts" option appeared. Untested: opening the file from the Files app, Messages or Mail (where "Add All" is reported by third-party guides).

## Decision (user, 2026-11-05)

Use one uniform flow on both platforms instead of different flows per phone: build each official's vCard in the browser (the blob approach, so the page stays one file) and put a save link next to each person, so saving the three takes three taps. For a ZIP with several districts, show all candidate representatives, each with its own link, and let the user choose. The single-click "save all three" goal is dropped as a requirement; it still works on Android and could be offered there only if it does not complicate the interface.

Why: iPhone cannot import a multi-contact file from Safari, and the single-card flow works on both platforms. The blob approach worked on both phones. Not yet tested: a single-contact blob on Android (the single-contact file by plain link worked, and a multi-contact blob worked).

## Conclusion

Answer to the intent's question: single-click import of several contacts at once does **not** work reliably on both platforms. It works on Android (Chrome 156, Android 10) by plain link, `download` link, browser-built blob and `data:` URL, but iPhone Safari (iOS 18.7) shows only the first card of a multi-contact `.vcf` with no "Add All" option. The Web Share API is unusable on Android (`NotAllowedError`).

Best approach and fallback: one vCard per official, built in the browser as a blob, with a save link next to each person (three taps), the same on both platforms. See the Decision section above.

Limits: tested on one iPhone and one Android phone only. Not tested: opening a multi-contact file from the Files app, Messages or Mail on iPhone; a single-contact blob on Android; Samsung's Contacts app; the Android Contacts app name and tap counts were not recorded. The temporary `vcard-test` GitHub Pages site and branch have been removed; the test files remain in `research/vcard-test/`.
