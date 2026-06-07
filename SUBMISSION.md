# Instrucciones de Entrega — Proyecto RAG

## Paso 1: API Key Groq (5 min)

1. Ir a https://console.groq.com
2. Crear cuenta → API Keys → Create API Key
3. Copiar key en `.env`:
   ```
   GROQ_API_KEY=gsk_...
   ```

## Paso 2: Probar Localmente (10 min)

```powershell
cd "c:\Users\jorge\Downloads\AI Engineering Project"
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Editar .env con tu GROQ_API_KEY

python scripts/ingest.py --seed 42 --rebuild
flask --app app run
```

Abrir http://127.0.0.1:5000 y probar:
- "How many PTO days do new employees receive?"
- "What is the capital of France?" (debe rechazar)

> **Nota Windows:** Si falla torch, instalar [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) o usar solo Render para demo.

## Paso 3: Evaluación (10 min)

```powershell
python scripts/evaluate.py
```

Copiar métricas de `evaluation/results.json` a la tabla en `design-and-evaluation.md`.

## Paso 4: GitHub (10 min)

```powershell
git init
git add .
git commit -m "Complete RAG policy assistant project"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/nexus-policy-rag-api.git
git push -u origin main
```

En GitHub:
1. **Settings → Collaborators → Add `quantic-grader`**
2. **Settings → Secrets → Actions:**
   - `GROQ_API_KEY`
   - `RENDER_DEPLOY_HOOK_URL` (después del paso 5)

## Paso 5: Deploy Render (15 min)

1. https://render.com → Sign Up → New **Blueprint** (o Web Service)
2. Conectar repo GitHub
3. Render detecta `render.yaml` automáticamente
4. Agregar env var `GROQ_API_KEY` en dashboard
5. Esperar build (~5–10 min, descarga modelos)
6. Copiar URL pública → pegar en `deployed.md`
7. En Render → Settings → Deploy Hook → copiar URL → GitHub Secret `RENDER_DEPLOY_HOOK_URL`

Verificar:
- `https://TU-APP.onrender.com/health` → `"index_loaded": true`
- Chat funciona con preguntas de prueba

## Paso 6: Verificar CI/CD (5 min)

1. GitHub → Actions → confirmar workflow verde en push
2. Push trivial a `main` → confirmar deploy en Render

## Paso 7: Demo Video (5–10 min)

Grabar pantalla con voz en off cubriendo:

1. **Chat en vivo** — 3–4 preguntas (PTO, security, remote work)
2. **Citas** — mostrar badges con snippets
3. **Guardrail** — pregunta off-topic rechazada
4. **Arquitectura** — breve walkthrough de `design-and-evaluation.md`
5. **Evaluación** — mostrar resultados en `evaluation/results.json`
6. **CI/CD** — GitHub Actions corriendo verde
7. **Deployment** — URL pública funcionando

Si es proyecto grupal: todos en cámara + ID gubernamental.

## Paso 8: Submit en Quantic

1. Crear PDF con **2 links**:
   - Link al repo GitHub
   - Link al video demo (YouTube unlisted, Loom, etc.)
2. Dashboard Quantic → **Submit Project**

---

**Tiempo estimado total:** ~1 hora (excluyendo build Render y grabación video)
