# n8n Workflow Portfolio

A collection of production-style n8n automations covering AI agents, RAG knowledge systems, e-commerce operations, real estate, marketing, and HR document processing. Each workflow lives in its own folder as a ready-to-import JSON file with a README explaining what it does, how it's wired, and how to configure it.

These were built as client and personal projects to solve real operational problems: recovering abandoned carts, routing leads, extracting data from invoices, answering guest and employee questions with grounded AI, and keeping teams informed without manual busywork.

## How to use a workflow

1. Open the folder for the workflow you want.
2. Read its `README.md` for what it does, the trigger, and the setup steps.
3. In n8n, go to **Workflows → Import from File** and select the `.json` file.
4. Connect the credentials listed in the workflow's README, then activate it.

Credentials are referenced by name only — no API keys, tokens, or secrets are stored in any of these files.

## Workflows

### AI Agents & RAG Knowledge Systems

| # | Workflow | Summary |
|---|----------|---------|
| 01 | [Multilingual AI Hotel Guest Assistant](multilingual_guest_assistant) | WhatsApp/Viber guest support agent that answers in the guest's language, grounded in a hotel knowledge base, with front-desk escalation. |
| 12 | [Financial Documents Assistant (Qdrant + Mistral AI)](financial_documents_assistant_qdrant_mistral) | Ingests financial PDFs into a Qdrant vector store using Mistral embeddings for retrieval-augmented Q&A. |
| 16 | [Autonomous AI Crawler](autonomous_ai_crawler) | Agent-driven web crawler that follows links autonomously and persists findings to Supabase. |
| 17 | [BambooHR AI Policies & Benefits Chatbot](bamboohr_policies_benefits_chatbot) | HR chatbot that answers policy and benefits questions by combining a vector store with live BambooHR employee data. |
| 18 | [RAG-Powered Internal Knowledge Chatbot](rag_internal_knowledge_chatbot) | Nightly sync from Notion and Google Drive into Pinecone, with a Slack-triggered Q&A agent. |
| 21 | [HR & IT Helpdesk Chatbot with Audio Transcription](hr_it_helpdesk_chatbot_audio_transcription) | Telegram helpdesk bot that transcribes voice notes and answers from a PGVector knowledge base. |
| 28 | [Customer Service Agent with RAG](customer_service_agent_rag) | Reads incoming support emails and drafts grounded replies from a Supabase vector store. |
| 35 | [RAG Model with Supabase](rag_model_supabase) | Google Drive documents indexed into Supabase, queried through a chat-triggered agent. |
| 36 | [RAG Model with Supabase & Postgres](rag_model_supabase_postgres) | Adds Telegram as a second interface and Postgres-backed chat memory on top of a Supabase RAG pipeline. |

### Customer Communication & Support

| # | Workflow | Summary |
|---|----------|---------|
| 14 | [WhatsApp AI Sales Agent](whatsapp_ai_sales_agent) | Pinecone-grounded sales agent on WhatsApp with calendar booking and conversation memory. |
| 26 | [Cold Email Outreach Automation](cold_email_outreach_automation) | Batches prospects from a sheet, personalizes outreach with an LLM, and sends with rate limiting. |
| 31 | [Gmail AI Auto-Reply Agent](gmail_ai_auto_reply_agent) | Watches a Gmail inbox and drafts context-aware replies automatically. |
| 32 | [Gmail Customer Support Agent](gmail_customer_support_agent) | Triages and answers customer support emails with an LLM agent and conversation memory. |

### E-commerce & Operations

| # | Workflow | Summary |
|---|----------|---------|
| 02 | [Vision AI Receipt & Document Verification](vision_receipt_verification) | Validates receipt/invoice images against expected booking values with GPT-4o Vision and routes exceptions for review. |
| 03 | [Abandoned Cart Recovery Engine](abandoned_cart_recovery_engine) | Shopify checkout-abandonment recovery sequence with timed follow-ups across email and WhatsApp. |
| 07 | [Order & Fulfillment Sync Automation](order_fulfillment_sync_automation) | Syncs new Shopify orders to a database and polls delivery status, notifying customers and staff. |
| 10 | [Ecommerce Order Notifier & Logger](ecommerce_order_notifier_logger) | Webhook-driven order intake that logs to Google Sheets and alerts the team on Slack. |
| 29 | [Daily Product Pricing Monitor](daily_product_pricing_monitor) | Scheduled competitor price checks with Slack/email alerts when prices move outside range. |
| 37 | [Real-Time Inventory & Auto-Reorder Pipeline](realtime_inventory_auto_reorder_pipeline) | Monitors stock levels and uses an AI agent to decide and trigger reorders before stockouts. |

### Real Estate & Appointment Scheduling

| # | Workflow | Summary |
|---|----------|---------|
| 06 | [Appointment Reminder Sender](appointment_reminder_sender) | Daily scheduled reminders pulled from a bookings sheet, sent by email with a Slack digest. |
| 08 | [Real Estate Lead Capture & Auto Reply](real_estate_lead_capture_auto_reply) | Webhook intake for property inquiries with instant auto-reply and CRM logging. |
| 09 | [Appointment Reminder & No-Show Killer](appointment_noshow_killer) | WhatsApp/SMS reminder flow with confirmation tracking to cut no-show rates. |
| 20 | [Real Estate Lead Capture and Route](real_estate_lead_capture_and_route) | Qualifies and routes inbound property leads to the right agent with validation and rejection handling. |

### Marketing, Content & Growth

| # | Workflow | Summary |
|---|----------|---------|
| 04 | [Negative Review Monitor](negative_review_monitor) | Polls review sources on a schedule and alerts the team the moment a negative review appears. |
| 05 | [AI Review & Reputation Manager](ai_review_reputation_manager) | LLM-drafted responses to incoming reviews, batched hourly with Slack approval routing. |
| 11 | [Automated Client Ad Reporting](automated_client_ad_reporting) | Weekly ad-performance pull, summarized by an LLM, and emailed to clients automatically. |
| 13 | [Hacker News "Who is Hiring" Scraper](hacker_news_hiring_scraper) | Extracts and filters relevant job listings from the monthly HN hiring thread into Airtable. |
| 19 | [AI Content Repurposing & Social Publishing](ai_content_repurposing_social_publishing) | Turns one submitted piece of content into multiple platform-ready posts and tracks weekly performance. |
| 22 | [SEO & Competitor Intelligence Pipeline](seo_competitor_intelligence_pipeline) | Weekly SEO and competitor data pull, summarized by an LLM and delivered by email. |
| 24 | [AI LinkedIn Content Machine](ai_linkedin_content_machine) | Sources trending topics via Apify/SerpAPI and drafts and publishes LinkedIn posts with AI. |
| 25 | [AI Newsletter Generator (RSS → Email)](ai_newsletter_generator_rss_to_email) | Aggregates RSS feeds, curates and writes a newsletter draft, and emails it out. |
| 27 | [Comment Responder for LinkedIn](linkedin_comment_responder) | Scheduled scan of LinkedIn post comments with AI-drafted replies logged for review. |
| 34 | [LinkedIn Post Scraper](linkedin_post_scraper) | Form-triggered LinkedIn scraping and AI analysis pipeline with results written to Google Sheets. |

### HR & Document Automation

| # | Workflow | Summary |
|---|----------|---------|
| 15 | [Automated Invoice & Document Processing Pipeline](automated_invoice_document_processing) | Extracts structured data from emailed invoices with an LLM and writes it to a database. |
| 23 | [AI Document & Invoice Extraction (Google Drive)](ai_document_invoice_extraction_google_drive) | Watches a Google Drive folder and extracts invoice data with GPT into Google Sheets. |
| 30 | [AI Employee Onboarding Automation](employee_onboarding_automation) | Form-triggered onboarding that generates welcome content, provisions access requests, and notifies HR/IT/manager. |
| 33 | [Job Application CV Processing Workflow](cv_processing_workflow) | Parses submitted CVs with an LLM, scores candidates, and logs structured results. |

## Stack

Built primarily on **n8n**, with LLM providers (OpenAI, Groq, Google Gemini, Mistral), vector stores (Pinecone, Supabase, Qdrant, PGVector), and integrations spanning Shopify, Gmail, Slack, WhatsApp, Telegram, Google Workspace, Notion, Airtable, and BambooHR.

## License

Released under the [MIT License](LICENSE). Workflows are shared as reference implementations — swap in your own credentials, sheet IDs, and endpoints before running them against production data.
