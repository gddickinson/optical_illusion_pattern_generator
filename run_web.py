"""Start the web interface: python run_web.py  ->  http://127.0.0.1:8127 (local only)."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("web.app:app", host="127.0.0.1", port=8127)
