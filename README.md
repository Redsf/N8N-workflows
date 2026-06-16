# n8n Hospitality Automation Workflows

Two production grade n8n workflows built for AI driven hospitality operations: multilingual guest support and Vision AI document verification. Both use messaging channels, Google Sheets as a live database, and real error handling throughout.

## Workflows

### 1. [Multilingual AI Hotel Guest Assistant](./multilingual_guest_assistant)

Answers WhatsApp and Viber messages in the guest's own language (Greek, English, Bulgarian and more), grounds answers in a hotel knowledge base, escalates sensitive requests to the front desk, and logs every exchange to Google Sheets. Built on an AI Agent with per guest memory and structured output.

### 2. [Vision AI Receipt & Document Verification](./vision_receipt_verification)

Reads receipts and invoices with GPT 4o Vision, validates totals and currency against the booking within a tolerance, auto approves clean documents, flags the rest for review, and logs every result. Includes a dedicated error path so a failed vision call is never silently dropped.

## How to import

1. In n8n, choose Import from File and select a workflow JSON.
2. Open any node with a credential warning and connect your own account. Placeholders are marked REPLACE.
3. Set your OpenAI key, Slack channels, Google Sheet id, and the messaging tokens.
4. Point your channel webhooks at the production URL of the webhook trigger.

Each folder has its own README with the full node by node breakdown, a sample request, setup steps, and error handling notes.
