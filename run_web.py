"""Start the web interface: http://127.0.0.1:8256 (the blog's own Django pages are at /django/).

Uses mysite/settings_demo.py: a separate demo database in .web_demo/, created by the blog's migrations and
seeded with labelled demo posts. Install first: pip install -r requirements-web.txt
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("web.app:app", host="127.0.0.1", port=8256)
