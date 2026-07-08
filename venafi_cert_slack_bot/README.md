# Venafi Cloud Slack Cert Bot

A Slack-native certificate request system that lets employees request a TLS certificate through a Slack modal, automatically screens the requested domain through VirusTotal, and either auto-issues the certificate via Venafi TLS Protect Cloud or routes it to a security team channel for manual approval with an AI-generated risk summary attached.

Built for security/SecOps teams who want to stop fielding ad-hoc "can I get a cert for X" requests in tickets or DMs, and instead give requesters a self-service modal that only escalates to a human when a domain actually looks risky.

## What it does

1. **Webhook** receives every Slack Events/Interactivity API callback (`POST /venafiendpoint`) and **Parse Webhook** lifts the Slack `payload` into a usable `response` object.
2. **Route Message** (switch) branches on the interaction type:
   - `request-certificate` callback_id → **Respond to Slack Webhook - Vulnerability** → **Venafi Request Certificate** opens the "Request New Certificate" Slack modal (domain name, validity period, optional note).
   - `view_submission` (modal submit) → **Close Modal Popup** closes the popup, then fans out to **Extract Fields** (domain/validity/note), **Get Slack User ID**, and **Get Slack Team ID** in parallel.
   - `block_actions` (button click) → **Respond to webhook success** → **Manual Issue Certificate** → **Venafi TLS Protect Cloud1** issues the certificate for the manual-approval path, then **Send Auto Generated Confirmation1** posts confirmation to Slack.
3. On the submission path, **Get Slack User ID** calls the **Translate Slack User ID to Email** sub-workflow ("Slack ID to Email") and **Get Slack Team ID** calls the **Execute Workflow** sub-workflow ("Slack Team ID to Name") in parallel; both results are joined by **Merge User and Team Data**.
4. **Extract Fields** feeds **VirusTotal HTTP Request**, which queries `virustotal.com/api/v3/domains/{domain}`. **Summarize output to save on tokens** trims the response before it's joined with the requester/team data in **Merge Requestor and VT Data**.
5. **Auto Issue Certificate Based on 0 Malicious Reports** (if) checks `last_analysis_stats.malicious <= 0`:
   - **True → Auto Issue Certificate** → **Venafi TLS Protect Cloud** generates the CSR and issues the cert, then **Send Auto Generated Confirmation** posts the result to Slack.
   - **False → Generate Report For Manual Approval** → **OpenAI** (GPT-4o-mini) summarizes the VirusTotal findings into a Low/Medium/High risk rating and recommendation, then **Send Message Request for Manual Approval** posts a formatted Slack block message (team, requester, VT stats, AI notes) with a "Submit for Approval" button to a fixed security channel.

## Sample request

The trigger is a raw webhook consumed by Slack's Events/Interactivity API, so the "request" is whatever Slack posts. A modal submission arrives roughly as:

```json
{
  "body": {
    "payload": {
      "type": "view_submission",
      "trigger_id": "1234567890.1234567890.abcdef",
      "user": { "id": "U01ABCDEF" },
      "team": { "id": "T01ABCDEF" },
      "view": {
        "callback_id": "certificate_request_modal",
        "state": {
          "values": {
            "domain_name_block": { "domain_name_input": { "value": "example.com" } },
            "validity_period_block": { "validity_period_select": { "selected_option": { "value": "P1Y" } } },
            "optional_note_block": { "optional_note_input": { "value": "Needed for staging rollout" } }
          }
        }
      }
    }
  }
}
```

## Setup (~30 minutes)

1. **Slack app** — create a Slack app with Events API and Interactivity enabled, pointed at this workflow's **Webhook** node (`/venafiendpoint`). Add a `slackApi` credential to **Venafi Request Certificate**, **Send Auto Generated Confirmation**, **Send Auto Generated Confirmation1**, and **Send Message Request for Manual Approval**.
2. **Venafi TLS Protect Cloud** — add a `venafiTlsProtectCloudApi` credential to **Venafi TLS Protect Cloud** and **Venafi TLS Protect Cloud1**. Both nodes hardcode an `applicationId` and `certificateIssuingTemplateId` — replace these GUIDs with the ones from your own Venafi environment. Automatic CSR generation also requires an active VSatellite deployment.
3. **VirusTotal** — add a `virusTotalApi` credential to **VirusTotal HTTP Request**. The node currently has an API key hardcoded directly in the header parameters (`X-Apikey`) instead of using the credential — replace it with your own key or wire it through the credential before deploying.
4. **OpenAI** — add an API key to the **OpenAI** node (GPT-4o-mini) used to summarize VirusTotal results into a risk rating.
5. **Sub-workflows** — **Translate Slack User ID to Email** and **Execute Workflow** call two separate companion workflows by hardcoded ID ("Slack ID to Email" `afeVlIVyoIF8Psu4` and "Slack Team ID to Name" `ZIl9VdWh7BiVRRBT`). These aren't included here; you'll need to build or re-link equivalents that accept a Slack user/team ID and return name/email/avatar, or update the `workflowId` values to point at your own.
6. **Hardcoded Slack channel** — **Send Message Request for Manual Approval** posts to a fixed channel ID (`C07MB8PGZ36`); update it to your SecOps channel.
7. The risk threshold (`malicious <= 0`) in **Auto Issue Certificate Based on 0 Malicious Reports** is a starting point — tune it to your organization's risk tolerance.
