# 📚 ReadMeBro

**ReadMeBro** is an AI-powered (and AI-optional) documentation assistant for Python codebases.  
It automatically scans your repository, finds functions and classes, detects where they are used, and generates **clear, concise documentation**.  
You can use it **with AI** (via Ollama + CodeLlama) or **without AI** for a plain text README.

---

## 🚀 Features

- **`@readmebro` Decorator** → Capture metadata of functions and classes.
- **Usage Mapping** → Find where each function/class is used in your codebase.
- **Two Documentation Modes**:
  - **Without AI** → Generate standard documentation with `readmebro generate`
  - **With AI** → Use `readmebro generate --llm ollama --model codellama:7b` for rich, contextual docs
- **JSON Registry** → Store raw scan data in `documentation/raw/`.
- **Function Graph** → Auto-generate a visual map of how functions connect.
- **Minimal Setup** → Works out of the box with or without AI.

---

## 📦 Installation

```bash
pip install readmebro
````

Or install directly from source:

```bash
git clone https://github.com/samartha-siddhartha/readmebro.git
cd readmebro
pip install -e .
```

---

## ⚡ Quick Start

```python
from readmebro.decorator import readmebro

@readmebro
def add_numbers(a, b):
    """Simple addition function"""
    return a + b
```

1️⃣ **Run your Python code at least once**
This ensures the `@readmebro` decorator captures the function/class in the registry.

2️⃣ **Scan your repository for usage**

```bash
readmebro scan
```

3️⃣ **Generate documentation**

---

### 🔹 Generate Documentation Without AI

```bash
readmebro generate
```

This will create a basic `README_GENERATED.md` from captured metadata.

---

### 🔹 Generate AI-Powered Documentation (Recommended: CodeLlama)

First, install **Ollama** and pull the CodeLlama model:

```bash
ollama pull codellama:7b
```

Then run:

```bash
readmebro generate --llm ollama --model codellama:7b
```

> ⚠️ Note: ReadMeBro uses the **local Ollama HTTP API** via `requests` (default: `http://localhost:11434`).
> No external servers are contacted unless *you* configure Ollama otherwise.

---

## 📂 Output Structure

```
documentation/
  raw/
    readmebro_registry.json   # Captured code metadata
    readmebro_usage.json      # Usage mapping
    README_GENERATED.md       # Generated documentation
    function_graph.md         # Mermaid function graph
    function_graph.html       # Interactive graph (pyvis)
```

---

## 🔗 Workflow Overview

```mermaid
graph TD
    A[Run your Python code] --> B[readmebro scan]
    B --> C[Usage & registry JSON]
    C --> D[readmebro generate]
    D --> E[README_GENERATED.md]
    D --> F[Function Graphs]
    F --> G[Mermaid + PyVis visualizations]
```

---

## 🖥 Requirements

* **Python 3.8+**
* *(Optional)* Ollama installed locally → [Install Ollama](https://ollama.ai/download)
* *(Optional)* Model downloaded for AI docs (recommended: CodeLlama 7B):

```bash
ollama pull codellama:7b
```

---

## 📌 Commands

```bash
readmebro scan
readmebro generate
readmebro generate --llm ollama --model codellama:7b
```

---

## 🤝 Contributing

We welcome contributions!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m "Added feature"`)
4. Push and create a Pull Request

---

## 📜 License

MIT License — Feel free to use and modify.

---

**Made with ❤️ + 🦙 by Samartha Siddhartha**

```

---

If you want, I can **add a workflow diagram** showing:  
`Run code → readmebro scan → readmebro generate`  
so that users can see the steps visually inside the README.  
That would make it extra intuitive for first-time users.
```
