# Intent: Research contact data source and freshness

## Outcome

Find an answer to this question, with enough supporting evidence that the project can make a decision:

> Where does the official and contact data (phone numbers, web forms, email, office addresses) come from, and how does a static page with no backend or API key keep it current?

## Background

This is one of three open questions recorded in [.agent_context.md](../../.agent_context.md) for the Congressional Contact project: a static web page, ideally one file, with no backend, accounts, or API keys. It lets a phone user save their two senators and their House representative as full-detail contacts. Contact details change when members change, so freshness matters.

## Scope

Answering the question above. Choosing the final design and building it are separate work.

The user clarified that matching is assumed complete. Research must establish how to build a VCF, dynamically or statically, containing DC and local office phone numbers where available, email addresses where published, and links to forms for feedback on specific issues. Distinguish real mailboxes from web forms and legislative feedback from other office services.

## Acceptance

A written answer to the question that names its sources, states the practical options and their tradeoffs against the project's constraints, and notes anything that stayed uncertain.
