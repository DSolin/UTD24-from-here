import os
import subprocess, sys, threading, re, time
from fastapi import APIRouter

router = APIRouter(prefix="/crawler", tags=["Crawler"])

crawl_status = {
    "running": False,
    "progress": 0,
    "current": "",
    "new_articles": 0,
    "total_journals": 24,
    "error": None,
    "start_time": None,
}


def _run_crawl(days: int):
    global crawl_status
    crawl_status = {
        "running": True, "progress": 0, "current": "Starting...",
        "new_articles": 0, "total_journals": 24, "error": None,
        "start_time": time.strftime("%H:%M:%S"),
    }

    script_path = "/app/crawl_all.py"
    if not os.path.exists(script_path):
        crawl_status["error"] = "crawl_all.py not found in container"
        crawl_status["running"] = False
        return

    try:
        proc = subprocess.Popen(
            [sys.executable, "-u", script_path, str(days)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd="/app",
            env={**__import__('os').environ, "PYTHONUNBUFFERED": "1"}
        )

        for line in iter(proc.stdout.readline, ""):
            m = re.match(r"PROGRESS:(\d+)/24:(\w+):(\d+)", line.strip())
            if m:
                done = int(m.group(1))
                abbr = m.group(2)
                new = int(m.group(3))
                crawl_status["progress"] = int(done / 24 * 100)
                crawl_status["current"] = f"{abbr} ({done}/24)"
                crawl_status["new_articles"] += new

        proc.wait()

        if proc.returncode != 0:
            stderr = proc.stderr.read()[-500:]
            crawl_status["error"] = stderr if stderr else f"Exit code {proc.returncode}"
        else:
            crawl_status["progress"] = 100
            crawl_status["current"] = "Complete"

    except Exception as e:
        crawl_status["error"] = str(e)
    finally:
        crawl_status["running"] = False


@router.post("/trigger")
async def trigger_crawl(days: int = 30):
    global crawl_status
    if crawl_status["running"]:
        return {"message": "Already running", "status": crawl_status}

    thread = threading.Thread(target=_run_crawl, args=(days,), daemon=True)
    thread.start()
    return {"message": "Crawl started", "status": crawl_status}


@router.get("/status")
async def get_status():
    return crawl_status
