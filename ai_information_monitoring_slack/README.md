# AI-Powered Information Monitoring (Slack)

Monitors a list of RSS feeds for new articles on a chosen topic, filters out anything irrelevant with an LLM classifier, scrapes the relevant ones with Jina AI, and posts a Slack-formatted summary to a monitoring channel — with every article's outcome logged to Google Sheets so nothing gets processed twice.

Built for teams or individuals who want a standing "watch this topic across these sites" feed piped straight into Slack, without manually checking multiple blogs.

## What it does

1. **Schedule Trigger** runs every 15 minutes.
2. **Google Sheets - Get article monitored database** loads the `article_database` sheet (every URL already processed), and **Set field - existing_url** normalizes each row's `article_url` into a plain `existing_url` string for comparison.
3. **Google Sheets - Get RSS Feed url followed** (execute-once) loads the list of RSS feed URLs to monitor from the `rss_feed` sheet.
4. **RSS Read** fetches each feed, and **Code** compares the feed's article links against the `existing_url` list, returning only genuinely new articles (or a `"No new articles found."` message if there are none).
5. **If** checks for that message — if none found, routes to **No Operation, do nothing**; otherwise continues to relevance filtering.
6. **Relevance Classification for Topic Monitoring** (a Text Classifier backed by **OpenAI Chat Model1**) reads each article's title and snippet and classifies it `relevant` or `not_relevant` against a configurable topic description (default: AI, data science, machine learning, big data).
7. **Not relevant** articles go to **Set fields - Not relevant articles** (tagging `summarized: "NO (not relevant)"`) and are logged via **Google Sheets - Add relevant articles** (despite the name, this appends to the same `article_database` sheet) so they're never re-evaluated.
8. **Relevant** articles go to **Jina AI - Read URL**, which scrapes the full article content as Markdown via the Jina Reader API (`r.jina.ai/<url>`).
9. **Basic LLM Chain** (backed by **OpenAI Chat Model**) summarizes the scraped Markdown and formats it directly in Slack's markdown syntax — bolded section headers, bullet points, and a clickable `<url|title>` link — per a detailed system prompt with a full worked example.
10. **Slack1** posts the formatted summary to a Slack channel, and in parallel **Set Fields - Relevant Articles** (tagging `summarized: "YES"` and storing the summary text) feeds **Google Sheets - Add relevant article**, logging the article so it isn't reprocessed on the next 15-minute run.

## Setup (~20 minutes)

1. **Google Sheets** — copy the "Template - AI-Powered Information Monitoring" sheet (linked in the sticky notes) and re-point **Google Sheets - Get article monitored database**, **Google Sheets - Get RSS Feed url followed**, **Google Sheets - Add relevant articles**, and **Google Sheets - Add relevant article** at your copy's document ID, using a service account credential. Populate the `rss_feed` sheet with the feed URLs you want to monitor.
2. **OpenAI** — add API credentials to **OpenAI Chat Model** (summarization) and **OpenAI Chat Model1** (relevance classification).
3. **Jina AI** — **Jina AI - Read URL** works without an API key (at reduced rate limits) or with a free Jina AI account key for higher throughput; add a credential/header if you have one.
4. **Slack** — add an OAuth2 credential to **Slack1** and select your target channel (default is `topic-monitoring`).
5. **Topic customization** — the relevance categories in **Relevance Classification for Topic Monitoring** are hardcoded around AI/data science; edit the category descriptions to match whatever topic you actually want monitored.
6. **Scraping compliance** — Jina AI's reader performs web scraping on your behalf; confirm this complies with the terms of service and legal regulations for the sites you're monitoring before enabling on a schedule.
7. Verify column names in your copied Google Sheet match the field names used by the Set nodes (`article_url`, `summarized`, `summary`, `website`, `fetched_at`, `publish_date`), since the Add-row nodes use auto-mapped columns.
