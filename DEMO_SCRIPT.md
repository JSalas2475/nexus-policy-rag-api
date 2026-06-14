# Demo Video Script — Nexus Policy RAG API

**Duration:** ~8–9 minutes | **Language:** English | **Project:** Individual

**Live app:** https://nexus-policy-rag-api.onrender.com  
**Repo:** https://github.com/JSalas2475/nexus-policy-rag-api

---

## Before Recording (10 min checklist)

- [ ] Tab 1: https://nexus-policy-rag-api.onrender.com/ (warm-up: ask 1 question)
- [ ] Tab 2: https://nexus-policy-rag-api.onrender.com/health
- [ ] Tab 3: https://github.com/JSalas2475/nexus-policy-rag-api
- [ ] Tab 4: GitHub → Actions → last run (green check)
- [ ] Tab 5: GitHub → design-and-evaluation.md
- [ ] Tab 6: GitHub → evaluation/results.json
- [ ] Camera + microphone ready
- [ ] Government ID ready
- [ ] Notifications silenced
- [ ] Copy the 4 demo questions below

### Questions to copy-paste

```
How many PTO days do new full-time employees receive annually?
```

```
What is the minimum password length required?
```

```
How many days per week must hybrid employees work in the office?
```

```
What is the capital of France?
```

---

## Quick timeline (print this)

```
0:00  CAMERA + ID → intro
0:50  /health → index_loaded true
1:15  Chat UI overview
1:30  PTO question → 15 days + citation
2:15  Security → 14 chars + citation
2:50  Remote work → 3 days + citation
3:20  France → guardrail refusal
4:00  DevTools POST /chat JSON (optional)
4:30  GitHub repo structure
5:15  design-and-evaluation.md
6:00  evaluation results (100/100/99.2%)
7:00  GitHub Actions green
7:40  render.yaml + deployed.md
8:10  ai-tooling.md → thank you
```

---

## BLOCK 1 — Camera intro (0:00 – 0:50)

**View:** Camera (your face)

**Do:**
1. Hold government ID next to face for 5 seconds
2. Lower ID
3. Switch to Share Screen (browser only)

**Say:**
> "Hi, my name is Jorge Salas. This is my AI Engineering project submission: the Nexus Policy RAG API. It's a retrieval-augmented generation application that answers employee questions about company policies using a vector index and an LLM. In this demo I'll walk through the live deployed app, the system architecture, evaluation metrics, and the CI/CD pipeline."

**Pause:** 2 seconds, then share screen.

---

## BLOCK 2 — Health check (0:50 – 1:15)

**Go to:** `https://nexus-policy-rag-api.onrender.com/health`

**Say:**
> "First, the health endpoint. This is a JSON API that confirms the service is running and that the vector index loaded successfully."

**Point at:** `"status": "ok"`, `"index_loaded": true`, `"model"`, `"embedding_model"`

**Say:**
> "index_loaded true means our Chroma vector database built during deployment is ready for retrieval."

---

## BLOCK 3 — Chat UI (1:15 – 1:30)

**Go to:** `https://nexus-policy-rag-api.onrender.com/`

**Say:**
> "This is the main chat interface. Users type a question, and the RAG pipeline retrieves relevant policy chunks, generates an answer with Groq, and returns citations with source snippets."

---

## BLOCK 4 — PTO question (1:30 – 2:15)

**Paste:** PTO question → Send → wait for response

**Say:**
> "Let me ask about PTO policy. The system should retrieve the paid time off document and answer with a citation."

**Point at:** "15 PTO days", citation badge `pto-policy`, hover for snippet, latency ms

**Say:**
> "The answer is grounded in the policy document, cites pto-policy as the source, and shows the relevant snippet. Response time is shown in milliseconds."

---

## BLOCK 5 — Security (2:15 – 2:50)

**Paste:** password question → Send

**Say:**
> "Next, an information security question — different policy domain, same pipeline."

**Point at:** "14 characters", citation `information-security`

**Say:**
> "Correct answer with citation to the security policy."

---

## BLOCK 6 — Remote work (2:50 – 3:20)

**Paste:** hybrid question → Send

**Say:**
> "Third question — hybrid remote work policy."

**Point at:** "3 days per week", citation `remote-work-policy`

---

## BLOCK 7 — Guardrail (3:20 – 4:00)

**Paste:** `What is the capital of France?` → Send

**Say:**
> "Now an important guardrail test. This question is not about company policies, so the system should refuse to answer."

**Point at:** exact message **"I can only answer about our company policies."**

**Say:**
> "The guardrail detected this is out-of-corpus and returned the refusal message instead of hallucinating an answer. This is one of three guardrails — along with answer length limits and mandatory citations."

---

## BLOCK 8 — API endpoint (4:00 – 4:30, optional)

**Do:** F12 → Network → send a question → click POST `chat` → Response tab

**Say:**
> "The same RAG logic is also exposed as a REST API. POST to /chat returns JSON with the answer, citations array, and latency in milliseconds."

**Point at:** `answer`, `citations`, `latency_ms`, `refused`

---

## BLOCK 9 — Repo structure (4:30 – 5:15)

**Go to:** GitHub repo root, scroll folders slowly

**Say:**
> "Now the codebase architecture. The project is organized into clear modules."

**Point at each folder:**
- `app/rag/` — RAG pipeline
- `data/policies/` — 12 synthetic policy documents
- `scripts/` — ingestion and evaluation CLIs
- `evaluation/` — gold questions and results
- `tests/` — automated smoke tests
- `.github/workflows/` — CI/CD

**Say:**
> "Documents are parsed from Markdown, TXT, and HTML, chunked by headings, embedded with FastEmbed, and stored in a Chroma vector database."

---

## BLOCK 10 — Design doc (5:15 – 6:00)

**Open:** `design-and-evaluation.md`

**Say:**
> "Design decisions are documented here. Key choices:"

**Point at:** diagram, Groq, Chroma, top-10→4 rerank, guardrails, Results table

**Say:**
> "All design choices and rationale are explained in this document as required by the project."

---

## BLOCK 11 — Evaluation (6:00 – 7:00)

**Open:** `evaluation/questions.json` → `scripts/evaluate.py` → `evaluation/results.json`

**Say:**
> "For evaluation, I created 20 gold-standard questions covering PTO, security, remote work, expenses, benefits, and other topics. The evaluate script runs all 20 through the pipeline and measures four metrics."

**Say the numbers aloud:**
- Groundedness: **100 percent**
- Citation accuracy: **100 percent**
- Partial match: **99.2 percent**
- Latency p50: **under 600 milliseconds**
- Latency p95: **under 3 seconds**

**Say:**
> "All metrics exceed the project targets. Per-question details are in the results file."

---

## BLOCK 12 — CI/CD (7:00 – 7:40)

**Go to:** GitHub → Actions → latest green run → job `test`

**Say:**
> "CI/CD runs on every push and pull request via GitHub Actions."

**Point at:** Install dependencies, Build vector index, Verify app import, Run tests

**Say:**
> "This ensures the app builds, the index ingests correctly, and all 13 tests pass before any deployment."

---

## BLOCK 13 — Deployment (7:40 – 8:10)

**Open:** `render.yaml` and `deployed.md`

**Say:**
> "The app is deployed on Render free tier. The blueprint runs pip install and ingestion during build, then starts Gunicorn with the Flask app. The live URL is documented in deployed.md."

**Point at:** https://nexus-policy-rag-api.onrender.com

---

## BLOCK 14 — Close (8:10 – 8:45)

**Open:** `ai-tooling.md`

**Say:**
> "I used Cursor with Claude for scaffolding, corpus generation, pipeline implementation, and documentation — all described in ai-tooling.md. The repository is shared with quantic-grader. That concludes my demo. Thank you."

**Stop recording.**

---

## After Recording

- [ ] Video is 5–10 minutes long
- [ ] You appear on camera with government ID
- [ ] Upload video (YouTube unlisted or Loom)
- [ ] Create PDF with repo link + video link
- [ ] Submit on Quantic dashboard

See [SUBMIT.md](SUBMIT.md) for submission steps.
