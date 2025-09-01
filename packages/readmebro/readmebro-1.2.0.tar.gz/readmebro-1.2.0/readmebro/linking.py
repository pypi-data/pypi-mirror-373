import json
from pathlib import Path
import networkx as nx
from pyvis.network import Network

USAGE_FILE = Path("documentation/raw/readmebro_usage.json")
GRAPH_HTML_FILE = Path("documentation/function_graph.html")
GRAPH_MD_FILE = Path("documentation/function_graph.md")

def generate_mermaid_graph():
    """Generate an interactive function/file usage graph with function call edges."""
    if not USAGE_FILE.exists():
        print("[ReadMeBro] No usage file found.")
        return

    with open(USAGE_FILE, "r", encoding="utf-8") as f:
        usage_map = json.load(f)

    if not usage_map:
        print("[ReadMeBro] Usage map empty.")
        return

    G = nx.DiGraph()
    nodes = {}

    # Build nodes and edges
    for func_name, usages in usage_map.items():
        nodes[func_name] = "function"
        G.add_node(func_name, type="function")

        for u in usages:
            file_node = Path(u.get("file", "")).stem
            if not file_node:
                continue
            nodes[file_node] = "file"
            G.add_node(file_node, type="file")

            # Function -> file edge
            G.add_edge(func_name, file_node)

            # Function -> function call edges
            code_line = u.get("code", "")
            for other_func in usage_map.keys():
                if other_func != func_name and other_func in code_line:
                    G.add_edge(func_name, other_func)

    if G.number_of_nodes() == 0:
        print("[ReadMeBro] No nodes to render.")
        return

    # Create PyVis network
    net = Network(height="800px", width="100%", directed=True)
    for node, data in G.nodes(data=True):
        color = "#f9a" if data["type"] == "function" else "#9af"
        # Ensure node names are strings
        net.add_node(str(node), label=str(node), color=color)

    for source, target in G.edges():
        net.add_edge(str(source), str(target))

    # Safe rendering
    try:
        html_content = net.generate_html()  # safer than net.show()
        GRAPH_HTML_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(GRAPH_HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[ReadMeBro] Interactive graph saved → {GRAPH_HTML_FILE}")

    except Exception as e:
        print(f"[ReadMeBro] Failed to generate interactive graph: {e}")
        print("[ReadMeBro] Falling back to Mermaid Markdown...")

        # Fallback Mermaid Markdown graph
        edges = set()
        for source, target in G.edges():
            edges.add(f"    {source} --> {target}")

        mermaid_lines = ["```mermaid", "graph TD"]
        for node, node_type in nodes.items():
            if node_type == "function":
                mermaid_lines.append(f'    {node}["{node}"]:::func')
            else:
                mermaid_lines.append(f'    {node}["{node}"]:::file')
        mermaid_lines.extend(sorted(edges))
        mermaid_lines.append("""
    classDef func fill:#f9f,stroke:#333,stroke-width:1px;
    classDef file fill:#bbf,stroke:#333,stroke-width:1px;
    ```""")

        GRAPH_MD_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(GRAPH_MD_FILE, "w", encoding="utf-8") as f:
            f.write("## 🔗 Function/Class Usage Graph\n\n")
            f.write("\n".join(mermaid_lines))

        print(f"[ReadMeBro] Mermaid Markdown graph saved → {GRAPH_MD_FILE}")
