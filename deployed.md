# Deployed Application

**Live URL:** https://nexus-policy-rag-api.onrender.com

## Endpoints

| URL | Description |
|-----|-------------|
| `/` | Chat UI |
| `/chat` | POST JSON API |
| `/health` | Service status |

## Verification

```bash
curl https://nexus-policy-rag-api.onrender.com/health
```

Expected: `"status": "ok"` and `"index_loaded": true`

## Notes

Render free tier services sleep after ~15 minutes of inactivity. The first request after sleep may take 30–60 seconds (cold start).
