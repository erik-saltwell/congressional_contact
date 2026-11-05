# Jekyll integration findings

Researched 2026-11-05 for the [Research Jekyll Integration work item](../.work-items/research-jekyll-integration/), which is now complete. Statements are research findings unless they are listed under "Owner decisions". The reproducible test kit is in [jekyll-integration-test/](jekyll-integration-test/).

## Summary

- **The owner's homepage, eriksaltwell.com, is a Jekyll site** (Beautiful Jekyll theme on GitHub Pages), so the research targets Jekyll.
- **Two ways of adding Congressional Contact to the site both work:**
  - a **single page file**, with everything inline and wrapped in `{% raw %}`;
  - a **Jekyll-native layout**, with a page file, data in `_data/`, and the JS and CSS under `assets/`.

  Both were tested with GitHub Pages' own Jekyll 3.10.0, on a local clone of the site, in a phone-sized browser. In both, the ZIP lookup, the vCard blob links, the theme's navbar, footer and search, and the site build all work.
- **The owner chose the Jekyll-native layout: four files** (see "Owner decisions"). A data refresh replaces one JSON file, and the page's code goes through Jekyll untouched. Without `{% raw %}`, the single-file approach can fail the whole site build.
- **The future data and build scripts must follow two rules:**
  - Never write a number in exponent form (`1e3`). Jekyll reads `_data/*.json` with a YAML parser, which turns such a number into a string.
  - Never let `</` appear inside the inlined data.
- **One shared source produces both the Jekyll files and the standalone single file**, as the owner wanted, using the same markup, JS and data.

## Owner decisions (2026-11-05)

These were agreed with the owner during this research. Some came before the local test and some after.

- **Build pipeline.** Two short Python scripts live in this repo:
  1. A **data script** rebuilds the officials and ZIP data. The owner runs it directly or through a Claude skill.
  2. A **build script** assembles both published outputs from that data plus source parts (markup, CSS and JS fragments).

  The source parts are build inputs and are never published themselves.
- **Two outputs from one source:**
  - a **standalone single HTML file** that anyone can upload to their own site;
  - a **Jekyll version** that is quick for the owner to add to eriksaltwell.com.

  Other owners of Jekyll sites may adopt the Jekyll version, but they may need to adjust the styling.
- **Data delivery.** The data is inlined in both outputs, so the JavaScript has one code path and never fetches data at runtime.
- **What "Jekyll-native" means:**
  - The page uses the site's layout and its Beautiful Jekyll and Bootstrap classes, so it looks like the rest of the site by default.
  - Files follow Jekyll conventions: data in `_data/` is put into the page by Liquid at build time, and CSS and JS go under `assets/`.
  - Nice to have: the page's wording can be edited like any other page.
- **The Jekyll version is four files** (chosen after the test):
  - `congress.html` at the site root;
  - `_data/congress.json`;
  - `assets/js/congress.js`;
  - `assets/css/congress.css`.
- **A small copy script** will put those four files into place in a local checkout of the site. After that, the owner commits and pushes, and GitHub Pages builds and publishes. The script is to be built in a later implementation item.
- **Menu listing.** The page appears in the site's top menu through a one-line `navbar-links` edit to `_config.yml`, made once by hand. Nothing else about the page needs a site config change.
- **Standalone styling.** The standalone file uses the same markup and theme classes as the Jekyll version. It inlines only the styles it uses, and collects colours and fonts into CSS variables at the top so self-hosters can restyle it. The details belong to the [Analyze Existing Site Design](../.work-items/analyze-existing-site-design/) item.
- **"Search" means the ZIP lookup.** The page's JavaScript covers the ZIP lookup and building and saving the vCards. The theme's own site search only needs to keep working.

## Hosting background (verified 2026-11-05)

| Fact | Evidence |
|---|---|
| eriksaltwell.com is built by Jekyll 3.10.0 with Beautiful Jekyll 6.0.1 | The live page's `generator` meta tag and its footer comment |
| Source repo: https://github.com/erik-saltwell/eriksaltwell.com (public, not a fork, one branch: `main`) | Linked from the live page. The GitHub Pages API shows a branch build from `main` at `/`, custom domain `www.eriksaltwell.com`, status "built" |
| Built by GitHub Pages' **legacy** branch build; the repo has no Actions workflow | Pages API reports `build_type: legacy`. The owner pushes source files and GitHub builds and publishes, so no local build is needed. Only GitHub Pages' allowed plugins are available, and the build runs in safe mode |
| The repo matches the live site | The newest live posts match `_posts/`, up to `2024-10-31-eye-of-agamotto`. Last commit `20887de`, 2025-01-23 |
| Theme files are copied into the repo, not loaded as a remote theme | `_layouts/`, `_includes/` and `assets/` are present. The repo's own `Gemfile` builds the theme gem; it is not set up to run the site |
| Domain is registered with Namecheap, which also hosts its DNS | Nameservers are `dns1` and `dns2.registrar-servers.com`; RDAP lists NameCheap, Inc. The domain was registered on 2025-01-19 and expires on 2035-01-19 |
| `www` is a CNAME to `erik-saltwell.github.io`; the bare domain points at GitHub Pages' A records (185.199.108–111.153) | DNS lookup |
| `erik-saltwell/saltwell_com` is an older, unused site repo, not the live site | Its `baseURL` is `saltwell.com`, which now redirects to an unrelated company (saltwellsalt.com) |

## Theme facts that shaped the test

- **Per-page CSS** is loaded with `css:` front matter, which produces `<link>` tags in the page head, after the theme's styles.
- **Per-page JS** is loaded with `js:` front matter, which produces `<script>` tags at the end of the body. They come after jQuery 3.5.1 slim, Popper, Bootstrap 4.4.1 and `beautifuljekyll.js`.
- **Script tags written in the page body** run before those theme scripts, so the page's code must not depend on jQuery. It doesn't.
- **External resources:** the theme loads Bootstrap 4.4.1 CSS, Font Awesome, and the Lora and Open Sans Google Fonts from CDNs. It also loads Google Analytics.
- **Theme scripts:** `beautifuljekyll.js` has one document-wide key handler, which closes the search overlay when Escape is released. It does not interfere with typing in the ZIP field (tested).
- **Site search:** `assets/data/searchcorpus.json` lists every page in `site.html_pages`, so the new page shows up in site search automatically. The corpus still parses with the page added (tested).
- **Page descriptions:** when a page has no `subtitle` or `share-description`, `head.html` fills the meta and og descriptions from the page's own content. Always set `subtitle`, `share-description` and `description` so script contents can never leak into these tags. The test set them and confirmed short, correct tags.
- **Menu:** the navbar is built from `navbar-links` in `_config.yml`. That is why the menu listing needs a one-line config edit.

## Variants tested

`build_variants.py` generated all variants from the same source files (`src/body.html`, `src/congress.js`, `src/congress.css`).

| | A0: single file, no `raw` | A: single file with `raw` | B: Jekyll-native (chosen) |
|---|---|---|---|
| Files the owner copies | 1 | 1: `congress.html` | 4: `congress.html`, `_data/congress.json`, `assets/js/congress.js`, `assets/css/congress.css` |
| How data gets in | Written literally | Written literally | Liquid `{{ site.data.congress \| jsonify }}` at build time |
| Site build | **Fails for the whole site**: `Liquid syntax error: Unknown tag 'not_a_tag'` | Passes | Passes |
| JS and CSS come out identical to source | n/a | Yes, Liquid-looking probe strings intact | Yes, asset files copied byte for byte |
| Data comes out identical to source | n/a | Yes | Yes, after passing through the YAML reader |
| What a data refresh touches | Whole page | Whole page | `_data/congress.json` only |
| Works in phone browser | n/a | Yes | Yes |

`check_output.py` ran 22 checks against the built `_site`, and all passed. Besides the rows above, it checked:
- no duplicate element ids;
- the app's elements are present;
- the description meta tags are correct;
- `_data/` is not published;
- variant B's script loads after the theme's scripts.

Results from the browser check (Chrome DevTools, 390×844 mobile emulation, served from the built `_site`), identical for A and B:
- ZIP 01001 shows 3 officials, and each Save link is a `blob:` URL with a `.vcf` filename.
- The vCard text is valid 3.0 with CRLF line endings.
- The site search overlay still opens.
- The body font is Lora, from the theme.
- The navbar and footer are present.
- No horizontal overflow and no console errors.

Screenshot of variant B: [variant-b-phone.png](jekyll-integration-test/variant-b-phone.png). The test data is synthetic. A Massachusetts ZIP shows an "AL" representative because of how the sample was generated, not because of a lookup error.

**Standalone file**, built by the same script from the same source plus the inlined Bootstrap 4.4.1 CSS:
- The lookup and vCards work, with no console errors.
- It has no Beautiful Jekyll styling or fonts yet; that belongs to the design item.

## Sizes and build time

Measured with a synthetic dataset in the proposed [data-design](data-design.md) schema: 535 officials with two offices each, and 33,000 ZIP keys, 10% of which have two candidates.

| Item | Raw | Gzipped |
|---|---|---|
| Dataset JSON | 2,888,985 B | 304,539 B |
| Built page, variant B (data inlined) | 2,901,840 B | 308,228 B |
| Standalone file (with Bootstrap CSS inlined) | 3,052,628 B | 331,316 B |
| *Standalone styling, upper bounds:* full Bootstrap 4.4.1 CSS | 159,515 B | 23,628 B |
| `beautifuljekyll.css` | 23,449 B | 5,073 B |
| `bootstrap-social.css` (social buttons; probably not needed) | 33,849 B | 3,873 B |
| Lora + Open Sans, Latin subset only (4 variable `woff2` files) | 177,096 B | does not compress further |

- **Real data will be somewhat larger:** HUD lists about 39–41k ZIPs, and real records have more offices.
- **Download size:** GitHub Pages serves pages gzipped (checked: `content-encoding: gzip` on www.eriksaltwell.com), so a phone downloads about 0.3 MB for the Jekyll page.
- **Fonts are the largest cost of the standalone styling.** Inlining the two theme fonts as base64 adds roughly 236 KB, about doubling what a phone downloads. The alternatives are:
  - system fonts;
  - loading Google Fonts externally, which breaks the no-external-dependencies rule for the standalone file.

  The CSS layers are small by comparison. This is for the design item to decide.
- **Build time:** the whole site built in about 1.4 s, against about 1.2 s without the page, so build time is not a concern.
- **A more compact ZIP index** (for example, short arrays instead of objects) would shrink the data a lot if size matters later. That is a data-design question, not a Jekyll one.

## Hazards and rules

1. **Liquid processes every `.html` and `.md` file that has front matter.**
   - Any `{{` or `{%` in inline JS or data becomes Liquid.
   - Lax error mode does not save you: an unknown tag is a hard error that **fails the whole site build** (variant A0). On GitHub Pages, that means no deploys at all until it is fixed.
   - A single-file page would have to wrap its JS and data in `{% raw %}`, and the build would have to refuse content that contains `{% endraw %}`.
   - The chosen variant B avoids this. Files under `assets/` with no front matter are copied untouched, and `jsonify` output is not re-parsed.
   - **Rule:** the asset files must never get front matter.
2. **`_data/*.json` is read by `SafeYAML.load_file`, not by a JSON parser** (Jekyll 3.10.0, `lib/jekyll/readers/data_reader.rb`).
   - Tested and safe: `\u` escapes, surrogate pairs, `\/`, `\n`, `\"`, `\\`, tabs, leading-zero strings such as `"01001"`, `null`, `true`, negative decimals, and `{{ }}` / `{% %}` inside strings. See [yaml-escape-sample.json](jekyll-integration-test/yaml-escape-sample.json).
   - **Exponent notation is not safe:** `1e3` becomes the string `"1e3"`.
   - **Rule:** the data script writes plain integers and decimals only. Python's `json.dumps` writes integers safely, but floats can come out in exponent form.
3. **`jsonify` does not escape `</`.** A data value containing `</script>` would end the data element early.
   - **Rule:** the data script rejects or escapes `</`.
   - `build_variants.py` asserts this for B, and escapes it as `<\/` for A and the standalone file.
4. **Name clashes with the theme:** the theme already uses ids such as `nav-search-input`.
   - **Rule:** prefix every id and class with `cc-`. The test found no duplicate ids.
5. **Privacy:** the live theme loads Google Analytics (`googletagmanager.com/gtag/js`), so the Jekyll version inherits page-view tracking; the standalone file does not. This follows the project's earlier choice not to send user data to third parties.
   - **Rule:** never put the ZIP in the URL (query string or hash) or in the page title.
   - **Rule:** the page fires no analytics events of its own.
   - The test code meets both rules: its submit handler calls `preventDefault` and never changes the URL.
6. **Local builds only:** with `JEKYLL_ENV=production` and no GitHub token, the `jekyll-github-metadata` plugin has two problems:
   - it needs `PAGES_REPO_NWO` to be set;
   - it guesses `baseurl` as `/pages/<owner>/<repo>`, which breaks the theme's asset paths.

   Build with `--baseurl ""` to match the live site. GitHub's own build is not affected.

## How the shared build produces both outputs

`build_variants.py` shows the shape the real build script can take. The same `body.html`, `congress.js`, `congress.css` and data produce two outputs.

**Jekyll output (chosen variant B).** It is laid out in a folder that mirrors the site root:
- `congress.html` containing:
  - front matter: `layout: page`, title, `subtitle`, `share-description`, `description`, `permalink`, `css:` and `js:`;
  - then `body.html`;
  - then one `<script type="application/json" id="cc-data">` holding `{{ site.data.congress | jsonify }}`.
- The data, JS and CSS files copied into `_data/` and `assets/`.

The copy script then places these four files into the owner's site checkout.

**Standalone output**, in this order:
1. an HTML skeleton;
2. the inlined theme styling layer, still to be defined by the design item;
3. `congress.css`;
4. `body.html`;
5. the data inlined, with `</` escaped;
6. `congress.js`.

The page's JS reads its data from `#cc-data` in both outputs, so it has one code path.

## Notes for other Jekyll sites

- **Front matter loading:** `css:` and `js:` front matter are Beautiful Jekyll features. In other themes, such as minima, they do nothing. A portable option is to put `<link>` and `<script src>` tags in the page body itself, which any theme renders. The page's JS has no jQuery dependency, so it can run before the theme's scripts.
- **Layout:** `layout: page` exists in most themes. If it doesn't, the user changes one front matter line.
- **Styling:** the markup uses Bootstrap 4 classes (`form-control`, `btn btn-primary`, `sr-only`). Themes without Bootstrap need a few CSS rules, which matches the owner's expectation that other site owners may need to adjust the styling.

## Open questions and untested areas

- **Where the CSS and JS tags go:** front matter is the most Beautiful-Jekyll-native option, while tags in the page body work in more themes. This is a minor choice for implementation.
- **Editable page wording was not tested.** This is the owner's nice-to-have. Making the page a `.md` file would also send the inlined `<script>` content through kramdown, which needs its own test.
- **Real data size**, once the HUD crosswalk is actually fetched.
- **What the standalone file's styling inlines** (Bootstrap subset, theme CSS, fonts): belongs to the design item.
- **Real-phone behaviour inside the theme was not retested.** The phone-import findings came from the `vcard-test` page; the blob mechanism used here is the same.

## Side note on the site (out of scope)

Three posts (`2022-06-08-unmasking-nyarlathotep.md`, `2022-11-09-dungeon-tiles.md`, `2022-12-17-dice-jails.md`) still contain leftover `{{< image ... >}}` lines, shortcode syntax left over from an earlier static-site generator that Jekyll does not understand.
- They produce Liquid warnings on every build.
- Lax mode renders them as nothing, and each sits next to a working Markdown image, so the live pages look fine (the dice-jails post was checked).
- They are harmless today, but deleting them would make build output clean, so real warnings stand out.

## Test kit

[jekyll-integration-test/](jekyll-integration-test/) holds throwaway fixtures, not production code:

| File | Purpose |
|---|---|
| `gen_sample.py OUT.json` | Synthetic dataset, sized like the real one, seeded with strings that stress Liquid, YAML and HTML |
| `src/body.html`, `src/congress.js`, `src/congress.css` | Shared source: markup, ZIP lookup and vCard blob JS, and app CSS |
| `build_variants.py DATA SITE STANDALONE_OUT [BOOTSTRAP_CSS]` | Writes variants A0, A and B into a site clone, plus the standalone file |
| `check_output.py DATA BUILT_SITE` | Byte-for-byte and round-trip checks on the built `_site` |
| `browser_check.js` | Run in a built page through Chrome DevTools `evaluate_script` (`sourcePath`). Returns a JSON report |
| `Gemfile.pages`, `Gemfile.pages.lock` | Pinned GitHub Pages environment: `github-pages` 233, Jekyll 3.10.0, Liquid 4.0.4, kramdown 2.4.0 |
| `yaml-escape-sample.json` | Escape-sequence sample used to test Jekyll's YAML reading of JSON |
| `variant-b-phone.png` | Phone-viewport screenshot of variant B inside the theme |

**Reproduce** (tested on Ubuntu 26.04 with Ruby 3.3.8):

1. Install Ruby and build tools:
   ```
   sudo apt install ruby-full build-essential zlib1g-dev
   ```
2. Clone https://github.com/erik-saltwell/eriksaltwell.com into a scratch directory, and copy `Gemfile.pages` and `Gemfile.pages.lock` into it.
3. Install the gems. `webrick`, `csv`, `base64`, `bigdecimal` and `logger` are in the Gemfile because Ruby 3.3 needs them.
   ```
   BUNDLE_GEMFILE=Gemfile.pages BUNDLE_PATH=<gem dir> bundle install
   ```
4. Generate the data and write the variants:
   ```
   python3 -I gen_sample.py sample.json
   python3 -I build_variants.py sample.json <clone> standalone.html [bootstrap.min.css]
   ```
5. Delete `congress-a0.html` from the clone. It exists only to show that the build fails; build once with it in place to see that.
6. From the clone, build the site:
   ```
   PAGES_REPO_NWO=erik-saltwell/eriksaltwell.com JEKYLL_ENV=production bundle exec jekyll build --safe --baseurl "" -d <out>
   ```
7. Run the output checks:
   ```
   python3 -I check_output.py sample.json <out>
   ```
8. Serve `<out>` locally with `python3 -m http.server`, open `/congress-a/` and `/congress-b/` with a mobile viewport, and run `browser_check.js`.
