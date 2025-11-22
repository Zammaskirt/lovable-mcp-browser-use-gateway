import tomllib
from pathlib import Path

lock_path = Path(__file__).resolve().parent.parent / "uv.lock"
if not lock_path.exists():
    raise SystemExit("uv.lock not found")

data = tomllib.loads(lock_path.read_text())
heavy = []
for pkg in data.get("package", []):
    name = pkg.get("name", "")
    if name.startswith("nvidia-") or name in {"torch", "transformers", "sentence-transformers", "faiss-cpu"}:
        heavy.append((name, pkg.get("version", "?")))

if not heavy:
    print("No heavy ML/runtime packages detected in lock file.")
else:
    print("Heavy packages currently locked:")
    for name, version in heavy:
        print(f"- {name}=={version}")
