# Analyze Existing Site Design: intent

## Intended outcome

Understand and document the design system used by the owner's existing Jekyll personal site, eriksaltwell.com, which uses the Beautiful Jekyll 6.0.1 theme. Its source is https://github.com/erik-saltwell/eriksaltwell.com. Capture enough of that design to guide construction of a Congressional Contact page that feels cohesive and consistent with the existing site.

The existing site is the design reference. Its actual styles, components, and customizations remain to be examined; this document records the intended analysis, not findings about the theme.

## Two delivery contexts

- **Jekyll-based page:** identify how the new page can reuse the existing site's design system, including applicable styles and components, rather than reimplementing it independently.
- **Standalone page:** identify how to preserve the same visual consistency in a page that works independently of Jekyll. Its styling and JavaScript must be included directly in the page, with no links to external stylesheets, external JavaScript files, or similar presentation dependencies.

How to achieve design reuse and standalone packaging remains an investigation question. No particular implementation or source-sharing approach has been selected.

## Deliverable and related work

Save the design analysis in the root-level [design_notes directory](../../design_notes/), with enough detail to guide later page development in both delivery contexts.

The [Research Jekyll Integration work item](../research-jekyll-integration/) separately investigates hosting and rendering the functional page within Jekyll, and how one shared source builds both the Jekyll version and the standalone file. This item's focus is the existing site's design system and how the new page can use it consistently.

This intent is captured for later work; analysis and implementation have not begun.
