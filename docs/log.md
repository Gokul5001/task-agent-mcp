## Deployment (Render + Supabase)
- Deployed the API as a Docker container on Render (free tier), with Postgres on Supabase.
- Verified with curl on the live URL: /health, POST /tasks, GET /tasks. The row also appears in Supabase's Table Editor.
- Enabled Row Level Security on the tasks table so it isn't open through Supabase's public API. The app connects with the database password, so it is unaffected.

## One thing that broke
- Symptom: first Render deploy failed ("Exited with status 1").
- What I checked: the last log line said `No module named 'psycopg'`, and the traceback went through SQLAlchemy's psycopg (v3) dialect.
- Root cause: DATABASE_URL had the wrong driver prefix; the app installs psycopg2.
- Fix: changed the prefix to `postgresql+psycopg2://` in Render's environment settings; the redeploy went live.