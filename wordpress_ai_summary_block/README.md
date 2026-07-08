# AI-Generated Summary Block for WordPress

Automatically adds a short, AI-written bullet-point summary to the top of WordPress posts — no plugin required. The workflow pulls post content, classifies whether a summary already exists, generates one with OpenAI, injects it back into the post via the WordPress REST API, and logs the result to Google Sheets with a Slack notification.

Built for content teams and blog owners who want a lightweight, self-hosted alternative to WordPress "AI summary" plugins, with full control over the prompt and styling.

## What it does

1. **When clicking 'Test workflow'** (manual trigger) drives the default test path; two alternate triggers are wired in but disabled — **Schedule Trigger** (polls on an interval) and **Webhook** (fires from a WordPress-side hook), each feeding a different retrieval path.
2. On the manual/schedule path, **WordPress - Get All Posts** (or **WordPress - Get Last Posts**, filtered by **Date & Time - Substract** from the schedule interval) pulls posts, and **Loop Over Items** processes them one at a time.
3. **Google Sheets - Get rows** looks up the post's `post_id` in the tracking sheet, and an **If** node checks whether a match already exists — if found, the post is skipped straight back to **Loop Over Items**; if not, it proceeds via **WordPress - Get Post2** (fetched with `context=edit` to get raw content).
4. **HTML to Markdown** converts the raw post HTML into Markdown so the LLM parses structure more reliably.
5. **Text Classifier** (powered by **OpenAI Chat Model**) does a second-pass check: does the content already contain an "AI Summary"? If `summarized`, the post is skipped (routed to **Loop Over Items**); if `not_summarized`, it proceeds to summarization — this is a safety net in case a post has a summary that isn't yet logged in Sheets.
6. **OpenAI** (GPT-4o-mini) generates the summary as a styled HTML block (`<!-- wp:html -->` with a bullet list under a "✨ AI Summary" heading), following a strict system prompt with worked good/bad examples.
7. **Wordpress - Update Post** prepends the generated HTML to the post's existing content and updates the excerpt, preserving any existing manual excerpt.
8. **Set fields - Prepare data for Gsheets & Slack** builds `post_id`, `title`, `post_link`, `edit_link`, `summary`, and `summary_date`.
9. **Google Sheets - Add Row** logs the processed post to the tracking sheet (auto-mapped columns), and **Slack - Notify Channel** posts a message with the post title, link, and edit link to a Slack channel.

## Setup (~20 minutes)

1. **OpenAI** — add credentials to **OpenAI Chat Model** (used by the Text Classifier) and **OpenAI** (used for summary generation, model `gpt-4o-mini`).
2. **WordPress** — add REST API credentials to **WordPress - Get All Posts**, **WordPress - Get Last Posts**, **WordPress - Get Post1**, **WordPress - Get Post2**, and **Wordpress - Update Post**. Replace the hardcoded `<your-domain.com>` placeholders in **Wordpress - Update Post**'s URL and in **Set fields - Prepare data for Gsheets & Slack**'s `edit_link` field with your real WordPress domain.
3. **Google Sheets** — copy the "Template - AI Summary WordPress Posts" sheet (linked in the sticky notes) and re-point **Google Sheets - Get rows** and **Google Sheets - Add Row** at your copy's document ID and the `AI-Summarized Posts` sheet, using a service account credential.
4. **Slack** — add OAuth2 credentials to **Slack - Notify Channel** and select your own channel (default is `wp-posts-ai`); consider disabling this node on the first run so a backlog of posts doesn't flood the channel.
5. **Choose one trigger for production** — the manual trigger is for testing only. Enable either **Schedule Trigger** (simple polling, works well with the **Loop Over Items** batch pattern) or **Webhook** (event-driven from a WordPress hook, pairs with **Set fields - From Webhook input**) and disable the other. If using the webhook, add a Header Auth credential matching what your WordPress-side call sends.
6. **Post limit safety** — **WordPress - Get All Posts** ships without a hard limit in this template; consider adding filters (category, tag, date) before enabling on a large blog, since every summarized post costs an OpenAI call.
7. **Prompt customization** — the OpenAI system prompt in the **OpenAI** node is written around an electric-vehicle blog example; update the topic framing and the good/bad output examples to match your own site's subject matter and HTML styling.
