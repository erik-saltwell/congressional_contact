# Existing site design: eriksaltwell.com

Analysed 2026-11-05 for the [Analyze Existing Site Design work item](../.work-items/analyze-existing-site-design/). It guides the styling of Congressional Contact in both outputs:
- the **Jekyll page** on eriksaltwell.com;
- the **standalone single file** for self-hosters.

Delivery decisions come from [research/jekyll-integration.md](../research/jekyll-integration.md). Statements here are findings and recommendations unless they are listed as owner decisions.

Reference files:
- [site-design-sample.html](site-design-sample.html): a self-contained styled sample, built as the standalone file would be.
- [site-design-sample-phone.png](site-design-sample-phone.png): that sample at 390×844.

The sample shows the **recommended options, which the owner did not choose**: embedded fonts and page-scoped accessible colours. It remains as evidence for those measurements. The chosen design is described under "Owner decisions".

## Site update: new colours (2026-11-05, after this analysis)

The owner recoloured eriksaltwell.com after this analysis. The changes are in the site repository's commits `48738c0`, `2637fd5`, `20887de` and `ff85299`. The site is no longer stock: the colour statements in "Summary" and the measurements below describe the site before this update. The table under "Design tokens" shows the new values.

- **`_config.yml`:**
  - warm off-white page;
  - orange navbar and footer;
  - brown-grey navbar and footer text;
  - copper and brown hover colours.

  Body text (`#404040`) and links (`#008AFF`) are unchanged.
- **`assets/css/beautifuljekyll.css` now differs from the theme:**
  - a new `--heading-col: #584F4E`, used for page and post titles that sit over no image, post-preview titles and "read more" links, and pager links;
  - the navbar hover uses `--navbar-hover-col`, not `--hover-col`;
  - footer links use `--footer-link-col`.
- **The styled 404 page has been removed.**

What this means for Congressional Contact:
- **The Jekyll page picks up the new colours automatically,** because it inherits the theme's variables.
- **Bootstrap's buttons, input border and focus ring are unchanged** (`#007bff`). The decision to keep stock Bootstrap colours still stands.
- **The standalone file does not copy these colours.** It uses neutral stock Beautiful Jekyll colours and carries none of the owner's branding (owner, 2026-11-06). See "Standalone file styling".
- **`.cc-*` rules must not hard-code a white background.** Use `var(--page-col)` so the page matches the off-white.
- **The contrast figures in this note were measured against white.** They have not been re-measured on `#F8F7F5`.

## Summary

- **Before the 2026-11-05 update, the site was stock Beautiful Jekyll with the theme's default colours.** Its theme files match upstream master commit `b1b667e` (2024-12-13, "Bluesky icon in font awesome"), not the 6.0.1 release named in the footer.
  - The owner's only design customization is a styled 404 page (`div.notfound`).
  - The other changes are a favicon link and the `{% seo %}` tag.
  - Every colour in `_config.yml` equals the theme default.
- **The Jekyll page gets almost everything from the theme:** fonts, colours, page header, navbar, footer and content column. It needs only a small `.cc-*` stylesheet.
- **The theme's default blues fail WCAG AA contrast, and so do Bootstrap's button, input border and focus ring.** Recommendation: a page-scoped accent (`#0066CC`, 5.57:1), plus a visible focus outline and a darker input border, applied only inside `.cc-app`.
- **The standalone file's styling is cheap apart from fonts:**
  - the reduced CSS is about 10 KB, or 3 KB gzipped;
  - the two fonts are 59 KB, or about 55 KB over the network once gzipped.
- **Owner decisions (2026-11-05):**
  - The standalone file **loads Lora and Open Sans from Google Fonts**.
  - Both outputs **keep the theme's and Bootstrap's stock colours**.

  See "Owner decisions".

## Design tokens

Beautiful Jekyll already stores its tokens as CSS custom properties on `:root`. They are generated from `_config.yml` in `assets/css/beautifuljekyll.css`.

| Token | Value on the site (after 2026-11-05 update) | Theme default | Used for |
|---|---|---|---|
| `--page-col` | `#F8F7F5` | `#FFFFFF` | Page background |
| `--text-col` | `#404040` | same | Body text, headings |
| `--heading-col` (site CSS, not `_config.yml`) | `#584F4E` | none | Page and post titles over no image, post-preview titles, pager links |
| `--link-col` | `#008AFF` | same | Links |
| `--hover-col` | `#C57735` | `#0085A1` | Link hover and focus |
| `--navbar-col` / `--navbar-text-col` / `--navbar-hover-col` / `--navbar-border-col` | `#F09D51` / `#584F4E` / `#804214` / `#DDDDDD` | `#EAEAEA` / `#404040` / hover-col / `#DDDDDD` | Navbar |
| `--footer-col` / `--footer-text-col` / `--footer-link-col` / `--footer-hover-col` | `#F09D51` / `#584F4E` / `#584F4E` / `#804214` | `#EAEAEA` / `#777777` / `#404040` / `#0085A1` | Footer |
| `--mid-col` | `#808080` | same | Blockquotes, the rule under the page title, secondary text |
| `--body-font` | `'Lora', 'Times New Roman', serif` | same | Body text |
| `--header-font` | `'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif` | same | Headings, navbar, footer, subheadings |

## Typography and layout

These values were measured on the live About page at a 390 px phone viewport (computed styles), and checked against the theme CSS.

- **Body:** Lora 400, 18 px (`1.125rem`), line height 1.5, `#404040` on white. Paragraph margins are `1.875rem`.
- **Headings:** Open Sans 800, line height 1.1. Sizes are h1 `2.25rem`, h2 `1.875rem`, h3 `1.5rem` and h4 `1.125rem`, each with a `1.25rem` top margin.
- **Page header** (`layout: page`):
  - `.intro-header` has an 80 px top margin and a 20 px bottom margin.
  - The title is Open Sans 800 at 50 px (`3.125rem`), centred.
  - Below it is `hr.small`: 100 px wide, a 4 px `--mid-col` rule with rounded ends.
  - The subtitle is Open Sans 300 at 27 px.
- **Navbar:** 51 px tall on a phone, `#EAEAEA` with a 1 px `#DDDDDD` bottom border, Open Sans. The 50 px round avatar is centred and overlaps the bottom edge.
- **Content column:** Bootstrap `container-md` > `row` > `col-xl-8 offset-xl-2 col-lg-10 offset-lg-1`. On a phone that is full width with 15 px side padding.
- **Footer:** `#EAEAEA` with round social icons in Font Awesome, then the copyright line in Open Sans.
- **Fonts the live site loads:** Lora 400 normal and italic, Open Sans 300, 400 and 800, and Font Awesome 6.
- **On a 390 px phone, the theme's page header pushes the ZIP field about 305 px down.** That accounts for the navbar, the 80 px margin, a two-line 50 px title, the rule and the subtitle. The field is still well above the fold on an 844 px screen. This is an observation, not a decision. A shorter title or the theme's `full-width` option would not change it much.

## Components available for the page

- **Theme's own:** the page header (title, rule and subtitle, from front matter), and notification boxes `.box-note`, `.box-warning`, `.box-error` and `.box-success`. The boxes are light backgrounds with a coloured left border, and their text contrast is 8:1 or better.
  - Use `.box-note` for "not sure which district?" guidance.
  - Use `.box-warning` for "no match for that ZIP".
- **Bootstrap 4.4.1 (unstyled by the theme):** `.btn`, `.btn-primary`, `.form-control`, `.sr-only` and the grid. **Beautiful Jekyll does not restyle buttons or form fields**, so they appear in Bootstrap's default blue (`#007bff`), not the site's link colour.
- **Icons:** the site uses Font Awesome from a CDN. **Do not use Font Awesome in the shared markup.** The standalone file cannot load it without an external dependency, and it is large. Use inline SVG or no icons.

## Accessibility findings

Contrast was computed with the WCAG 2.x formula.

| Pair | Ratio | AA requirement | Result |
|---|---|---|---|
| Body text `#404040` on white | 10.37 | 4.5 | Pass |
| Link `#008AFF` on white | **3.45** | 4.5 | **Fail** (theme default) |
| Link hover `#0085A1` on white | 4.31 | 4.5 | Fail (theme default) |
| White on Bootstrap `.btn-primary` `#007bff` | **3.98** | 4.5 | **Fail** |
| White on `.btn-primary:hover` `#0069d9` | 5.22 | 4.5 | Pass |
| Bootstrap input border `#ced4da` on white | **1.49** | 3.0 (control boundary) | **Fail** |
| Bootstrap button focus ring `rgba(38,143,255,.5)` | **1.77** | 3.0 | **Fail** |
| Bootstrap input focus ring `rgba(0,123,255,.25)` | **1.39** | 3.0 | **Fail** |
| Footer text `#777777` on `#EAEAEA` | 3.72 | 4.5 | Fail (theme default; affects the whole site) |
| `--mid-col` `#808080` on white | 3.95 | 4.5 | Fail if used for text |
| Navbar and footer links `#404040` on `#EAEAEA` | 8.62 | 4.5 | Pass |
| Bootstrap placeholder `#6c757d` on white | 4.69 | 4.5 | Pass |

**Recommendation:** use page-scoped app tokens, defined in the shared `congress.css` on `.cc-app` and never on `:root`, so the theme's navbar, links and footer are untouched.

| App token | Value | Ratio | Purpose |
|---|---|---|---|
| `--cc-accent` | `#0066CC` | 5.57 with white | Primary buttons. It stays in the theme's blue family |
| `--cc-accent-hover` | `#005A9E` | 7.10 | Button hover |
| `--cc-control-border` | `#8A8A8A` | 3.45 | ZIP input border |
| `--cc-focus` | `#0066CC` | 5.57 | A solid 3 px focus outline with a 2 px offset, replacing Bootstrap's faint glow |
| `--cc-rule` | `#DDDDDD` | (decorative) | Dividers between officials, matching the navbar border |

Other recommendations:
- **Tap targets:** make the primary actions ("Find my officials" and each "Save contact") full-size buttons at least 44 px tall. Don't use `btn-sm`, since saving is the main action on a phone.
- **Official names:** set names in Open Sans 700, which the variable Open Sans file covers. Bold Lora would need another font file, or the browser would fake it.
- **Theme-wide failures** (links at 3.45:1, footer text at 3.72:1) are the owner's call to fix site-wide in `_config.yml`. They are outside this project.

**Verification:**
- `site-design-sample.html` passed the design gate (`gate.mjs verify_states.mjs`): 12 element states, WCAG AA in default, hover and focus.
- A negative control (the same page with the stock Bootstrap colours) failed on 3 button states at 3.98:1, so the gate does catch the stock colours.
- The gate does not measure focus rings or input borders. Those ratios are computed, not gated.

## Two CSS layers

The shared build adds styling in two layers so the Jekyll page never redefines the theme's variables.

1. **App layer, `congress.css` (shared by both outputs).** It contains only `.cc-*` rules and `--cc-*` tokens scoped to `.cc-app`: the accessible button, border and focus overrides, plus the results list, ZIP form and spacing. It must not set `--link-col` or any other theme variable on `:root`, because on the Jekyll page that would recolour the theme's navbar and footer.
2. **Theme layer (standalone file only).** It reproduces what the Jekyll page gets from the site:
   - `:root` variables with **the theme's own names and values** (`--page-col`, `--text-col`, `--link-col`, `--body-font` and so on). A self-hoster restyles the page with the same variables Beautiful Jekyll users already know. This meets the decision to collect colours and fonts in CSS variables.
   - the Bootstrap 4.4.1 and Beautiful Jekyll rules the markup uses;
   - `@font-face` rules for the fonts, if the owner chooses to embed them.

The standalone file should include the theme's page header markup (`.intro-header` > `.page-heading`) so it reads like the Jekyll page. It also has an empty header bar and a footer bar; see "Standalone file styling".

## Standalone styling cost

Measured with the test markup (`research/jekyll-integration-test/src/`) plus a page-header and content-column skeleton.

| Piece | Raw | Gzipped |
|---|---|---|
| Full Bootstrap 4.4.1 CSS (for comparison) | 159,515 B | 23,628 B |
| Full `beautifuljekyll.css` (for comparison) | 23,449 B | 5,073 B |
| **Reduced Bootstrap + Beautiful Jekyll rules for this page** | **10,190 B** | **3,193 B** |
| Lora 400, Latin, unmodified from Google Fonts | 21,148 B | (woff2; doesn't compress) |
| Open Sans variable 300–800, cut down to Latin-1 | 37,900 B | (woff2) |
| **Both fonts as base64 in the file** | ~79 KB | **~56 KB** |

- The reduced CSS figure is **a lower bound for the test page.** The real page will add components (the candidate chooser for ZIPs that span several districts, messages, the official-lookup link) once the [Define User Flow](../.work-items/define-user-flow/) item defines them. Expect a few KB more, not tens of KB.
- **Earlier figure corrected:** the Jekyll research estimated about 236 KB for fonts. That counted all four Google Fonts files (both typefaces in both regular and italic) before any cutting down. The page needs only Lora regular and one variable Open Sans file, about 56 KB over the network, or about 18% on top of the roughly 300 KB gzipped data.
- With the sample assembled the way the build would do it, `site-design-sample.html` is 93 KB raw, with no data.

### Font licensing

Both fonts are under the SIL Open Font License 1.1. This was checked from the font files' `name` tables.
- **Lora:** "Copyright 2011 The Lora Project Authors … with Reserved Font Name "Lora"". Cutting a font down counts as modifying it under the OFL, and a modified version may not keep a reserved name. **So embed Google's Latin Lora file unmodified** (21 KB), as the sample does, rather than cutting it down further.
- **Open Sans:** "Copyright 2020 The Open Sans Project Authors", with no reserved font name. Cutting it down is fine.
- The standalone file must carry both copyright lines and the OFL reference in a CSS comment, because self-hosters redistribute it. The sample shows the wording.
- The real build could derive Open Sans's character set from the actual data plus the page's own text. A missing character falls back to the next font in the stack, which is a small visual mismatch, not a failure.

## Notes for the Jekyll page

- Use `layout: page` and set `title`, `subtitle`, `share-description` and `description`. The theme renders the header.
- Load `congress.css` through `css:` front matter. It sits after the theme CSS, so the `.cc-app` overrides win without `!important`.
- No fonts, Bootstrap or theme CSS are added; the theme already loads them.

## Standalone file styling (owner, 2026-11-06)

The standalone file is for other people's sites. It carries none of the owner's branding, and it uses neutral stock Beautiful Jekyll colours instead of eriksaltwell.com's. The Jekyll page is unaffected.

**Nothing that identifies the owner:**
- no name, logo or avatar;
- no homepage or navbar links, and no search;
- no social icons;
- no copyright.

**Layout:**
- **Header bar:** an empty bar in the stock navbar style, `#EAEAEA` with a 1 px `#DDDDDD` bottom border.
- **Page header:** below the bar, the theme's centred title ("Your Congress") and subtitle, as on the Jekyll page.
- **The app,** with the same markup and `congress.css` as the Jekyll page.
- **Footer bar:** stock `#EAEAEA`, holding a single small "Host your own copy" link to the project's repository, which is the Phase 8 link to downloads and updates. Nothing else goes in it.

**Colours,** set as `:root` variables in the standalone theme layer:

| Role | Value | Notes |
|---|---|---|
| Page background, text | `#FFFFFF`, `#404040` | stock |
| Header and footer bars | `#EAEAEA`, border `#DDDDDD` | stock |
| Headings (`--heading-col`) | `#404040` | stock text colour. Stock Beautiful Jekyll has no heading colour, and without this the page would fall back to the owner's `#584F4E`. |
| Buttons and links (`--cc-accent`) | `#006B80` | the stock teal `#0085A1`, darkened to pass AA: white on it is 6.2:1, and it is 6.2:1 as link text on white. Stock teal is 4.3:1 and stock blue `#008AFF` is 3.5:1. |
| Hover (`--hover-col`) | `#0085A1` | stock |
| Button hover | a darker teal | to be chosen when it's built |
| Messages and errors | red burgundy `#8E1B2E` | the same as the Jekyll page, 9.0:1 on white |
| Invalid-ZIP field border | `--hover-col`, so stock teal | |

Fonts stay as decided: Lora and Open Sans from Google Fonts.

## Owner decisions after the site recolour (2026-11-06)

These replace decisions 2 and 3 below where they conflict. The owner made them after reviewing phone screenshots of the page.

1. **Colours follow the recoloured site, not stock Bootstrap.** The page reads the theme's variables and never sets them. `congress.css` falls back to eriksaltwell.com's values on hosts without them.

   | Element | Colour | Theme variable |
   |---|---|---|
   | Buttons | brown `#804214` with white text (7.8:1); darker `#66340F` on hover and press | `--navbar-hover-col` |
   | Links | the same brown, underlined, because brown against body text is only 1.3:1 | `--navbar-hover-col` |
   | Link hover | copper `#C57735` | `--hover-col` |
   | All headings | `#584F4E` | `--heading-col` |
   | Heading links on hover | copper | `--hover-col` |
   | Note-box left border | brown | `--navbar-hover-col` |

   No blue is used anywhere on the page.
2. **One button style.** Find and Save are the same brown `btn btn-primary btn-lg`, 48 px tall, which is phone-touchable. Start over is a text link. A second button style is used only when two buttons are on screen together and need different weights.
3. **Invalid ZIP:** Bootstrap's `is-invalid` on the field, with a copper border. The error message is in the body text colour (`#404040`, 10:1).
   - The owner first chose copper for it, which is 3.2:1, below AA.
   - The second review changed it to brown.
   - The third review changed it to body text, because brown means "tappable" on this page.
4. **State labels appear only when a ZIP spans two or more states.** They are small, uppercase and letter-spaced, below the names in the hierarchy.
5. **Title "Your Congress".** Below 576 px wide, `congress.css` shrinks the theme's page title to 2.25 rem and the subtitle to 1.25 rem. That stylesheet loads only on this page, so this is the one rule outside `.cc-*`.
6. **Shorter copy:**
   - no intro paragraph: the subtitle and the field label are enough (second review);
   - no "to your phone": the subtitle is "Save your senators and representative", and the descriptions say "save them as contacts", because desktop visitors download a file instead;
   - a one-sentence split-district note;
   - a two-line no-match message;
   - "(opens in a new tab)" only on the first house.gov link on screen;
   - at most one note box. A ZIP that is both split and in two states gets a single combined note.

**Second review (owner, 2026-11-06):**

7. **After a search,** the results scroll into view below the theme's fixed navbar (`scroll-margin-top`), so a small phone no longer hides their top.
8. **State groups:** each state label has a 2 px heading-colour rule and extra space above it, so the boundary between two states is clear.
9. **Choosing a representative:** when a state has more than one House candidate, a "Representatives (choose yours)" label sits above them.
10. **Note boxes** drop the theme's side margins, so they line up with the dividers.
11. **Opened cards are marked.** Once a Save button has been tapped, it turns into the outlined version of the same brown button. The outline is the one exception to "one button style", and it exists only to show this state. It records the tap only; it doesn't claim the contact was saved. The mark lasts until the next search or Start over.

**Third review (owner, 2026-11-06):**
- The split-district note is "This ZIP code is split between 2 House districts. Not sure which is yours? Check house.gov.", because the "choose yours" label already gives the instruction.
- The form has 2 rem of space above it, to set it apart from the page header.
- "Officials for ZIP code …" and "Representatives (choose yours)" share one label style: Lora 600 in the heading colour.
- **The page uses "add" throughout** (owner, 2026-11-06):
  - the subtitle is "Add your lawmakers to your contacts";
  - each button says "Add to contacts";
  - the meta descriptions say "add them to your contacts";
  - the combined note says "Add the senators and representative…";
  - the card note says "Added from Congressional Contact".

  The subtitle fits on one line at 390 px and wraps to two at 320 px.

**Hierarchy and messages (owner, 2026-11-06).** These replace the state label, the "choose yours" label, the note boxes, the opened-results summary and Start over, all described above.
- **Structure:**
  - A state heading appears on every result, even for a single state (this may be removed later).
  - Under it are two peer cards, "Senator(s)" and "Representative(s)". Each is a 1 px warm-grey bordered card with a small uppercase label, and the label is singular or plural to match.
  - Each person is a row: the name (Lora 600, 1.0625 rem, body colour) and district on the left, and the Add button on the right. Senators have no role line.
  - This is the "cards" treatment, chosen from five mock-ups.
- **Burgundy messages:** every message and error is red burgundy text (`#8E1B2E`, 8.4:1), with no box. It was `#7A1F2B` at first, which was so close to the brown that it looked like a mistake. It then went to `#A11D33`, and was darkened slightly to this colour (owner, 2026-11-06). That covers:
  - the invalid-ZIP error;
  - no match;
  - "crosses N states", shown above the states;
  - "split between N House districts. Pick yours…", shown inside the Representatives card;
  - "has no U.S. senators", shown inside the Senators card;
  - the vacant seat, shown inside its Representative card.
- **House.gov links** appear only right after a burgundy message that offers one: no match, crosses states, and split.
- **Removed:**
  - Start over, because a new search replaces the results;
  - the bottom "Not seeing your representative?" line;
  - the "Officials for ZIP code …" line, because the field already shows the ZIP.

## Owner decisions (2026-11-05)

The owner chose differently from both recommendations below. These decisions override two constraints recorded in the work item's intent.

1. **Fonts: load Google Fonts externally (option c).**
   - The standalone file links the Google Fonts stylesheet for **Lora 400 and Open Sans 300, 400 and 800**, the faces this page uses, instead of embedding font files.
   - This is a deliberate exception to the no-external-dependencies rule, for fonts only. All other CSS and JS stay inline.
   - Consequences:
     - Visitors' browsers contact Google's font servers, which see their IP address.
     - The file stays about 56 KB smaller.
     - If Google Fonts is blocked or unavailable, the theme's own font stacks take over ('Times New Roman', serif for body text; 'Helvetica Neue', Helvetica, Arial, sans-serif for headings). The page still works, with a different look.
   - With nothing embedded, the font-licensing and cutting-down notes above don't apply to the standalone file.
   - The Jekyll page is unaffected, because the theme already loads these fonts from Google.
2. **Colours: keep the stock theme and Bootstrap colours (option b).**
   - `congress.css` does not override Bootstrap's button colour, input border or focus ring, and adds no `--cc-accent` tokens.
   - The standalone file's theme layer uses the site's `_config.yml` values as listed under "Design tokens".
   - **The owner accepts the AA contrast failures** in the table above. These are buttons at 3.98:1, the input border at 1.49:1 and focus rings at 1.4 to 1.8:1.
3. **Guiding preference: be consistent with the existing site wherever possible.** This rule settles design choices that are still open, and it settles the three left over from the recommendations as follows. Each one follows a pattern the theme already uses.
   - **Buttons use the theme's Bootstrap sizes, with no custom sizing.**
     - The ZIP form's submit button is `btn btn-primary btn-lg`, as on the theme's comment form. It renders about 48 px tall.
     - Each "Save contact" link is a standard-size `btn btn-primary`, as on the Tags page. It renders about 38 px tall.
     - No `btn-sm`, and no custom `min-height`.
   - **Official names use the theme's heading styles, not a custom weight.** Each name is a heading element styled by the theme (Open Sans 800, for example an `h3`). Entries are separated the way the post list does it: a 1 px `#eee` bottom border with the theme's spacing. This replaces the earlier Open Sans 700 suggestion.
   - **Icons follow the theme's Font Awesome usage, and only if they add something.**
     - The theme's form submit buttons have no icon, and neither does the ZIP button.
     - If the Save button gets an icon, use a Font Awesome icon the way the Tags page does (`<i class="fas …" aria-hidden="true">`). On the Jekyll page the theme already loads Font Awesome.
     - The standalone file would then load the same Font Awesome stylesheet from its CDN, as it does the fonts. That adds roughly 100 KB of CSS plus a font file, so the default is no icons.
     - Do not draw custom SVG icons, because the site doesn't use them.

## Questions put to the owner (as asked, with the recommendations)

1. **Fonts in the standalone file:**
   - (a) **Embed** Lora (unmodified) and cut-down Open Sans, about 56 KB over the network. It looks exactly like the site.
   - (b) **System fonts**, adding 0 KB. It is close in layout but visibly different: no Lora serif body or Open Sans headings.
   - (c) **Load Google Fonts externally**, which breaks the no-external-dependencies rule and sends visitors' IP addresses to Google.

   **Recommendation: (a).** The cost is modest next to the data, and it keeps the standalone file looking like the site.
2. **Accessible accent for the app:**
   - (a) **Page-scoped tokens** as above (`#0066CC` buttons, darker input border, solid focus outline), affecting only Congressional Contact.
   - (b) **Keep the stock theme and Bootstrap colours**, which fail AA.

   **Recommendation: (a).**

   Separately, the owner may want to fix the site-wide link and footer colours in `_config.yml`. That is out of this project's scope.

## Reproducing the measurements

- **Theme comparison:** clone `https://github.com/daattali/beautiful-jekyll` and search for the commit whose `assets/css/beautifuljekyll.css`, `_layouts/` and `_includes/` differ least from the site. That is `b1b667e`; the remaining differences are the 404 styling, the favicon link and `{% seo %}`.
- **Reduced CSS:**
  1. Render `beautifuljekyll.css` with the site's colour values: drop the front matter, the `{% %}` blocks and the image-URL lines.
  2. Run:
     ```
     npx -y purgecss@6.0.0 --css bootstrap.min.css bj.css --content body.html skeleton.html congress.js --output out
     ```
  - Bootstrap comes from `https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css`.
  - The skeleton is the theme's page header and content column markup, as in the sample.
- **Fonts:**
  1. Request `https://fonts.googleapis.com/css?family=Lora:400` and `...family=Open+Sans:300,400,800` with a desktop Chrome user agent, and take the `/* latin */` `woff2` URLs.
  2. Cut down Open Sans with:
     ```
     uvx --from 'fonttools[woff]==4.55.0' pyftsubset OpenSans.woff2 --unicodes='U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201D,U+2022,U+2026' --flavor=woff2 --layout-features='kern,liga'
     ```
  3. Check licences with `ttx -t name`.
- **Contrast:** use the WCAG 2.x relative-luminance formula. For translucent focus rings, blend them over white first.
- **Gate:**
  ```
  node <ux-ui-agent-skills>/scripts/gate.mjs verify_states.mjs design_notes/site-design-sample.html
  ```
