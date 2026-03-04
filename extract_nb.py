import json
import os

notebook_path = r"C:\Users\tanis\Downloads\06_RAG_Advanced_Complete_Pipeline.ipynb"
output_path = r"d:\Projects\patent_multimodal\reference_code.py"

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

with open(output_path, 'w', encoding='utf-8') as out:
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            out.write("".join(source))
            out.write("\n\n")

print(f"Extracted code to {output_path}")
