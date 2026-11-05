# Analyze Existing Site Design: intent

## Intended outcome

Understand and document the design system of the owner's existing Jekyll personal site, eriksaltwell.com. The site uses the Beautiful Jekyll 6.0.1 theme, and its source is https://github.com/erik-saltwell/eriksaltwell.com.

Capture enough of that design to guide building a Congressional Contact page that feels cohesive and consistent with the existing site.

The existing site is the design reference. Its actual styles, components and customizations remain to be examined. This document records the intended analysis and the decisions it builds on, not findings about the theme.

## Settled context from the Jekyll integration research

The [Research Jekyll Integration](../research-jekyll-integration/) item (complete) settled how the page is delivered. Its findings are in [research/jekyll-integration.md](../../research/jekyll-integration.md). This item builds on these owner decisions; it does not revisit them.

- **One shared source builds both outputs.** The standalone single file and the Jekyll version share the same markup, CSS and JS source parts, assembled by a build script.
- **Same markup in both.** The page uses the theme's Bootstrap 4.4.1 and Beautiful Jekyll classes (for example `form-control`, `btn btn-primary`, `sr-only`). App-specific ids and classes are prefixed `cc-`.
- **Jekyll version.** The page uses `layout: page`, so the site's navbar, avatar, title and subtitle header, footer, fonts and colours come from the theme automatically. The page adds only its own small app stylesheet (`assets/css/congress.css`).
- **Standalone version.**
  - Uses the site's look, but inlines only the styles the page actually uses.
  - Collects colours and fonts into CSS variables at the top so self-hosters can restyle it.
  - Has no links to external stylesheets, scripts or similar presentation dependencies.

## Two delivery contexts

- **Jekyll-based page:** confirm which theme styles and components the page gets for free. Identify any app-specific styling it still needs to look native, rather than reimplementing the theme.
- **Standalone page:** work out what must be inlined to reproduce the site's look without Jekyll or the theme's CDNs. Then decide how that styling layer and its CSS variables are organised so the build script can add it to the shared markup.

## Questions for the analysis

- What are the site's actual design tokens? This covers the colours set in `_config.yml` (`page-col`, `text-col`, `link-col`, `hover-col`, `navbar-col` and others), typography, spacing and components, and any owner customizations to Beautiful Jekyll.
- Which Bootstrap 4.4.1 and `beautifuljekyll.css` rules does the page's markup actually use, and roughly how large is that subset? The research measured upper bounds: full Bootstrap CSS is 159,515 B (23,628 B gzipped), and `beautifuljekyll.css` is 23,449 B (5,073 B gzipped).
- **Fonts in the standalone file (open; left to this item by the research).** The theme uses the Lora and Open Sans Google Fonts. The research estimated roughly 236 KB for inlining them. The design analysis corrected this to about 56 KB over the network for the two files the page needs (see [design_notes/existing-site-design.md](../../design_notes/existing-site-design.md)). Loading them externally breaks the no-external-dependencies rule. System fonts avoid both costs but look less like the site. Recommend an option and let the owner choose.
- Should the standalone file reproduce the theme's page header (title and subtitle styling) or other chrome, given that it has no navbar or footer?
- Which values belong in the standalone file's CSS variables so a self-hoster can restyle it easily?
- Does the page need any app-specific components beyond the theme's? Examples are a results list, a candidate chooser for ZIPs that span several districts, and save-contact buttons. How should they be styled to look native?

## Constraints

> **Superseded in part (owner decisions, 2026-11-05; see the design notes):**
> - The standalone file loads its fonts from Google Fonts, an exception to its no-external-dependencies rule.
> - The page keeps the stock theme and Bootstrap colours, accepting their AA contrast failures.


- **Phone first.** The primary user is on a phone, so the styling should not add much download weight.
- **Accessibility.** The page must meet WCAG AA contrast and focus states. An earlier design-gate pass on the test markup checked unstyled HTML only. With the theme's styling applied, the stock Bootstrap button, input border and focus ring fail AA (see the design notes).
- **No visitor tracking.** Do not add any analytics or third-party requests. The Jekyll version inherits the theme's Google Analytics, and the standalone file must not add any.

## Deliverable and related work

Save the design analysis in the root-level [design_notes directory](../../design_notes/), with enough detail to guide later page development in both delivery contexts.

The [Define User Flow](../define-user-flow/) item separately defines the page's behaviour. This item covers only visual design and styling.

This intent is captured for later work. Analysis and implementation have not begun.
