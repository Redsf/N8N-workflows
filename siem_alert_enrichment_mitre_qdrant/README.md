# SIEM Alert Enrichment with MITRE ATT&CK

A security-operations assistant that enriches raw SIEM/Zendesk alerts with MITRE ATT&CK context — tactics, techniques, technique IDs, remediation steps, and external references — so analysts don't have to manually map alert text to the ATT&CK framework. A separate chat interface lets analysts ask ad hoc questions against the same MITRE knowledge base.

Built for SOC and incident-response teams who want triage tickets automatically tagged with structured TTP data instead of relying on an analyst's memory of the ATT&CK matrix.

## What it does

The workflow has three independent parts sharing one Qdrant knowledge base:

**Knowledge base ingestion (manual trigger):**

1. **When clicking 'Test workflow'** starts the ingest run.
2. **Pull Mitre Data From Gdrive** downloads `cleaned_mitre_attack_data.json` from Google Drive.
3. **Extract from File** parses the JSON, **Split Out** breaks the `data` array into individual technique records.
4. **Embed JSON in Qdrant Collection** (insert mode, collection `mitre`) embeds and stores each record, using **Embeddings OpenAI1** for vectors, **Default Data Loader** to read each technique's `description` field (tagging metadata with `id`, `name`, `killchain`, `external`), and **Token Splitter1** to chunk the text.

**Ticket enrichment (manual trigger, separate branch):**

1. **Get all Zendesk Tickets** fetches all tickets, and **Loop Over Items** processes them one at a time.
2. **AI Agent1** (system prompt: extract TTPs, provide remediation, cross-reference history, recommend resources) receives each ticket's `raw_subject` and `description`, powered by **OpenAI Chat Model1**, with **Qdrant Vector Store query** exposed as a retrieval tool (`mitre_attack_vector_store`) via **Embeddings OpenAI** against the same `mitre` collection. **Structured Output Parser** forces the reply into a fixed schema (`ttp_identification`, `remediation_steps`, `historical_patterns`, `external_resources`).
3. **Update Zendesk with Mitre Data** writes the alert summary and top technique ID/tactic back onto the ticket as an internal note and custom fields, then **Move on to next ticket** loops back into **Loop Over Items** to continue the batch.

**Ad hoc chat (chat trigger):**

1. **When chat message received** starts a chat session.
2. **AI Agent** answers using **OpenAI Chat Model** and **Window Buffer Memory** for conversational context, with **Query Qdrant Vector Store** as a retrieval tool (same `mitre_attack_vector_store` description) backed by **Embeddings OpenAI2** against the `mitre` collection.

Sticky notes in the canvas label these three sections: "Deploy your Vector Store" (ticket enrichment), "Embed your Vector Store" (ingestion), and "Talk to your Vector Store" (chat).

## Sample request

For the chat branch, open the chat panel on **When chat message received** and send a message such as:

```
We saw a beacon from a host to 194.180.191.64 over port 443 that looks like NetSupport RAT check-in traffic. What ATT&CK techniques does this map to?
```

The ticket-enrichment branch has no external trigger payload to send manually — **Get all Zendesk Tickets** pulls tickets directly from Zendesk. **AI Agent1**'s input template expects each item to carry `raw_subject` and `description` fields, matching what Zendesk's ticket-list response provides.

## Setup (about 20 minutes)

1. **OpenAI** — add API key credentials (currently "Marketing OpenAI") to **OpenAI Chat Model**, **OpenAI Chat Model1**, **Embeddings OpenAI**, **Embeddings OpenAI1**, and **Embeddings OpenAI2**. Note **Embeddings OpenAI** and **Embeddings OpenAI2** are both configured for `text-embedding-3-large` at 1536 dimensions — keep this consistent with whatever embedded the `mitre` collection, or retrieval will silently return poor matches.
2. **Qdrant** — add credentials (currently "Angel MitreAttack Demo Cluster") to **Embed JSON in Qdrant Collection**, **Query Qdrant Vector Store**, and **Qdrant Vector Store query**. All three point at a hardcoded collection name `mitre` — create it before running ingestion.
3. **Google Drive** — add credentials (currently "Angel Gdrive") to **Pull Mitre Data From Gdrive**, which references a hardcoded file ID for `cleaned_mitre_attack_data.json`. Replace with your own MITRE ATT&CK dataset file or update the file ID.
4. **Zendesk** — add API credentials (currently "Zendesk Demo Access") to **Get all Zendesk Tickets** and **Update Zendesk with Mitre Data**. The custom field IDs (`34479547176212` for technique ID, `34479570659732` for tactic) are hardcoded to this Zendesk instance's field schema — you'll need to create matching custom fields in your own instance and swap in the correct IDs.
5. **Run ingestion first** — trigger **When clicking 'Test workflow'** (ingestion branch) before running ticket enrichment or chat, since both depend on the `mitre` Qdrant collection being populated.
6. **AI Agent** node (top-level chat agent) has an empty main-output connection in the current wiring — its response isn't routed anywhere further, which is expected since the chat trigger renders the agent's reply directly in the n8n chat UI.
