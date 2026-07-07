# Real Estate Lead Capture and Auto Reply

Captures property inquiries from a website form, validates and cleans the data, upserts each lead into a CRM Google Sheet without creating duplicate rows on repeat inquiries, and routes hot leads to a senior agent for faster follow-up. The website gets an immediate confirmation or rejection response, and the whole workflow is wrapped in error alerting.

Built for real estate agents and brokerage teams who want inbound property inquiries triaged and acknowledged instantly, with urgent buyers surfaced to a senior agent instead of sitting in a shared inbox.

## What it does

1. **New Property Inquiry** is a webhook that receives the inquiry form submission.
2. **Structure Lead** maps the raw payload into named fields: name, email, phone, property, message, source (defaults to "website"), and submitted_at timestamp.
3. **Validate Lead Input** checks that name and phone are non-empty and email matches a valid email pattern.
   - **Invalid path:** **Format Rejection Reason** builds a human-readable reason (missing name, invalid email, or missing phone) and **Reject Inquiry** responds to the webhook with HTTP 400 and the rejection reason.
   - **Valid path:** continues to normalization.
4. **Normalize Lead Data** (Code node) lowercases the email and strips non-numeric characters from the phone number.
5. **Classify Lead Interest** (Code node) scans the message and property fields for urgency keywords (luxury, urgent, cash buyer, today, asap, pre-approved) and sets `lead_priority` to `high` or `standard`.
6. **Upsert Lead in CRM Sheet** writes the lead to Google Sheets, matched on email so a repeat inquiry from the same person updates the existing row instead of duplicating it.
7. **Is High Priority Lead** branches on the priority flag:
   - **High priority:** **Send Priority Auto Reply** emails the lead a faster-turnaround message, then **Notify Senior Agent** posts an urgent alert to Slack.
   - **Standard:** **Send Auto Reply to Lead** sends the regular acknowledgement email, then **Notify Agent Team** posts a standard alert to Slack.
8. **Merge Notification Branches** waits for whichever path ran and passes a single stream forward.
9. **Confirm Inquiry** responds to the original webhook call with a success JSON payload.
10. **Workflow Error Trigger** catches any unhandled failure anywhere in the workflow, and **Alert Team on Workflow Failure** posts the error message to Slack.

## Sample request

Send a POST to the webhook with a body like this:

```json
{
  "name": "Jordan Lee",
  "email": "jordan.lee@example.com",
  "phone": "+1-555-0142",
  "property_id": "MLS-4471",
  "message": "Cash buyer, looking to move fast on this one.",
  "source": "website"
}
```

The response is either `{"status": "received"}` on success or `{"status": "rejected", "reason": "..."}` with HTTP 400 if name, email, or phone fail validation.

## Setup (about 15 minutes)

1. **Webhook** — point your website's inquiry form at the production URL of **New Property Inquiry**.
2. **Google Sheets** — connect your account in **Upsert Lead in CRM Sheet**. The document id is set to the placeholder `REPLACE_WITH_YOUR_CRM_SHEET` — point it at your own CRM sheet and confirm it has Name, Email, Phone, Property, Message, Source, Priority, and Submitted At columns.
3. **Gmail** — connect your account in **Send Auto Reply to Lead** and **Send Priority Auto Reply**, and edit the message wording to match your brand voice.
4. **Slack** — connect your account in **Notify Agent Team** (channel "agent-team"), **Notify Senior Agent** (channel "senior-agents"), and **Alert Team on Workflow Failure** (channel "workflow-alerts"). All three currently point at the same underlying channel ID — split them into distinct channels as needed for your workspace.

## Error handling

A dedicated **Workflow Error Trigger** catches any failure at any step and **Alert Team on Workflow Failure** posts the failing error message to Slack, so a broken CRM write or a rejected email send doesn't go unnoticed. Invalid form submissions are also handled gracefully with a specific 400 rejection reason rather than a silent failure.
