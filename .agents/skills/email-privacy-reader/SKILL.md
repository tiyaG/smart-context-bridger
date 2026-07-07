---
name: email-privacy-reader
description: Scans email text structures to safely redact high-risk PII before it reaches processing engines.
---
# Goal
Enforce a data protection shield. Locate passwords, API keys, or credit card digits and strip them from the data payload.

# Instructions
1. Review the text objects supplied within the email bodies.
2. Locate credit card configurations (e.g., strings matching multi-digit blocks like 4111-2222-3333-4444).
3. Overwrite those exact substrings with a clear placeholder token: `[REDACTED_BY_PRIVACY_SKILL]`.
4. Return the cleaned output string while keeping the remaining surrounding conversation untouched.
