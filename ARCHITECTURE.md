# Architecture Diagrams — Flagship Workflows

Visual reference for the highest-impact workflows in this portfolio. Diagrams are Mermaid
flowcharts — they render natively on GitHub, no images or external tools required.

Each diagram reflects the **actual node graph** of the referenced workflow file, not a
simplified marketing version.

---

## 1. Abandoned Cart Recovery Engine
[`abandoned_cart_recovery_engine/03_abandoned_cart_recovery_engine.json`](abandoned_cart_recovery_engine)

```mermaid
flowchart LR
    A[Shopify Trigger\nCheckout Abandoned] --> B[Wait 15 Min]
    B --> C[HTTP Request\nCheck Order Status]
    C --> D{Order\nCompleted?}
    D -->|yes| E[No-Op\nCart Converted]
    D -->|no| F[Set\nBuild Recovery Message]
    F --> G[Gmail\nSend Recovery Email]
    F --> H[WhatsApp\nSend Recovery Message]
    A -.error.-> I[Error Trigger]
    I --> J[Slack\nNotify Ops]
```

**What it does:** Waits 15 minutes after a Shopify checkout is abandoned, re-checks order status,
and if still incomplete, fires a recovery message on both email and WhatsApp. Converted carts are
left alone — no message sent to someone who already bought. Errors alert ops directly in Slack
instead of failing silently.

---

## 2. Order & Fulfillment Sync
[`order_fulfillment_sync_automation/07_order_fulfillment_sync_automation.json`](order_fulfillment_sync_automation)

```mermaid
flowchart TD
    A[Shopify Trigger\nNew Order Placed] --> B[HTTP Request\nBook Courier]
    B --> C{Booking\nSuccess?}
    C -->|yes| D[HTTP Request\nUpdate Order Tracking]
    D --> E[Gmail\nNotify Customer]
    D --> F[WhatsApp\nNotify Customer]
    C -->|no| G[Slack\nFlag Ops - Booking Failed]

    H[Schedule Trigger\nPoll Delivery Status] --> I[Postgres\nGet In-Transit Orders]
    I --> J[Split In Batches\nCheck Each Shipment]
    J --> K[HTTP Request\nGet Courier Status]
    K --> L{Stage\nChanged?}
    L -->|yes| M[WhatsApp\nNotify Stage Update]
    M --> N[Postgres\nUpdate Shipment Record]
    L -->|no| J
    J --> O[No-Op\nPolling Done]
```

**What it does:** Two loops in one workflow. Loop 1 books a courier the moment a Shopify order
lands and notifies the customer on success (or flags ops on failure). Loop 2 runs on a schedule,
polls every in-transit shipment's courier status from Postgres, and pushes a WhatsApp update only
when the delivery stage actually changes — no spam on every poll.

---

## 3. Cold Email Outreach Automation
[`cold_email_outreach_automation/26_cold_email_outreach_automation.json`](cold_email_outreach_automation)

```mermaid
flowchart TD
    A[Google Sheets\nGet All Leads] --> B[Split In Batches\nOne Lead at a Time]
    B --> C{Status\nPending?}
    C -->|yes| D[AI Agent\nPersonalize Email\nOpenAI Chat Model]
    D --> E[Gmail\nSend Cold Email]
    E --> F[Google Sheets\nUpdate: Email 1 Sent]
    F --> G[Wait 2 Min]
    G --> H[Gmail\nCheck for Reply]
    H --> I{Replied or\nNot Replied?}
    I -->|replied| J[Google Sheets\nUpdate: Replied]
    I -->|no reply| K[AI Agent\nGenerate Follow-up\nOpenAI Chat Model]
    K --> L[Gmail\nSend Follow-up Email]
    L --> M[Google Sheets\nUpdate: Follow-up Sent]
    A -.error.-> N[Error Trigger]
    N --> O[Slack\nError Alert]
```

**What it does:** Pulls leads from Sheets one at a time, has an AI agent write a personalized
first-touch email, sends it, then checks for a reply after a wait window. No reply → a second AI
agent drafts a follow-up automatically. Every state change is logged back to Sheets so the lead
list itself is always the source of truth.

---

## 4. CV / Applicant Screening Pipeline
[`cv_processing_workflow/33_cv_processing_workflow.json`](cv_processing_workflow)

```mermaid
flowchart LR
    A[Form Trigger\nOn Form Submission] --> B[Google Drive\nUpload Resume]
    B --> C[Google Drive\nDownload File]
    C --> D[Extract From File\nParse Resume Text]
    D --> E[AI Agent\nStructured Output Parser\nOpenAI Chat Model]
    E --> F[Gmail\nSend Confirmation Email]
    E --> G[Google Sheets\nAppend Row]
```

**What it does:** A candidate submits a resume via form, it's stored in Drive, text is extracted
from the file, and an AI agent scores/evaluates it against a **structured output schema** — so
results are consistent, sortable fields in a sheet, not paragraphs a recruiter has to re-read.
Candidate gets an automatic confirmation the moment they apply.

---

## 5. AI Voice Chatbot (ElevenLabs, RAG-grounded)
[`voice_chatbot_elevenlabs_restaurants/75_voice_chatbot_elevenlabs_restaurants.json`](voice_chatbot_elevenlabs_restaurants)

```mermaid
flowchart TD
    subgraph Ingestion [One-time / scheduled ingestion]
        G1[Google Drive\nGet Folder] --> G2[Google Drive\nDownload Files]
        G2 --> G3[Document Loader\n+ Token Splitter]
        G3 --> G4[Embeddings OpenAI]
        G4 --> G5[(Qdrant Vector Store)]
    end

    subgraph Live [Live call handling]
        A[Webhook\nListen] --> B[AI Agent\n+ Window Buffer Memory]
        B --> C[Vector Store Tool]
        C --> G5
        B --> D[OpenAI Chat Model]
        B --> E[Respond to ElevenLabs]
        E --> A
    end
```

**What it does:** Two halves. The ingestion half indexes source documents into Qdrant as
embeddings. The live half is the actual voice loop: ElevenLabs sends the transcribed caller
input to a webhook, an AI agent with conversation memory retrieves grounded context from the
vector store tool, generates a response, and hands it back to ElevenLabs for speech synthesis.

Full strategy write-up, reliability guardrails, and results for the production version of this
build: **[AI Voice Agent case study →](https://github.com/Redsf/Redsf/blob/main/case-studies/ai-voice-agent-homeware.md)**

---

*Diagrams are generated from each workflow's actual node graph and updated as workflows change.*
