# Proxmox Infrastructure AI Agent

A conversational agent that turns natural-language requests into live Proxmox VE API calls — creating, cloning, resizing, migrating, starting, stopping, or deleting VMs across a multi-node cluster without anyone touching the Proxmox UI or hand-writing API payloads.

Built for infrastructure teams who want a chat-driven front end over Proxmox: type "create a VM with 4 cores and 8GB RAM on psb1" and get a real VM, not a suggestion.

## What it does

1. **When chat message received** (or the alternate **Telegram Trigger**, **Gmail Trigger**, **Webhook** entry points also wired into the canvas) captures the user's request.
2. **AI Agent** is a ReAct agent running on **Google Gemini Chat Model**, given three tools — **Proxmox** (a live HTTP tool pointed at the cluster's `/cluster/status` endpoint, seeded with the node map for psb1/psb2/psb3), **Proxmox API Wiki**, and **Proxmox API Documentation** — plus a detailed system prompt that enforces strict JSON output (`response_type`, `url`, `details`) and default behaviors (default node, auto-incrementing VM IDs, omitting unset optional fields).
3. Its output is validated by an **Auto-fixing Output Parser** backed by **Structured Output Parser** (schema example includes `vmid`, `cores`, `memory`, `net0`, `disk0`) and a second **Google Gemini Chat Model1**, which retries the agent's output if it doesn't match the schema.
4. **Switch** routes on `output.response_type` into five branches: `GET`, `POST`, `Update` (PUT), `OPTIONS`, and `DELETE`.
5. **GET** requests go straight to **HTTP Request**, which calls the Proxmox API and pipes the result into **Structure Response** (a Code node that flattens the JSON into a single string) and then **AI Agent1** (a second Gemini-backed agent) that turns the raw Proxmox response into a human-readable summary.
6. **POST** requests go through an **If** node checking whether `output.details` exists — with details, **HTTP Request1** posts the body; without details (e.g. a start/stop action), **HTTP Request2** posts with no body. Both branches converge on **Merge**.
7. **DELETE** requests go through **If1** the same way into **HTTP Request3** / **HTTP Request4**, converging on **Merge1**.
8. Both merge paths feed **Structgure Response from Proxmox** (parses the Proxmox UPID string into node, task ID, timestamp, operation, and user) and then **Format Response and Hide Sensitive Data**, which converts the hex timestamp to a readable date and returns a plain-language confirmation message — without ever exposing the API token.

## Sample request

Using the chat trigger (**When chat message received**), send a message like:

```
Create a VM with ID 105, 4 cores, 8GB RAM, and a 10GB disk on node psb1 using virtio networking.
```

The agent replies with a structured plan internally (e.g. `{"response_type":"POST","url":"/nodes/psb1/qemu","details":{"vmid":105,"cores":4,"memory":8192,...}}`), executes it against Proxmox, and returns a plain-English confirmation such as "The VM with ID 105 has been successfully configured to be created on node psb1."

Other example prompts that exercise different branches: "List all VMs on psb1" (GET), "Delete VM 105 on psb1" (DELETE), "Migrate VM 202 from psb2 to psb3" (POST).

## Setup (~20 minutes)

1. **Proxmox API token** — create an API token in the Proxmox datacenter, then in n8n create a **Header Auth** credential named `Proxmox` with header name `Authorization` and value `PVEAPIToken=<user>@<realm>!<token-id>=<token-value>`. Attach it to every node that calls Proxmox directly: **Proxmox** (tool), **HTTP Request** through **HTTP Request4**, and **Webhook** (if used as a trigger).
2. **Google Gemini** — add a Google PaLM/Gemini API credential to **Google Gemini Chat Model**, **Google Gemini Chat Model1**, and **Google Gemini Chat Model2**. Any chat model (OpenAI, Anthropic, Ollama) can be swapped in instead.
3. **Hardcoded cluster endpoints** — the workflow hardcodes `https://10.11.12.101:8006` (and `.102`) as the Proxmox node addresses inside the **Proxmox** tool description, **HTTP Request** nodes, and the **AI Agent** system prompt. Update all of these to match your own cluster's IPs/hostnames and node names (`psb1`/`psb2`/`psb3` throughout).
4. **`allowUnauthorizedCerts: true`** is set on every HTTP Request node — this assumes a self-signed Proxmox cert. Remove it if you have a trusted cert.
5. **Optional triggers** — **Telegram Trigger**, **Gmail Trigger**, and **Webhook** are included as alternative entry points but are not connected to the main flow; wire one in if you don't want to use n8n's built-in chat.
6. This workflow performs real, destructive infrastructure operations (VM creation, deletion, migration) — test against a non-production Proxmox cluster first.
