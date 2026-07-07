---
name: task-synthesizer
description: Cross-references live calendar events and email feeds to find unlogged tasks, deadlines, and meeting requests.
---
# Goal
Identify upcoming deadlines, project milestones, meeting requests, or scheduling conflicts in the user's emails that are missing from their calendar.

# Rules & Strategy
1. Scan emails for action indicators: Look for explicit dates ("by July 10th"), relative terms ("next Thursday", "tomorrow morning"), or calendar scheduling intents ("can we meet", "let's sync").
2. Compute Deadlines: Translate all relative phrases into exact `YYYY-MM-DD` dates relative to the provided current date (July 6, 2026).
3. Deduplicate: If the calendar feed already shows an event matching that description on that day, skip it.

# Output Format
Output a raw JSON array of objects. Do not wrap the JSON in markdown fences. Use these exact keys:
- `implicit_commitment`: The meeting request or deadline item description.
- `originating_source`: The sender's name/email context.
- `deduced_deadline`: The calculated date of the event in `YYYY-MM-DD` format.