# API Schema Extractor Agent

A self-driving research pipeline that takes a list of software/service names in a Google Sheet and produces a structured JSON API schema file for each one — no manual digging through vendor documentation required. It works through three stages (research, extraction, generation), tracks progress per row in the sheet as a lightweight state machine, and calls itself as a sub-workflow to process each stage's queue.

Built for teams building integrations or AI agents who need a fast, repeatable way to turn "here's a list of SaaS tools we use" into machine-readable API schemas they can feed into other automations.

## What it does

The workflow is triggered by **When clicking 'Test workflow'**, which reads the shared control sheet and walks all three stages in sequence during a single run:

1. **Get All Research** pulls rows where "Stage 1 - Research" is blank; **All Research Done?** loops via **For Each Research...** until empty. **Research Event** builds a per-row payload and **Research** invokes this same workflow (`$workflow.id`) as a sub-workflow, routed by **EventRouter** to the "research" branch.
2. Research branch: **Web Search For API Schema** (Apify Google-search actor) finds candidate pages, **Results to List** / **Remove Dupes** / **Filter Results** clean the SERP, **Scrape Webpage Contents** (Apify web-scraper) pulls page bodies, and **Has API Documentation?** (a **Google Gemini Chat Model** text classifier) keeps only real API docs. **Set Embedding Variables** → **For Each Document...** → **Content Chunking @ 50k Chars** → **Recursive Character Text Splitter1** / **Default Data Loader** chunk the text, and **Store Document Embeddings** (Qdrant, via **Embeddings Google Gemini**) saves it to the `api_schema_crawler_and_extractor` collection. **Research Result** / **Research Error** write "ok"/"error" back to the sheet.
3. **Get All Extract** pulls rows where research is "ok" but extraction is blank; **For Each Extract...** loops, and **Extract Event** + **Extract** re-enter the sub-workflow's "extract" branch.
4. Extract branch: **Identify Service Products** (LLM via **Google Gemini Chat Model2**) names the service's products from vector search results, **Extract API Templates** turns each into an API-specific question, **Search in Relevant Docs1** (Qdrant, top 20) retrieves matching chunks, and **Extract API Operations** (an Information Extractor backed by **Google Gemini Chat Model1**) pulls structured `{resource, operation, method, url, description}` records. **Append Row** writes them to the "Extracted API Operations" tab; **Extract Result** / **Extract Error** update row status.
5. **Get All Generate** pulls rows where both prior stages are "ok" and output is blank; **For Each Generate...** loops, and **Generate Event** + **Generate** re-enter the "generate" branch: **Get API Operations** reads all extracted rows for the service, **Contruct JSON Schema** (Code node) groups them by resource into one schema object, and **Upload to Drive** saves it to Google Drive. **Generate Result** / **Generate Error** record the outcome.

Sticky notes in the workflow label the three stages and their sub-workflow sections directly (e.g. "Stage 1 - Research for API Documentation", "Stage 2 - Extract API Operations From Documentation", "Stage 3 - Generate Custom Schema From API Operations").

## Sample input

There's no external trigger — the workflow reads its queue from a Google Sheet named "API Schema Crawler & Extractor" (tab `Sheet1`) with columns `Service`, `Website`, `Stage 1 - Research`, `Stage 2 - Extraction`, `Stage 3 - Output File`, `Output Destination`. A new row to process looks like:

```
Service: Formstack
Website: https://www.formstack.com/
Stage 1 - Research: (blank)
Stage 2 - Extraction: (blank)
Stage 3 - Output File: (blank)
```

The repo ships pinned test data on **Execute Workflow Trigger** matching this shape: `{"data": {"url": "https://www.formstack.com/", "service": "Formstack", "collection": "api_schema_crawler_and_extractor", "row_number": 2}, "eventType": "research"}`.

## Setup (about 30 minutes)

1. **Apify** — add generic HTTP auth credentials to **Web Search For API Schema** (Google search actor) and **Scrape Webpage Contents** (web-scraper actor).
2. **Google Gemini** — add API credentials to **Google Gemini Chat Model / 1 / 2** and **Embeddings Google Gemini / 1 / 2**.
3. **Qdrant** — add credentials to **Store Document Embeddings** and **Search in Relevant Docs / 1**, and create the `api_schema_crawler_and_extractor` collection in advance.
4. **Google Sheets** — add credentials to every Sheets node (**Get All Research/Extract/Generate**, the **Pending/Result/Error** nodes per stage, **Get API Operations**, **Append Row**). All point at a hardcoded spreadsheet ID — swap it for your own sheet with matching column names (`Service`, `Website`, `Stage 1 - Research`, `Stage 2 - Extraction`, `Stage 3 - Output File`) and an `Extracted API Operations` tab.
5. **Google Drive** — add credentials to **Upload to Drive**, which targets a hardcoded folder ID; point it at your own destination.
6. **Self-referencing sub-workflow** — **Research**, **Extract**, and **Generate** all call `{{ $workflow.id }}` (this same workflow), routed by **EventRouter** on `eventType`. Don't rename or duplicate the workflow without checking these references. Each call runs in "each" mode with `waitForSubWorkflow: true`, so large queues process serially and can take a while.
7. **Seed the sheet** — add rows with `Service` and `Website` before running; only rows with empty stage columns are processed, so re-running is safe and idempotent per stage.

---

<!-- ARCHITECTURE:START -->
## Architecture

```mermaid
flowchart TD
    N0["When clicking ‘Test workflow’<br/><small>manualTrigger</small>"]
    N1["Web Search For API Schema<br/><small>httpRequest</small>"]
    N2["Scrape Webpage Contents<br/><small>httpRequest</small>"]
    N3["Results to List<br/><small>splitOut</small>"]
    N4["Recursive Character Text Splitter1<br/><small>textSplitterRecursiveCharacterTextSplitter</small>"]
    N5["Content Chunking @ 50k Chars<br/><small>set</small>"]
    N6["Split Out Chunks<br/><small>splitOut</small>"]
    N7["Default Data Loader<br/><small>documentDefaultDataLoader</small>"]
    N8["Set Embedding Variables<br/><small>set</small>"]
    N9["Execute Workflow Trigger<br/><small>executeWorkflowTrigger</small>"]
    N10["Execution Data<br/><small>executionData</small>"]
    N11["EventRouter<br/><small>switch</small>"]
    N12["Google Gemini Chat Model<br/><small>lmChatGoogleGemini</small>"]
    N13["Successful Runs<br/><small>filter</small>"]
    N14["For Each Document...<br/><small>splitInBatches</small>"]
    N15["Embeddings Google Gemini<br/><small>embeddingsGoogleGemini</small>"]
    N16["Has API Documentation?<br/><small>textClassifier</small>"]
    N17["Store Document Embeddings<br/><small>vectorStoreQdrant</small>"]
    N18["Embeddings Google Gemini1<br/><small>embeddingsGoogleGemini</small>"]
    N19["Google Gemini Chat Model1<br/><small>lmChatGoogleGemini</small>"]
    N20["Extract API Operations<br/><small>informationExtractor</small>"]
    N21["Search in Relevant Docs<br/><small>vectorStoreQdrant</small>"]
    N22["Wait<br/><small>wait</small>"]
    N23["Remove Dupes<br/><small>removeDuplicates</small>"]
    N24["Filter Results<br/><small>filter</small>"]
    N25["Research<br/><small>executeWorkflow</small>"]
    N26["Has Results?<br/><small>if</small>"]
    N27["Response Empty<br/><small>set</small>"]
    N28["Response OK<br/><small>set</small>"]
    N29["Combine Docs<br/><small>aggregate</small>"]
    N30["Template to List<br/><small>splitOut</small>"]
    N31["Query Templates<br/><small>set</small>"]
    N32["Google Gemini Chat Model2<br/><small>lmChatGoogleGemini</small>"]
    N33["For Each Template...<br/><small>splitInBatches</small>"]
    N34["Query & Docs<br/><small>set</small>"]
    N35["Identify Service Products<br/><small>informationExtractor</small>"]
    N36["Extract API Templates<br/><small>set</small>"]
    N37["Embeddings Google Gemini2<br/><small>embeddingsGoogleGemini</small>"]
    N38["Search in Relevant Docs1<br/><small>vectorStoreQdrant</small>"]
    N39["Combine Docs1<br/><small>aggregate</small>"]
    N40["Query & Docs1<br/><small>set</small>"]
    N41["For Each Template...1<br/><small>splitInBatches</small>"]
    N42["Merge Lists<br/><small>code</small>"]
    N43["Remove Duplicates<br/><small>removeDuplicates</small>"]
    N44["Append Row<br/><small>googleSheets</small>"]
    N45["Response OK1<br/><small>set</small>"]
    N46["Has Operations?<br/><small>if</small>"]
    N47["Response Empty1<br/><small>set</small>"]
    N48["Research Pending<br/><small>googleSheets</small>"]
    N49["Research Result<br/><small>googleSheets</small>"]
    N50["Research Error<br/><small>googleSheets</small>"]
    N51["Extract Pending<br/><small>googleSheets</small>"]
    N52["Research Event<br/><small>set</small>"]
    N53["Extract Event<br/><small>set</small>"]
    N54["Extract<br/><small>executeWorkflow</small>"]
    N55["Extract Result<br/><small>googleSheets</small>"]
    N56["Extract Error<br/><small>googleSheets</small>"]
    N57["Get API Operations<br/><small>googleSheets</small>"]
    N58["Contruct JSON Schema<br/><small>code</small>"]
    N59["Upload to Drive<br/><small>googleDrive</small>"]
    N60["Set Upload Fields<br/><small>set</small>"]
    N61["Response OK2<br/><small>set</small>"]
    N62["Generate Event<br/><small>set</small>"]
    N63["Generate Pending<br/><small>googleSheets</small>"]
    N64["Generate<br/><small>executeWorkflow</small>"]
    N65["Generate Error<br/><small>googleSheets</small>"]
    N66["Generate Result<br/><small>googleSheets</small>"]
    N67["Get All Extract<br/><small>googleSheets</small>"]
    N68["Get All Research<br/><small>googleSheets</small>"]
    N69["For Each Research...<br/><small>splitInBatches</small>"]
    N70["For Each Extract...<br/><small>splitInBatches</small>"]
    N71["Wait1<br/><small>wait</small>"]
    N72["All Research Done?<br/><small>if</small>"]
    N73["All Extract Done?<br/><small>if</small>"]
    N74["Get All Generate<br/><small>googleSheets</small>"]
    N75["All Generate Done?<br/><small>if</small>"]
    N76["For Each Generate...<br/><small>splitInBatches</small>"]
    N77["Wait2<br/><small>wait</small>"]
    N78["Has Results?1<br/><small>if</small>"]
    N79["Response Scrape Error<br/><small>set</small>"]
    N80["Has Results?3<br/><small>if</small>"]
    N81["Response No API Docs<br/><small>set</small>"]
    N22 --> N69
    N71 --> N70
    N77 --> N76
    N54 -->|0| N55
    N54 -->|1| N56
    N64 -->|0| N66
    N64 -->|1| N65
    N25 -->|0| N49
    N25 -->|1| N50
    N44 --> N45
    N11 -->|out0| N1
    N11 -->|out1| N31
    N11 -->|out2| N57
    N42 --> N46
    N29 --> N34
    N26 -->|true| N3
    N26 -->|false| N27
    N34 --> N33
    N23 --> N2
    N39 --> N40
    N56 --> N71
    N53 --> N54
    N78 -->|true| N16
    N78 -->|false| N79
    N80 -->|true| N8
    N80 -->|false| N81
    N40 --> N41
    N10 --> N11
    N55 --> N71
    N24 --> N23
    N65 --> N77
    N62 --> N64
    N50 --> N22
    N52 --> N25
    N51 --> N53
    N66 --> N77
    N67 --> N73
    N46 -->|true| N43
    N46 -->|false| N47
    N31 --> N30
    N49 --> N22
    N3 --> N24
    N13 --> N78
    N59 --> N61
    N63 --> N62
    N74 --> N75
    N68 --> N72
    N48 --> N52
    N6 --> N17
    N30 --> N33
    N73 -->|true| N74
    N73 -->|false| N70
    N43 --> N44
    N60 --> N59
    N75 --> N76
    N72 -->|true| N67
    N72 -->|false| N69
    N57 --> N58
    N7 -.document.-> N17
    N70 -->|0| N74
    N70 -->|1| N51
    N58 --> N60
    N14 -->|0| N28
    N14 -->|1| N5
    N76 --> N63
    N69 -->|0| N67
    N69 -->|1| N48
    N33 -->|0| N35
    N33 -->|1| N21
    N36 --> N41
    N41 -->|0| N20
    N41 -->|1| N38
    N20 --> N42
    N16 --> N80
    N2 --> N13
    N21 --> N29
    N8 --> N14
    N15 -.embedding.-> N17
    N9 --> N10
    N12 -.languageModel.-> N16
    N38 --> N39
    N18 -.embedding.-> N21
    N37 -.embedding.-> N38
    N19 -.languageModel.-> N20
    N32 -.languageModel.-> N35
    N35 --> N36
    N17 --> N14
    N1 --> N26
    N5 --> N6
    N0 --> N68
    N4 -.textSplitter.-> N7
```
<!-- ARCHITECTURE:END -->
