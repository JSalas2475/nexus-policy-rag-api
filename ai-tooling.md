# AI Tooling Used

## Tools

- **Cursor IDE with Claude (Auto/Agent mode):** Primary development environment for scaffolding, implementation, and iteration
- **Groq API:** LLM inference for generation and evaluation (LLM-as-judge)

## How AI Tools Were Used

### Project Scaffolding
AI generated the initial project structure, Flask routes, RAG pipeline modules, and configuration files based on the project rubric. This accelerated setup from empty workspace to working architecture in a single session.

### Policy Corpus Generation
AI authored 12 synthetic Nexus Technologies policy documents covering PTO, security, remote work, expenses, and other required topics. Documents were structured with headings and tables to support heading-aware chunking.

### RAG Pipeline Implementation
AI implemented ingestion, chunking, embedding, retrieval with re-ranking, generation prompts, and guardrails. The prompt template and citation extraction logic were iterated with AI assistance.

### Evaluation Suite
AI created the 20-question gold dataset and `scripts/evaluate.py` with groundedness, citation accuracy, and latency metrics.

### Documentation
AI drafted README, design-and-evaluation.md, and this file. Manual review ensured accuracy against actual implementation.

### CI/CD and Deployment
AI generated GitHub Actions workflow and Render blueprint configuration.

## What Worked Well

- Rapid end-to-end scaffolding from rubric requirements
- Generating coherent, structured policy corpus with consistent cross-references
- Creating evaluation questions aligned with corpus content
- Flask + LangChain + Chroma integration patterns

## What Required Manual Attention

- Retrieval score threshold tuning (similarity vs rerank scores use different scales)
- Ensuring citation format consistency in prompts
- Verifying chunk metadata integrity across file formats
- Testing guardrails with off-topic questions

## What Did Not Work as Expected

- Initial guardrails used rerank scores for threshold checks; fixed to use original similarity scores
- Cross-encoder model adds significant first-load time; mitigated with lazy loading

## Academic Integrity Note

AI tools were used as assistants for code generation and documentation. All design decisions, evaluation methodology, and final review were validated against the project rubric requirements. The policy corpus is synthetic and created for this assignment.
