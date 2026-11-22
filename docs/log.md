## Deployment (Render + Supabase)
- Deployed the API as a Docker container on Render (free tier), with Postgres on Supabase.
- Verified with curl on the live URL: /health, POST /tasks, GET /tasks. The row also appears in Supabase's Table Editor.
- Enabled Row Level Security on the tasks table so it isn't open through Supabase's public API. The app connects with the database password, so it is unaffected.

## One thing that broke
- Symptom: first Render deploy failed ("Exited with status 1").
- What I checked: the last log line said `No module named 'psycopg'`, and the traceback went through SQLAlchemy's psycopg (v3) dialect.
- Root cause: DATABASE_URL had the wrong driver prefix; the app installs psycopg2.
- Fix: changed the prefix to `postgresql+psycopg2://` in Render's environment settings; the redeploy went live.




## One more thing that broke (MCP server)
- Symptom: `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` when importing the server.
- What I checked: the error said this is mcp 2.x, where FastMCP was renamed. pip had installed 2.3.0 because the package was not pinned.
- Fix: pinned `mcp<2` in `mcp_server/requirements.txt` and reinstalled (now mcp 1.30.0).
- Side note: I first created the files in the wrong folder, outside the Git repo, and had to move them in.
- Checked against the live API: list and get return the task, and an unknown id gives "task not found".