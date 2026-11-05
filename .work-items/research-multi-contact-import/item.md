---
name: "Research multi-contact import on iOS and Android"
status: complete
---

# Research multi-contact import on iOS and Android

Research item: find an answer to the question in [intent.md](intent.md).

## Completion note

Completed 2026-11-05. The question in [intent.md](intent.md) is answered in [findings.md](findings.md), with a copy in `research/multi-contact-import-findings.md`.

- **Answer:** multi-contact import works on Android but not on iPhone Safari, which shows only the first card. The Web Share API is unusable on Android.
- **Decision (user):** one uniform flow on both platforms: a browser-built vCard per official with a save link next to each person (three taps).
- **Verification:** desk research plus tests on one iPhone (iOS 18.7, Safari) and one Android phone (Chrome 156, Android 10), using a temporary GitHub Pages page that has since been removed. Not tested: iPhone Files, Messages or Mail routes, a single-contact blob on Android, Samsung's Contacts app, and tap counts on Android.
- **Test files:** kept in `research/vcard-test/`.
