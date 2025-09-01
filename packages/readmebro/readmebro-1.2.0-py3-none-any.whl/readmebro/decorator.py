import inspect
import json
from pathlib import Path

RAW_DOCS_DIR = Path("documentation/raw")
RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = RAW_DOCS_DIR / "readmebro_registry.json"



def readmebro(obj):
    """Decorator to capture function/class metadata for documentation."""
    try:
        source = inspect.getsource(obj)
        source_lines = source.splitlines()
        source_lines = [line for line in source_lines if "@readmebro" not in line.strip()]
        source = "\n".join(source_lines)

        filepath = Path(inspect.getfile(obj)).resolve()
        filepath = filepath.relative_to(Path.cwd())
    except Exception as e:
        source = f"Could not retrieve source: {e}"
        filepath = None

    entry = {
        "name": obj.__name__,
        "type": "class" if inspect.isclass(obj) else "function",
        "file": str(filepath) if filepath else "unknown",
        "source": source
    }

    if inspect.isclass(obj):
        entry["bases"] = [base.__name__ for base in obj.__bases__]
        methods = {}
        for name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
            try:
                src_file = inspect.getsourcefile(method)
                # Skip dynamically generated or in-memory functions
                if not src_file or src_file == "<string>":
                    continue
                methods[name] = inspect.getsource(method)
            except (OSError, TypeError):
                continue
        entry["methods"] = methods

    existing = []
    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []

    existing.append(entry)

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    return obj
