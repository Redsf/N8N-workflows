# Real Estate Lead Capture and Auto Reply

Captures property inquiries submitted from a website form, saves each one to a CRM spreadsheet, immediately emails the prospect a confirmation, and alerts the agent team in Slack.

Built for real estate agents and brokerage teams that want every inbound lead acknowledged and logged the moment it comes in, without a person manually checking a form inbox.

## What it does

1. **New Property Inquiry** (Webhook, POST `/property-inquiry`) receives the website form submission.
2. **Structure Lead** maps the raw payload into clean fields: name, email, phone, property and message.
3. **Add Lead to CRM Sheet** appends the lead as a new row in a Google Sheet.
4. From there the flow splits two ways:
   - **Send Auto Reply to Lead** emails the prospect a thank-you message referencing the property they asked about.
   - **Notify Agent Team** posts the lead's name, email and property to a Slack channel.
5. **Confirm Inquiry** (Respond to Webhook) returns a `{"status": "received"}` JSON response to the website once the auto reply has sent.

## Sample request

Send a POST to the webhook with a body like this:

```json
{
  "name": "Alex Rivera",
  "email": "alex.rivera@example.com",
  "phone": "+1 555 0100",
  "property_id": "LST-4521",
  "message": "Interested in a viewing this weekend."
}
```

## Setup (about 10 minutes)

1. **Webhook** — point your website's inquiry form at the **New Property Inquiry** webhook URL.
2. **Google Sheets** — connect your account on **Add Lead to CRM Sheet** and point it at your own CRM sheet.
3. **Gmail** — connect an account on **Send Auto Reply to Lead** and adjust the message wording.
4. **Slack** — connect an account on **Notify Agent Team** and point it at your own agent channel.

