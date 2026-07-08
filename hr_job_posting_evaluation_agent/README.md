# HR Job Posting & Evaluation Agent

A full-cycle candidate-screening workflow that takes a job application from web form submission through AI resume scoring, custom interview questions, candidate email outreach, phone-screen scheduling, and screening-question generation — all tracked in Airtable.

Built for small hiring teams who want AI to handle the first-pass CV screen and the administrative overhead of an interview pipeline, while keeping every decision and artifact recorded for a human to review.

## What it does

1. **On form submission** (n8n Form Trigger) collects First Name, Last Name, Email, Phone, Years of experience, and a PDF CV upload, alongside a form description containing the actual job posting text (used as the job description reference).
2. **Upload CV to google drive** stores the uploaded PDF, and **applicant details** (Set) assembles the applicant's name, phone, email, experience, application date, and the resulting Drive `webViewLink`.
3. **Airtable** creates a new row in the "Applicants" table (base "Simple applicant tracker") with `Name`, `Phone`, `Email address`, `Applying for`, and `CV Link`.
4. **download CV** (Google Drive) re-downloads the file by its Drive link, and **Extract from File** (PDF operation) converts it to plain text.
5. **AI Agent** (backed by **OpenAI Chat Model**, with **Airtable1** as an attached tool for looking up the job description from the "Positions" table) compares the job description against the resume text and returns a qualification score between 0 and 1 plus a short reason, enforced by a **Structured Output Parser** (`{score, reason}`).
6. **shortlisted?** branches on `score >= 0.7`: qualifying candidates go to **Potential Hire** (Airtable update: `Stage` → "Interviewing", plus the score/reason); others go to **Rejected** (Airtable update: `Stage` → "No hire").
7. For shortlisted candidates, **generate questionnaires** (`@n8n/n8n-nodes-langchain.openAi`, gpt-4o-mini, with **Airtable2** as a job-description lookup tool) drafts 5 interview questions targeting specific projects, achievements, relevant skills, problem-solving, and culture fit.
8. **questionnaires** (n8n Form node) presents those 5 questions to the candidate (or interviewer) as a follow-up form, and **update questionnaires** (Airtable) writes the responses into a "Questonnaires and responses" field.
9. **Personalize email** (OpenAI, gpt-4o, with **job_posting** and **candidate_insights** as Airtable lookup tools) drafts a warm, specific outreach email referencing the candidate's actual strengths, and **Edit Fields** extracts `To`/`Subject`/`Email Content`. **Send Email** (SMTP) sends it.
10. **Book Meeting** (OpenAI, gpt-4o, with **Google Calendar** as a tool) checks the interviewer's calendar for a 30-minute slot the next business day and books it, returning start/end times; **update phone meeting time** (Airtable) records the booked slot.
11. **Screening Questions** (OpenAI, gpt-4o, with **job_posting1** and **candidate_insights1** as Airtable tools) generates a minimum of 5 phone-screen questions from the job description, CV, and questionnaire answers; **Edit Fields1** extracts the text and **screening questions** (Airtable) writes it to the applicant's record.

## Sample request

The entry point is the **On form submission** node, an n8n-hosted form at path `automation-specialist-application`. A submission includes:

```
First Name: Jane
Last Name: Doe
Email: jane.doe@example.com
Phone: 555123456
Years of experience: 4
Upload your CV: resume.pdf
```

The form's description field doubles as the job posting shown to applicants — edit it directly in **On form submission** to advertise a different role.

## Setup (~30 minutes)

1. **Airtable** — add an Airtable Personal Access Token credential to **Airtable**, **Rejected**, **Potential Hire**, **Airtable1**, **Airtable2**, **update questionnaires**, **job_posting**, **candidate_insights**, **job_posting1**, **candidate_insights1**, **update phone meeting time**, and **screening questions**. All point at base `appublMkWVQfHkZ09` ("Simple applicant tracker") with "Applicants" and "Positions" tables — either reuse the referenced Airtable template or repoint every node at your own base/tables.
2. **Google Drive** — add a Google Drive OAuth2 credential to **Upload CV to google drive** and **download CV**; both use a hardcoded target folder ("HR Test") — change the `folderId` to your own.
3. **OpenAI** — add API keys to **OpenAI Chat Model**, **generate questionnaires**, **Personalize email**, **Book Meeting**, and **Screening Questions** (two different OpenAI credentials appear across nodes — consolidate to one for consistency).
4. **Google Calendar** — add a Google Calendar OAuth2 credential to the **Google Calendar** tool node; it's hardcoded to a specific calendar (`gaturanjenga@gmail.com`) — change it to the interviewer's actual calendar.
5. **SMTP** — add SMTP credentials to **Send Email**; the `fromEmail` (`gatura@bulkbox.co.ke`) and email sign-off ("Regards, Francis") in the **Personalize email** prompt are hardcoded — update both to match your own sender identity.
6. **Shortlist threshold** — the 0.7 cutoff in **shortlisted?** is hardcoded; adjust to match your hiring bar.
7. **Job description source of truth** — the AI Agent, questionnaire generator, and screening-question generator all rely on Airtable's "Positions" table (via tool calls) for job description context, while the form description in **On form submission** is a separate, manually-maintained copy of the same text — keep both in sync when the posting changes.
