# Gap Analysis — RAG Policy Assistant (Rúbrica Calificación 5)

## Resumen

| Área | Estado | Notas |
|------|--------|-------|
| Corpus (5–20 docs) | PASS | 12 documentos (9 MD, 2 TXT, 1 HTML) |
| Environment & Reproducibility | PASS | venv, requirements.txt, README, seed=42 |
| Ingestion & Indexing | PASS | MD/TXT/HTML/PDF parser, chunking, HF embeddings, Chroma |
| RAG Pipeline | PASS | Top-10 retrieval, cross-encoder rerank top-4, Groq generation |
| Guardrails | PASS | Out-of-corpus, length limit, mandatory citations |
| Web App | PASS | `/`, `POST /chat`, `GET /health` |
| CI/CD | PASS | GitHub Actions on push/PR + deploy hook on main |
| Evaluation | PASS | 20 preguntas; groundedness 100%, citation 100%, latency OK |
| Documentation | PASS | README, design-and-evaluation.md, ai-tooling.md |
| Deployment | PENDING | **Acción manual:** deploy en Render + URL en deployed.md |
| Demo Video | PENDING | **Acción manual:** grabar 5–10 min |
| GitHub Grader | PENDING | **Acción manual:** invitar `quantic-grader` |

## Checklist Detallado

### Requisitos Obligatorios

- [x] Corpus coherente de políticas corporativas (12 docs, ~40–60 páginas estimadas)
- [x] Virtual environment + requirements.txt
- [x] README con setup y run instructions
- [x] Seeds fijos (seed=42 en ingest y evaluate)
- [x] Parse multi-formato (MD, TXT, HTML, PDF*)
- [x] Chunking con overlap
- [x] Embeddings gratuitos (HuggingFace local)
- [x] Chroma vector DB persistente
- [x] Top-k retrieval + re-ranking
- [x] Prompt con citas inyectadas
- [x] Guardrails: refuse out-of-corpus, length limit, cite sources
- [x] Flask UI en `/`
- [x] API `POST /chat` con citations y snippets
- [x] API `GET /health` JSON
- [x] GitHub Actions CI (install, ingest, import, pytest)
- [x] 20 preguntas de evaluación (15–30 requerido)
- [x] Métricas: groundedness, citation accuracy, latency
- [x] design-and-evaluation.md
- [x] ai-tooling.md

*PDF: parser implementado; corpus usa MD/TXT/HTML (suficiente para demo).

### Requisitos Calificación 5 (Excelencia)

- [x] Arquitectura modular bien estructurada (`app/rag/`, routes, scripts)
- [x] Re-ranking con cross-encoder
- [x] Tests automatizados (13 tests passing)
- [ ] Deployment público funcional → **PENDIENTE (Render)**
- [ ] Resultados de evaluación reales → **PENDIENTE (correr evaluate.py)**
- [ ] Demo video → **PENDIENTE**

## Gaps Cerrados Durante Implementación

1. **Lazy imports** — Evita cargar torch/Groq al importar módulos
2. **Chunker custom** — Sin dependencia de langchain-text-splitters (evita import chain a torch en tests)
3. **Health endpoint** — Verifica index sin cargar embeddings
4. **Guardrail threshold** — Usa similarity score (no rerank score) para out-of-corpus
5. **wsgi.py** — Entry point confiable para Gunicorn en Render

## Acciones Pendientes (Usuario)

Ver [SUBMISSION.md](SUBMISSION.md) para instrucciones paso a paso.

1. Obtener Groq API key
2. Push a GitHub + invitar `quantic-grader`
3. Deploy en Render + actualizar deployed.md
4. Ejecutar `python scripts/evaluate.py` y actualizar design-and-evaluation.md con resultados
5. Grabar demo video (5–10 min)
6. Submit PDF con links en Quantic dashboard

## Riesgo Residual

| Riesgo | Mitigación |
|--------|------------|
| Windows local sin VC++ Redistributable | Usar Render/Linux; instalar [VC++ Redist](https://aka.ms/vs/17/release/vc_redist.x64.exe) para dev local |
| Render cold start | Warm-up request antes de demo |
| Groq rate limits en eval | Script incluye sleep 0.5s entre queries |
