# Runicorn

Local, open-source experiment tracking and visualization. 100% local. A lightweight, self-hosted alternative to W&B.

- Package/Library name: runicorn
- Default storage path: ./.runicorn
- Viewer: read-only, serves metrics/logs/media from local storage
- GPU telemetry: optional panel (reads nvidia-smi if available)

Quick start (SDK)
-----------------
```python
import runicorn as rn

run = rn.init(project="demo")
for epoch in range(3):
    rn.log({"epoch": epoch, "train_loss": 1.0/(epoch+1)})
# Or rn.log(key=value, epoch=epoch)

rn.summary(update={"best_val_acc_top1": 77.3})
rn.finish()
```

Launch viewer
-------------
```
runicorn viewer --storage ./.runicorn --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000

Frontend (dev)
--------------
For local frontend development with live-reload and API proxy:
```
./run_dev.ps1 -PythonExe "python"
```
Then open http://127.0.0.1:5173. The frontend proxies `/api/*` to `http://127.0.0.1:8000`.

See `web/README.md` for manual steps.

Storage layout
--------------
```
.runicorn/
  runs/
    <run_id>/
      meta.json
      status.json
      summary.json
      events.jsonl
      media/
```

Notes
-----
- The viewer is read-only. No train start/stop APIs.
- GPU telemetry is shown if `nvidia-smi` is available.
- Windows compatible.
