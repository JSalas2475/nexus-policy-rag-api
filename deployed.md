# Deployed Application

## Status

Deployment pending. After deploying to Render, update this file with your live URL.

## Expected URL Format

```
https://nexus-policy-rag-api.onrender.com
```

## Deployment Steps

1. Push repository to GitHub
2. Create Render Web Service from `render.yaml` blueprint
3. Set `GROQ_API_KEY` in Render environment variables
4. Wait for build to complete (ingestion runs during build)
5. Verify endpoints:
   - `GET /health` → `{"status": "ok", "index_loaded": true}`
   - `GET /` → Chat UI
   - `POST /chat` → JSON response with citations

## Live URL

<!-- Replace with your actual URL after deployment -->
**URL:** _Not yet deployed — add URL here after Render setup_

## Notes

- Render free tier services spin down after 15 minutes of inactivity
- First request after sleep may take 30–60 seconds (cold start)
- Warm up the service before recording your demo video
