# n8n Workflow Documentation Generator

A self-hosted documentation site for an entire n8n instance, served directly from a workflow. It exposes a browsable Docsify-powered site listing every workflow on the instance, auto-generates a Markdown/Mermaid description for any workflow that doesn't have one yet (using an LLM), and includes a live in-browser Markdown editor so docs can be corrected and saved back to disk without leaving the page.

Built for teams running enough n8n workflows that "what does this one do again" has become a real problem, and who want documentation living a click away from the workflows themselves rather than in a separate wiki.

## What it does

1. **docsify** and **single workflow** are the two webhook entry points (**single workflow** uses path `/:file`). **docsify** serves the app shell; **single workflow** handles page requests, tag filters, and edit/save actions.
2. **CONFIG** holds shared values used downstream: `project_path` (where generated `.md` files live), `instance_url`, and the raw HTML snippets injected into rendered pages.
3. For the root request, **Merge4** joins the trigger with **CONFIG** into **Main Page**, which renders the Docsify shell and returns it via **Respond with main page HTML**.
4. For `/:file` requests, **Merge5** routes through **file types** (Switch: `.md` vs. other) then **md files** (Switch on filename):
   - `README.md` → **Get All Workflows** (n8n API) → **Sort-workflows** (by `updatedAt`) → **Fill Workflow Table** (Markdown row per workflow with view/edit/recreate links) → **Instance overview** → **Respond with markdown**.
   - `summary.md` → **Get Workflow tags** → **Workflow Tags** (left nav pane) → **Respond with markdown**.
   - a `docs_<id>` request → **doc action** (Switch on `?action=view|edit|recreate|save`), covered below.
   - a `tag-<name>.md` request → re-routes to **Get All Workflows**, filtered by tag.
   - anything else → **No Operation, do nothing** → **Fallback file name** → **Respond with markdown**.
5. Inside **doc action**, the **view/edit/recreate** branches run **mkdir** and **Load Doc File**, converging through **Merge3**/**Merge** into **HasFile?**:
   - If a doc already exists (and action isn't `recreate`), **Extract from File** reads it, and **Is Action Edit?1** routes to the **Edit Page** live editor or plain **Workflow md content** view.
   - Otherwise, **Fetch Single Workflow1** pulls the workflow JSON, **Generate Mermaid Chart** (Code node) builds a flowchart from its `nodes`/`connections`, and **Basic LLM Chain** (**OpenAI Chat Model**, with **Auto-fixing Output Parser** wrapping **Structured Output Parser**) writes the description and node settings. **Generated Doc** assembles the Markdown, saved via **Convert to File** → **Save New Doc File**, then served through **Is Action Edit?2**.
   - The **save** branch runs posted content through **Edit Fields**, saves it the same way, and confirms via **Respond OK on Save** (no auth check — see Setup).
6. **Edit Page** renders a two-pane HTML editor (Markdown + live Docsify/Mermaid preview) with Save/Cancel buttons posting back with `?action=save`.

## Sample request

This workflow is driven by webhook GET/POST requests, not a form or chat trigger.

Load the instance overview:
```
GET /<single-workflow-webhook-path>/README.md
```

View or regenerate docs for a specific workflow (the segment after `docs_` is the workflow's n8n ID):
```
GET /<single-workflow-webhook-path>/docs_VY4TXYGmqth57Een.md?action=view
GET /<single-workflow-webhook-path>/docs_VY4TXYGmqth57Een.md?action=recreate
```

Open the live editor, then save:
```
GET  /<single-workflow-webhook-path>/docs_VY4TXYGmqth57Een.md?action=edit
POST /<single-workflow-webhook-path>/docs_VY4TXYGmqth57Een.md?action=save
Content-Type: application/json

{ "content": "# Updated docs\n\nEdited by hand." }
```

## Setup (about 20 minutes)

1. **n8n API credential** — add an n8n API key to **Fetch Single Workflow1**, **Get All Workflows**, and **Get Workflow tags** (currently reference a credential named "Ted n8n account" — replace with your own).
2. **OpenAI** — add your API key to **OpenAI Chat Model** (used for both doc generation and the auto-fixing parser).
3. **CONFIG node** — update `project_path` to a directory n8n can write to (defaults to `./.n8n/test_docs`), and confirm `instance_url` resolves; it's built from `N8N_PROTOCOL`/`N8N_HOST` for self-hosted instances but needs manual adjustment on n8n Cloud.
4. **Filesystem access** — **mkdir**, **Load Doc File**, and **Save New Doc File** assume local filesystem access from the n8n process. This won't work on a filesystem-restricted or containerized deployment without a mounted writable volume.
5. **No authentication on save** — the `?action=save` path (**Respond OK on Save**) writes arbitrary posted content to disk with no auth check. Put this behind a reverse proxy or add a credential/header check before exposing it publicly.
6. **Webhook paths** — **single workflow**'s path is `/:file`, so it catches any single-segment path under its webhook — verify this doesn't collide with other webhooks on the instance.

---

<!-- ARCHITECTURE:START -->
## Architecture

```mermaid
flowchart TD
    N0["CONFIG<br/><small>set</small>"]
    N1["Convert to File<br/><small>convertToFile</small>"]
    N2["HasFile?<br/><small>if</small>"]
    N3["Extract from File<br/><small>extractFromFile</small>"]
    N4["Main Page<br/><small>html</small>"]
    N5["Instance overview<br/><small>html</small>"]
    N6["Sort-workflows<br/><small>sort</small>"]
    N7["doc action<br/><small>switch</small>"]
    N8["Empty Set<br/><small>set</small>"]
    N9["Load Doc File<br/><small>readWriteFile</small>"]
    N10["Respond with markdown<br/><small>respondToWebhook</small>"]
    N11["Respond with HTML<br/><small>respondToWebhook</small>"]
    N12["Save New Doc File<br/><small>readWriteFile</small>"]
    N13["Blank Doc File<br/><small>set</small>"]
    N14["Fetch Single Workflow1<br/><small>n8n</small>"]
    N15["Fill Workflow Table<br/><small>set</small>"]
    N16["Basic LLM Chain<br/><small>chainLlm</small>"]
    N17["OpenAI Chat Model<br/><small>lmChatOpenAi</small>"]
    N18["Structured Output Parser<br/><small>outputParserStructured</small>"]
    N19["Auto-fixing Output Parser<br/><small>outputParserAutofixing</small>"]
    N20["Respond with main page HTML<br/><small>respondToWebhook</small>"]
    N21["Workflow Tags<br/><small>html</small>"]
    N22["No Operation, do nothing<br/><small>noOp</small>"]
    N23["Merge<br/><small>merge</small>"]
    N24["Fallback file name<br/><small>html</small>"]
    N25["mkdir<br/><small>executeCommand</small>"]
    N26["Merge1<br/><small>merge</small>"]
    N27["Edit Page<br/><small>html</small>"]
    N28["Workflow md content<br/><small>html</small>"]
    N29["Is Action Edit?1<br/><small>if</small>"]
    N30["Is Action Edit?2<br/><small>if</small>"]
    N31["Generate Mermaid Chart<br/><small>code</small>"]
    N32["Merge2<br/><small>merge</small>"]
    N33["Generated Doc<br/><small>set</small>"]
    N34["Passthrough<br/><small>noOp</small>"]
    N35["Merge3<br/><small>merge</small>"]
    N36["Merge4<br/><small>merge</small>"]
    N37["Merge5<br/><small>merge</small>"]
    N38["Edit Fields<br/><small>set</small>"]
    N39["Is Action Save?<br/><small>if</small>"]
    N40["Merge6<br/><small>merge</small>"]
    N41["Respond OK on Save<br/><small>respondToWebhook</small>"]
    N42["single workflow<br/><small>webhook</small>"]
    N43["file types<br/><small>switch</small>"]
    N44["Get All Workflows<br/><small>n8n</small>"]
    N45["md files<br/><small>switch</small>"]
    N46["Get Workflow tags<br/><small>n8n</small>"]
    N47["docsify<br/><small>webhook</small>"]
    N23 --> N29
    N25 --> N26
    N0 --> N36
    N0 --> N37
    N26 --> N2
    N32 --> N33
    N35 --> N30
    N36 --> N4
    N37 --> N43
    N40 --> N39
    N47 --> N0
    N47 --> N36
    N2 -->|true| N3
    N2 -->|false| N14
    N45 -->|out0| N44
    N45 -->|out1| N7
    N45 -->|out2| N46
    N45 -->|out3| N44
    N45 -->|out4| N22
    N27 --> N11
    N8 --> N26
    N4 --> N20
    N7 -->|out0| N25
    N7 -->|out0| N9
    N7 -->|out0| N34
    N7 -->|out1| N25
    N7 -->|out1| N9
    N7 -->|out1| N34
    N7 -->|out2| N25
    N7 -->|out2| N8
    N7 -->|out2| N34
    N7 -->|out3| N38
    N43 --> N45
    N38 --> N1
    N38 --> N40
    N34 --> N35
    N34 --> N23
    N33 --> N1
    N33 --> N30
    N9 --> N26
    N21 --> N10
    N13 --> N30
    N6 --> N15
    N16 --> N32
    N1 --> N12
    N39 --> N41
    N42 -->|0| N0
    N42 -->|0| N37
    N42 -->|1| N0
    N42 -->|1| N37
    N29 -->|true| N13
    N29 -->|false| N16
    N29 -->|false| N32
    N30 -->|true| N27
    N30 -->|false| N28
    N3 --> N35
    N44 --> N6
    N46 --> N21
    N5 --> N10
    N17 -.languageModel.-> N16
    N17 -.languageModel.-> N19
    N12 --> N40
    N24 --> N10
    N15 --> N5
    N28 --> N10
    N14 --> N31
    N14 --> N23
    N31 --> N23
    N22 --> N24
    N18 -.outputParser.-> N19
    N19 -.outputParser.-> N16
```
<!-- ARCHITECTURE:END -->
