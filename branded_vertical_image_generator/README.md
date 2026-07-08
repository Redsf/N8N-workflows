# Branded Vertical Image Generator

A content-repurposing pipeline that turns existing blog posts into short-form video assets: it pulls brand guidelines and SEO-tagged content from Airtable, drafts a 4-scene script with an LLM, and generates a 9:16 thumbnail plus one image per scene through Leonardo.ai — all tagged with brand-consistent art direction and logged back into an Airtable asset library.

Built for solo creators or small marketing teams who want to batch-produce on-brand vertical video visuals (Reels/Shorts/TikTok format) from written content they've already published.

## What it does

1. **When clicking 'Test workflow'** starts the run manually.
2. **Get Brand Guidelines** (Airtable search) pulls every row from the "Brand Guidelines" table (tone, voice, audience, do's/don'ts, etc.), and **Set Guidelines** tags each with its record `id`.
3. **Get SEO Keywords** (Airtable search) retrieves keyword records, and **Keyword Filter** keeps only rows whose `Keyword` field contains `"ai automation"` — the topic filter for this run.
4. **Remove Duplicates** dedupes by record `id`, then **Split Out Keywords** and **Get Content** (Airtable, looked up by the keyword's `RelatedContent` field) fetch the actual blog post content tied to each matching keyword.
5. **Split Out Content** and **Limit** cap the run to one piece of content at a time before it reaches script generation.
6. **Script Prep** (`@n8n/n8n-nodes-langchain.openAi`, gpt-4o-mini, with **Wikipedia** as an attached tool for fact-checking) writes a sub-30-second, 4-scene video script from the blog post's title and content, plus an image prompt per scene and one thumbnail prompt, returned as structured JSON.
7. **Split Out TN Prompt** extracts the thumbnail prompt and **Split Out Scenes** extracts the per-scene array; from here the workflow forks into two parallel image-generation pipelines.
8. **Thumbnail pipeline:** **Prompt Settings** sets the Leonardo Phoenix model ID and a composition hint ("rule of thirds, leading lines, & balance"), **Leo - Improve Prompt1** calls Leonardo's prompt-improvement endpoint, **Leo - Generate Image1** submits the generation job (768x1376, alchemy on), **Wait 30 Seconds** pauses for the async job, **Leo - Get imageId1** polls the result, and **Add Asset Info** logs the resulting image URL into Airtable's "Assets" table as a "TN - `<title>`" record.
9. **Scene pipeline:** **Loop Over Items** iterates each scene, and the same Leonardo sequence runs per scene — **Prompt Settings1** → **Leo - Improve Prompt** → **Leo - Generate Image** (ultra mode instead of alchemy) → **Wait 30 Seconds1** → **Leo - Get imageId** → **Add Asset Info1** (logs as "Scene - `<script text>`" in the Assets table) — looping back until all scenes are processed.

## Sample input

There is no webhook or form trigger — this workflow runs from **When clicking 'Test workflow'** and pulls its working set entirely from Airtable. The pinned example data shows the expected shape of a Brand Guidelines row:

```json
{
  "id": "rec4h9vioTgCwE7f1",
  "Name": "Tagline",
  "Description": "Smart Automation. Smarter Results."
}
```

and a Content Manager / SEO Keywords row needs a `Keyword` field and a `RelatedContent` field pointing at a linked blog-post record with `Title` and `Content`.

## Setup (~30 minutes)

1. **Airtable** — add an Airtable Personal Access Token credential to **Get Brand Guidelines**, **Get SEO Keywords**, **Get Content**, **Add Asset Info**, and **Add Asset Info1**. All are pinned to base `appRDq3E42JNtruIP` ("Content Manager") — replace with your own base/table IDs (Brand Guidelines, SEO Keywords, Assets tables).
2. **OpenAI** — add an API key to the **Script Prep** node (uses gpt-4o-mini).
3. **Leonardo.ai** — add a custom-auth (bearer token) credential named to match **Leo - Improve Prompt**, **Leo - Generate Image**, **Leo - Get imageId**, and their `1`-suffixed counterparts for the thumbnail path. The model ID `de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3` (Leonardo Phoenix) is hardcoded in **Prompt Settings** / **Prompt Settings1** — swap it if you use a different Leonardo model.
4. **Keyword filter** — the topic filter `"ai automation"` is hardcoded in **Keyword Filter**; change it to match the content you actually want to pull for a given run.
5. **Wait nodes are fixed at 30 seconds** — Leonardo generation can occasionally take longer, especially at high resolution; if you see empty results from **Leo - Get imageId** / **Leo - Get imageId1**, increase the **Wait 30 Seconds** / **Wait 30 Seconds1** duration.
6. **Image count** — sticky notes call out that `num_images` (currently 1) can be increased in both **Leo - Generate Image** and **Leo - Generate Image1** if you want multiple options per scene/thumbnail.
