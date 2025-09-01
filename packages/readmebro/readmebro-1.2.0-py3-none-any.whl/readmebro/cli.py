import click
import json
import re
from pathlib import Path
import requests
from yaspin import yaspin
from .linking import generate_mermaid_graph

RAW_DOCS_DIR = Path("documentation/raw")
REGISTRY_FILE = RAW_DOCS_DIR / "readmebro_registry.json"
USAGE_FILE = RAW_DOCS_DIR / "readmebro_usage.json"

EXCLUDE_DIRS = {"venv", ".git", "documentation", "__pycache__"}

def query_ollama(model, prompt):
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False  # Ensure single JSON object, no streaming chunks
            },
            timeout=60
        )
        resp.raise_for_status()

        try:
            data = resp.json()
            return data.get("response", "").strip()
        except json.JSONDecodeError:
            # Show what Ollama actually returned to help debugging
            return f"[ReadMeBro] Ollama returned invalid JSON:\n{resp.text}"

    except requests.RequestException as e:
        return f"[ReadMeBro] Ollama request failed: {e}"


@click.group()
def cli():
    pass

@cli.command()
def scan():
    """Scan repo to find where registered functions/classes are used."""
    if not REGISTRY_FILE.exists():
        click.echo("[ReadMeBro] No registry file found. Run your code with @readmebro first.")
        return

    # Clean up old usage map before scanning
    if USAGE_FILE.exists():
        USAGE_FILE.unlink()
        click.echo("[ReadMeBro] Old usage map removed.")

    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        registry = json.load(f)

    usage_map = {item["name"]: [] for item in registry}

    with yaspin(text="Scanning repository for usage...", color="cyan") as spinner:
        try:
            for py_file in Path(".").rglob("*.py"):
                if any(part in EXCLUDE_DIRS for part in py_file.parts):
                    continue

                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                for idx, line in enumerate(lines, start=1):
                    for name in usage_map.keys():
                        if re.search(rf"\b{name}\b", line):
                            usage_map[name].append({
                                "file": str(py_file),
                                "line": idx,
                                "code": line.strip()
                            })

            with open(USAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(usage_map, f, indent=2)
            generate_mermaid_graph()

            spinner.ok("✅")
            click.echo(f"[ReadMeBro] Usage map saved → {USAGE_FILE}")

        except Exception as e:
            spinner.fail("💥")
            click.echo(f"[ReadMeBro] Scan failed: {e}")


@cli.command()
@click.option("--llm", default="none", help="LLM provider: ollama / none")
@click.option("--model", default="llama3", help="Model name if using ollama")
def generate(llm, model):
    """Generate documentation with optional LLM enrichment."""
    if not REGISTRY_FILE.exists():
        click.echo("[ReadMeBro] No registry file found.")
        return

    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        registry = json.load(f)

    usage_map = {}
    if USAGE_FILE.exists():
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            usage_map = json.load(f)

    doc_folder = Path("documentation")
    doc_folder.mkdir(exist_ok=True)
    output_file = doc_folder / "README.md"

    with yaspin(text=f"Generating docs with {llm}:{model}", color="cyan") as spinner:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for item in registry:
                    usage_info = usage_map.get(item["name"], [])
                    usage_text = "\n".join(
                        [f"- {u['file']} (line {u['line']}): `{u['code']}`" for u in usage_info]
                    ) or "Not used anywhere in scanned files."

                    if llm == "ollama":
                        prompt = (
                            f"You are a professional Python documentation generator.\n"
                            f"Analyze the following {item['type']} named '{item['name']}' from the file '{Path(item['file']).name}'.\n\n"
                            f"### Source Code\n```python\n{item['source']}\n```\n"
                            f"### Usage References\n{usage_text or 'No usage found.'}\n\n"
                            f"Generate concise, structured documentation in Markdown with these sections:\n"
                            f"1. **Summary** – One clear sentence about purpose.\n"
                            f"2. **Parameters** – List with types and short descriptions.\n"
                            f"3. **Returns** – Type and meaning.\n"
                            f"4. **Example** – Minimal working code snippet.\n"
                            f"5. **Related** – Other linked functions/classes in this codebase.\n"
                            f"6. **Tips** – Performance considerations, caveats, or gotchas.\n\n"
                            f"Rules:\n"
                            f"- Be factual, avoid filler.\n"
                            f"- Use bullet points where possible.\n"
                            f"- Keep output under 200 words.\n"
                        )

                        doc_text = query_ollama(model, prompt)
                    else:
                        doc_text = (
                            f"## {item['name']} ({item['type']})\n\n"
                            f"**File:** {item['file']}\n\n"
                            f"```python\n{item['source']}\n```\n\n"
                            f"**Usage:**\n{usage_text}\n"
                        )

                    f.write(f"{doc_text}\n\n")
            spinner.ok("✅")
            click.echo(f"[ReadMeBro] Documentation saved in {output_file}")
        except Exception as e:
            spinner.fail("💥")
            click.echo(f"[ReadMeBro] Documentation generation failed: {e}")

def main():
    """Main entry point for console_scripts."""
    cli()