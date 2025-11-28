# roi_watch.py
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

# Folder to watch
WATCH_DIR = os.path.join(os.getcwd(), "examples")

class ROIScriptHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".roi"):
            print(f"🔄 Change detected: {event.src_path}")
            # Call ROI-DSL compiler
            output_dir = "cloudflare"
            cmd = ["python", "roi_compile.py", "compile", event.src_path, "--output", output_dir]
            subprocess.run(cmd)
            print(f" Recompiled {os.path.basename(event.src_path)} → {output_dir}")

if __name__ == "__main__":
    observer = Observer()
    handler = ROIScriptHandler()
    observer.schedule(handler, WATCH_DIR, recursive=False)
    observer.start()
    print(f"👀 Watching for ROI-DSL file changes in {WATCH_DIR} ...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
